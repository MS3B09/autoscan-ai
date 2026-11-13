"""Compatibility smoke check using trusted project weights, not an accuracy benchmark."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_SHA256 = {
    "logo": "52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356",
    "plate": "aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb",
    "vehicle": "31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95",
}
LOGO_CLASSES = [
    "audi", "bmw", "chevrolet", "citroen", "dacia", "fiat", "ford", "honda",
    "hyundai", "kia", "lexus", "mazda", "mercedes", "mitsubishi", "nissan", "opel",
    "peugeot", "renault", "seat", "skoda", "suzuki", "toyota", "volkswagen", "volvo",
]


def checkpoint_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as checkpoint:
        for chunk in iter(lambda: checkpoint.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_models(vehicle_weights, device):
    paths = {"logo": ROOT / "models/logo.pt", "plate": ROOT / "models/plate.pt",
             "vehicle": vehicle_weights}
    hashes = {name: checkpoint_hash(path) for name, path in paths.items()}
    for name, digest in hashes.items():
        if digest != CHECKPOINT_SHA256[name]:
            raise ValueError(f"Untrusted checkpoint digest: {name}")
    # Check digests before importing a loader that can unpickle trusted weights.
    from ultralytics import YOLO

    models = {name: YOLO(str(path), task="detect").to(device) for name, path in paths.items()}
    if models["logo"].names != dict(enumerate(LOGO_CLASSES)):
        raise ValueError(f"Logo class map changed: {models['logo'].names}")
    if models["plate"].names != {0: "0"}:
        raise ValueError("Plate checkpoint class map changed")
    if [models["vehicle"].names[index] for index in [2, 5, 7]] != ["car", "bus", "truck"]:
        raise ValueError("Vehicle checkpoint is not the expected COCO detector")
    return models, paths, hashes


def run_checks(models, paths, hashes, output, device, video_source=None):
    import importlib.metadata

    import cv2
    import numpy as np
    from PIL import Image
    import psutil
    import torch

    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()

    def detect(source, bgr):
        counts = {}
        annotated = bgr.copy()
        height, width = annotated.shape[:2]
        for name, model in models.items():
            result = model.predict(source=source, conf=0.4, imgsz=640, device=device,
                                   classes=[2, 5, 7] if name == "vehicle" else None,
                                   save=False, verbose=False)[0]
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            if result.orig_shape != (height, width):
                raise ValueError("Detection coordinates do not refer to input dimensions")
            if not np.isfinite(boxes).all() or not np.isfinite(confidences).all():
                raise ValueError("Non-finite detection values")
            if (confidences < 0.4 - 1e-6).any() or (confidences > 1).any():
                raise ValueError("Confidence values outside the requested range")
            if len(boxes) and not (
                (boxes[:, 0] >= 0).all() and (boxes[:, 1] >= 0).all()
                and (boxes[:, 2] <= width).all() and (boxes[:, 3] <= height).all()
                and (boxes[:, 2] > boxes[:, 0]).all() and (boxes[:, 3] > boxes[:, 1]).all()
            ):
                raise ValueError("Invalid bounding-box coordinates")
            counts[name] = len(boxes)
            annotated = result.plot(img=annotated)
        return annotated, counts

    # This existing composite checks compatibility, not real-world accuracy.
    with Image.open(ROOT / "imgs/image.JPG") as source:
        image = source.convert("RGB")
    bgr = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    image_started = time.perf_counter()
    annotated, counts = detect(image, bgr)
    image_seconds = time.perf_counter() - image_started
    if not sum(counts.values()):
        raise ValueError("No detections on the existing vehicle demonstration image")
    image_path = output / "annotated-image.png"
    if not cv2.imwrite(str(image_path), annotated) or cv2.imread(str(image_path)) is None:
        raise RuntimeError("Annotated image could not be written and decoded")

    source_path = video_source or output / "source-video.mp4"
    if video_source is None:
        frame = cv2.resize(bgr, (720, 404))
        writer = cv2.VideoWriter(str(source_path), cv2.VideoWriter_fourcc(*"mp4v"), 3, (720, 404))
        try:
            if not writer.isOpened():
                raise RuntimeError("MP4 smoke-test input encoder is unavailable")
            for _ in range(3):
                writer.write(frame)
        finally:
            writer.release()

    if source_path.stat().st_size > 20_000_000:
        raise ValueError("Video exceeds 20 MB")
    capture = cv2.VideoCapture(str(source_path))
    source_frames = 0
    try:
        fps = capture.get(cv2.CAP_PROP_FPS)
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        expected = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if not capture.isOpened() or not math.isfinite(fps) or fps <= 0:
            raise ValueError("Video cannot be decoded with a finite positive frame rate")
        if not (0 < width <= 1280 and 0 < height <= 720):
            raise ValueError("Video exceeds 720p or has invalid dimensions")
        while True:
            success, frame = capture.read()
            if not success:
                break
            source_frames += 1
            if frame.shape[:2] != (height, width):
                raise ValueError("Source video frame dimensions changed")
            if source_frames > 600 or source_frames / fps > 10 + 1e-6:
                raise ValueError("Video exceeds 600 frames or ten seconds")
    finally:
        capture.release()
    if not source_frames or source_frames != expected:
        raise ValueError(f"Source video did not decode completely: {source_frames} of {expected} frames")

    video_path = output / "annotated-video.mp4"
    capture = cv2.VideoCapture(str(source_path))
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    written = 0
    video_started = time.perf_counter()
    try:
        if not capture.isOpened() or not writer.isOpened():
            raise RuntimeError("MP4 smoke-test decoder or output encoder is unavailable")
        while True:
            success, frame = capture.read()
            if not success:
                break
            if frame.shape[:2] != (height, width) or written >= source_frames:
                raise ValueError("Video changed between validation and inference")
            annotated, _ = detect(frame, frame)
            writer.write(annotated)
            written += 1
    finally:
        capture.release()
        writer.release()
    video_seconds = time.perf_counter() - video_started

    capture = cv2.VideoCapture(str(video_path))
    decoded = 0
    try:
        if not capture.isOpened():
            raise RuntimeError("Annotated MP4 cannot be opened")
        while True:
            success, frame = capture.read()
            if not success:
                break
            if frame.shape[:2] != (height, width):
                raise ValueError("Encoded frame dimensions changed")
            decoded += 1
    finally:
        capture.release()
    if written != source_frames or decoded != source_frames:
        raise ValueError(f"Video frames lost: wrote {written}, decoded {decoded}, expected {source_frames}")

    for name, path in paths.items():
        if checkpoint_hash(path) != hashes[name]:
            raise ValueError(f"Checkpoint changed during validation: {name}")
    report = {
        "scope": ("Compatibility and measured capacity for the supplied video; not an accuracy benchmark"
                  if video_source else "Compatibility only; composite plus 3 repeated frames, not a capacity benchmark"),
        "device": device,
        "gpu": torch.cuda.get_device_name() if device == "cuda" else None,
        "versions": {name: importlib.metadata.version(name) for name in
                      ["torch", "torchvision", "ultralytics", "numpy", "Pillow", "opencv-python"]},
        "python": platform.python_version(),
        "installed_distributions": {package.metadata["Name"]: package.version
                                    for package in importlib.metadata.distributions()},
        "models": {name: {"sha256": hashes[name],
                          "classes": {str(index): label for index, label in model.names.items()}}
                   for name, model in models.items()},
        "image": {"detection_count": sum(counts.values()), "counts": counts,
                  "seconds_including_first_prediction": image_seconds},
        "video": {"frames_written": written, "frames_decoded": decoded,
                   "source_frames_decoded": source_frames, "source_bytes": source_path.stat().st_size,
                   "source_sha256": checkpoint_hash(source_path),
                   "width": width, "height": height, "fps": fps,
                   "duration_seconds": source_frames / fps, "seconds": video_seconds,
                  "codec": "mp4v", "browser_playback_verified": False},
        "process_rss_bytes_at_completion": psutil.Process().memory_info().rss,
        "elapsed_seconds": time.perf_counter() - started,
        "remaining_gates": ["anonymous_browser_api",
                            "download_isolation", "cancellation", "30_minute_expiry",
                            "browser_playback", "detection_accuracy"],
    }
    if video_source is None:
        report["remaining_gates"].append("representative_10_second_video")
    (output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vehicle-weights", type=Path, required=True,
                        help="Path to the trusted standard yolov8n.pt (never a visitor upload)")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="New directory for the smoke-check report and media")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--video", type=Path, help="Representative video instead of repeated-frame smoke input")
    args = parser.parse_args()
    if not args.vehicle_weights.is_file():
        parser.error("Vehicle checkpoint does not exist; provision trusted yolov8n.pt first")
    if args.output_dir.exists():
        parser.error("Output directory already exists; choose a new path to avoid overwriting data")
    if args.video is not None and not args.video.is_file():
        parser.error("Representative video does not exist")
    if args.video is not None and args.video.stat().st_size > 20_000_000:
        parser.error("Video exceeds 20 MB")
    models, paths, hashes = load_models(args.vehicle_weights, args.device)
    report = run_checks(models, paths, hashes, args.output_dir, args.device, args.video)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Validation failed: {type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
