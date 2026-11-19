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


class ScheduleTest(unittest.TestCase):
    def rebuild(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "data").mkdir()
        shutil.copy(ROOT / "data/schedule.csv", root / "data")
        shutil.copy(ROOT / "build_schedule.py", root)
        subprocess.run([sys.executable, "build_schedule.py"], cwd=root, check=True)
        return root / "outputs"

    def test_baseline_reports_early_and_late_dates_for_every_package(self) -> None:
        outputs = self.rebuild()
        rows = read_csv(outputs / "schedule-baseline.csv")
        self.assertEqual(
            [(r["wbs"], r["es"], r["ef"], r["ls"], r["lf"], r["total_float"]) for r in rows],
            [
                ("1.1", "0", "1", "0", "1", "0"),
                ("2.1", "1", "3", "2", "4", "1"),
                ("2.2", "1", "4", "1", "4", "0"),
                ("2.3", "1", "5", "3", "7", "2"),
                ("3.1", "4", "6", "4", "6", "0"),
                ("3.2", "6", "8", "6", "8", "0"),
                ("3.3", "5", "6", "7", "8", "2"),
                ("4.1", "6", "7", "7", "8", "1"),
                ("4.2", "8", "9", "8", "9", "0"),
            ],
        )
        self.assertEqual([r["wbs"] for r in rows if r["critical"] == "1"],
                         ["1.1", "2.2", "3.1", "3.2", "4.2"])

    def test_hl7_delay_moves_the_critical_path_to_integration(self) -> None:
        outputs = self.rebuild()
        baseline = {r["wbs"]: r for r in read_csv(outputs / "schedule-baseline.csv")}
        delayed = {r["wbs"]: r for r in read_csv(outputs / "schedule-hl7-delay.csv")}
        self.assertEqual(baseline.keys(), delayed.keys())
        self.assertEqual(
            [(wbs, baseline[wbs]["duration_days"], r["duration_days"])
             for wbs, r in delayed.items() if baseline[wbs]["duration_days"] != r["duration_days"]],
            [("2.3", "4", "7")],
        )
        self.assertEqual([r["wbs"] for r in delayed.values() if r["critical"] == "1"],
                         ["1.1", "2.3", "3.3", "4.2"])
        self.assertEqual((delayed["3.3"]["ef"], delayed["4.2"]["es"], delayed["4.2"]["ef"]),
                         ("9", "9", "10"))
        self.assertEqual(delayed["3.2"]["total_float"], "1")
