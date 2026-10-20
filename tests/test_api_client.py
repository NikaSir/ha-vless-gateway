from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest
import pytest
from aiohttp import web, ClientSession

path = Path(__file__).resolve().parents[1] / "custom_components/vless_gateway/api.py"
spec = spec_from_file_location("gateway_api", path)
api = module_from_spec(spec)
spec.loader.exec_module(api)


class ClientTests(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.usefixtures("socket_enabled")
    async def test_authenticated_read_only_and_schema_errors(self):
        async def handler(request):
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.headers.get("Authorization"), "Bearer test-token")
            return web.json_response(
                {
                    "schema_version": "1",
                    "gateway_version": "1.0.0-beta001",
                    "generated_at": "2026-10-20T00:00:00Z",
                    "state": "healthy",
                    "freshness": {"available": True, "age_seconds": 1, "stale": False},
                    "data": {"mode": "auto"},
                }
            )

        app = web.Application()
        app.router.add_get("/api/v1/status", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        try:
            async with ClientSession() as session:
                c = api.GatewayClient(
                    f"http://127.0.0.1:{port}", "test-token", session, allow_http=True
                )
                result = await c.async_get("status")
                self.assertEqual(result["data"]["mode"], "auto")
                with self.assertRaises(api.GatewayError):
                    await c.async_get("reload")
        finally:
            await runner.cleanup()

    def test_url_policy_and_schema_validation(self):
        for url, allow in (
            ("http://192.168.1.5", False),
            ("http://8.8.8.8", True),
            ("https://user:secret@example.com", False),
            ("https://example.com?token=secret", False),
        ):
            with self.assertRaises(api.GatewayError):
                api.normalize_base_url(url, allow_http=allow)
        self.assertEqual(
            api.normalize_base_url("https://gateway.example/"),
            "https://gateway.example",
        )
        with self.assertRaises(api.GatewaySchemaError):
            api.validate_envelope({"schema_version": "2"})
