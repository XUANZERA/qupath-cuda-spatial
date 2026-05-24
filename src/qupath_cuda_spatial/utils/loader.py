import ctypes

from qupath_cuda_spatial.utils.path import DLL_DIR


def load_library(name: str):

    dll_path = DLL_DIR / f"{name}.dll"

    print(f"[CUDA] Loading: {dll_path}")

    if not dll_path.exists():
        raise FileNotFoundError(
            f"CUDA DLL not found: {dll_path}"
        )

    return ctypes.CDLL(str(dll_path))