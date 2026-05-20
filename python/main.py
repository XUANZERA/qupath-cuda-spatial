from pathlib import Path
from python.engine import Engine

import sys

from python.io import read_point_set_csv
from python.data_structure.contract import NearestNeighborInput

from python.registry import REGISTRY
import python.primitives.nearest_neighbor
import python.primitives.distance_to_polygon
from python.utils.loader import load_project_root

PROJECT_ROOT = load_project_root()

engine = Engine()
print(REGISTRY)
source_path = Path(PROJECT_ROOT, "data/src.csv").resolve()
target_path = Path(PROJECT_ROOT, "data/tar.csv").resolve()
source = read_point_set_csv(source_path)
target = read_point_set_csv(target_path)

my_input = NearestNeighborInput(
    source=source,
    target=target,
)


result = engine.run(
    primitive="nearest_neighbor",
    backend="gpu",
    data=my_input,
)

print(result)