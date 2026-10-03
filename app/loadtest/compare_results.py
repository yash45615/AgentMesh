from __future__ import annotations

import json
from pathlib import Path


REPORT_DIR = Path("artifacts/load_tests")


def load_reports() -> list[dict]:
    reports = []

    for path in sorted(REPORT_DIR.glob("benchmark_*.json")):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            data["_file"] = path.name
            reports.append(data)

        except (OSError, json.JSONDecodeError) as exc:
            print(f"Skipping {path.name}: {exc}")

    return reports


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    print()
    print("=" * 110)
    print("AgentMesh Load Test Comparison")
    print("=" * 110)

    reports = load_reports()

    if not reports:
        print("No benchmark reports found.")
        print(f"Expected reports in: {REPORT_DIR.resolve()}")
        return

    print(
        f"{'Tasks':>8} "
        f"{'Workers':>9} "
        f"{'Success':>12} "
        f"{'Throughput':>16} "
        f"{'Avg Latency':>16} "
        f"{'Duration':>14}"
    )

    print("-" * 110)

    for data in reports:
        tasks = int(data.get("tasks", 0))
        workers = int(data.get("workers", 0))

        success_rate = float(data.get("success_rate", 0.0))
        throughput = float(
            data.get("throughput_tasks_per_second", 0.0)
        )

        latency_data = data.get("latency", {})
        avg_latency = float(
            latency_data.get("average_seconds", 0.0)
        )

        duration = float(
            data.get("duration_seconds", 0.0)
        )

        print(
            f"{tasks:>8} "
            f"{workers:>9} "
            f"{format_percent(success_rate):>12} "
            f"{throughput:>16.4f} "
            f"{avg_latency:>16.4f}s "
            f"{duration:>14.4f}s"
        )

    print("-" * 110)

    # ---------------------------------------------------------
    # Scaling analysis
    # ---------------------------------------------------------

    print()
    print("=" * 110)
    print("Scaling Analysis")
    print("=" * 110)

    sorted_reports = sorted(
        reports,
        key=lambda item: (
            int(item.get("workers", 0)),
            int(item.get("tasks", 0)),
        ),
    )

    baseline = None

    for data in sorted_reports:
        workers = int(data.get("workers", 0))
        throughput = float(
            data.get("throughput_tasks_per_second", 0.0)
        )

        if baseline is None:
            baseline = {
                "workers": workers,
                "throughput": throughput,
            }

            print(
                f"{workers} worker(s): "
                f"{throughput:.4f} tasks/s "
                f"(baseline)"
            )
            continue

        baseline_throughput = baseline["throughput"]

        if baseline_throughput > 0:
            improvement = (
                throughput / baseline_throughput
            )

            print(
                f"{workers} worker(s): "
                f"{throughput:.4f} tasks/s "
                f"({improvement:.2f}x baseline)"
            )

    print()
    print("=" * 110)
    print("Reports")
    print("=" * 110)

    for data in reports:
        print(f"- {data['_file']}")

    print()


if __name__ == "__main__":
    main()