"""Free ZeroGPU entrypoint. Run from the repository root: python -m image_service.app."""

import os

os.environ["YOLO_VERBOSE"] = "False"

import gradio as gr
import spaces
from huggingface_hub import hf_hub_download
from spaces.zero.context import ZeroGPUContext, set_context_var
from starlette.middleware import Middleware
from starlette.responses import Response
from starlette.routing import Mount

from image_service.api import create_app
from image_service.detector import detect
from image_service.video import detect_video
from scripts.validate_inference import ROOT, load_models


for filename in ["logo.pt", "plate.pt", "yolov8n.pt"]:
    if not (ROOT / "models" / filename).is_file():
        hf_hub_download("MS3B09/autoscan-ai-validation", repo_type="space",
                        revision="da8e0cdd5a03d0d3c60fab3f942910ef6472310b",
                        filename="models/" + filename, local_dir=ROOT)
MODELS, PATHS, HASHES = load_models(ROOT / "models/yolov8n.pt", "cuda")


@spaces.GPU(duration=60)
def gpu_image(source, settings, cancelled):
    try:
        return (detect_video if source.suffix == ".video" else detect)(MODELS, source, settings, cancelled)
    except Exception:
        raise gr.Error("Media inference or video encoding failed. Re-export the clip or try again later.", print_exception=False) from None


def run_image(source, settings, cancelled, context):
    # Queued jobs run outside Gradio's request context but still need quota attribution.
    with set_context_var(ZeroGPUContext(headers=context["headers"], log_emitter=lambda _: None)):
        return gpu_image(source, settings, cancelled)


class FrameworkRouteGuard:
    """Close generic framework routes even during launch, before the API mount is attached."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] == "http" and not (path.startswith("/api/") or path in [
                "/", "/startup-events", "/gradio_api/startup-events"]):
            await Response(status_code=404, headers={"Cache-Control": "no-store"})(scope, receive, send)
            return
        await self.app(scope, receive, send)


if __name__ == "__main__":
    import logging

    api = create_app(run_image, origins=os.environ.get(
                     "AUTOSCAN_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
                     model_metadata={kind: {"sha256": HASHES[kind], "classes": model.names}
                                     for kind, model in MODELS.items()})
    with gr.Blocks(analytics_enabled=False) as demo:
        gr.Markdown("AutoScan AI media service. Use the /detect workspace.")
    # Ordinary Gradio launch initializes ZeroGPU before serving the API.
    # The first mount intercepts ALL public routes: Gradio uploads/files/events are unreachable.
    logging.getLogger("uvicorn.access").disabled = True
    with api.state.job_lifecycle():
        server, _, _ = demo.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False,
                                    show_error=False, prevent_thread_lock=True,
                                    app_kwargs={"middleware": [Middleware(FrameworkRouteGuard)]},
                                    blocked_paths=[str(ROOT), str(api.state.storage_root)])
        server.router.routes.insert(0, Mount("/", app=api))
        demo.block_thread()
