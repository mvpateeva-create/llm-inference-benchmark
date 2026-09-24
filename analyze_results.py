"""Build percentile summaries from the raw benchmark CSV files.

This script does not run inference or create new measurements. It derives
P50/P95/P99 from observations already committed under ``results/``.
"""

import csv
from pathlib import Path


RESULTS_DIR = Path(__file__).parent / "results"
OUTPUT_FILE = RESULTS_DIR / "percentiles.csv"


def percentile(values: list[float], probability: float) -> float:
    """Return a linearly interpolated percentile (NumPy-compatible default)."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot calculate a percentile for an empty sample")
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def read_rows(filename: str) -> list[dict[str, str]]:
    with (RESULTS_DIR / filename).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def add_summary(output, experiment, configuration, metric, unit, values):
    output.append({
        "experiment": experiment,
        "configuration": configuration,
        "metric": metric,
        "unit": unit,
        "samples": str(len(values)),
        "p50": f"{percentile(values, 0.50):.4f}",
        "p95": f"{percentile(values, 0.95):.4f}",
        "p99": f"{percentile(values, 0.99):.4f}",
    })


def summarize_grouped(output, rows, experiment, group_column, metrics):
    groups = {}
    for row in rows:
        groups.setdefault(row[group_column], []).append(row)
    for configuration, group_rows in groups.items():
        for metric, unit in metrics:
            add_summary(output, experiment, configuration, metric, unit,
                        [float(row[metric]) for row in group_rows])


def main() -> None:
    summaries = []
    baseline = read_rows("baseline.csv")
    for metric, unit in (("ttft_seconds", "seconds"),
                         ("total_latency_seconds", "seconds"),
                         ("tokens_per_second", "tokens/second")):
        add_summary(summaries, "baseline", "max_tokens=100", metric, unit,
                    [float(row[metric]) for row in baseline])

    summarize_grouped(summaries, read_rows("output_length.csv"),
                      "output_length", "max_tokens",
                      [("ttft_seconds", "seconds"),
                       ("total_latency_seconds", "seconds"),
                       ("tokens_per_second", "tokens/second")])
    summarize_grouped(summaries, read_rows("prompt_size.csv"),
                      "prompt_size", "prompt_type",
                      [("ttft_seconds", "seconds"),
                       ("total_latency_seconds", "seconds")])

    fieldnames = ["experiment", "configuration", "metric", "unit",
                  "samples", "p50", "p95", "p99"]
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)
    print(f"Wrote {len(summaries)} summaries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
