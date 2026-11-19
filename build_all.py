"""Rebuild the Dashboard, CPM schedules, and costs from the fixed inputs."""

from pathlib import Path
from tempfile import TemporaryDirectory

import build_cost
import build_schedule
import build_weekly


def main() -> None:
    root = Path(__file__).resolve().parent
    outputs = root / "outputs"
    # Keep the previous results until all three builds succeed.
    with TemporaryDirectory(dir=root) as directory:
        staged = Path(directory)
        build_weekly.rebuild(staged)
        build_schedule.rebuild(staged)
        build_cost.rebuild(staged)
        outputs.mkdir(exist_ok=True)
        for artifact in staged.iterdir():
            artifact.replace(outputs / artifact.name)
    print("Rebuilt Dashboard, schedules, and costs in outputs/")


if __name__ == "__main__":
    main()
