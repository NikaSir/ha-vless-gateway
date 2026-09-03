from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = (
    ROOT
    / "custom_components"
    / "vless_gateway"
    / "frontend"
    / "vless-gateway-panel.js"
)
SOURCE = (
    ROOT
    / "custom_components"
    / "vless_gateway"
    / "frontend"
    / "src"
    / "vless-gateway-panel.js"
)


class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUNDLE.read_text(encoding="utf-8")
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_generated_bundle_is_deterministic_and_valid_javascript(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        subprocess.run(
            [node, "scripts/build-frontend-bundle.mjs", "--check"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([node, "--check", str(BUNDLE)], cwd=ROOT, check=True)

    def test_bundle_is_one_autonomous_entrypoint(self) -> None:
        executable = "\n".join(
            line for line in self.bundle.splitlines() if not line.lstrip().startswith("//")
        )
        self.assertIsNone(re.search(r"^\s*(?:import|export)\b", executable, re.MULTILINE))
        self.assertNotRegex(executable, r"\bimport\s*\(")
        self.assertIn('customElements.define("vless-gateway-panel"', self.bundle)
        self.assertIn("0.1.1", self.bundle)
        self.assertIn('const NIKAS_SHELL_V2_VERSION = "2.1"', self.bundle)

    def test_navigation_contract_is_source_aware(self) -> None:
        for marker in (
            "nikas.specialized.source_route.v1",
            "nikas.specialized.source_route_at.v1",
            "/dashboard-house-v13/home",
            "/dashboard-rooms-v11/rooms",
            "/dashboard-actions/home",
            "/dashboard-infrastructure/overview",
            '...params.getAll("return_to")',
            "history.pushState",
            "location-changed",
            "document.referrer",
        ):
            self.assertIn(marker, self.bundle)
        self.assertNotIn("history.back(", self.bundle)
        self.assertIn('class="nikas-shell__title" id="return-source"', self.bundle)
        self.assertIn(".nikas-shell__title:focus-visible", self.bundle)
        self.assertIn(".nikas-shell__title:active", self.bundle)

    def test_shell_and_views_remain_stable(self) -> None:
        self.assertEqual(self.source.count("this.shadowRoot.innerHTML ="), 1)
        for marker in (
            "this._visitedViews = new Map()",
            "slot.toggleAttribute(\"inert\", !active)",
            "commitStableMarkup(slot",
            'class="nikas-shell__viewport canvas-viewport"',
            'class="nikas-shell__canvas nikas-shell__content work-canvas"',
            'class="nikas-shell__tabs"',
        ):
            self.assertIn(marker, self.source)

    def test_zoom_contract_is_embedded(self) -> None:
        for marker in (
            "const DEFAULT_MIN = 0.75",
            "const DEFAULT_MAX = 2.0",
            "this.state.scale >= 0.97",
            "this.state.scale <= 1.03",
            "twoFingerTap",
            "resetPosition()",
            "Масштаб 100%",
            "createNikasShellScrollBoundaryGuard",
        ):
            self.assertIn(marker, self.bundle)

    def test_panel_has_expected_information_architecture(self) -> None:
        for marker in (
            "Обзор",
            "Маршруты",
            "Трафик",
            "Диагн.",
            "Локальная сеть",
            "VLESS Gateway",
            "VLESS-сервер",
            "Интернет",
        ):
            self.assertIn(marker, self.bundle)

    def test_meaningful_typography_stays_in_standard_envelope(self) -> None:
        sizes = [int(value) for value in re.findall(r"font-size:(\d+)px", self.source)]
        self.assertTrue(sizes)
        self.assertGreaterEqual(min(sizes), 12)
        self.assertLessEqual(max(sizes), 25)

    def test_host_bound_shell_v22_geometry_is_embedded(self) -> None:
        for marker in (
            "block-size:100%",
            "calc(60px + env(safe-area-inset-top,0px))",
            "calc(64px + env(safe-area-inset-bottom,0px))",
            "max-inline-size:1280px",
            "--nikas-shell-tab-count",
            "--mdc-icon-size:26px",
            'host.addEventListener("touchmove", moveTouch, { passive: false, capture: true })',
        ):
            self.assertIn(marker, self.bundle)
        for forbidden in ("100vw", "100vh", "100dvh", "position:fixed"):
            self.assertNotIn(forbidden, self.source)

    def test_data_truth_is_explicit_and_read_only(self) -> None:
        self.assertIn("Нет данных", self.bundle)
        self.assertIn("Источник недоступен", self.bundle)
        self.assertIn("unknown", self.bundle)
        self.assertIn("unavailable", self.bundle)
        self.assertIn('entry?.platform === VLESS_APP.domain', self.bundle)
        self.assertNotIn(".callService(", self.bundle)
        self.assertIsNone(
            re.search(
                r"[\"'](?:sensor|binary_sensor|switch|button|select|number|text)\.[a-z0-9_]",
                self.source,
            )
        )

    def test_entity_backed_content_preserves_more_info(self) -> None:
        self.assertIn("hass-more-info", self.bundle)
        self.assertIn("pointercancel", self.bundle)
        self.assertIn("data-entity", self.bundle)


if __name__ == "__main__":
    unittest.main()
