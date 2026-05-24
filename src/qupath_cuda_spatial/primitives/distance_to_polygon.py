from pathlib import Path
from dataclasses import dataclass

# 范式发生了根本性的变化 0~1很难 高级程序员有自己的代码仓 在大模型下建立自己的代码仓 一直更新
# 通过大模型生成了新的好的代码以后把他人工挑选出来 不能直接扔进去

import math
import ctypes
import numpy as np
import numpy.typing as npt

from qupath_cuda_spatial.types.schema import DistanceResult
from qupath_cuda_spatial.utils.loader import load_library
from qupath_cuda_spatial.types.contract import (
    DistanceToPolygonInput,
    DistanceToPolygonOutput
    )
from qupath_cuda_spatial.core.registry import (
    register_implementation
)

cuda_lib = load_library("distance_to_polygon")

cuda_lib.launch_distance_to_polygon_kernel.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,

    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,

    ctypes.POINTER(ctypes.c_float),
]

cuda_lib.launch_distance_to_polygon_kernel.restype = None


@register_implementation(
    primitive_name="distance_to_polygon",
    backend_name="gpu",
)
def distance_to_polygon_gpu(
    data: DistanceToPolygonInput
) -> DistanceToPolygonOutput:
    
    source_x = data.source.x
    source_y = data.source.y
    polygon_x = data.polygon.x
    polygon_y = data.polygon.y
    output = np.zeros_like(source_x, dtype=np.float32)
    
    source_x = np.ascontiguousarray(source_x, dtype=np.float32)
    source_y = np.ascontiguousarray(source_y, dtype=np.float32)

    polygon_x = np.ascontiguousarray(polygon_x, dtype=np.float32)
    polygon_y = np.ascontiguousarray(polygon_y, dtype=np.float32)

    cuda_lib.launch_distance_to_polygon_kernel(

        source_x.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        source_y.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        len(source_x),

        polygon_x.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        polygon_y.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        len(polygon_x),

        output.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),
    )

    return DistanceToPolygonOutput(
        DistanceResult(
            ids=data.source.ids,
            distance=output
        )
    )


def point_to_segment_distance(
    px: float,
    py: float,

    x1: float,
    y1: float,

    x2: float,
    y2: float
) -> float:
    
    dx = x2 - x1
    dy = y2 - y1
    l2 = dx * dx + dy * dy

    if l2 == 0.0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
    
    t = ((px - x1) * dx + (py - y1) * dy) / l2
    t = max(0.0, min(1.0, t)) # clip

    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)


def point_to_polygon_distance(
    px: float,
    py: float,

    polygon_x: npt.NDArray[np.float32],
    polygon_y: npt.NDArray[np.float32]
) -> float:
    
    min_distance = float("inf")

    for i in range(len(polygon_x) - 1):
        distance = point_to_segment_distance(
            px,
            py,

            polygon_x[i],
            polygon_y[i],
            
            polygon_x[i + 1],
            polygon_y[i + 1]
        )

        if distance < min_distance:
            min_distance = distance

    return min_distance


@register_implementation(
    primitive_name="distance_to_polygon",
    backend_name="cpu",
)
def distance_to_polygon_cpu(
    data: DistanceToPolygonInput
) -> DistanceToPolygonOutput:
    
    source_x = data.source.x
    source_y = data.source.y
    polygon_x = data.polygon.x
    polygon_y = data.polygon.y
    output = np.zeros_like(source_x, dtype=np.float32)

    for i in range(len(source_x)):
        distance = point_to_polygon_distance(
            source_x[i],
            source_y[i],

            polygon_x,
            polygon_y
        )

        output[i] = distance

    return DistanceToPolygonOutput(
        DistanceResult(
            ids=data.source.ids,
            distance=output
        )
    )