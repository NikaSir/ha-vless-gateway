from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "vless_gateway"


class IntegrationContractTests(unittest.TestCase):
    def test_manifest_and_panel_versions_are_coherent(self) -> None:
        manifest = json.loads((INTEGRATION / "manifest.json").read_text(encoding="utf-8"))
        panel_manifest = json.loads(
            (INTEGRATION / "panel_manifest.json").read_text(encoding="utf-8")
        )
        constants = (INTEGRATION / "const.py").read_text(encoding="utf-8")
        panel = (INTEGRATION / "panel.py").read_text(encoding="utf-8")

        self.assertEqual(manifest["domain"], "vless_gateway")
        self.assertEqual(manifest["version"], "0.1.2")
        self.assertTrue(manifest["config_flow"])
        self.assertEqual(panel_manifest["ui_version"], "0.1.1")
        self.assertEqual(panel_manifest["template_version"], "2.2")
        self.assertEqual(panel_manifest["path"], "/dashboard-vless-gateway")
        self.assertEqual(
            panel_manifest["parent_route"], "/dashboard-infrastructure/overview"
        )
        self.assertIn('INTEGRATION_VERSION = "0.1.2"', constants)
        self.assertIn('PANEL_UI_VERSION = "0.1.1"', constants)
        self.assertIn('?v={PANEL_UI_VERSION}', panel)

    def test_panel_is_read_only_and_does_not_invent_entities(self) -> None:
        panel = (INTEGRATION / "panel.py").read_text(encoding="utf-8")
        panel_manifest = json.loads(
            (INTEGRATION / "panel_manifest.json").read_text(encoding="utf-8")
        )
        self.assertIn('"read_only": True', panel)
        self.assertIn('"entity_roles": {}', panel)
        self.assertTrue(panel_manifest["read_only"])
        self.assertFalse(panel_manifest["runtime_contract"]["synthetic_entity_ids"])
        self.assertEqual(
            panel_manifest["runtime_contract"]["command_policy"],
            "read_only_until_gateway_api_is_verified",
        )

    def test_config_flow_is_single_entry(self) -> None:
        source = (INTEGRATION / "config_flow.py").read_text(encoding="utf-8")
        self.assertIn("async_set_unique_id(DOMAIN)", source)
        self.assertIn("_abort_if_unique_id_configured()", source)
        self.assertIn('title="VLESS Gateway"', source)

    def test_hacs_and_translations_are_present(self) -> None:
        hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
        strings = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))
        translation = json.loads(
            (INTEGRATION / "translations" / "ru.json").read_text(encoding="utf-8")
        )
        self.assertEqual(hacs["name"], "NikaS VLESS Gateway")
        self.assertEqual(strings, translation)


if __name__ == "__main__":
    unittest.main()
