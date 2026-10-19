import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "gateway_roles",
    Path(__file__).resolve().parents[1] / "custom_components/vless_gateway/roles.py",
)
roles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roles)


def envelope(data, stale=False):
    return {
        "state": "healthy",
        "freshness": {"available": True, "age_seconds": 1, "stale": stale},
        "data": data,
    }


class MappingTests(unittest.TestCase):
    def test_direct_traffic_is_total_sing_box_traffic_not_vless_accounting(self):
        data = {
            "status": envelope({"active_route": {"available": True, "value": "direct"}}),
            "traffic": envelope({"download_total": {"available": True, "value": 120}, "upload_total": {"available": True, "value": 30}}),
        }
        self.assertEqual(roles.role_value(data, "routed_traffic"), 150)
        self.assertEqual(roles.SENSOR_ROLES["routed_traffic"], "Трафик sing-box")

    def test_fresh_selector_loss_does_not_reuse_desired_or_prior_route(self):
        data = {"status": envelope({"state": "control_error", "desired_route": "de", "active_route": {"available": False, "value": None, "error": "selector_unavailable"}})}
        self.assertIsNone(roles.role_value(data, "active_route"))
        self.assertIsNone(roles.role_value(data, "latency"))
        self.assertEqual(roles.role_value(data, "gateway_status"), "control_error")

    def test_available_zero_is_factual_but_unavailable_is_none(self):
        data = {
            "traffic": envelope(
                {
                    "download_rate": {"available": True, "value": 0},
                    "upload_rate": {"available": False, "value": None},
                }
            )
        }
        self.assertEqual(roles.role_value(data, "download_rate"), 0)
        self.assertIsNone(roles.role_value(data, "upload_rate"))
        data["traffic"]["freshness"]["stale"] = True
        self.assertIsNone(roles.role_value(data, "download_rate"))

    def test_route_and_latency_use_confirmed_selection(self):
        data = {
            "status": envelope(
                {
                    "active_route": {"available": True, "value": "nl"},
                    "desired_route": "de",
                    "mode": "auto",
                }
            ),
            "routes": envelope(
                {
                    "germany": {"latency_ms": {"available": True, "value": 10}},
                    "netherlands": {"latency_ms": {"available": True, "value": 40}},
                }
            ),
        }
        self.assertEqual(roles.role_value(data, "active_route"), "nl")
        self.assertEqual(roles.role_value(data, "default_route"), "de")
        self.assertEqual(roles.role_value(data, "latency"), 40)
        self.assertIsNone(roles.role_value(data, "traffic_month"))
