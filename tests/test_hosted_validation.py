"""Opt-in, anonymous integration check; consumes the Space's free GPU quota."""

import json
import os
from pathlib import Path
import time
import unittest
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@unittest.skipUnless(os.environ.get("AUTOSCAN_VALIDATION_URL"),
                     "Set AUTOSCAN_VALIDATION_URL after the diagnostic Space is running")
class HostedValidationTests(unittest.TestCase):
    def test_temporary_result_requires_its_capability_and_cannot_bypass_file_routes(self):
        base = os.environ["AUTOSCAN_VALIDATION_URL"].rstrip("/")
        with urlopen(Request(base + "/isolation-probes", method="POST"), timeout=60) as response:
            probe = json.load(response)
        endpoint = base + "/isolation-probes/" + probe["id"]
        headers = {"Authorization": "Bearer " + probe["token"]}
        try:
            for method in ["GET", "DELETE"]:
                for unauthorized in [{}, {"Authorization": "Bearer another-visitor"}]:
                    with self.assertRaises(HTTPError) as error:
                        urlopen(Request(endpoint, method=method, headers=unauthorized), timeout=30)
                    self.assertEqual(error.exception.code, 404)
            with urlopen(Request(endpoint, headers=headers), timeout=30) as response:
                result = json.load(response)
                self.assertEqual(result["kind"], "private diagnostic result")
                self.assertIn("no-store", response.headers["Cache-Control"])
            for prefix in ["/gradio_api/file=", "/file="]:
                with self.assertRaises(HTTPError) as error:
                    urlopen(base + prefix + probe["path"], timeout=30)
                self.assertIn(error.exception.code, [403, 404])
            with urlopen(Request(endpoint, method="DELETE", headers=headers), timeout=30) as response:
                self.assertEqual(response.status, 204)
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(endpoint, headers=headers), timeout=30)
            self.assertEqual(error.exception.code, 404)
        finally:
            try:
                urlopen(Request(endpoint, method="DELETE", headers=headers), timeout=30).close()
            except HTTPError as error:
                if error.code != 404:
                    raise

    def test_temporary_result_expires_without_a_browser_cleanup_request(self):
        base = os.environ["AUTOSCAN_VALIDATION_URL"].rstrip("/")
        with urlopen(Request(base + "/isolation-probes", method="POST"), timeout=60) as response:
            probe = json.load(response)
        self.assertEqual(probe["expires_in_seconds"], 30)
        endpoint = base + "/isolation-probes/" + probe["id"]
        headers = {"Authorization": "Bearer " + probe["token"]}
        with urlopen(Request(endpoint, headers=headers), timeout=30) as response:
            self.assertEqual(response.status, 200)
        time.sleep(probe["expires_in_seconds"] + 1)
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(endpoint, headers=headers), timeout=30)
        self.assertEqual(error.exception.code, 404)

    def test_anonymous_cross_origin_job_preserves_models_and_video_frames(self):
        base = os.environ["AUTOSCAN_VALIDATION_URL"].rstrip("/")
        parsed = urlparse(base)
        self.assertEqual(parsed.scheme, "https")
        self.assertTrue(parsed.hostname and parsed.hostname.endswith(".hf.space"))
        endpoint = base + "/gradio_api/call/validate"
        origin = "https://autoscan-ai.netlify.app"
        preflight = Request(endpoint, method="OPTIONS", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        with urlopen(preflight, timeout=60) as response:
            self.assertIn(response.headers.get("Access-Control-Allow-Origin"), [origin, "*"])
            self.assertIn("POST", response.headers.get("Access-Control-Allow-Methods", ""))

        request = Request(endpoint, data=b'{"data": []}', headers={
            "Content-Type": "application/json", "Origin": origin,
        })
        with urlopen(request, timeout=60) as response:
            self.assertIn(response.headers.get("Access-Control-Allow-Origin"), [origin, "*"])
            event_id = json.load(response)["event_id"]

        # This stream blocks on server events; it does not repeatedly submit jobs.
        report = None
        event = None
        deadline = time.monotonic() + 240
        result_request = Request(endpoint + "/" + event_id, headers={"Origin": origin})
        with urlopen(result_request, timeout=60) as response:
            for raw in response:
                if time.monotonic() > deadline:
                    self.fail("Hosted validation exceeded the four-minute event-stream budget")
                line = raw.decode("utf-8").strip()
                if line.startswith("event: "):
                    event = line[7:]
                elif line.startswith("data: ") and event == "error":
                    self.fail("Hosted diagnostic failed: " + line[6:])
                elif line.startswith("data: ") and event == "complete":
                    report = json.loads(line[6:])[0]
                    break
        self.assertIsInstance(report, dict, "No completed report received")
        self.assertEqual(report["device"], "cuda")
        self.assertTrue(report["gpu"])
        self.assertEqual(report["models"]["logo"]["sha256"],
                         "52e8aceec272ba35decc6b85f61cb21af06a4c14f9f245cfedb22caf465cf356")
        self.assertEqual(report["models"]["plate"]["sha256"],
                         "aa9742bb9fe5728cbe74027a9c4f8842d6c11f1423903b8ec8fc97e05e6293bb")
        self.assertEqual(report["models"]["vehicle"]["sha256"],
                         "31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95")
        self.assertEqual(len(report["models"]["logo"]["classes"]), 24)
        self.assertEqual(report["models"]["logo"]["classes"]["16"], "peugeot")
        self.assertEqual(report["models"]["plate"]["classes"], {"0": "0"})
        self.assertGreater(report["image"]["detection_count"], 0)
        self.assertEqual(report["video"]["frames_written"], 300)
        self.assertEqual(report["video"]["frames_decoded"], 300)
        self.assertEqual(report["video"]["source_frames_decoded"], 300)
        self.assertEqual((report["video"]["width"], report["video"]["height"]), (1280, 720))
        self.assertEqual(report["video"]["duration_seconds"], 10)
        self.assertLessEqual(report["video"]["source_bytes"], 20_000_000)
        if os.environ.get("AUTOSCAN_VALIDATION_REPORT"):
            Path(os.environ["AUTOSCAN_VALIDATION_REPORT"]).write_text(
                json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
