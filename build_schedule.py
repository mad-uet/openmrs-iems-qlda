"""Rebuild the proposed IEMS schedule from the work package table."""

import csv
from dataclasses import dataclass, replace
from graphlib import TopologicalSorter
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import TextIO


ROOT = Path(__file__).resolve().parent
FIELDS = ("id", "wbs", "name", "duration_days", "predecessors", "calendar")


@dataclass(frozen=True)
class Package:
    id: int
    wbs: str
    name: str
    duration_days: int
    predecessors: tuple[int, ...]
    calendar: str


@dataclass(frozen=True)
class Timing:
    es: int
    ef: int
    ls: int
    lf: int

    @property
    def total_float(self) -> int:
        return self.ls - self.es

    @property
    def is_critical(self) -> bool:
        return self.total_float == 0


def read_packages(source: Path) -> list[Package]:
    packages: list[Package] = []
    with source.open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream)
        if next(rows, []) != list(FIELDS):
            raise ValueError(f"Expected schedule columns: {FIELDS}")
        for id_text, wbs, name, duration, predecessors, calendar in rows:
            package = Package(int(id_text), wbs, name, int(duration),
                              tuple(map(int, predecessors.split(","))) if predecessors else (),
                              calendar)
            if package.id != len(packages) + 1:
                raise ValueError(f"Task IDs must follow row order: {package.id}")
            if not re.fullmatch(r"[1-9]\d*\.[1-9]\d*", wbs) or not name.strip():
                raise ValueError(f"Task {package.id}: expected a WBS code and name")
            if package.duration_days <= 0 or calendar != "LV":
                raise ValueError(f"Task {package.id}: expected positive days and calendar LV")
            packages.append(package)
    if not packages or len({p.wbs for p in packages}) != len(packages):
        raise ValueError("Expected a nonempty schedule with unique WBS codes")
    for package in packages:
        if any(not 1 <= pred <= len(packages) for pred in package.predecessors):
            raise ValueError(f"Task {package.id}: unknown predecessor")
    return packages


def calculate(packages: list[Package]) -> dict[int, Timing]:
    graph = {p.id: p.predecessors for p in packages}
    durations = {p.id: p.duration_days for p in packages}
    order = tuple(TopologicalSorter(graph).static_order())
    successors: dict[int, list[int]] = {p.id: [] for p in packages}
    early_finish: dict[int, int] = {}
    for task in order:
        for pred in graph[task]:
            successors[pred].append(task)
        early_start = max((early_finish[pred] for pred in graph[task]), default=0)
        early_finish[task] = early_start + durations[task]

    finish = max(early_finish.values())
    timing: dict[int, Timing] = {}
    for task in reversed(order):
        late_finish = min((timing[successor].ls for successor in successors[task]), default=finish)
        duration = durations[task]
        ef = early_finish[task]
        timing[task] = Timing(ef - duration, ef, late_finish - duration, late_finish)
    return timing


def write_csv(path: Path, packages: list[Package], timing: dict[int, Timing]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow((*FIELDS, "es", "ef", "ls", "lf", "total_float", "critical"))
        for p in packages:
            t = timing[p.id]
            writer.writerow((p.id, p.wbs, p.name, p.duration_days, ",".join(map(str, p.predecessors)),
                             p.calendar, t.es, t.ef, t.ls, t.lf, t.total_float, int(t.is_critical)))


def tex_text(text: str) -> str:
    escape = {
        "\\": r"\textbackslash{}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        **{c: "\\" + c for c in "#$%&_{}"},
    }
    return "".join(escape.get(c, c) for c in text)


def tex_call(name: str, *args: str | int) -> str:
    return "\\" + name + "".join("{" + str(arg) + "}" for arg in args)


def tex_define(stream: TextIO, name: str, lines: list[str]) -> None:
    stream.write("\\newcommand{\\" + name + "}{%\n")
    stream.writelines(line + "%\n" for line in lines)
    stream.write("}\n")


def write_scenario_tex(stream: TextIO, name: str, packages: list[Package],
                       timing: dict[int, Timing]) -> None:
    result_rows = []
    bars = []
    nodes = []
    edges = []
    critical = []
    for p in packages:
        t = timing[p.id]
        style = "schedule critical" if t.is_critical else "schedule regular"
        if t.is_critical:
            critical.append(p)
        result_rows.append(tex_call("ScheduleResultRow", p.wbs, t.es, t.ef, t.ls, t.lf, t.total_float))
        bars.append(tex_call("ScheduleBar", p.wbs, p.id, t.es, t.ef, style))
        nodes.append(tex_call("ScheduleNode", p.id, p.wbs, p.wbs.replace(".", "-"),
                              p.duration_days, style))
        for predecessor in p.predecessors:
            pred = timing[predecessor]
            on_critical_path = t.is_critical and pred.is_critical and pred.ef == t.es
            edge_style = "schedule critical" if on_critical_path else "schedule regular"
            edges.append(tex_call("ScheduleEdge", predecessor, p.id, edge_style))
    critical.sort(key=lambda p: timing[p.id].es)
    tex_define(stream, name + "Results", result_rows)
    tex_define(stream, name + "Bars", bars)
    tex_define(stream, name + "Nodes", nodes)
    tex_define(stream, name + "Edges", edges)
    tex_define(stream, name + "Days", [str(max(t.ef for t in timing.values()))])
    tex_define(stream, name + "Critical", [", ".join(p.wbs for p in critical)])


def rebuild(outputs: Path) -> None:
    packages = read_packages(ROOT / "data/schedule.csv")
    hl7 = next((p for p in packages if p.wbs == "2.3"), None)
    if hl7 is None:
        raise ValueError("The HL7 delay scenario requires WBS 2.3")
    delayed = [replace(p, duration_days=p.duration_days + 3) if p == hl7 else p for p in packages]
    baseline_timing = calculate(packages)
    delayed_timing = calculate(delayed)
    outputs.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=outputs) as directory:
        staged = Path(directory)
        write_csv(staged / "schedule-baseline.csv", packages, baseline_timing)
        write_csv(staged / "schedule-hl7-delay.csv", delayed, delayed_timing)
        with (staged / "schedule.tex").open("w", encoding="utf-8", newline="\n") as stream:
            stream.write("% Generated by build_schedule.py. Edit data/schedule.csv instead.\n")
            tex_define(stream, "ScheduleInputRows", [
                tex_call("ScheduleInputRow", p.id, p.wbs, tex_text(p.name), p.duration_days,
                         ", ".join(map(str, p.predecessors)) or r"\textemdash", p.calendar)
                for p in packages
            ])
            tex_define(stream, "ScheduleTaskCount", [str(len(packages))])
            tex_define(stream, "ScheduleBaseHLSevenDays", [str(hl7.duration_days)])
            tex_define(stream, "ScheduleDelayHLSevenDays", [str(delayed[hl7.id - 1].duration_days)])
            write_scenario_tex(stream, "ScheduleBase", packages, baseline_timing)
            write_scenario_tex(stream, "ScheduleDelay", delayed, delayed_timing)
        for file in staged.iterdir():
            file.replace(outputs / file.name)


if __name__ == "__main__":
    rebuild(ROOT / "outputs")
