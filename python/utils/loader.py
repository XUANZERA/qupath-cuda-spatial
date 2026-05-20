import ctypes

from python.utils.path import get_cuda_dll, get_project_root


def load_cuda_library(name: str):

    dll_path = get_cuda_dll(name)

    print(f"[CUDA] Loading: {dll_path}")

    if not dll_path.exists():
        raise FileNotFoundError(
            f"CUDA DLL not found: {dll_path}"
        )

    return ctypes.CDLL(str(dll_path))


def load_project_root():
    return get_project_root()

# load_cuda_library("nearest_neighbor")