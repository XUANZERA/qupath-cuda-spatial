import subprocess
import time
import re

import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


# =========================================================
# CONFIG
# =========================================================

BIN = "target/release/qupath_gpu_tool.exe"

BENCHMARK_ROOT = Path("benchmarks")

PRIMITIVES = [
    "nearest_neighbor",
    "distance_to_polygon",
]


# =========================================================
# REGEX
# =========================================================

GPU_TIME_PATTERN = re.compile(
    r"GPU time:\s*([\d\.]+)\s*(ms|s)"
)

CPU_TIME_PATTERN = re.compile(
    r"CPU time:\s*([\d\.]+)\s*(ms|s)"
)


# =========================================================
# UTILS
# =========================================================

def parse_time(value, unit):

    value = float(value)

    if unit == "ms":
        return value / 1000.0

    return value


# =========================================================
# MAIN LOOP
# =========================================================

for primitive in PRIMITIVES:

    print("\n")
    print("=" * 80)
    print(f"BENCHMARK: {primitive}")
    print("=" * 80)

    primitive_root = (
        BENCHMARK_ROOT / primitive
    )

    results = []

    # -----------------------------------------------------
    # iterate benchmark cases
    # -----------------------------------------------------

    for case_dir in sorted(
        primitive_root.iterdir()
    ):

        if not case_dir.is_dir():
            continue

        source_csv = (
            case_dir / "source.csv"
        )

        target_csv = (
            case_dir / "target.csv"
        )

        output_csv = (
            case_dir / "result.csv"
        )

        print("\n")
        print("-" * 60)
        print(case_dir.name)
        print("-" * 60)

        try:

            wallclock_start = (
                time.perf_counter()
            )

            completed = subprocess.run(
                [
                    BIN,

                    "--mode",
                    primitive,

                    "--source",
                    str(source_csv),

                    "--target",
                    str(target_csv),

                    "--output",
                    str(output_csv),
                ],

                capture_output=True,
                text=True,

                check=True,
            )

            wallclock_time = (
                time.perf_counter()
                - wallclock_start
            )

            stdout = completed.stdout

            print(stdout)

            # ---------------------------------------------
            # parse GPU time
            # ---------------------------------------------

            gpu_match = (
                GPU_TIME_PATTERN.search(stdout)
            )

            if gpu_match is None:

                print(
                    "[WARNING] Failed to parse GPU time"
                )

                continue

            gpu_time = parse_time(
                gpu_match.group(1),
                gpu_match.group(2),
            )

            # ---------------------------------------------
            # parse CPU time
            # ---------------------------------------------

            cpu_match = (
                CPU_TIME_PATTERN.search(stdout)
            )

            if cpu_match is None:

                print(
                    "[WARNING] Failed to parse CPU time"
                )

                continue

            cpu_time = parse_time(
                cpu_match.group(1),
                cpu_match.group(2),
            )

            # ---------------------------------------------
            # parse case name
            # ---------------------------------------------

            parts = (
                case_dir.name.split("_")
            )

            source_size = int(parts[1])

            target_size = int(parts[3])

            # ---------------------------------------------
            # metrics
            # ---------------------------------------------

            speedup = (
                cpu_time / gpu_time
            )

            throughput = (
                source_size / gpu_time
            )

            results.append({

                "primitive": primitive,

                "source_size": source_size,

                "target_size": target_size,

                "wallclock_time_sec":
                    wallclock_time,

                "gpu_time_sec":
                    gpu_time,

                "cpu_time_sec":
                    cpu_time,

                "speedup":
                    speedup,

                "throughput_points_per_sec":
                    throughput,
            })

        except subprocess.CalledProcessError as e:

            print(
                "[ERROR] Benchmark failed"
            )

            print(e.stdout)
            print(e.stderr)

            continue

    # =====================================================
    # SAVE CSV
    # =====================================================

    if len(results) == 0:

        print(
            f"[WARNING] No results for {primitive}"
        )

        continue

    df = pd.DataFrame(results)

    df = df.sort_values(
        ["source_size", "target_size"]
    )

    csv_name = (
        f"{primitive}_benchmark.csv"
    )

    df.to_csv(
        csv_name,
        index=False,
    )

    print("\n")
    print(df)

    print(
        f"\nSaved CSV: {csv_name}"
    )

    # =====================================================
    # FIGURE 1
    # GPU Runtime Scaling
    # =====================================================

    plt.figure(figsize=(8, 6))

    for target_size in sorted(
        df["target_size"].unique()
    ):

        sub = df[
            df["target_size"]
            == target_size
        ]

        plt.plot(
            sub["source_size"],

            sub["gpu_time_sec"],

            marker="o",

            label=f"target={target_size}",
        )

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Source Size")
    plt.ylabel("GPU Runtime (sec)")

    plt.title(
        f"{primitive} GPU Runtime Scaling"
    )

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    runtime_fig = (
        f"{primitive}_runtime.png"
    )

    plt.savefig(
        runtime_fig,
        dpi=300,
    )

    plt.show()

    print(
        f"Saved figure: {runtime_fig}"
    )

    # =====================================================
    # FIGURE 2
    # Speedup
    # =====================================================

    plt.figure(figsize=(8, 6))

    for target_size in sorted(
        df["target_size"].unique()
    ):

        sub = df[
            df["target_size"]
            == target_size
        ]

        plt.plot(
            sub["source_size"],

            sub["speedup"],

            marker="o",

            label=f"target={target_size}",
        )

    plt.xscale("log")

    plt.xlabel("Source Size")

    plt.ylabel("CPU / GPU Speedup")

    plt.title(
        f"{primitive} GPU Speedup"
    )

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    speedup_fig = (
        f"{primitive}_speedup.png"
    )

    plt.savefig(
        speedup_fig,
        dpi=300,
    )

    plt.show()

    print(
        f"Saved figure: {speedup_fig}"
    )