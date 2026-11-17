"""Private, bounded media-job HTTP API. No framework upload or static-file routes."""

from collections import deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import csv
from importlib.metadata import PackageNotFoundError, version
from io import BytesIO, StringIO
import json
import math
from pathlib import Path
import platform
import re
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

from image_service.video import VIDEO_FORMATS, MAX_VIDEO_BYTES, VideoError, prepare_video


FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".bmp": "BMP", ".webp": "WEBP"}
MAX_BYTES = 10_000_000
MAX_PIXELS = 12_000_000
CSV_COLUMNS = ["source_filename", "object_type", "class_name", "label", "confidence",
               "x1", "y1", "x2", "y2", "width", "height"]


def quota_retry_at(message):
    # spaces==0.51.3 includes a Python timedelta in timed quota rejections, not every rejection.
    match = re.search(r"\btry again in (?:(\d{1,2}) days?, )?(\d{1,2}):([0-5]\d):"
                      r"([0-5]\d(?:\.\d{1,6})?)(?=\.?(?:\s|$))", message.lower())
    if not match:
        return None
    days, hours, minutes, seconds = match.groups()
    wait = int(days or 0) * 86400 + int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    if int(hours) < 24 and 0 < wait <= 86400:
        return math.ceil(time.time() + wait)
    return None


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
    video: dict | None = None
    context: Any = None
    state: str = "queued"
    detections: list = field(default_factory=list)
    error: str | None = None
    retry_at: int | None = None
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
                source = job.directory / ("source.video" if job.video else "source.png")
                image, detections = self.runner(source, job.settings,
                                               job.directory / "cancel", job.context)
                with self.lock:
                    source.unlink(missing_ok=True)
                    (job.directory / "video.json").unlink(missing_ok=True)
                    if job.state == "cancelling":
                        for path in job.directory.iterdir():
                            path.unlink()
                        job.state = "cancelled"
                        job.expires = time.monotonic() + 60
                    else:
                        (job.directory / ("result.mp4" if job.video else "result.png")).write_bytes(image)
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
                    quota = not isinstance(error, VideoError) and ("quota" in message or "runs limit" in message)
                    job.retry_at = quota_retry_at(message) if quota and not cancelled else None
                    retry = ("Try again after " + datetime.fromtimestamp(job.retry_at, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") + "."
                             if job.retry_at is not None else "Hugging Face did not provide a reset time. Try again later.")
                    job.error = None if cancelled else (str(error) if isinstance(error, VideoError) else
                                 "Free GPU quota is exhausted. " + retry if quota else
                                 "Video processing failed or the free backend is unavailable. Try again later; if it repeats, re-export the complete clip as H.264 MP4."
                                 if job.video else "Inference is unavailable or failed. The free backend may be starting; try again later.")
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
    for name in ["torch", "torchvision", "ultralytics", "numpy", "pillow", "gradio", "spaces", "fastapi", "starlette", "av"]:
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            continue
    runtime = {"python": platform.python_version(), "packages": packages}
    root = Path(storage_root) if storage_root else Path(tempfile.gettempdir()) / "autoscan-image-jobs"
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # This dedicated directory belongs exclusively to this single-process service.
    for pattern in ["job-*", "preview-*"]:
        for old in root.glob(pattern):
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
            is_video = Path(filename).suffix.lower() in VIDEO_FORMATS
            maximum = MAX_VIDEO_BYTES if is_video else MAX_BYTES
            too_large = "Video exceeds 20 MB." if is_video else "Image exceeds 10 MB."
            length = request.headers.get("content-length")
            if length is not None:
                if len(length) > 12 or not length.isascii() or not length.isdecimal():
                    raise HTTPException(400, "Invalid upload length.")
                if int(length) > maximum:
                    raise HTTPException(413, too_large)
            content = bytearray()
            try:
                with fail_after(30):
                    async for chunk in request.stream():
                        if len(content) + len(chunk) > maximum:
                            raise HTTPException(413, too_large)
                        content.extend(chunk)
            except TimeoutError:
                raise HTTPException(408, "Upload timed out; try a smaller file.") from None
            if is_video:
                try:
                    normalized, info = await run_in_threadpool(prepare_video, content, Path(filename).suffix.lower(), root, kind == "preview")
                except VideoError as error:
                    raise HTTPException(error.status, str(error)) from None
                yield normalized, (info["width"], info["height"]), info
            else:
                normalized, size = await run_in_threadpool(normalize, content, filename)
                yield normalized, size, None
        finally:
            with jobs.lock:
                uploading[0] -= 1

    @app.post("/api/preview")
    async def preview(request: Request, filename: str):
        async with upload(request, filename, "preview") as (normalized, size, video):
            if video:
                return Response(normalized, media_type="video/mp4")
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
        async with upload(request, filename, "job") as (normalized, size, video):
            with jobs.lock:
                identifier, token = secrets.token_hex(16), secrets.token_urlsafe(32)
                directory = Path(tempfile.mkdtemp(prefix="job-", dir=root))
                try:
                    (directory / ("source.video" if video else "source.png")).write_bytes(normalized)
                    if video:
                        (directory / "video.json").write_text(json.dumps(video))
                except OSError:
                    shutil.rmtree(directory)
                    raise HTTPException(503, "Temporary storage is unavailable. Try again later.") from None
                jobs.items[identifier] = Job(token, directory, filename,
                                             {"types": selected, "confidence": int(confidence)}, width=size[0], height=size[1],
                                             video=video, context={"headers": {"x-ip-token": request.headers.get("x-ip-token", "")}})
                jobs.pending.append(identifier)
                jobs.lock.notify_all()
        return {"id": identifier, "token": token, "state": "queued"}

    def result(identifier, job):
        progress = 0
        if job.video:
            if job.state in ["success", "empty"]:
                progress = job.video["frame_count"]
            elif job.state in ["processing", "cancelling"]:
                try:
                    progress = json.loads((job.directory / "progress.json").read_text())["processed_frames"]
                except (OSError, ValueError, KeyError):
                    pass
        return {"schema_version": "1.0", "id": identifier, "state": job.state, "filename": job.filename, "settings": job.settings,
                    "media_type": "video" if job.video else "image",
                    **({"frame_count": job.video["frame_count"], "processed_frames": progress,
                        "duration_seconds": job.video["duration_seconds"],
                        "output_width": job.width + job.width % 2, "output_height": job.height + job.height % 2} if job.video else {}),
                    "queue_position": list(jobs.pending).index(identifier) + 1 if identifier in jobs.pending else None,
                    "width": job.width, "height": job.height,
                    "detections": [{**detection, "source_filename": job.filename} for detection in job.detections],
                    "error": job.error, "expires_at": job.expires_at, "models": model_metadata or {},
                    **({"retry_at": job.retry_at} if job.retry_at is not None else {}),
                    "runtime": runtime,
                    "coordinate_system": ("xyxy pixels from top-left of upright source frame; zero-based frame_index; timestamp_seconds relative to first presentation timestamp"
                                          if job.video else "xyxy pixels from top-left of EXIF-oriented, white-composited RGB input")}

    @app.get("/api/jobs/{identifier}")
    def status(identifier: str, request: Request):
        with jobs.lock:
            return result(identifier, authorized(identifier, request))

    @app.get("/")
    @app.get("/api/health")
    def health():
        return {"status": "ready", "retention_seconds": retention, "max_active": 1, "max_pending": 2}

    def media_bytes(job, kind):
        if kind != ("video" if job.video else "image"):
            raise HTTPException(404, "Media format unavailable for this job.")
        if job.state not in ["success", "empty"]:
            raise HTTPException(409, "Annotated media is not ready.")
        try:
            return (job.directory / ("result.mp4" if job.video else "result.png")).read_bytes()
        except OSError:
            raise HTTPException(503, "Result media is unavailable. Try again or run a new detection.") from None

    @app.get("/api/jobs/{identifier}/image")
    def result_image(identifier: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            return Response(media_bytes(job, "image"), media_type="image/png")

    @app.get("/api/jobs/{identifier}/video")
    def result_video(identifier: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            return Response(media_bytes(job, "video"), media_type="video/mp4")

    @app.get("/api/jobs/{identifier}/download/{format}")
    def download(identifier: str, format: str, request: Request):
        with jobs.lock:
            job = authorized(identifier, request)
            if format not in ["image", "video", "json", "csv"]:
                raise HTTPException(404, "Download format unavailable.")
            if job.state not in ["success", "empty"]:
                raise HTTPException(409, "Downloads are available after detection completes successfully.")
            try:
                if format == "image":
                    content, media_type, extension = media_bytes(job, "image"), "image/png", "png"
                elif format == "video":
                    content, media_type, extension = media_bytes(job, "video"), "video/mp4", "mp4"
                elif format == "json":
                    exported = result(identifier, job)
                    exported["schema_version"] = "1.1"
                    for detection in exported["detections"]:
                        detection.pop("class_id", None)
                    content = json.dumps(exported, ensure_ascii=False, allow_nan=False).encode("utf-8")
                    media_type, extension = "application/json", "json"
                else:
                    output = StringIO(newline="")
                    writer = csv.writer(output)
                    columns = CSV_COLUMNS + (["frame_index", "timestamp_seconds"] if job.video else [])
                    writer.writerow(columns)
                    for detection in job.detections:
                        row = {**detection, "source_filename": job.filename,
                               **dict(zip(["x1", "y1", "x2", "y2"], detection["bbox"]))}
                        # Quoting alone does not stop spreadsheets interpreting text as formulas.
                        writer.writerow(["'" + value if isinstance(value, str) and
                                         value.lstrip().startswith(("=", "+", "-", "@", "＝", "＋", "－", "＠", "\t", "\r", "\n"))
                                          else value for value in (row[column] for column in columns)])
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
