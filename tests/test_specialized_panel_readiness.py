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

    def test_bootstrap_does_not_claim_a_runtime(self) -> None:
        self.assertEqual(self.contract["standard_version"], "1.8")
        self.assertFalse(self.contract["integration"]["present"])
        self.assertFalse(self.contract["panel"]["runtime_present"])
        self.assertFalse(self.contract["panel"]["runtime_compliance_claimed"])
        self.assertFalse((ROOT / "custom_components").exists())

    def test_future_shell_contract_is_complete(self) -> None:
        future = self.contract["future_panel_contract"]
        self.assertEqual(future["scale_percent"], [75, 200])
        self.assertEqual(future["snap_to_100_percent"], [97, 103])
        self.assertTrue(future["native_vertical_scroll_at_100_percent"])
        self.assertFalse(future["horizontal_scroll_at_100_percent"])
        self.assertTrue(future["one_finger_pan_only_above_100_percent"])
        self.assertEqual(future["pan_axes"], "overflow_only")
        self.assertTrue(future["stable_dom_after_initial_mount"])
        self.assertEqual(future["meaningful_font_range_px"], [12, 25])

    def test_optional_indicator_is_disabled(self) -> None:
        indicator = self.contract["optional_connection_indicator"]
        self.assertFalse(indicator["enabled"])
        self.assertEqual(indicator["policy"], "explicit_repository_request_only")

    def test_approved_repository_icon_is_512_square_alpha_png(self) -> None:
        path = ROOT / self.contract["repository_identity"]["icon"]
        data = path.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (512, 512))
        self.assertIn(data[25], (4, 6))
        self.assertIn("assets/icon.png", (ROOT / "README.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
