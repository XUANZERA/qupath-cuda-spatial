from pathlib import Path
from tkinter import PROJECTING

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# print(PROJECT_ROOT)

DLL_DIR = PROJECT_ROOT / "build"
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARK_DIR = PROJECT_ROOT / "benchmasrks"


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_dll(name: str) -> Path:
    return DLL_DIR / f"{name}.dll"