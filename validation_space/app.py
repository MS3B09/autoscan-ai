"""Temporary ZeroGPU diagnostics; this is not the public detection application."""

from pathlib import Path
import json
import logging
import secrets
import tempfile
import threading
import time

from fastapi import APIRouter, HTTPException, Request, Response
import gradio as gr
import spaces

from scripts.validate_inference import ROOT, load_models, run_checks


# ZeroGPU emulates CUDA during startup; real inference runs inside the decorator.
MODELS, PATHS, HASHES = load_models(ROOT / "models/yolov8n.pt", "cuda")


@spaces.GPU(duration=60)
def validate():
    with tempfile.TemporaryDirectory(prefix="autoscan-validation-") as temporary:
        return run_checks(MODELS, PATHS, HASHES, Path(temporary) / "results", "cuda",
                          ROOT / "fixtures/traffic-10s.mp4")


demo = gr.Interface(
    fn=validate,
    inputs=[],
    outputs=gr.JSON(label="Compatibility report"),
    title="AutoScan AI — backend compatibility check",
    description="Runs the bundled project example and every frame of a ten-second traffic clip. "
                "No visitor uploads. This does not establish accuracy, throughput, or privacy of the future app.",
    api_name="validate",
    concurrency_limit=1,
    flagging_mode="never",
)
demo.queue(max_size=2)

# shortcut: fixed JSON and 30-second expiry only, replace with T2's media-job lifecycle before accepting uploads.
PRIVATE_ROOT = tempfile.TemporaryDirectory(prefix="autoscan-private-")
PROBES = {}
LOCK = threading.Lock()
routes = APIRouter()


def remove_probe(identifier):
    with LOCK:
        probe = PROBES.pop(identifier, None)
        if probe:
            probe["directory"].cleanup()


@routes.post("/isolation-probes")
def create_probe(response: Response):
    with LOCK:
        if len(PROBES) >= 4:
            raise HTTPException(429, "Diagnostic probe capacity reached")
        identifier, token = secrets.token_hex(16), secrets.token_urlsafe(32)
        directory = tempfile.TemporaryDirectory(dir=PRIVATE_ROOT.name)
        path = Path(directory.name) / "result.json"
        path.write_text(json.dumps({"kind": "private diagnostic result", "nonce": secrets.token_hex(16)}),
                        encoding="utf-8")
        PROBES[identifier] = {"token": token, "directory": directory, "path": path,
                              "expires": time.monotonic() + 30}
        timer = threading.Timer(30, remove_probe, args=[identifier])
        timer.daemon = True
        timer.start()
        response.headers["Cache-Control"] = "no-store"
        # Reveal the path intentionally: knowing a path must not bypass authorization.
        return {"id": identifier, "token": token, "path": str(path), "expires_in_seconds": 30}


@routes.api_route("/isolation-probes/{identifier}", methods=["GET", "DELETE"])
def access_probe(identifier: str, request: Request):
    with LOCK:
        probe = PROBES.get(identifier)
        if (not probe or time.monotonic() >= probe["expires"] or not secrets.compare_digest(
                request.headers.get("Authorization", "").encode(), ("Bearer " + probe["token"]).encode())):
            raise HTTPException(404, "Result unavailable")
        if request.method == "DELETE":
            probe["directory"].cleanup()
            del PROBES[identifier]
            return Response(status_code=204, headers={"Cache-Control": "no-store"})
        return Response(probe["path"].read_bytes(), media_type="application/json",
                        headers={"Cache-Control": "no-store"})


if __name__ == "__main__":
    # spaces==0.51.3 initializes ZeroGPU in Gradio's launch hook, not an ASGI mount.
    app, _, _ = demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False,
                            show_error=False, prevent_thread_lock=True, blocked_paths=[
                                PRIVATE_ROOT.name, str(ROOT / "models"),
                                str(ROOT / "imgs"), str(ROOT / "fixtures")])
    logging.getLogger("uvicorn.access").disabled = True
    app.include_router(routes)
    demo.block_thread()
