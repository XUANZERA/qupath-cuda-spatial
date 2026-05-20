from dataclasses import dataclass
from python.data_structure.schema import (
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
    output: DistanceResult


@dataclass
class NearestNeighborInput:
    source: PointSet
    target: PointSet


@dataclass
class NearestNeighborOutput:
    output: DistanceResult