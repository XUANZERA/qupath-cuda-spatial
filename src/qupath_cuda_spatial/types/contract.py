from dataclasses import dataclass
from src.qupath_cuda_spatial.types.schema import (
    PolygonSet, 
    PointSet,
    DistanceResult
    )

@dataclass
class DistanceToPolygonInput:
    source: PointSet
    polygon: PolygonSet


@dataclass
class DistanceToPolygonOutput:
    distance: DistanceResult


@dataclass
class NearestNeighborInput:
    source: PointSet
    target: PointSet


@dataclass
class NearestNeighborOutput:
    distance: DistanceResult