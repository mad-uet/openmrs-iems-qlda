"""Rebuild the issue dashboard from the fixed GitHub sample."""

import csv
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path
import subprocess
import tempfile

from issue_analysis import write_analysis


ROOT = Path(__file__).resolve().parent
ISSUE_FIELDS = ("number", "state", "created_at", "closed_at")
WEEK = timedelta(days=7)


def parse_utc(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def week_start(timestamp: datetime) -> date:
    day = timestamp.date()
    return day - timedelta(days=day.weekday())


def build(out: Path) -> None:
    created: Counter[date] = Counter()
    closed: Counter[date] = Counter()
    issue_hours: dict[int, float | None] = {}

    with (ROOT / "data/issues.csv").open(encoding="utf-8", newline="") as source, (
        out / "issue-weeks.csv"
    ).open("w", encoding="utf-8", newline="") as audit:
        issues = csv.DictReader(source)
        if issues.fieldnames != list(ISSUE_FIELDS):
            raise ValueError(f"data/issues.csv must have exactly these columns: {ISSUE_FIELDS}")
        row = csv.writer(audit, lineterminator="\n")
        row.writerow(("number", "created_week_utc", "closed_week_utc"))
        for issue in issues:
            if any(value is None for value in issue.values()) or None in issue:
                raise ValueError(f"data/issues.csv:{issues.line_num}: wrong number of fields")
            number = int(issue["number"])
            state = issue["state"]
            start = parse_utc(issue["created_at"])
            end = parse_utc(issue["closed_at"]) if issue["closed_at"] else None
            if number <= 0 or number in issue_hours:
                raise ValueError(f"Invalid or repeated issue number: {number}")
            if state != ("closed" if end is not None else "open"):
                raise ValueError(f"Issue #{number}: state and dates do not agree")
            if end is not None and end < start:
                raise ValueError(f"Issue #{number}: closed before creation")
            issue_hours[number] = (end - start).total_seconds() / 3600 if end is not None else None
            creation_week = week_start(start)
            created[creation_week] += 1
            closure_week = week_start(end) if end is not None else None
            if closure_week is not None:
                closed[closure_week] += 1
            row.writerow((number, creation_week, closure_week))

    if not created:
        raise ValueError("data/issues.csv does not contain any issues")
    events = created.keys() | closed.keys()
    week = min(events)
    last_week = max(events)
    with (out / "weekly.csv").open("w", encoding="utf-8", newline="") as stream:
        row = csv.writer(stream, lineterminator="\n")
        row.writerow(("week_start_utc", "created", "closed"))
        while week <= last_week:
            row.writerow((week, created[week], closed[week]))
            week += WEEK

    write_analysis(out, ROOT / "data/issue-classifications.csv", issue_hours)
    result = subprocess.run(
        ["xelatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
         "-jobname=weekly", "-output-comment=Weekly issue dashboard",
         str(ROOT / "weekly-chart.tex")],
        cwd=out, env={**os.environ, "SOURCE_DATE_EPOCH": "0"},
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout)


def rebuild(outputs: Path) -> None:
    outputs.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=outputs) as directory:
        staged = Path(directory)
        build(staged)
        for name in ("issue-weeks.csv", "weekly.csv", "weekly.pdf", "issue-analysis.tex", "dashboard.md"):
            (staged / name).replace(outputs / name)
    print("Wrote outputs/dashboard.md and its supporting files")


if __name__ == "__main__":
    rebuild(ROOT / "outputs")
