"""Private, bounded image-job HTTP API. No framework upload or static-file routes."""

from collections import deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
import csv
from importlib.metadata import PackageNotFoundError, version
from io import BytesIO, StringIO
import json
from pathlib import Path
import platform
import secrets
import shutil
import tempfile
import threading
import time
from typing import Any
import warnings

from anyio import fail_after
from fastapi import FastAPI, HTTPException, Request
from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.concurrency import run_in_threadpool


FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".bmp": "BMP", ".webp": "WEBP"}
MAX_BYTES = 10_000_000
MAX_PIXELS = 12_000_000
CSV_COLUMNS = ["source_filename", "object_type", "class_id", "class_name", "label", "confidence",
               "x1", "y1", "x2", "y2", "width", "height"]


def normalize(content, filename):
    expected = FORMATS.get(Path(filename).suffix.lower())
    if not expected:
        raise HTTPException(415, "Choose a PNG, JPG, BMP, or WebP image; checkpoints are never accepted.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as source:
                if source.format != expected:
                    raise HTTPException(415, "The decoded image format does not match its filename.")
                if source.width * source.height > MAX_PIXELS:
                    raise HTTPException(413, "Image exceeds 12 megapixels.")
                if getattr(source, "n_frames", 1) != 1:
                    raise HTTPException(415, "Choose a still image, not an animation.")
                source.verify()
            with Image.open(BytesIO(content)) as source:
                oriented = ImageOps.exif_transpose(source).convert("RGBA")
                image = Image.new("RGB", oriented.size, "white")
                image.paste(oriented, mask=oriented.getchannel("A"))
                output = BytesIO()
                image.save(output, format="PNG")
                return output.getvalue(), image.size
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(422, "Image is corrupt, unsupported, or cannot be decoded safely.") from None


@dataclass
class Job:
    token: str
    directory: Path
    filename: str
    settings: dict
    width: int
    height: int
    context: Any = None
    state: str = "queued"
    detections: list = field(default_factory=list)
    error: str | None = None
    deleted: bool = False
    expires: float = field(default_factory=lambda: time.monotonic() + 300)
    expires_at: float | None = None


class Jobs:
    def __init__(self, runner, retention, root):
        self.runner = runner
        self.retention = retention
        self.root = root
        self.items: dict[str, Job] = {}
        self.pending: deque[str] = deque()
        self.lock = threading.Condition(threading.RLock())
        self.stopping = False

    def remove(self, identifier):
        job = self.items.pop(identifier, None)
        if job:
            shutil.rmtree(job.directory)

    def cancel(self, identifier, *, delete=False):
        job = self.items[identifier]
        if job.state == "cancelled" and not delete:
            return
        if job.state in ["processing", "cancelling"]:
            (job.directory / "cancel").touch()
            job.state = "cancelling"
            job.deleted = job.deleted or delete
        else:
            if identifier in self.pending:
                self.pending.remove(identifier)
            if delete:
                self.remove(identifier)
            else:
                for path in job.directory.iterdir():
                    path.unlink()
                job.state = "cancelled"
                job.expires = time.monotonic() + 60

    def work(self):
        while True:
            with self.lock:
                self.lock.wait_for(lambda: self.stopping or self.pending)
                if self.stopping:
                    return
                identifier = self.pending.popleft()
                job = self.items.get(identifier)
                if job is None:
                    continue
                job.state = "processing"
            try:
                image, detections = self.runner(job.directory / "source.png", job.settings,
                                               job.directory / "cancel", job.context)
                with self.lock:
                    (job.directory / "source.png").unlink(missing_ok=True)
                    if job.state == "cancelling":
                        for path in job.directory.iterdir():
                            path.unlink()
                        job.state = "cancelled"
                        job.expires = time.monotonic() + 60
                    else:
                        (job.directory / "result.png").write_bytes(image)
                        job.detections = detections
                        job.state = "success" if detections else "empty"
                        job.expires = time.monotonic() + self.retention
                        job.expires_at = time.time() + self.retention
            except Exception as error:
                with self.lock:
                    for path in job.directory.iterdir():
                        path.unlink()
                    cancelled = job.state == "cancelling"
                    job.state = "cancelled" if cancelled else "error"
                    # Only known infrastructure categories leave the process; never payloads or tracebacks.
                    message = str(error).lower()
                    job.error = None if cancelled else ("Free GPU quota is exhausted. Try again after the platform resets its quota."
                                 if "quota" in message or "runs limit" in message else
                                 "Inference is unavailable or failed. The free backend may be starting; try again later.")
                    job.expires = time.monotonic() + 60
            finally:
                with self.lock:
                    job.context = None
                    if job.deleted:
                        self.remove(identifier)
                    self.lock.notify_all()

    def sweep(self):
        while True:
            with self.lock:
                if self.stopping:
                    return
                for identifier, job in list(self.items.items()):
                    if time.monotonic() >= job.expires:
                        self.cancel(identifier, delete=True)
                self.lock.wait(timeout=1)


def create_app(runner, *, submission_limit=6, retention=1800, storage_root=None,
                origins=("http://localhost:5173",), model_metadata=None):
    packages = {}
    for name in ["torch", "torchvision", "ultralytics", "numpy", "pillow", "gradio", "spaces", "fastapi", "starlette"]:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            continue
    runtime = {"python": platform.python_version(), "packages": packages}
    root = Path(storage_root) if storage_root else Path(tempfile.gettempdir()) / "autoscan-image-jobs"
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # This dedicated directory belongs exclusively to this single-process service.
    for old in root.glob("job-*"):
        shutil.rmtree(old)
    jobs = Jobs(runner, retention, root)
    uploading = [0]
    attempts: dict[str, deque[float]] = {"job": deque(), "preview": deque()}

    @contextmanager
    def job_lifecycle():
        threads = [threading.Thread(target=target, daemon=True) for target in [jobs.work, jobs.sweep]]
        for thread in threads:
            thread.start()
        try:
            yield
        finally:
            with jobs.lock:
                jobs.stopping = True
                for identifier in list(jobs.items):
                    jobs.cancel(identifier, delete=True)
                jobs.lock.notify_all()
            for thread in threads:
                thread.join()
            with jobs.lock:
                for identifier in list(jobs.items):
                    jobs.remove(identifier)

    @asynccontextmanager
    async def lifespan(app):
        with job_lifecycle():
            yield

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.job_lifecycle = job_lifecycle
    app.state.storage_root = root
    app.add_middleware(CORSMiddleware, allow_origins=list(origins),
                       allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "Authorization"])

    @app.middleware("http")
    async def no_cache(request: Request, call_next):
        response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "Referrer-Policy": "no-referrer"})
        return response

    def authorized(identifier, request):
        job = jobs.items.get(identifier)
        if not job or job.deleted or time.monotonic() >= job.expires or not secrets.compare_digest(
                request.headers.get("Authorization", "").encode(), ("Bearer " + job.token).encode()):
            raise HTTPException(404, "Job unavailable, deleted, or expired.")
        return job

    @asynccontextmanager
    async def upload(request, filename, kind):
        if len(filename) > 255 or any(ord(char) < 32 for char in filename):
            raise HTTPException(422, "Invalid source filename.")
        with jobs.lock:
            recent = attempts[kind]
            now = time.monotonic()
            while recent and now - recent[0] >= 600:
                recent.popleft()
            limit = submission_limit * (2 if kind == "preview" else 1)
            if len(recent) >= limit:
                raise HTTPException(429, "This free demo has reached its shared upload limit. Try again later.",
                                    headers={"Retry-After": str(max(1, int(600 - (now - recent[0])) + 1))})
            if sum(job.state in ["queued", "processing", "cancelling"] for job in jobs.items.values()) + uploading[0] >= 3:
                raise HTTPException(503, "Backend is busy: one active job and two pending slots. Try again later.",
                                    headers={"Retry-After": "30"})
            if len(jobs.items) + uploading[0] >= 8:
                raise HTTPException(503, "Temporary result storage is full. Delete an old result or try again later.",
                                    headers={"Retry-After": "60"})
            recent.append(now)
            uploading[0] += 1
        try:
            length = request.headers.get("content-length")
            if length is not None:
                if len(length) > 12 or not length.isascii() or not length.isdecimal():
                    raise HTTPException(400, "Invalid upload length.")
                if int(length) > MAX_BYTES:
                    raise HTTPException(413, "Image exceeds 10 MB.")
            content = bytearray()
            try:
                with fail_after(30):
                    async for chunk in request.stream():
                        if len(content) + len(chunk) > MAX_BYTES:
                            raise HTTPException(413, "Image exceeds 10 MB.")
                        content.extend(chunk)
            except TimeoutError:
                raise HTTPException(408, "Upload timed out; try a smaller image.") from None
            normalized, size = await run_in_threadpool(normalize, content, filename)
            yield normalized, size
        finally:
            with jobs.lock:
                uploading[0] -= 1

    @app.post("/api/preview")
    async def preview(request: Request, filename: str):
        async with upload(request, filename, "preview") as (normalized, size):
            return Response(normalized, media_type="image/png")

    @app.post("/api/jobs", status_code=202)
    async def submit(request: Request, filename: str, types: str = "vehicle,logo,plate", confidence: str = "40"):
        selected = types.split(",")
        if (not selected or len(selected) != len(set(selected))
                or not set(selected) <= {"vehicle", "logo", "plate"}):
            raise HTTPException(422, "Select at least one of vehicles, logos, or plates.")
        if (len(confidence) > 3 or not confidence.isascii() or not confidence.isdecimal()
                or not 25 <= int(confidence) <= 100):
            raise HTTPException(422, "Confidence must be a whole percentage from 25 to 100.")
        async with upload(request, filename, "job") as (normalized, size):
            with jobs.lock:
                identifier, token = secrets.token_hex(16), secrets.token_urlsafe(32)
                directory = Path(tempfile.mkdtemp(prefix="job-", dir=root))
                try:
                    (directory / "source.png").write_bytes(normalized)
                except OSError:
                    shutil.rmtree(directory)
                    raise HTTPException(503, "Temporary storage is unavailable. Try again later.") from None
                jobs.items[identifier] = Job(token, directory, filename,
                                             {"types": selected, "confidence": int(confidence)}, width=size[0], height=size[1],
                                             context={"headers": {"x-ip-token": request.headers.get("x-ip-token", "")}})
                jobs.pending.append(identifier)
                jobs.lock.notify_all()
        return {"id": identifier, "token": token, "state": "queued"}

    def result(identifier, job):
        return {"schema_version": "1.0", "id": identifier, "state": job.state, "filename": job.filename, "settings": job.settings,
                    "width": job.width, "height": job.height,
                    "detections": [{**detection, "source_filename": job.filename} for detection in job.detections],
                    "error": job.error, "expires_at": job.expires_at, "models": model_metadata or {},
                    "runtime": runtime,
                    "coordinate_system": "xyxy pixels from top-left of EXIF-oriented, white-composited RGB input"}

    @app.get("/api/jobs/{identifier}")
    def status(identifier: str, request: Request):
        with jobs.lock:
            return result(identifier, authorized(identifier, request))

    @app.get("/")
    @app.get("/api/health")
    def health():
        return {"status": "ready", "retention_seconds": retention, "max_active": 1, "max_pending": 2}

    def image_bytes(job):
        if job.state not in ["success", "empty"]:
            raise HTTPException(409, "Annotated image is not ready.")
        try:
            return (job.directory / "result.png").read_bytes()
        except OSError:
            raise HTTPException(503, "Result image is unavailable. Try again or run a new detection.") from None

    @app.get("/api/jobs/{identifier}/image")
    def result_image(identifier: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            return Response(image_bytes(job), media_type="image/png")

    @app.get("/api/jobs/{identifier}/download/{format}")
    def download(identifier: str, format: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            if format not in ["image", "json", "csv"]:
                raise HTTPException(404, "Download format unavailable.")
            if job.state not in ["success", "empty"]:
                raise HTTPException(409, "Downloads are available after detection completes successfully.")
            try:
                if format == "image":
                    content, media_type, extension = image_bytes(job), "image/png", "png"
                elif format == "json":
                    content = json.dumps(result(identifier, job), ensure_ascii=False, allow_nan=False).encode("utf-8")
                    media_type, extension = "application/json", "json"
                else:
                    output = StringIO(newline="")
                    writer = csv.writer(output)
                    writer.writerow(CSV_COLUMNS)
                    for detection in job.detections:
                        row = {**detection, "source_filename": job.filename,
                               **dict(zip(["x1", "y1", "x2", "y2"], detection["bbox"]))}
                        # Quoting alone does not stop spreadsheets interpreting text as formulas.
                        writer.writerow(["'" + value if isinstance(value, str) and
                                         value.lstrip().startswith(("=", "+", "-", "@", "＝", "＋", "－", "＠", "\t", "\r", "\n"))
                                         else value for value in (row[column] for column in CSV_COLUMNS)])
                    content = output.getvalue().encode("utf-8-sig")
                    media_type, extension = "text/csv", "csv"
            except (OSError, ValueError, TypeError, KeyError):
                raise HTTPException(503, "Download could not be prepared. Try again or run a new detection.") from None
            return Response(content, media_type=media_type,
                            headers={"Content-Disposition": f'attachment; filename="autoscan-{identifier}.{extension}"'})

    @app.delete("/api/jobs/{identifier}", status_code=204)
    def delete(identifier: str, request: Request):
        with jobs.lock:
            authorized(identifier, request)
            jobs.cancel(identifier, delete=True)
        return Response(status_code=204)

    @app.post("/api/jobs/{identifier}/cancel")
    def cancel(identifier: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            if job.state not in ["queued", "processing", "cancelling", "cancelled"]:
                raise HTTPException(409, "Job already finished; use Delete now to remove its results.")
            jobs.cancel(identifier)
            return {"state": job.state}

    return app
