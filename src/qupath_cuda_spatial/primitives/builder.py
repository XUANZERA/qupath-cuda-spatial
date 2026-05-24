from pathlib import Path

from qupath_cuda_spatial.io.io import (
    read_point_set_csv,
    geojson_to_csv,
    read_polygon_csv,
)

from qupath_cuda_spatial.types.contract import (
    DistanceToPolygonInput,
    NearestNeighborInput
)
from qupath_cuda_spatial.core.registry import (
    register_input_builder
)



@register_input_builder(
    primitive_name="distance_to_polygon"
)
def build_distance_to_polygon(
    source_path: Path,
    target_path: Path,
    temp_path: Path,
) -> DistanceToPolygonInput:

    geojson_to_csv(
        input_path=target_path,
        output_path=temp_path,
    )

    source = read_point_set_csv(source_path)

    polygon = read_polygon_csv(temp_path)

    return DistanceToPolygonInput(
        source=source,
        polygon=polygon,
    )

@register_input_builder(
    primitive_name="nearest_neighbor"
)
def build_nearest_neighbor(
    source_path: Path,
    target_path: Path
) -> NearestNeighborInput:
    source = read_point_set_csv(source_path)
    target = read_point_set_csv(target_path)

    return NearestNeighborInput(
        source=source,
        target=target
    )