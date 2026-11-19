import csv
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


class WeeklyDashboardTest(unittest.TestCase):
    def test_rebuilds_the_dashboard_and_traces_issue_17(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "analysis"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("outputs", "tests", ".git"))
            subprocess.run([sys.executable, "build_weekly.py"], cwd=root, check=True)
            outputs = root / "outputs"
            self.assertEqual(
                [(r["week_start_utc"], int(r["created"]), int(r["closed"]))
                 for r in read_csv(outputs / "weekly.csv")],
                [
                    ("2020-04-06", 8, 3),
                    ("2020-04-13", 0, 0),
                    ("2020-04-20", 18, 6),
                    ("2020-04-27", 0, 4),
                    ("2020-05-04", 0, 0),
                    ("2020-05-11", 0, 11),
                    ("2020-05-18", 0, 1),
                ],
            )
            audit = {r["number"]: r for r in read_csv(outputs / "issue-weeks.csv")}
            self.assertEqual(len(audit), 26)
            self.assertEqual([n for n, r in audit.items() if not r["closed_week_utc"]], ["17"])
            self.assertEqual(audit["17"]["created_week_utc"], "2020-04-20")
            self.assertEqual(audit["26"]["created_week_utc"], "2020-04-20")
            self.assertEqual(audit["26"]["closed_week_utc"], "2020-05-11")
            self.assertTrue((outputs / "weekly.pdf").read_bytes().startswith(b"%PDF-"))

    def test_rejects_a_closure_before_the_issue_was_created(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "analysis"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("outputs", "tests", ".git"))
            (root / "data/issues.csv").write_text(
                "number,state,created_at,closed_at\n"
                "1,closed,2020-04-10T12:00:00Z,2020-04-9T12:00:00Z\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "build_weekly.py"], cwd=root, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Issue #1: closed before creation", result.stderr)
            self.assertFalse((root / "outputs/weekly.csv").exists())
