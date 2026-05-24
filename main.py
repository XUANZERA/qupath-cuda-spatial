from pathlib import Path
from qupath_cuda_spatial.core.engine import Engine

import argparse
import numpy as np

from qupath_cuda_spatial.io.io import read_point_set_csv, geojson_to_csv, read_polygon_csv
from qupath_cuda_spatial.types.contract import (
    NearestNeighborInput, 
    NearestNeighborOutput,
    DistanceToPolygonInput,
    DistanceToPolygonOutput
) 

from qupath_cuda_spatial.core.registry import REGISTRY
import qupath_cuda_spatial.primitives.nearest_neighbor
import qupath_cuda_spatial.primitives.distance_to_polygon
from qupath_cuda_spatial.utils.loader import load_library
from qupath_cuda_spatial.utils.path import PROJECT_ROOT

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

parser = argparse.ArgumentParser()

parser.add_argument("--primitive")
parser.add_argument("--source")
parser.add_argument("--target")
parser.add_argument("--out")
parser.add_argument("--backend", default="gpu", choices=["cpu", 'gpu'])

args = parser.parse_args()

primitive = args.primitive
source_path = args.source
target_path = args.target
out_path = args.out
backend = args.backend



engine.run(
    primitive=primitive,
    backend=backend,
    data=my_input
)


