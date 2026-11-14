"""Opt-in real HTTP/model checks. Uses anonymous free GPU quota; never retries submission."""

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import time
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image


@unittest.skipUnless(os.environ.get("AUTOSCAN_IMAGE_URL"), "Set AUTOSCAN_IMAGE_URL for real hosted image jobs")
class HostedImageTests(unittest.TestCase):
    def call(self, path, method="GET", data=None, job=None):
        headers = {"Content-Type": "application/octet-stream"}
        if job:
            headers["Authorization"] = "Bearer " + job["token"]
        return urlopen(Request(os.environ["AUTOSCAN_IMAGE_URL"].rstrip("/") + path,
                               data=data, method=method, headers=headers), timeout=90)

    def submit(self, data, filename="sample.png", types="vehicle,logo,plate", confidence=40):
        with self.call("/api/jobs?" + urlencode({"filename": filename, "types": types, "confidence": confidence}),
                       "POST", data) as response:
            return json.load(response)

    def wait(self, job):
        for _ in range(180):
            with self.call("/api/jobs/" + job["id"], job=job) as response:
                status = json.load(response)
            if status["state"] in ["success", "empty", "error", "cancelled"]:
                self.assertNotEqual(status["state"], "error", status.get("error"))
                return status
            time.sleep(1)
        self.fail("Backend did not complete within the three-minute test budget")

    def delete(self, job):
        try:
            self.call("/api/jobs/" + job["id"], "DELETE", job=job).close()
        except HTTPError as error:
            if error.code != 404:
                raise

    def test_a_real_selection_confidence_raw_classes_and_private_result(self):
        # Existing composite is a compatibility fixture, never an accuracy target.
        source = Path(__file__).resolve().parents[1] / "imgs/image.JPG"
        job = self.submit(source.read_bytes(), "sample.jpg")
        try:
            result = self.wait(job)
            self.assertEqual(result["state"], "success")
            self.assertTrue(result["detections"])
            self.assertEqual(len(result["models"]["logo"]["classes"]), 24)
            self.assertEqual(result["models"]["plate"]["classes"], {"0": "0"})
            for detection in result["detections"]:
                self.assertIn(detection["object_type"], ["vehicle", "logo", "plate"])
                self.assertGreaterEqual(detection["confidence"], .4 - 1e-6)
                if detection["object_type"] == "vehicle":
                    self.assertIn(detection["class_id"], [2, 5, 7])
                if detection["object_type"] == "plate":
                    self.assertEqual(detection["class_name"], "0")
                    self.assertEqual(detection["label"], "Plate")
            with self.call("/api/jobs/" + job["id"] + "/image", job=job) as response:
                self.assertIn("no-store", response.headers["Cache-Control"])
                with Image.open(BytesIO(response.read())) as image:
                    self.assertEqual(image.size, (result["width"], result["height"]))
            for path, method in [("", "GET"), ("/image", "GET"), ("/cancel", "POST"), ("", "DELETE")]:
                for visitor in [None, {"token": "another-visitor"}]:
                    with self.assertRaises(HTTPError) as caught:
                        self.call("/api/jobs/" + job["id"] + path, method, job=visitor)
                    self.assertEqual(caught.exception.code, 404)
            for bypass in ["/gradio_api/upload", "/gradio_api/file=/tmp/autoscan-image-jobs/",
                           "/file=/tmp/autoscan-image-jobs/", "/gradio_api/call/gpu_image"]:
                with self.assertRaises(HTTPError) as caught:
                    self.call(bypass)
                self.assertIn(caught.exception.code, [403, 404, 405])
        finally:
            self.delete(job)
        with self.assertRaises(HTTPError) as caught:
            self.call("/api/jobs/" + job["id"], job=job)
        self.assertEqual(caught.exception.code, 404)

    def test_b_supported_previews_and_invalid_content_and_settings(self):
        with self.call("/api/health") as response:
            self.assertEqual(json.load(response)["retention_seconds"], 1800)
        for format, suffix in [("PNG", "png"), ("JPEG", "jpg"), ("JPEG", "jpeg"), ("BMP", "bmp"), ("WEBP", "webp")]:
            output = BytesIO()
            Image.new("RGB", (48, 32), "white").save(output, format)
            with self.call("/api/preview?filename=sample." + suffix, "POST", output.getvalue()) as response:
                with Image.open(BytesIO(response.read())) as preview:
                    self.assertEqual(preview.size, (48, 32))
        for data, filename, status in [(b"corrupt", "sample.png", 422), (b"pickle", "model.pt", 415),
                                       (output.getvalue(), "sample.png", 415)]:
            with self.assertRaises(HTTPError) as caught:
                self.call("/api/preview?filename=" + filename, "POST", data)
            self.assertEqual(caught.exception.code, status)
        # Wait for rejection before sending a known-oversized body; Windows can abort a concurrent send.
        oversized = subprocess.run([
            "curl", "--disable", "--silent", "--show-error", "--max-time", "90", "--expect100-timeout", "5",
            "--header", "Expect: 100-continue", "--header", "Content-Type: application/octet-stream",
            "--data-binary", "@-", "--output", os.devnull, "--write-out", "%{http_code}",
            os.environ["AUTOSCAN_IMAGE_URL"].rstrip("/") + "/api/preview?filename=sample.png",
        ], input=b"x" * 10_000_001, capture_output=True, timeout=100)
        self.assertEqual(oversized.returncode, 0, oversized.stderr.decode(errors="replace"))
        self.assertEqual(oversized.stdout, b"413")
        for types, confidence in [("", 40), ("plate", 24), ("logo", 101), ("unknown", 40)]:
            with self.assertRaises(HTTPError) as caught:
                self.submit(b"", types=types, confidence=confidence)
            self.assertEqual(caught.exception.code, 422)

    def test_c_plate_only_at_100_percent_is_a_successful_empty_result(self):
        source = Path(__file__).resolve().parents[1] / "imgs/image.JPG"
        selected_job = self.submit(source.read_bytes(), "sample.jpg", types="plate", confidence=40)
        try:
            selected = self.wait(selected_job)
            self.assertEqual(selected["state"], "success")
            self.assertTrue(selected["detections"])
            self.assertTrue(all(item["object_type"] == "plate" for item in selected["detections"]))
        finally:
            self.delete(selected_job)
        output = BytesIO()
        Image.new("RGB", (48, 32), "white").save(output, "PNG")
        job = self.submit(output.getvalue(), types="plate", confidence=100)
        try:
            result = self.wait(job)
            self.assertEqual(result["state"], "empty")
            self.assertEqual(result["detections"], [])
            self.assertEqual(result["settings"], {"types": ["plate"], "confidence": 100})
            self.assertAlmostEqual(result["expires_at"] - time.time(), 1800, delta=20)
        finally:
            self.delete(job)

    # Admission runs first so earlier inference tests cannot spend its six-attempt rate budget.
    def test_a_admission_is_bounded_and_jobs_can_be_cancelled(self):
        output = BytesIO()
        Image.new("RGB", (4000, 3000), "white").save(output, "PNG")
        barrier = threading.Barrier(4)

        def submit_together(_):
            barrier.wait()
            try:
                return self.submit(output.getvalue(), types="plate")
            except HTTPError as error:
                return error.code

        with ThreadPoolExecutor(4) as pool:
            outcomes = list(pool.map(submit_together, range(4)))
        jobs = [item for item in outcomes if isinstance(item, dict)]
        try:
            self.assertLessEqual(len(jobs), 3)
            self.assertTrue(503 in outcomes, "Concurrent admission did not exercise saturation")
            for job in reversed(jobs):
                try:
                    with self.call("/api/jobs/" + job["id"] + "/cancel", "POST", job=job) as response:
                        self.assertIn(json.load(response)["state"], ["cancelled", "cancelling"])
                    self.assertEqual(self.wait(job)["state"], "cancelled")
                except HTTPError as error:
                    self.assertEqual(error.code, 409, "Only an already-completed job may reject cancellation")
        finally:
            for job in jobs:
                self.delete(job)

    @unittest.skipUnless(os.environ.get("AUTOSCAN_TEST_30_MINUTE_EXPIRY") == "1",
                         "Opt in to the actual 30-minute hosted retention check")
    def test_e_result_expires_without_browser_activity(self):
        output = BytesIO()
        Image.new("RGB", (48, 32), "white").save(output, "PNG")
        job = self.submit(output.getvalue(), types="plate", confidence=100)
        try:
            result = self.wait(job)
            time.sleep(max(0, result["expires_at"] - time.time()) + 2)
            with self.assertRaises(HTTPError) as caught:
                self.call("/api/jobs/" + job["id"], job=job)
            self.assertEqual(caught.exception.code, 404)
        finally:
            self.delete(job)
