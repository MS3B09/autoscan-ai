"""Space root entrypoint; implementation remains importable in image_service."""

import runpy

runpy.run_module("image_service.app", run_name="__main__")
