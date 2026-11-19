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


class FullBuildTest(unittest.TestCase):
    def test_one_command_reproduces_the_submission_from_fixed_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("outputs", "__pycache__", ".git"))
            subprocess.run([sys.executable, "build_all.py"], cwd=root, check=True)
            outputs = root / "outputs"
            dashboard = (outputs / "dashboard.md").read_text(encoding="utf-8")
            self.assertIn("**Trung vị 430,2 giờ**. Phép tính dùng 25 issue đã đóng và bỏ qua 1 issue còn mở.", dashboard)
            self.assertTrue((outputs / "weekly.pdf").is_file())
            for name in ("issue-analysis.tex", "schedule.tex", "cost.tex"):
                self.assertTrue((outputs / name).is_file(), name)
            self.assertEqual(
                [(row["created"], row["closed"]) for row in read_csv(outputs / "weekly.csv")],
                [("8", "3"), ("0", "0"), ("18", "6"), ("0", "4"), ("0", "0"), ("0", "11"), ("0", "1")],
            )
            for scenario, days, critical in (
                ("baseline", 9, ["1.1", "2.2", "3.1", "3.2", "4.2"]),
                ("hl7-delay", 10, ["1.1", "2.3", "3.3", "4.2"]),
            ):
                with self.subTest(scenario=scenario):
                    schedule = read_csv(outputs / f"schedule-{scenario}.csv")
                    self.assertEqual(max(int(row["ef"]) for row in schedule), days)
                    self.assertEqual([row["wbs"] for row in schedule if row["critical"] == "1"], critical)

            daily = read_csv(outputs / "cost-daily.csv")
            for scenario, days, total in (
                ("baseline", 9, 9620), ("hl7-delay", 10, 11600), ("hl7-rate", 9, 10345),
            ):
                with self.subTest(scenario=scenario):
                    rows = [row for row in daily if row["scenario"] == scenario]
                    self.assertEqual(len(rows), days)
                    self.assertEqual(int(rows[-1]["cumulative_usd"]), total)
