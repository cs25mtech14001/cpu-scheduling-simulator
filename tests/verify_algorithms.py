#!/usr/bin/env python3
"""Human-readable scheduler demo + regression checks.

Runs the same sample workload through every C++ scheduler, prints the actual
Gantt chart and per-process metrics, and checks exact reference values for
FCFS, SJF, and Round Robin. All algorithms are also checked for structural
and metric invariants.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DATA = ROOT / "data"
INPUT = DATA / "input.json"
OUTPUT = DATA / "output.json"
SAMPLE = ROOT / "sample_data" / "manual_test.json"

ALGORITHMS = [
    "fcfs", "sjf", "srtf", "rr", "priority",
    "hrrn", "mqs", "mlfq", "ljf", "lrtf"
]

# Manually verified reference outputs for the canonical workload.
# Exact values are checked for three representative algorithms.
EXPECTED = {
    "fcfs": {
        "avg_waiting": 10 / 3,
        "avg_turnaround": 20 / 3,
        "results": {
            "P1": (5, 5, 0),
            "P2": (8, 7, 4),
            "P3": (10, 8, 6),
        },
        "gantt": "P1 × 5 | P2 × 3 | P3 × 2",
    },
    "sjf": {
        "avg_waiting": 3.0,
        "avg_turnaround": 19 / 3,
        "results": {
            "P1": (5, 5, 0),
            "P2": (10, 9, 6),
            "P3": (7, 5, 3),
        },
        "gantt": "P1 × 5 | P3 × 2 | P2 × 3",
    },
    "rr": {
        "avg_waiting": 4.0,
        "avg_turnaround": 22 / 3,
        "results": {
            "P1": (10, 10, 5),
            "P2": (9, 8, 5),
            "P3": (6, 4, 2),
        },
        "gantt": "P1 × 2 | P2 × 2 | P3 × 2 | P1 × 2 | P2 × 1 | P1 × 1",
    },
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def fmt(x: float) -> str:
    return f"{x:.2f}"


def compress_gantt(gantt: list[str]) -> str:
    if not gantt:
        return "<empty>"
    parts: list[str] = []
    start = 0
    for i in range(1, len(gantt) + 1):
        if i == len(gantt) or gantt[i] != gantt[start]:
            parts.append(f"{gantt[start]} × {i - start}")
            start = i
    return " | ".join(parts)


def check_invariants(algorithm: str, out: dict, processes: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    results = out.get("results")
    gantt = out.get("gantt_chart")
    if not isinstance(results, list) or len(results) != len(processes):
        errors.append("wrong number of process results")
        return errors
    if not isinstance(gantt, list) or not gantt:
        errors.append("missing Gantt chart")
        return errors

    by_pid = {p.get("pid"): p for p in results}
    if set(by_pid) != set(processes):
        errors.append("result PIDs do not match input PIDs")

    for pid, src in processes.items():
        p = by_pid.get(pid)
        if not p:
            continue
        c = p.get("completion")
        t = p.get("turnaround")
        w = p.get("waiting")
        expected_t = c - src["arrival"] if isinstance(c, int) else None
        expected_w = expected_t - src["burst"] if isinstance(expected_t, int) else None
        if expected_t != t:
            errors.append(f"{pid}: turnaround formula mismatch")
        if expected_w != w:
            errors.append(f"{pid}: waiting formula mismatch")
        if not isinstance(c, int) or c < src["arrival"]:
            errors.append(f"{pid}: invalid completion time")
        if not isinstance(w, int) or w < 0:
            errors.append(f"{pid}: invalid waiting time")

    avg_w = sum(p["waiting"] for p in results) / len(results)
    avg_t = sum(p["turnaround"] for p in results) / len(results)
    if not math.isclose(float(out.get("average_waiting", -1)), avg_w, abs_tol=1e-9):
        errors.append("average waiting time mismatch")
    if not math.isclose(float(out.get("average_turnaround", -1)), avg_t, abs_tol=1e-9):
        errors.append("average turnaround time mismatch")
    return errors


def exact_check(algorithm: str, out: dict) -> list[str]:
    expected = EXPECTED.get(algorithm)
    if not expected:
        return []
    errors: list[str] = []
    if not math.isclose(float(out["average_waiting"]), expected["avg_waiting"], abs_tol=1e-9):
        errors.append(
            f"average waiting: expected {fmt(expected['avg_waiting'])}, got {fmt(float(out['average_waiting']))}"
        )
    if not math.isclose(float(out["average_turnaround"]), expected["avg_turnaround"], abs_tol=1e-9):
        errors.append(
            f"average turnaround: expected {fmt(expected['avg_turnaround'])}, got {fmt(float(out['average_turnaround']))}"
        )

    for p in out["results"]:
        exp = expected["results"].get(p["pid"])
        if exp and (p["completion"], p["turnaround"], p["waiting"]) != exp:
            errors.append(
                f"{p['pid']}: expected C/T/W={exp}, got "
                f"C/T/W={(p['completion'], p['turnaround'], p['waiting'])}"
            )

    if compress_gantt(out["gantt_chart"]) != expected["gantt"]:
        errors.append(
            f"Gantt chart: expected '{expected['gantt']}', got '{compress_gantt(out['gantt_chart'])}'"
        )
    return errors


def print_input(sample: dict) -> None:
    print("\n" + "=" * 82)
    print("CANONICAL MANUAL TEST CASE")
    print("=" * 82)
    print(f"Time Quantum (RR): {sample.get('quantum', 2)}")
    print("\nProcess   Arrival   Burst   Priority   Queue")
    print("-------   -------   -----   --------   -----")
    for p in sample["processes"]:
        print(
            f"{p['pid']:<9}{p['arrival']:<10}{p['burst']:<8}"
            f"{p.get('priority', '-'): <11}{p.get('queue', '-')}"
        )
    print("\nFormulas used for manual verification:")
    print("  Turnaround Time = Completion Time - Arrival Time")
    print("  Waiting Time    = Turnaround Time - Burst Time")
    print("  Average         = sum(process metric) / number of processes")


def print_algorithm(algorithm: str, out: dict, exact: list[str]) -> None:
    title = algorithm.upper()
    print("\n" + "-" * 82)
    print(f"{title}  |  ACTUAL OUTPUT")
    print("-" * 82)
    print("Gantt: ", compress_gantt(out["gantt_chart"]))
    print()
    print("Process   Arrival   Burst   Completion   Turnaround   Waiting")
    print("-------   -------   -----   ----------   ----------   -------")
    for p in out["results"]:
        print(
            f"{p['pid']:<9}{p['arrival']:<10}{p['burst']:<8}"
            f"{p['completion']:<13}{p['turnaround']:<13}{p['waiting']}"
        )
    print(f"\nAverage Waiting Time   : {fmt(float(out['average_waiting']))}")
    print(f"Average Turnaround Time: {fmt(float(out['average_turnaround']))}")

    if algorithm in EXPECTED:
        exp = EXPECTED[algorithm]
        print("\nREFERENCE CHECK")
        print(f"  Expected Average Waiting   : {fmt(exp['avg_waiting'])}")
        print(f"  Actual   Average Waiting   : {fmt(float(out['average_waiting']))}")
        print(f"  Expected Average Turnaround: {fmt(exp['avg_turnaround'])}")
        print(f"  Actual   Average Turnaround: {fmt(float(out['average_turnaround']))}")
        if exact:
            print("  RESULT: ✗ FAILED")
            for e in exact:
                print("    -", e)
        else:
            print("  RESULT: ✓ EXACT REFERENCE MATCH")
    else:
        print("\nRESULT: ✓ STRUCTURAL + METRIC CHECK PASSED")


def main() -> int:
    SAMPLE.parent.mkdir(exist_ok=True)
    sample = {
        "time_quantum": 2,
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2, "queue": 1},
            {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1, "queue": 1},
            {"pid": "P3", "arrival": 2, "burst": 2, "priority": 3, "queue": 2},
        ],
    }
    SAMPLE.write_text(json.dumps(sample, indent=2) + "\n")

    print("Building CPU scheduling engine...")
    build = run(["make"], ROOT)
    if build.returncode != 0:
        print(build.stdout)
        print(build.stderr)
        print("\nBUILD: ✗ FAILED")
        return 1
    print("BUILD: ✓ SUCCESS")

    print_input(sample)
    all_failed = False

    # Keep the user's sample input available after the tests.
    INPUT.write_text(json.dumps(sample, indent=2) + "\n")

    for algorithm in ALGORITHMS:
        INPUT.write_text(json.dumps(sample, indent=2) + "\n")
        result = run([f"./{algorithm}"], BACKEND)
        if result.returncode != 0:
            print("\n" + "-" * 82)
            print(f"{algorithm.upper()}  |  EXECUTION FAILED")
            print("-" * 82)
            print(result.stdout.strip())
            print(result.stderr.strip())
            all_failed = True
            continue
        try:
            out = json.loads(OUTPUT.read_text())
        except Exception as exc:
            print(f"\n{algorithm.upper()}: could not parse data/output.json: {exc}")
            all_failed = True
            continue

        proc_map = {p["pid"]: p for p in sample["processes"]}
        structural = check_invariants(algorithm, out, proc_map)
        exact = exact_check(algorithm, out)
        print_algorithm(algorithm, out, exact)
        if structural:
            print("  INVARIANT ERRORS:")
            for e in structural:
                print("    -", e)
        if structural or exact:
            all_failed = True

    print("\n" + "=" * 82)
    if all_failed:
        print("OVERALL RESULT: ✗ SOME CHECKS FAILED")
        print("Review the section(s) marked FAILED above.")
        return 1
    print("OVERALL RESULT: ✓ ALL SCHEDULERS EXECUTED SUCCESSFULLY")
    print("The three representative algorithms were also matched against manual reference values.")
    print("=" * 82)
    print("\nTip: data/output.json contains the complete JSON result from the last algorithm run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
