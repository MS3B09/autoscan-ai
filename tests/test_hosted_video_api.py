"""Opt-in real short-video inference. One submission, no automatic quota retries."""

import csv
from io import BytesIO
import json
import os
from pathlib import Path
import unittest
from urllib.error import HTTPError

import av

import test_hosted_image_api as image_tests
from scripts.validate_inference import CHECKPOINT_SHA256


@unittest.skipUnless(os.environ.get("AUTOSCAN_IMAGE_URL") and os.environ.get("AUTOSCAN_VIDEO_SOURCE"),
                     "Set AUTOSCAN_IMAGE_URL and AUTOSCAN_VIDEO_SOURCE for real hosted video inference")
class HostedVideoTests(unittest.TestCase):
    call = image_tests.HostedImageTests.call
    submit = image_tests.HostedImageTests.submit
    wait = image_tests.HostedImageTests.wait
    delete = image_tests.HostedImageTests.delete

    def test_representative_every_frame_private_playable_exports(self):
        source = Path(os.environ["AUTOSCAN_VIDEO_SOURCE"])
        with av.open(str(source)) as container:
            original = [(frame.pts * frame.time_base, frame.width, frame.height) for frame in container.decode(video=0)]
        self.assertGreater(len(original), 3, "Use representative changing footage, not the repeated-frame smoke clip")
        job = self.submit(source.read_bytes(), source.name)
        try:
            result = self.wait(job)
            self.assertIn(result["state"], ["success", "empty"])
            self.assertEqual(result["frame_count"], len(original))
            self.assertEqual(result["processed_frames"], len(original))
            for kind, digest in CHECKPOINT_SHA256.items():
                self.assertEqual(result["models"][kind]["sha256"], digest)
            for detection in result["detections"]:
                index = detection["frame_index"]
                self.assertGreaterEqual(index, 0)
                self.assertLess(index, len(original))
                self.assertAlmostEqual(detection["timestamp_seconds"], float(original[index][0] - original[0][0]), places=6)
                self.assertIn(detection["object_type"], ["vehicle", "logo", "plate"])
                self.assertGreaterEqual(detection["confidence"], .4 - 1e-6)
            endpoint = "/api/jobs/" + job["id"]
            downloads = {}
            for kind in ["video", "json", "csv"]:
                with self.call(endpoint + "/download/" + kind, job=job) as response:
                    downloads[kind] = response.read()
                    self.assertIn("no-store", response.headers["Cache-Control"])
            with self.call(endpoint + "/video", job=job) as response:
                self.assertEqual(response.read(), downloads["video"])
            with av.open(BytesIO(downloads["video"])) as container:
                self.assertEqual(container.streams.video[0].codec_context.name, "h264")
                self.assertEqual(len(container.streams.audio), 0)
                frames = [(frame.pts * frame.time_base, frame.width, frame.height) for frame in container.decode(video=0)]
                self.assertEqual(len(frames), len(original))
                for actual, expected in zip(frames, original):
                    self.assertAlmostEqual(float(actual[0]), float(expected[0] - original[0][0]), places=5)
                    self.assertEqual(actual[1:], expected[1:])
            expected = [{key: value for key, value in item.items() if key != "class_id"}
                        for item in result["detections"]]
            self.assertEqual(json.loads(downloads["json"]), {**result, "schema_version": "1.1", "detections": expected})
            rows = list(csv.DictReader(downloads["csv"].decode("utf-8-sig").splitlines()))
            self.assertEqual(len(rows), len(result["detections"]))
            for row, detection in zip(rows, result["detections"]):
                self.assertNotIn("class_id", row)
                self.assertEqual(int(row["frame_index"]), detection["frame_index"])
                self.assertEqual(float(row["timestamp_seconds"]), detection["timestamp_seconds"])
            for suffix, method in [("", "GET"), ("/video", "GET"), ("/download/video", "GET"),
                                   ("/download/json", "GET"), ("/download/csv", "GET"), ("/cancel", "POST"), ("", "DELETE")]:
                for visitor in [None, {"token": "other-visitor"}]:
                    with self.assertRaises(HTTPError) as denied:
                        self.call(endpoint + suffix, method, job=visitor)
                    self.assertEqual(denied.exception.code, 404)
            destination = os.environ.get("AUTOSCAN_VIDEO_EVIDENCE")
            if destination:
                directory = Path(destination)
                directory.mkdir(parents=True, exist_ok=True)
                for kind, extension in [("video", "mp4"), ("json", "json"), ("csv", "csv")]:
                    (directory / ("annotated." + extension)).write_bytes(downloads[kind])
        finally:
            self.delete(job)
        for suffix in ["", "/video", "/download/video", "/download/json", "/download/csv"]:
            with self.assertRaises(HTTPError) as deleted:
                self.call(endpoint + suffix, job=job)
            self.assertEqual(deleted.exception.code, 404)
