from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

@dataclass
class PointSet:
    ids: npt.NDArray[np.int64]
    x: npt.NDArray[np.float32]
    y: npt.NDArray[np.float32]

    def validate(self) -> None:
        assert self.ids.ndim == 1
        assert self.x.ndim == 1
        assert self.y.ndim == 1
        assert len(self.ids) == len(self.x) == len(self.y)


@dataclass
##############################################################################################
# feature_idx,polygon_idx,ring_idx,vertex_idx, x, y
# 0          ,          0,       0,         0,10,10
# 0          ,          0,       0,         1,20,10
# 0          ,          0,       0,         2,20,20
# 0          ,          0,       0,         3,10,20
# feature: 一个语义annotation，例如Nerve1, Vessle2
# polygon: 同一个feature_id的annotation的多个polygon (多个即为MultiPolygon)
# ring: 同一个polygon的多个环
# vertex: 同一个环的不同vertex
# x, y: 同一个环的(x, y)
##############################################################################################
class PolygonSet:
    feature_idx: npt.NDArray[np.int64]
    polygon_idx: npt.NDArray[np.int64]
    ring_idx: npt.NDArray[np.int64]
    vertex_idx: npt.NDArray[np.int64]
    x: npt.NDArray[np.float32]
    y: npt.NDArray[np.float32]

    def validate(self) -> None:
        assert len(self.feature_idx) == \
        len(self.polygon_idx) == \
        len(self.ring_idx) == \
        len(self.vertex_idx) == \
        len(self.x) == \
        len(self.y)


@dataclass
class DistanceResult:
    ids: npt.NDArray[np.int64]
    distance: npt.NDArray[np.float32]

    def validate(self) -> None:
        assert len(self.ids) == len(self.distance)