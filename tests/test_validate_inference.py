import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ValidateInferenceTests(unittest.TestCase):
    def test_help_does_not_require_inference_dependencies(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_inference.py"), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("--vehicle-weights", process.stdout)

    def test_missing_vehicle_weights_fail_before_creating_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "results"
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", str(Path(temporary) / "missing.pt"),
                 "--output-dir", str(output)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("Vehicle checkpoint does not exist", process.stderr)
            self.assertFalse(output.exists())

    def test_untrusted_checkpoint_is_rejected_before_loading_inference_libraries(self):
        with tempfile.TemporaryDirectory() as temporary:
            checkpoint = Path(temporary) / "yolov8n.pt"
            checkpoint.write_bytes(b"not the pinned trusted vehicle checkpoint")
            output = Path(temporary) / "results"
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", str(checkpoint), "--output-dir", str(output)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(process.returncode, 1)
            self.assertIn("Untrusted checkpoint digest: vehicle", process.stderr)
            self.assertFalse(output.exists())

    def test_existing_output_directory_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            checkpoint = directory / "yolov8n.pt"
            checkpoint.write_bytes(b"not loaded because the output path is rejected first")
            marker = directory / "keep.txt"
            marker.write_text("existing user data", encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", str(checkpoint), "--output-dir", str(directory)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("Output directory already exists", process.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "existing user data")

    def test_missing_representative_video_fails_before_loading_models(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            checkpoint = directory / "yolov8n.pt"
            checkpoint.write_bytes(b"must not be loaded")
            output = directory / "results"
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", str(checkpoint), "--output-dir", str(output),
                 "--video", str(directory / "missing.mp4")],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("Representative video does not exist", process.stderr)
            self.assertFalse(output.exists())

    def test_video_over_twenty_mb_is_rejected_before_loading_models(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            checkpoint = directory / "yolov8n.pt"
            checkpoint.write_bytes(b"must not be loaded")
            video = directory / "oversized.mp4"
            with video.open("wb") as source:
                source.truncate(20_000_001)
            output = directory / "results"
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", str(checkpoint), "--output-dir", str(output),
                 "--video", str(video)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("Video exceeds 20 MB", process.stderr)
            self.assertFalse(output.exists())

    @unittest.skipUnless(
        os.environ.get("AUTOSCAN_VEHICLE_WEIGHTS") and importlib.util.find_spec("torch"),
        "Integration gate requires PyTorch and AUTOSCAN_VEHICLE_WEIGHTS; not a passing model check",
    )
    def test_unchanged_checkpoints_process_an_image_and_every_video_frame(self):
        vehicle_weights = os.environ.get("AUTOSCAN_VEHICLE_WEIGHTS")
        self.assertTrue(vehicle_weights, "Set AUTOSCAN_VEHICLE_WEIGHTS to trusted yolov8n.pt")
        weights = [ROOT / "models/logo.pt", ROOT / "models/plate.pt", Path(vehicle_weights)]
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in weights]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "validation"
            process = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_inference.py"),
                 "--vehicle-weights", vehicle_weights, "--output-dir", str(output)],
                cwd=ROOT, capture_output=True, text=True, timeout=300,
            )
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            report = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual([hashlib.sha256(path.read_bytes()).hexdigest() for path in weights], hashes)
            self.assertEqual(report["models"]["logo"]["classes"]["0"], "audi")
            self.assertEqual(len(report["models"]["logo"]["classes"]), 24)
            self.assertEqual(report["models"]["plate"]["classes"], {"0": "0"})
            self.assertEqual(report["video"]["frames_written"], 3)
            self.assertEqual(report["video"]["frames_decoded"], 3)
            self.assertGreater(report["image"]["detection_count"], 0)
            self.assertTrue((output / "annotated-image.png").is_file())
            self.assertTrue((output / "annotated-video.mp4").is_file())


if __name__ == "__main__":
    unittest.main()
