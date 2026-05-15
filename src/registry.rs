use std::collections::HashMap;

use crate::primitive::SpatialPrimitive;

use crate::distance_to_polygon;
use crate::nearest_neighbor;

pub fn build_registry()
    -> HashMap<&'static str, SpatialPrimitive>
{
    let mut registry = HashMap::new();

    registry.insert(
        "distance-to-polygon",
        SpatialPrimitive {
            name: "distance-to-polygon",

            gpu: distance_to_polygon::distance_to_polygon_gpu,

            cpu: distance_to_polygon::distance_to_polygon_cpu,
        },
    );

    registry.insert(
        "nearest-neighbor",
        SpatialPrimitive {
            name: "nearest-neighbor",

            gpu: nearest_neighbor::nearest_neighbor_gpu,

            cpu: nearest_neighbor::nearest_neighbor_cpu,
        },
    );

    registry
}