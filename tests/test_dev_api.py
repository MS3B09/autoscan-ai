"""Local developer HTTP contract; fake external Hub/Space replies, no GPU or real tokens."""

from contextlib import contextmanager
from unittest.mock import patch
import unittest

from fastapi.testclient import TestClient
import httpx

from scripts.dev_api import create_app


class DeveloperAPITests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.profile = {"name": "MS3B09", "isPro": False, "auth": {"accessToken": {"role": "read"}}}
        self.quota = {"base": 300, "current": 300, "overquotaUsed": 0, "resetsAt": None,
                      "runs": {"remaining": 8, "resetsAt": None}}
        self.job = {"id": "a" * 32, "token": "k" * 43, "state": "queued"}
        self.failure = None

    def upstream(self, request):
        self.requests.append(request)
        if request.url.host == "huggingface.co":
            self.assertEqual(request.headers["authorization"], "Bearer hf_readonlytest")
            self.assertFalse(request.headers.get("cookie"))
            if request.url.path == "/api/whoami-v2":
                return httpx.Response(200, json=self.profile)
            if request.url.path == "/api/spaces/zero-gpu/quota":
                return httpx.Response(200, json=self.quota)
            self.fail("Unexpected authenticated Hub endpoint")
        self.assertEqual(request.url.host, "ms3b09-autoscan-ai-images.hf.space")
        if self.failure == "timeout":
            raise httpx.ReadTimeout("sensitive path hf_readonlytest", request=request)
        if self.failure == "redirect":
            return httpx.Response(307, headers={"Location": "https://attacker.example/steal"})
        if self.failure == "html":
            return httpx.Response(500, text="sensitive path hf_readonlytest")
        if self.failure == "echo":
            return httpx.Response(200, json={"unexpected": "hf_readonlytest"})
        if request.url.path == "/api/jobs":
            return httpx.Response(202, json=self.job, headers={"Set-Cookie": "owner=session; Path=/"})
        return httpx.Response(200, json={"state": "success"})

    @contextmanager
    def client(self, peer="127.0.0.1"):
        async_client = httpx.AsyncClient
        with patch("scripts.dev_api.httpx.AsyncClient", side_effect=lambda **kwargs:
                   async_client(transport=httpx.MockTransport(self.upstream), **kwargs)):
            with TestClient(create_app("hf_readonlytest"), base_url="http://127.0.0.1:7862",
                            headers={"Origin": "http://127.0.0.1:5173"}, client=(peer, 50000)) as client:
                yield client

    def test_only_submission_uses_hf_token_and_private_operations_keep_the_job_key(self):
        with self.client() as client:
            submitted = client.post("/api/jobs?filename=photo.png&types=vehicle&confidence=40", content=b"source")
            self.assertEqual(submitted.status_code, 202)
            self.assertEqual(submitted.json(), self.job)
            endpoint = "/api/jobs/" + self.job["id"]
            for path, method in [("/api/preview?filename=photo.png", "POST"), ("/api/health", "GET"),
                                 (endpoint, "GET"), (endpoint + "/download/json", "GET"),
                                 (endpoint + "/cancel", "POST"), (endpoint, "DELETE")]:
                client.request(method, path, headers={"Authorization": "Bearer " + self.job["token"]})
            space_requests = [request for request in self.requests if request.url.host.endswith("hf.space")]
            self.assertEqual(space_requests[0].headers["authorization"], "Bearer hf_readonlytest")
            self.assertEqual(space_requests[0].content, b"source")
            self.assertEqual(space_requests[0].url.params["filename"], "photo.png")
            for request in space_requests[1:]:
                if request.url.path in ["/api/preview", "/api/health"]:
                    self.assertNotIn("authorization", request.headers)
                else:
                    self.assertEqual(request.headers["authorization"], "Bearer " + self.job["token"])
                self.assertFalse(request.headers.get("cookie"))
            self.assertNotIn("hf_readonlytest", submitted.text)
            self.assertNotIn("set-cookie", submitted.headers)

    def test_startup_requires_an_explicit_read_token_and_free_personal_account(self):
        for token in ["", "hf_secret\r\nInjected: yes", "not-a-token"]:
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, "READ"):
                create_app(token)
        for change in ["write", "pro", "other_account", "paid_quota", "paid_usage"]:
            with self.subTest(change=change):
                self.setUp()
                if change == "write": self.profile["auth"]["accessToken"]["role"] = "write"
                if change == "pro": self.profile["isPro"] = True
                if change == "other_account": self.profile["name"] = "another-account"
                if change == "paid_quota": self.quota["base"] = 2400
                if change == "paid_usage": self.quota["overquotaUsed"] = 10
                with self.assertRaisesRegex(ValueError, "READ.*free"):
                    with self.client(): pass
                self.assertFalse(any(request.url.host.endswith("hf.space") for request in self.requests))

    def test_other_sites_hosts_and_remote_peers_cannot_spend_account_quota(self):
        with self.client() as client:
            before = len(self.requests)
            for headers in [{"Origin": "https://attacker.example"}, {"Origin": ""},
                            {"Host": "attacker.example:7862"}, {"Host": "localhost:7862"}]:
                with self.subTest(headers=headers):
                    response = client.post("/api/jobs?filename=photo.png", content=b"source", headers=headers)
                    self.assertEqual(response.status_code, 403)
                    self.assertNotIn("hf_readonlytest", response.text)
            self.assertEqual(len(self.requests), before)
            allowed = client.options("/api/jobs", headers={"Access-Control-Request-Method": "POST"})
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed.headers["access-control-allow-origin"], "http://127.0.0.1:5173")
            self.assertNotIn("access-control-allow-credentials", allowed.headers)
        with self.client(peer="192.168.1.10") as client:
            before = len(self.requests)
            self.assertEqual(client.post("/api/jobs", content=b"source").status_code, 403)
            self.assertEqual(len(self.requests), before)

    def test_uploads_are_bounded_before_forwarding(self):
        with self.client() as client:
            before = len(self.requests)
            for content, headers in [(b"x" * 20_000_001, {}),
                                     (iter([b"x" * 10_000_001] * 2), {}),
                                     (b"x", {"Content-Length": "invalid"})]:
                response = client.post("/api/preview?filename=clip.mp4", content=content, headers=headers)
                self.assertIn(response.status_code, [400, 413])
                self.assertNotIn("hf_readonlytest", response.text)
            self.assertEqual(len(self.requests), before)

    def test_only_known_job_api_paths_and_methods_are_forwarded(self):
        with self.client() as client:
            before = len(self.requests)
            for path, method in [("/api/jobs//attacker.example", "POST"), ("/api/gradio_api/upload", "POST"),
                                 ("/api/jobs", "GET"), ("/api/preview", "GET"), ("/api/health", "DELETE"),
                                 ("/api/jobs/" + "a" * 32 + "/download/weights", "GET")]:
                with self.subTest(path=path, method=method):
                    self.assertEqual(client.request(method, path).status_code, 404)
            self.assertEqual(len(self.requests), before)

    def test_exhausted_developer_quota_returns_reset_without_submitting_or_paying(self):
        with self.client() as client:
            self.quota.update(current=10, resetsAt="2030-01-01T00:00:00Z")
            response = client.post("/api/jobs?filename=photo.png", content=b"source")
            self.assertEqual(response.status_code, 429)
            self.assertEqual(response.json()["retry_at"], 1893456000)
            self.assertIn("2030-01-01 00:00:00 UTC", response.json()["detail"])
            self.quota["runs"] = {"remaining": 0, "resetsAt": "2030-01-02T00:00:00Z"}
            response = client.post("/api/jobs?filename=photo.png", content=b"source")
            self.assertEqual(response.json()["retry_at"], 1893542400)
            self.quota["runs"]["resetsAt"] = None
            response = client.post("/api/jobs?filename=photo.png", content=b"source")
            self.assertEqual(response.status_code, 429)
            self.assertNotIn("retry_at", response.json())
            self.assertIn("did not provide a reset time", response.json()["detail"])
            self.quota.update(base=2400, current=2400)
            self.assertEqual(client.post("/api/jobs", content=b"source").status_code, 503)
            self.assertFalse(any(request.url.host.endswith("hf.space") for request in self.requests))

    def test_transport_failures_and_redirects_never_reveal_tokens_or_retry_submission(self):
        with self.client() as client:
            for self.failure in ["timeout", "redirect", "html", "echo"]:
                with self.subTest(failure=self.failure):
                    before = len([request for request in self.requests if request.url.host.endswith("hf.space")])
                    response = client.post("/api/jobs?filename=photo.png", content=b"source")
                    self.assertEqual(response.status_code, 503)
                    self.assertNotIn("hf_readonlytest", response.text)
                    self.assertNotIn("sensitive", response.text)
                    self.assertNotIn("location", response.headers)
                    self.assertEqual(response.headers["cache-control"], "no-store")
                    after = len([request for request in self.requests if request.url.host.endswith("hf.space")])
                    self.assertEqual(after - before, 1)

    def test_unknown_or_malformed_run_allowance_fails_closed(self):
        with self.client() as client:
            for runs in [None, {}, {"remaining": -1}, {"remaining": "8"}, {"remaining": True}, []]:
                with self.subTest(runs=runs):
                    self.quota["runs"] = runs
                    response = client.post("/api/jobs?filename=photo.png", content=b"source")
                    self.assertEqual(response.status_code, 503)
                    self.assertIn("No detection was submitted", response.json()["detail"])
            self.assertFalse(any(request.url.host.endswith("hf.space") for request in self.requests))
