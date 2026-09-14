"""Execute the required CI gate without third-party test dependencies."""

import json
import os
from pathlib import Path
import re
import subprocess
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/repository-checks.yml"
REQUIRED = ("repository-checks", "hacs-validation", "hassfest")


class RequiredCIGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = WORKFLOW.read_text(encoding="utf-8")
        self.jobs = dict(
            re.findall(
                r"^  ([\w-]+):\n(.*?)(?=^  [\w-]+:|\Z)",
                self.source.split("\njobs:\n", 1)[1],
                re.M | re.S,
            )
        )

    def gate(self) -> str:
        self.assertIn(
            "repository-checks",
            self.jobs,
            "validate must aggregate the repository's substantive checks",
        )
        self.assertIn("validate", self.jobs)
        return self.jobs["validate"]

    def success(self) -> dict[str, dict[str, object]]:
        return {name: {"result": "success", "outputs": {}} for name in REQUIRED}

    def run_gate(self, results: object) -> subprocess.CompletedProcess[str]:
        script = re.search(
            r"^        run: \|\n((?:          .*\n|\n)+)",
            self.gate(),
            re.M,
        )
        self.assertIsNotNone(script, "validate must execute a fail-closed gate")
        env = os.environ.copy()
        env["VLESS_JOB_RESULTS"] = json.dumps(results)
        return subprocess.run(
            [
                "bash",
                "--noprofile",
                "--norc",
                "-e",
                "-o",
                "pipefail",
                "-c",
                textwrap.dedent(script.group(1)),
            ],
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )

    def test_validate_covers_all_required_jobs_without_bypass(self) -> None:
        gate = self.gate()
        self.assertEqual(set(self.jobs), {"validate", *REQUIRED})
        needs = re.search(r"^    needs: \[([^\]]+)\]$", gate, re.M)
        self.assertIsNotNone(needs)
        self.assertEqual(
            [name.strip() for name in needs.group(1).split(",")],
            list(REQUIRED),
        )
        self.assertRegex(gate, r"(?m)^    if: \$\{\{ always\(\) \}\}$")
        self.assertRegex(
            gate,
            r"(?m)^          VLESS_JOB_RESULTS: \$\{\{ toJSON\(needs\) \}\}$",
        )
        self.assertRegex(gate, r"(?m)^        shell: bash$")
        self.assertNotRegex(gate, r"(?m)^        if:")
        self.assertEqual(len(re.findall(r"^      - ", gate, re.M)), 1)
        self.assertNotIn("continue-on-error:", self.source)
        self.assertIn(
            "python -m unittest discover -s tests -v",
            self.jobs["repository-checks"],
        )
        self.assertIn("uses: hacs/action@", self.jobs["hacs-validation"])
        self.assertIn(
            "uses: home-assistant/actions/hassfest@",
            self.jobs["hassfest"],
        )

    def test_complete_success_passes(self) -> None:
        result = self.run_gate(self.success())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsuccessful_dependencies_fail_closed(self) -> None:
        for name in REQUIRED:
            for status in ("failure", "cancelled", "skipped"):
                with self.subTest(job=name, status=status):
                    results = self.success()
                    results[name]["result"] = status
                    self.assertNotEqual(self.run_gate(results).returncode, 0)

    def test_missing_unexpected_and_malformed_results_fail_closed(self) -> None:
        cases: list[object] = [{}, [], None]
        for name in REQUIRED:
            missing = self.success()
            del missing[name]
            cases.append(missing)
            missing_result = self.success()
            missing_result[name] = {"outputs": {}}
            cases.append(missing_result)
        unexpected = self.success()
        unexpected["unexpected"] = {"result": "success"}
        cases.append(unexpected)
        for results in cases:
            with self.subTest(results=results):
                self.assertNotEqual(self.run_gate(results).returncode, 0)


if __name__ == "__main__":
    unittest.main()
