from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "SPECIALIZED_PANEL_READINESS.json"


class SpecializedPanelReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_installable_scaffold_is_declared_truthfully(self) -> None:
        self.assertEqual(self.contract["standard_version"], "1.9")
        self.assertEqual(self.contract["repository_state"], "installable_panel_scaffold")
        self.assertTrue(self.contract["integration"]["present"])
        self.assertTrue(self.contract["integration"]["config_flow_present"])
        self.assertTrue(self.contract["panel"]["runtime_present"])
        self.assertTrue(self.contract["panel"]["route_registered"])
        self.assertFalse(self.contract["panel"]["runtime_compliance_claimed"])
        self.assertEqual(
            self.contract["panel"]["acceptance_status"],
            "automated_checks_then_real_iphone_required",
        )

    def test_runtime_paths_exist(self) -> None:
        integration = ROOT / "custom_components" / "vless_gateway"
        for path in (
            integration / "manifest.json",
            integration / "config_flow.py",
            integration / "panel.py",
            integration / "frontend" / "vless-gateway-panel.js",
            ROOT / "hacs.json",
        ):
            self.assertTrue(path.is_file(), path)

    def test_shell_contract_is_complete(self) -> None:
        panel = self.contract["panel_contract"]
        self.assertEqual(panel["scale_percent"], [75, 200])
        self.assertEqual(panel["snap_to_100_percent"], [97, 103])
        self.assertTrue(panel["native_vertical_scroll_at_100_percent"])
        self.assertFalse(panel["horizontal_scroll_at_100_percent"])
        self.assertTrue(panel["one_finger_pan_only_above_100_percent"])
        self.assertEqual(panel["pan_axes"], "overflow_only")
        self.assertTrue(panel["stable_dom_after_initial_mount"])
        self.assertFalse(panel["invented_entity_ids"])
        self.assertEqual(panel["meaningful_font_range_px"], [12, 25])
        self.assertEqual(panel["tabs"], ["overview", "routes", "traffic", "diagnostics"])

    def test_optional_indicator_remains_disabled(self) -> None:
        indicator = self.contract["optional_connection_indicator"]
        self.assertFalse(indicator["enabled"])
        self.assertEqual(indicator["policy"], "explicit_repository_request_only")

    def test_repository_and_packaged_icons_are_approved(self) -> None:
        repository_icon = ROOT / self.contract["repository_identity"]["icon"]
        packaged_icon = ROOT / self.contract["repository_identity"]["packaged_icon"]
        packaged_icon_2x = packaged_icon.with_name("icon@2x.png")
        data = packaged_icon.read_bytes()
        data_2x = packaged_icon_2x.read_bytes()
        self.assertEqual(repository_icon.read_bytes(), data_2x)
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(data_2x[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (256, 256))
        self.assertEqual(struct.unpack(">II", data_2x[16:24]), (512, 512))
        self.assertIn(data[25], (4, 6))
        self.assertIn(data_2x[25], (4, 6))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("assets/icon.png", readme)
        self.assertIn("/dashboard-vless-gateway", readme)


if __name__ == "__main__":
    unittest.main()
