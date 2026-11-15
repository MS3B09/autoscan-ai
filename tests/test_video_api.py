"""Video job contract: real codecs/files/HTTP, with external GPU compute substituted."""

from fractions import Fraction
from io import BytesIO
import csv
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import subprocess
from unittest.mock import patch

import av
from fastapi.testclient import TestClient
from PIL import Image

from image_service.api import create_app
from image_service.video import render_video


def clip(*, frames=4, rate=4, size=(64, 48), format="mp4", codec="libx264", timestamps=None):
    output = BytesIO()
    with av.open(output, "w", format=format) as container:
        stream = container.add_stream(codec, rate=rate)
        stream.width, stream.height = size
        stream.pix_fmt = "yuv420p"
        clock = Fraction(1, rate) if format in ["avi", "mpeg"] else Fraction(1, 1000)
        stream.time_base = stream.codec_context.time_base = clock
        for index in range(frames):
            frame = av.VideoFrame.from_image(Image.new("RGB", size, (index % 255, 40, 80)))
            frame.pts = timestamps[index] if timestamps else round(Fraction(index, rate) / clock)
            frame.time_base = clock
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    return output.getvalue()


class VideoAPITests(unittest.TestCase):
    def wait(self, client, job):
        for _ in range(500):
            result = client.get("/api/jobs/" + job["id"], headers={"Authorization": "Bearer " + job["token"]})
            if result.json()["state"] not in ["queued", "processing", "cancelling"]:
                return result.json()
            time.sleep(0.01)
        self.fail("Job did not finish")

    def test_every_frame_and_source_timestamps_are_exported_with_protected_silent_mp4(self):
        def video_gpu(source, settings, cancelled, context):
            info = json.loads((source.parent / "video.json").read_text())

            def annotate(image):
                return image, [{"object_type": "plate", "class_id": 0, "class_name": "0", "label": "Plate",
                                "confidence": .75, "bbox": [1, 2, 20, 30], "width": 64, "height": 48}]

            output = source.parent / "result.mp4"
            detections = render_video(source, output, info, cancelled, annotate)
            return output.read_bytes(), detections

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(video_gpu, storage_root=storage)) as client:
                response = client.post("/api/jobs?filename=traffic.mp4&types=plate", content=clip(timestamps=[0, 100, 400, 900]))
                self.assertEqual(response.status_code, 202, response.text)
                job = response.json()
                result = self.wait(client, job)
                self.assertEqual(result["state"], "success", result.get("error"))
                self.assertEqual(result["media_type"], "video")
                self.assertEqual(result["frame_count"], 4)
                self.assertEqual(result["processed_frames"], 4)
                self.assertEqual([d["frame_index"] for d in result["detections"]], [0, 1, 2, 3])
                self.assertEqual([d["timestamp_seconds"] for d in result["detections"]], [0, .1, .4, .9])
                endpoint = "/api/jobs/" + job["id"]
                headers = {"Authorization": "Bearer " + job["token"]}
                for suffix, method in [("/video", "GET"), ("/download/video", "GET"), ("/download/json", "GET"),
                                       ("/download/csv", "GET"), ("/cancel", "POST"), ("", "DELETE")]:
                    for visitor in [{}, {"Authorization": "Bearer other-visitor"}]:
                        self.assertEqual(client.request(method, endpoint + suffix, headers=visitor).status_code, 404)
                movie = client.get(endpoint + "/download/video", headers=headers)
                self.assertEqual(movie.status_code, 200)
                self.assertEqual(movie.content, client.get(endpoint + "/video", headers=headers).content)
                self.assertTrue(movie.headers["content-disposition"].endswith('.mp4"'))
                with av.open(BytesIO(movie.content)) as output:
                    self.assertEqual(len(output.streams.audio), 0)
                    self.assertEqual(output.streams.video[0].codec_context.name, "h264")
                    frames = list(output.decode(video=0))
                    self.assertEqual([float(f.pts * f.time_base) for f in frames], [0, .1, .4, .9])
                self.assertEqual(client.get(endpoint + "/download/json", headers=headers).json(), result)
                rows = list(csv.DictReader(client.get(endpoint + "/download/csv", headers=headers).content.decode("utf-8-sig").splitlines()))
                self.assertEqual([int(row["frame_index"]) for row in rows], [0, 1, 2, 3])
                self.assertEqual([float(row["timestamp_seconds"]) for row in rows], [0, .1, .4, .9])
                self.assertFalse(any(Path(storage).glob("job-*/source.*")))
                self.assertEqual(client.get(endpoint + "/image", headers=headers).status_code, 404)
                client.delete(endpoint, headers=headers)
                self.assertEqual(client.get(endpoint + "/video", headers=headers).status_code, 404)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_preview_is_browser_codec_without_inference_and_rejects_invalid_content(self):
        def no_inference(*args):
            raise AssertionError("Preview must never start inference")

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(no_inference, storage_root=storage, submission_limit=100)) as client:
                response = client.post("/api/preview?filename=traffic.mp4", content=clip())
                self.assertEqual(response.status_code, 200, response.text[:200])
                self.assertEqual(response.headers["content-type"], "video/mp4")
                self.assertIn("no-store", response.headers["cache-control"])
                with av.open(BytesIO(response.content)) as output:
                    self.assertEqual(output.streams.video[0].codec_context.name, "h264")
                    self.assertEqual(len(output.streams.audio), 0)
                    self.assertEqual(len(list(output.decode(video=0))), 4)
                for data, filename, status in [(b"corrupt", "bad.mp4", 422),
                                                (clip(), "bad.avi", 415),
                                                (clip(), "bad.pt", 415),
                                                (b"x" * 20_000_001, "big.mp4", 413)]:
                    with self.subTest(filename=filename):
                        response = client.post("/api/preview", params={"filename": filename}, content=data)
                        self.assertEqual(response.status_code, status)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_all_containers_and_decoded_duration_dimension_frame_and_byte_ceilings(self):
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(lambda *args: None, storage_root=storage, submission_limit=100)) as client:
                for format, codec, extension in [("mp4", "libx264", "mp4"), ("mov", "libx264", "mov"),
                                                  ("mp4", "libx264", "m4v"), ("avi", "mpeg4", "avi"),
                                                  ("asf", "msmpeg4", "asf"), ("mpeg", "mpeg2video", "mpeg")]:
                    with self.subTest(container=extension):
                        data = clip(format=format, codec=codec, rate=25)
                        response = client.post("/api/preview?filename=source." + extension, content=data)
                        self.assertEqual(response.status_code, 200, response.text[:200])
                for data, expected in [(clip(frames=600, rate=60), 200),
                                       (clip(frames=601, rate=61), 413),
                                       (clip(frames=40, rate=4), 200),
                                       (clip(frames=41, rate=4), 413),
                                       (clip(size=(1280, 720)), 200),
                                       (clip(size=(720, 1280)), 200),
                                       (clip(size=(1282, 720)), 413),
                                       (clip(size=(1280, 722)), 413),
                                       (clip()[:200], 422)]:
                    with self.subTest(bytes=len(data), expected=expected):
                        response = client.post("/api/preview?filename=boundary.mp4", content=data)
                        self.assertEqual(response.status_code, expected, response.text[:200])
                data = clip()
                response = client.post("/api/preview?filename=exact.mp4", content=data + bytes(20_000_000 - len(data)))
                self.assertEqual(response.status_code, 200, response.text[:200])
                response = client.post("/api/jobs?filename=chunked.mp4", content=iter([b"x" * 10_000_001] * 2))
                self.assertEqual(response.status_code, 413)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_real_frame_progress_cancellation_and_failure_remove_partial_media(self):
        entered, release = threading.Event(), threading.Event()

        def held_gpu(source, settings, cancelled, context):
            info = json.loads((source.parent / "video.json").read_text())
            calls = 0

            def annotate(image):
                nonlocal calls
                calls += 1
                if calls == 2:
                    entered.set()
                    if not release.wait(5):
                        raise RuntimeError("Test release timeout")
                return image, []

            def progress(count):
                (source.parent / "progress.json").write_text(json.dumps({"processed_frames": count}))

            output = source.parent / "result.mp4"
            detections = render_video(source, output, info, cancelled, annotate, progress)
            return output.read_bytes(), detections

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(held_gpu, storage_root=storage, submission_limit=100)) as client:
                job = client.post("/api/jobs?filename=active.mp4", content=clip()).json()
                endpoint = "/api/jobs/" + job["id"]
                headers = {"Authorization": "Bearer " + job["token"]}
                try:
                    self.assertTrue(entered.wait(3))
                    result = client.get(endpoint, headers=headers).json()
                    self.assertEqual(result["processed_frames"], 1)
                    self.assertEqual(result["frame_count"], 4)
                    queued = client.post("/api/jobs?filename=queued.mp4", content=clip()).json()
                    second = client.post("/api/jobs?filename=second.mp4", content=clip()).json()
                    self.assertEqual(client.post("/api/jobs?filename=busy.mp4", content=clip()).status_code, 503)
                    for position, pending in enumerate([queued, second], 1):
                        path = "/api/jobs/" + pending["id"]
                        auth = {"Authorization": "Bearer " + pending["token"]}
                        self.assertEqual(client.get(path, headers=auth).json()["queue_position"], 1)
                        self.assertEqual(client.post(path + "/cancel", headers=auth).json()["state"], "cancelled")
                        self.assertEqual(client.get(path, headers=auth).json()["processed_frames"], 0)
                    self.assertEqual(client.post(endpoint + "/cancel", headers=headers).json()["state"], "cancelling")
                finally:
                    release.set()
                self.assertEqual(self.wait(client, job)["state"], "cancelled")
                self.assertFalse(any(path.is_file() for path in Path(storage).rglob("*")))
                for suffix in ["/video", "/download/video", "/download/json", "/download/csv"]:
                    self.assertEqual(client.get(endpoint + suffix, headers=headers).status_code, 409)

        def failed_gpu(source, settings, cancelled, context):
            (source.parent / "result.mp4").write_bytes(b"partial")
            raise RuntimeError("encoder failed: secret upload data")

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(failed_gpu, storage_root=storage)) as client:
                job = client.post("/api/jobs?filename=failure.mp4", content=clip()).json()
                result = self.wait(client, job)
                self.assertEqual(result["state"], "error")
                self.assertNotIn("secret", str(result))
                self.assertEqual(result["detections"], [])
                self.assertFalse(any(path.is_file() for path in Path(storage).rglob("*")))

    def test_video_empty_exports_and_expiry(self):
        def empty_gpu(source, settings, cancelled, context):
            info = json.loads((source.parent / "video.json").read_text())
            output = source.parent / "result.mp4"
            render_video(source, output, info, cancelled)
            return output.read_bytes(), []

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(empty_gpu, storage_root=storage, retention=.2)) as client:
                job = client.post("/api/jobs?filename=empty.mp4&types=plate&confidence=100", content=clip()).json()
                result = self.wait(client, job)
                self.assertEqual(result["state"], "empty")
                self.assertEqual(result["settings"], {"types": ["plate"], "confidence": 100})
                endpoint = "/api/jobs/" + job["id"]
                headers = {"Authorization": "Bearer " + job["token"]}
                rows = list(csv.reader(client.get(endpoint + "/download/csv", headers=headers).content.decode("utf-8-sig").splitlines()))
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][-2:], ["frame_index", "timestamp_seconds"])
                time.sleep(.3)
                for suffix in ["", "/video", "/download/video", "/download/json", "/download/csv"]:
                    self.assertEqual(client.get(endpoint + suffix, headers=headers).status_code, 404)
                time.sleep(1)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_invalid_timing_and_truncated_frames_are_rejected(self):
        original = clip(frames=20, rate=4)
        invalid = bytearray(original)
        atom = invalid.index(b"stts")
        # MP4 time-to-sample entries: force every sample duration to zero.
        entries = int.from_bytes(invalid[atom + 8:atom + 12], "big")
        for index in range(entries):
            offset = atom + 16 + index * 8
            invalid[offset:offset + 4] = bytes(4)
        corrupt = bytearray(original)
        start = corrupt.index(b"mdat") + 4
        corrupt[start:start + 100] = bytes(100)
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(lambda *args: None, storage_root=storage)) as client:
                for content in [invalid, corrupt]:
                    response = client.post("/api/jobs?filename=invalid.mp4", content=bytes(content))
                    self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_codec_timeout_is_actionable_and_does_not_leave_uploads_or_block_service(self):
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(lambda *args: None, storage_root=storage)) as client:
                content = clip()
                with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("codec", 50)):
                    response = client.post("/api/preview?filename=timeout.mp4", content=content)
                self.assertEqual(response.status_code, 503)
                self.assertIn("tim", response.json()["detail"].lower())
                self.assertEqual(client.get("/api/health").status_code, 200)
                self.assertEqual(list(Path(storage).iterdir()), [])

    def test_truncated_avi_is_not_presented_as_a_shorter_completed_clip(self):
        original = clip(frames=20, rate=25, format="avi", codec="mpeg4")
        position = original.index(b"movi") + 4
        pictures = 0
        while position + 8 <= len(original):
            if original[position:position + 4] in [b"00dc", b"00db"]:
                if pictures == 10:
                    break
                pictures += 1
            length = int.from_bytes(original[position + 4:position + 8], "little")
            position += 8 + length + length % 2
        self.assertEqual(pictures, 10)
        shortened = bytearray(original[:position])
        shortened[4:8] = (len(shortened) - 8).to_bytes(4, "little")
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(lambda *args: None, storage_root=storage)) as client:
                for content in [original[:position], shortened]:
                    with self.subTest(rewritten_outer_length=content is shortened):
                        response = client.post("/api/preview?filename=truncated.avi", content=bytes(content))
                        self.assertEqual(response.status_code, 422)
                        self.assertEqual(list(Path(storage).iterdir()), [])

    def test_video_storage_failure_is_actionable_and_leaves_no_upload(self):
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(lambda *args: None, storage_root=storage), raise_server_exceptions=False) as client:
                content = clip()
                for target in ["tempfile.TemporaryDirectory", "pathlib.Path.write_bytes"]:
                    with self.subTest(operation=target), patch(target, side_effect=OSError("private disk path")):
                        response = client.post("/api/preview?filename=storage.mp4", content=content)
                    self.assertEqual(response.status_code, 503)
                    self.assertNotIn("private", response.text)
                    self.assertEqual(list(Path(storage).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
