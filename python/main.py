from pathlib import Path
from python.engine import Engine

import numpy as np

from python.io import read_point_set_csv, geojson_to_csv, read_polygon_csv
from python.data_structure.contract import (
    NearestNeighborInput, 
    NearestNeighborOutput,
    DistanceToPolygonInput,
    DistanceToPolygonOutput
) 

from python.registry import REGISTRY
import python.primitives.nearest_neighbor
import python.primitives.distance_to_polygon
from python.utils.loader import load_project_root

PROJECT_ROOT = load_project_root()

engine = Engine()

# source_path = Path(PROJECT_ROOT, "data/src.csv").resolve()
# target_path = Path(PROJECT_ROOT, "data/tar.csv").resolve()

# source = read_point_set_csv(source_path)
# target = read_point_set_csv(target_path)

# my_input = NearestNeighborInput(
#     source=source,
#     target=target,
# )


# result = engine.run(
#     primitive="nearest_neighbor",
#     backend="gpu",
#     data=my_input,
# )

# print(result)

source_path = Path(PROJECT_ROOT, "data/src.csv").resolve()
geojson_path = Path(PROJECT_ROOT, "data/rectangle.geojson").resolve()
csv_path = Path(PROJECT_ROOT, "data/rectangle.csv").resolve()

geojson_to_csv(input_path=geojson_path, output_path=csv_path)
source = read_point_set_csv(source_path)
polygon = read_polygon_csv(csv_path)

my_input = DistanceToPolygonInput(
    source=source,
    polygon=polygon
)


gpu_result = engine.run(
    primitive="distance_to_polygon",
    backend="gpu",
    data=my_input,
)

cpu_result = engine.run(
    primitive="distance_to_polygon",
    backend="cpu",
    data=my_input,
)

print(
    np.allclose(
        gpu_result.distance.distance,
        cpu_result.distance.distance,
        atol=1e-5,
    )
)