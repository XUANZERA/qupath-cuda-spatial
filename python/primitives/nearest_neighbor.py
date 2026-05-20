from math import sqrt
from pathlib import Path

import ctypes
import numpy as np
import numpy.typing as npt

from python.data_structure.schema import DistanceResult
from python.registry import register_primitive
from python.data_structure.contract import (
    NearestNeighborInput, 
    NearestNeighborOutput
) 


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
print(ROOT_DIR,"123123132")
path_dll = ROOT_DIR / "cuda" / "nearest_neighbor.dll"
cuda_lib = ctypes.CDLL(path_dll)


cuda_lib.launch_nearest_neighbor_kernel.argtypes = [
    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,

    ctypes.POINTER(ctypes.c_float),
    ctypes.POINTER(ctypes.c_float),
    ctypes.c_int,
    
    ctypes.POINTER(ctypes.c_float),
]

cuda_lib.launch_nearest_neighbor_kernel.restype = None


@register_primitive(
    primitive_name="nearest_neighbor",
    backend_name="gpu"
)
def nearest_neighbor_gpu(
    data: NearestNeighborInput
) -> NearestNeighborOutput:
    
    source_x = data.source.x
    source_y = data.source.y
    target_x = data.target.x
    target_y = data.target.y

    output = np.zeros_like(source_x, dtype=np.float32)

    source_x = np.ascontiguousarray(source_x, dtype=np.float32)
    source_y = np.ascontiguousarray(source_y, dtype=np.float32)

    target_x = np.ascontiguousarray(target_x, dtype=np.float32)
    target_y = np.ascontiguousarray(target_y, dtype=np.float32)


    cuda_lib.launch_nearest_neighbor_kernel(

        source_x.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        source_y.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        len(source_x),

        target_x.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        target_y.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),

        len(target_x),

        output.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        ),
    )

    return NearestNeighborOutput(
        DistanceResult(
            ids=data.source.ids,
            output=output
        )
    )


@register_primitive(
    primitive_name="nearest_neighbor",
    backend_name="cpu"
)
def nearest_neighbor_cpu(
    data: NearestNeighborInput
) -> NearestNeighborOutput:
    
    source_x = data.source.x
    source_y = data.source.y
    target_x = data.target.x
    target_y = data.target.y
    output = np.zeros_like(source_x, dtype=np.float32)

    for i in range(len(source_x)):
        sx = source_x[i]
        sy = source_y[i]

        min_distance = float("inf")

        for j in range(len(target_x)):
            dx = target_x[j] - sx
            dy = target_y[j] - sy

            distance = sqrt((dx * dx + dy * dy))

            if distance < min_distance:
                min_distance = distance
        
        output[i] = min_distance

    return NearestNeighborOutput(
        DistanceResult(
            ids=data.source.ids,
            output=output
        )
    )
        