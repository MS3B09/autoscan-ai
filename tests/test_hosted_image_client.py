"""Outgoing HTTP credential checks, not evidence of hosted GPU authentication."""

from io import BytesIO
import json
import os
import unittest
from unittest.mock import patch

import test_hosted_image_api as hosted


def echo_request(request, timeout):
    return BytesIO(json.dumps({"authorization": request.get_header("Authorization"),
                               "method": request.get_method(), "url": request.full_url}).encode())


class HostedImageClientTests(unittest.TestCase):
    def test_submission_uses_explicit_inference_token(self):
        with patch.dict(os.environ, {"AUTOSCAN_IMAGE_URL": "https://ms3b09-autoscan-ai-images.hf.space",
                                     "AUTOSCAN_TEST_HF_TOKEN": "hf_fake_inference_token"}):
            with patch.object(hosted, "urlopen", side_effect=echo_request):
                response = hosted.HostedImageTests().submit(b"test image")
        self.assertEqual(response["authorization"], "Bearer hf_fake_inference_token")
        self.assertEqual(response["method"], "POST")
        self.assertTrue(response["url"].startswith("https://ms3b09-autoscan-ai-images.hf.space/api/jobs?"))

    def test_inference_token_is_not_sent_to_other_hosts(self):
        with patch.dict(os.environ, {"AUTOSCAN_IMAGE_URL": "https://unrelated.example",
                                     "AUTOSCAN_TEST_HF_TOKEN": "hf_fake_inference_token"}):
            with patch.object(hosted, "urlopen", side_effect=AssertionError("Must reject before HTTP")):
                with self.assertRaisesRegex(ValueError, "restricted"):
                    hosted.HostedImageTests().submit(b"test image")

    def test_private_operations_use_only_the_job_key_and_public_probes_stay_anonymous(self):
        with patch.dict(os.environ, {"AUTOSCAN_IMAGE_URL": "https://ms3b09-autoscan-ai-images.hf.space",
                                     "AUTOSCAN_TEST_HF_TOKEN": "hf_fake_inference_token"}):
            with patch.object(hosted, "urlopen", side_effect=echo_request):
                client = hosted.HostedImageTests()
                for path, method in [("/api/jobs/id", "GET"), ("/api/jobs/id/download/json", "GET"),
                                     ("/api/jobs/id/cancel", "POST"), ("/api/jobs/id", "DELETE")]:
                    with self.subTest(path=path, method=method):
                        with client.call(path, method, job={"token": "private-job-key"}) as response:
                            self.assertEqual(json.load(response)["authorization"], "Bearer private-job-key")
                for path, method in [("/api/health", "GET"), ("/api/preview?filename=photo.png", "POST"),
                                     ("/api/jobs/id", "GET"), ("/gradio_api/upload", "GET")]:
                    with client.call(path, method) as response:
                        self.assertIsNone(json.load(response)["authorization"])

    def test_absent_inference_token_does_not_fall_back_to_the_deployment_token(self):
        with patch.dict(os.environ, {"AUTOSCAN_IMAGE_URL": "https://ms3b09-autoscan-ai-images.hf.space",
                                     "HF_TOKEN": "hf_fake_write_token"}):
            os.environ.pop("AUTOSCAN_TEST_HF_TOKEN", None)
            with patch.object(hosted, "urlopen", side_effect=echo_request):
                response = hosted.HostedImageTests().submit(b"test image")
        self.assertIsNone(response["authorization"])


if __name__ == "__main__":
    unittest.main()
