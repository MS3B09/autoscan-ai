"""Local-only developer adapter. Never deploy this module or expose it on a LAN."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import math
from pathlib import Path
import re

from anyio import fail_after
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
import httpx

from image_service.video import VIDEO_FORMATS


UPSTREAM = "https://ms3b09-autoscan-ai-images.hf.space"
ORIGIN = "http://127.0.0.1:5173"


def create_app(token):
    if not isinstance(token, str) or not re.fullmatch(r"hf_[A-Za-z0-9]{1,128}", token):
        raise ValueError("Enter the dedicated HF READ token, not a saved deployment credential.")

    async def free_quota(client):
        response = await client.get("https://huggingface.co/api/spaces/zero-gpu/quota",
                                    headers={"Authorization": "Bearer " + token, "Cookie": ""})
        response.raise_for_status()
        quota = response.json()
        runs = quota.get("runs")
        if (type(quota.get("base")) not in [int, float] or not 0 < quota["base"] <= 300
                or type(quota.get("current")) not in [int, float] or not 0 <= quota["current"] <= quota["base"]
                or not isinstance(runs, dict) or type(runs.get("remaining")) is not int or runs["remaining"] < 0
                or quota.get("overquotaUsed") not in [None, 0]):
            raise ValueError("Cannot verify free quota")
        return quota

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(timeout=60, follow_redirects=False, trust_env=False) as client:
            try:
                headers = {"Authorization": "Bearer " + token, "Cookie": ""}
                identity = await client.get("https://huggingface.co/api/whoami-v2", headers=headers)
                identity.raise_for_status()
                profile = identity.json()
                if (profile.get("name") != "MS3B09" or profile.get("isPro") is not False
                        or profile.get("auth", {}).get("accessToken", {}).get("role") != "read"):
                    raise ValueError("Wrong account, role or quota tier")
                await free_quota(client)
            except (httpx.HTTPError, ValueError, TypeError, AttributeError, KeyError):
                raise ValueError("Use a READ token for the free MS3B09 personal account, with access to its quota information.") from None
            app.state.upstream = client
            yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(CORSMiddleware, allow_origins=[ORIGIN], allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["Content-Type", "Authorization"])

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        if (not request.client or request.client.host not in ["127.0.0.1", "::1"]
                or request.headers.get("host") != "127.0.0.1:7862" or request.headers.get("origin") != ORIGIN):
            return JSONResponse({"detail": "Developer access is restricted to the local frontend."}, status_code=403,
                                headers={"Cache-Control": "no-store"})
        response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})
        return response

    @app.api_route("/api/{path:path}", methods=["GET", "POST", "DELETE"])
    async def forward(path: str, request: Request):
        allowed = {"health": ["GET"], "preview": ["POST"], "jobs": ["POST"]}.get(path, [])
        job = re.fullmatch(r"jobs/[a-f0-9]{32}(/(?:image|video|cancel|download/(?:image|video|json|csv)))?", path)
        if job:
            allowed = ["POST"] if job[1] == "/cancel" else ["GET", "DELETE"] if job[1] is None else ["GET"]
        if request.method not in allowed:
            raise HTTPException(404, "Unknown developer API operation.")
        length = request.headers.get("content-length")
        if length is not None and (not length.isascii() or not length.isdecimal()):
            raise HTTPException(400, "Invalid upload length.")
        if length is not None and int(length) > 20_000_000:
            raise HTTPException(413, "Developer uploads are limited to 20 MB.")
        is_video_upload = (request.method == "POST" and path in ["preview", "jobs"]
                           and Path(request.query_params.get("filename", "")).suffix.lower() in VIDEO_FORMATS)
        upload_seconds = 60 if is_video_upload else 30
        body = bytearray()
        try:
            with fail_after(upload_seconds):
                async for chunk in request.stream():
                    if len(body) + len(chunk) > 20_000_000:
                        raise HTTPException(413, "Developer uploads are limited to 20 MB.")
                    body.extend(chunk)
        except TimeoutError:
            raise HTTPException(408, f"The local server did not receive the full file within {upload_seconds} seconds. Retry the upload.") from None
        headers = {"Cookie": ""}
        if request.method == "POST" and path == "jobs":
            try:
                quota = await free_quota(app.state.upstream)
                runs = quota["runs"]
                blocked = ([quota.get("resetsAt")] if quota["current"] < 60 else [])
                if runs.get("remaining") == 0:
                    blocked.append(runs.get("resetsAt"))
            except (httpx.HTTPError, ValueError, TypeError, AttributeError, KeyError):
                raise HTTPException(503, "Cannot verify the account's free quota. No detection was submitted.") from None
            if blocked:
                try:
                    resets = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in blocked]
                    if any(value.tzinfo is None for value in resets):
                        raise ValueError("Missing reset timezone")
                    retry_at = math.ceil(max(value.timestamp() for value in resets))
                except (ValueError, TypeError, AttributeError, OverflowError):
                    retry_at = None
                detail = "Free GPU quota is exhausted. " + (
                    "Try again after " + datetime.fromtimestamp(retry_at, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") + "."
                    if retry_at is not None else "Hugging Face did not provide a reset time. Try again later.")
                return JSONResponse({"detail": detail, **({"retry_at": retry_at} if retry_at is not None else {})}, status_code=429)
            headers["Authorization"] = "Bearer " + token
        elif path not in ["preview", "health"] and request.headers.get("authorization"):
            headers["Authorization"] = request.headers["authorization"]
        try:
            response = await app.state.upstream.request(request.method, UPSTREAM + "/api/" + path,
                                                         params=request.query_params.multi_items(),
                                                         headers=headers, content=bytes(body),
                                                         timeout=115 if is_video_upload else 60)
        except httpx.TimeoutException:
            raise HTTPException(504, "The hosted server did not respond in time. No automatic retry was made.") from None
        except httpx.HTTPError:
            raise HTTPException(503, "Cannot reach the hosted backend. No automatic submission retry was made.") from None
        forwarded = {name: response.headers[name] for name in ["content-type", "content-disposition", "retry-after"]
                     if name in response.headers}
        media_type = response.headers.get("content-type", "").split(";")[0].lower()
        if (300 <= response.status_code < 400 or response.status_code in [401, 403] or response.status_code >= 500
                or token.encode() in response.content or any(token in value for value in forwarded.values())
                or (response.status_code != 204 and media_type not in ["application/json", "image/png", "video/mp4", "text/csv"])):
            raise HTTPException(503, "Hosted backend unavailable or developer authentication rejected. Check the READ token or try later.")
        return Response(response.content, status_code=response.status_code,
                        headers={**forwarded, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    return app


if __name__ == "__main__":
    import getpass
    import warnings
    import uvicorn

    warnings.filterwarnings("error", category=getpass.GetPassWarning)
    token = getpass.getpass("Paste autoscan-inference READ token (hidden, kept only in memory): ").strip()
    print("Starting local developer API at http://127.0.0.1:7862; checking READ identity and free quota.")
    uvicorn.run(create_app(token), host="127.0.0.1", port=7862, access_log=False, proxy_headers=False)
