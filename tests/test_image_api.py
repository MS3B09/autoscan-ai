"""Job-API contract checks; the injected GPU boundary is NOT hosted model evidence."""

from io import BytesIO
import time
import tempfile
import threading
import unittest

from fastapi.testclient import TestClient
from PIL import Image

from image_service.api import create_app


def image_bytes(format="PNG", size=(48, 32)):
    output = BytesIO()
    Image.new("RGB", size, "white").save(output, format=format)
    return output.getvalue()


def empty_gpu(source, settings, cancelled, context):
    # External-compute test double; production always uses the trusted detectors.
    with Image.open(source) as image:
        output = BytesIO()
        image.save(output, format="PNG")
    return output.getvalue(), []


class ImageAPITests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory(prefix="autoscan-api-test-")
        self.addCleanup(self.storage.cleanup)
        self.context = TestClient(create_app(empty_gpu, submission_limit=100, storage_root=self.storage.name))
        self.client = self.context.__enter__()
        self.addCleanup(self.context.__exit__, None, None, None)

    def submit(self, content=None, filename="photo.png", types="vehicle,logo,plate", confidence="40"):
        return self.client.post("/api/jobs", content=image_bytes() if content is None else content,
                                params={"filename": filename, "types": types, "confidence": confidence},
                                headers={"Content-Type": "application/octet-stream"})

    def wait(self, job):
        for _ in range(200):
            response = self.client.get("/api/jobs/" + job["id"],
                                       headers={"Authorization": "Bearer " + job["token"]})
            if response.status_code != 200 or response.json()["state"] not in ["queued", "processing", "cancelling"]:
                return response
            time.sleep(0.01)
        self.fail("Job did not reach a terminal state")

    def test_decoded_upload_is_validated_before_a_job_is_accepted(self):
        for data, filename, status in [(b"not an image", "photo.png", 422),
                                       (image_bytes(), "weights.pt", 415),
                                       (image_bytes("JPEG"), "photo.png", 415),
                                       (b"x" * 10_000_001, "photo.png", 413),
                                       (image_bytes(size=(4001, 3000)), "photo.png", 413)]:
            with self.subTest(filename=filename, status=status):
                self.assertEqual(self.submit(data, filename).status_code, status)
        for types, confidence in [("", "40"), ("vehicle,unknown", "40"), ("logo", "24"),
                                  ("plate", "101"), ("vehicle", "nan"), ("logo", "40.5")]:
            with self.subTest(types=types, confidence=confidence):
                self.assertEqual(self.submit(types=types, confidence=confidence).status_code, 422)
        # A chunked body cannot bypass the ceiling by omitting Content-Length.
        response = self.client.post("/api/jobs?filename=chunked.png", content=iter([b"x" * 5_000_001] * 2))
        self.assertEqual(response.status_code, 413)

    def test_supported_images_finish_empty_and_results_require_their_capability(self):
        for format, extension in [("PNG", "png"), ("JPEG", "jpeg"), ("BMP", "bmp"), ("WEBP", "webp")]:
            with self.subTest(format=format):
                response = self.submit(image_bytes(format), "photo." + extension, "plate", "100")
                self.assertEqual(response.status_code, 202)
                job = response.json()
                result = self.wait(job)
                self.assertEqual(result.status_code, 200)
                self.assertEqual(result.json()["state"], "empty")
                self.assertEqual(result.json()["detections"], [])
                self.assertEqual(result.json()["settings"], {"types": ["plate"], "confidence": 100})
                self.assertEqual((result.json()["width"], result.json()["height"]), (48, 32))
                endpoint = "/api/jobs/" + job["id"]
                headers = {"Authorization": "Bearer " + job["token"]}
                for suffix, method in [("", "GET"), ("/image", "GET"), ("/cancel", "POST"), ("", "DELETE")]:
                    for unauthorized in [{}, {"Authorization": "Bearer wrong-visitor"}]:
                        self.assertEqual(self.client.request(method, endpoint + suffix, headers=unauthorized).status_code, 404)
                image = self.client.get(endpoint + "/image", headers=headers)
                self.assertEqual(image.status_code, 200)
                self.assertIn("no-store", image.headers["cache-control"])
                with Image.open(BytesIO(image.content)) as annotated:
                    self.assertEqual(annotated.size, (48, 32))
                self.assertEqual(self.client.delete(endpoint, headers=headers).status_code, 204)
                self.assertEqual(self.client.get(endpoint, headers=headers).status_code, 404)
                self.assertEqual(self.client.get(endpoint + "/image", headers=headers).status_code, 404)

    def test_one_active_two_pending_and_safe_cancellation_and_delete(self):
        entered, release = threading.Event(), threading.Event()

        def held_gpu(source, settings, cancelled, context):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("Test GPU did not release")
            return empty_gpu(source, settings, cancelled, context)

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(held_gpu, submission_limit=100, storage_root=storage)) as client:
                self.client = client
                active = self.submit().json()
                self.assertTrue(entered.wait(2))
                queued = self.submit().json()
                deleted = self.submit().json()
                try:
                    self.assertEqual(self.submit().status_code, 503)
                    for job in [queued, deleted]:
                        state = client.get("/api/jobs/" + job["id"], headers={"Authorization": "Bearer " + job["token"]})
                        self.assertEqual(state.json()["state"], "queued")
                    response = client.post("/api/jobs/" + queued["id"] + "/cancel",
                                           headers={"Authorization": "Bearer " + queued["token"]})
                    self.assertEqual(response.json()["state"], "cancelled")
                    self.assertEqual(client.delete("/api/jobs/" + deleted["id"],
                                                   headers={"Authorization": "Bearer " + deleted["token"]}).status_code, 204)
                    response = client.post("/api/jobs/" + active["id"] + "/cancel",
                                           headers={"Authorization": "Bearer " + active["token"]})
                    self.assertEqual(response.json()["state"], "cancelling")
                finally:
                    release.set()
                self.assertEqual(self.wait(active).json()["state"], "cancelled")
                self.assertEqual(client.get("/api/jobs/" + active["id"] + "/image",
                                             headers={"Authorization": "Bearer " + active["token"]}).status_code, 409)

    def test_server_expiry_and_rate_limit_do_not_depend_on_the_browser(self):
        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(empty_gpu, submission_limit=1, retention=0.05, storage_root=storage)) as client:
                self.client = client
                job = self.submit().json()
                self.assertEqual(self.wait(job).json()["state"], "empty")
                time.sleep(0.1)
                self.assertEqual(client.get("/api/jobs/" + job["id"],
                                             headers={"Authorization": "Bearer " + job["token"]}).status_code, 404)
                response = self.submit()
                self.assertEqual(response.status_code, 429)
                self.assertIn("retry-after", response.headers)

    def test_preview_normalizes_orientation_without_starting_inference(self):
        source = BytesIO()
        image = Image.new("RGB", (48, 32), "red")
        exif = Image.Exif()
        exif[274] = 6
        image.save(source, format="JPEG", exif=exif)
        response = self.client.post("/api/preview", params={"filename": "rotated.jpg"}, content=source.getvalue())
        self.assertEqual(response.status_code, 200)
        with Image.open(BytesIO(response.content)) as preview:
            self.assertEqual(preview.size, (32, 48))
            self.assertFalse(preview.getexif())
        transparent = BytesIO()
        Image.new("RGBA", (1, 1), (255, 0, 0, 0)).save(transparent, "PNG")
        response = self.client.post("/api/preview?filename=transparent.png", content=transparent.getvalue())
        with Image.open(BytesIO(response.content)) as preview:
            self.assertEqual(preview.mode, "RGB")
            self.assertEqual(preview.getpixel((0, 0)), (255, 255, 255))

    def test_delete_processing_revokes_access_before_compute_returns(self):
        entered, release = threading.Event(), threading.Event()

        def held_gpu(source, settings, cancelled, context):
            entered.set()
            release.wait(5)
            return empty_gpu(source, settings, cancelled, context)

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(held_gpu, storage_root=storage)) as client:
                self.client = client
                job = self.submit(filename="../../private.png").json()
                try:
                    self.assertTrue(entered.wait(2))
                    endpoint = "/api/jobs/" + job["id"]
                    headers = {"Authorization": "Bearer " + job["token"]}
                    self.assertEqual(client.delete(endpoint, headers=headers).status_code, 204)
                    for suffix in ["", "/image"]:
                        self.assertEqual(client.get(endpoint + suffix, headers=headers).status_code, 404)
                    self.assertEqual(client.post(endpoint + "/cancel", headers=headers).status_code, 404)
                    for path in ["/gradio_api/upload", "/gradio_api/file=" + storage + "/source.png",
                                 "/file=" + storage + "/result.png"]:
                        self.assertEqual(client.get(path).status_code, 404)
                finally:
                    release.set()

    def test_gpu_failure_is_not_empty_and_does_not_expose_exception_payloads(self):
        def failed_gpu(source, settings, cancelled, context):
            raise RuntimeError("ZeroGPU quota exhausted: sensitive image/detection details")

        with tempfile.TemporaryDirectory() as storage:
            with TestClient(create_app(failed_gpu, storage_root=storage)) as client:
                self.client = client
                job = self.submit().json()
                result = self.wait(job).json()
                self.assertEqual(result["state"], "error")
                self.assertIn("quota", result["error"])
                self.assertNotIn("sensitive", str(result))
                self.assertEqual(client.get("/api/jobs/" + job["id"] + "/image",
                                             headers={"Authorization": "Bearer " + job["token"]}).status_code, 409)

    def test_retained_jobs_are_bounded_and_deletion_releases_capacity(self):
        jobs = []
        for _ in range(8):
            job = self.submit().json()
            self.assertEqual(self.wait(job).json()["state"], "empty")
            jobs.append(job)
        self.assertEqual(self.submit().status_code, 503)
        first = jobs[0]
        self.client.delete("/api/jobs/" + first["id"], headers={"Authorization": "Bearer " + first["token"]})
        self.assertEqual(self.submit().status_code, 202)


if __name__ == "__main__":
    unittest.main()
