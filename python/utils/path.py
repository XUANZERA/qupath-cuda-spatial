from pathlib import Path
from tkinter import PROJECTING

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# print(PROJECT_ROOT)

CUDA_DIR = PROJECT_ROOT / "cuda"
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARK_DIR = PROJECT_ROOT / "benchmarks"


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_cuda_dll(name: str) -> Path:
    return CUDA_DIR / f"{name}.dll"