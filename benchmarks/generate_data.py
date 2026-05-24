import numpy as np
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("benchmarks")
OUTPUT_DIR.mkdir(exist_ok=True)

DISTANCE_TO_POLYGON = Path("distance_to_polygon")
NEAREST_NEIGHBOR = Path("nearest_neighbor")

# ----------------------------------------
# benchmark scales
# ----------------------------------------

SOURCE_SIZES = [
    1_000,
    10_000,
    100_000,
    1_000_000,
]

TARGET_SIZES = [
    100,
    1_000,
    10_000,
]

# ----------------------------------------
# random seed
# ----------------------------------------

np.random.seed(42)

# ----------------------------------------
# generate nearest neighbor benchmark
# ----------------------------------------

for n_source in SOURCE_SIZES:

    for n_target in TARGET_SIZES:

        case_name = (
            f"src_{n_source}_tar_{n_target}"
        )

        case_dir = OUTPUT_DIR / NEAREST_NEIGHBOR / case_name
        case_dir.mkdir(exist_ok=True)

        # --------------------------------
        # source points
        # --------------------------------

        source = pd.DataFrame({
            "x": np.random.uniform(
                0,
                10000,
                n_source,
            ),
            "y": np.random.uniform(
                0,
                10000,
                n_source,
            ),
        })

        # --------------------------------
        # target points
        # --------------------------------

        target = pd.DataFrame({
            "x": np.random.uniform(
                0,
                10000,
                n_target,
            ),
            "y": np.random.uniform(
                0,
                10000,
                n_target,
            ),
        })

        source.to_csv(
            case_dir / "source.csv",
            index=False,
        )

        target.to_csv(
            case_dir / "target.csv",
            index=False,
        )

        print(
            f"Generated: {case_name}"
        )


# ----------------------------------------
# generate distance to polygon benchmark
# ----------------------------------------

for n_source in SOURCE_SIZES:

    for n_target in TARGET_SIZES:

        case_name = (
            f"src_{n_source}_tar_{n_target}"
        )

        case_dir = OUTPUT_DIR / DISTANCE_TO_POLYGON / case_name
        case_dir.mkdir(exist_ok=True)

        # --------------------------------
        # source points
        # --------------------------------

        source = pd.DataFrame({
            "x": np.random.uniform(
                0,
                10000,
                n_source,
            ),
            "y": np.random.uniform(
                0,
                10000,
                n_source,
            ),
        })

        # --------------------------------
        # target points
        # --------------------------------

        target = pd.DataFrame({
            "x": np.random.uniform(
                0,
                10000,
                n_target,
            ),
            "y": np.random.uniform(
                0,
                10000,
                n_target,
            ),
        })

        source.to_csv(
            case_dir / "source.csv",
            index=False,
        )

        target.to_csv(
            case_dir / "target.csv",
            index=False,
        )

        print(
            f"Generated: {case_name}"
        )