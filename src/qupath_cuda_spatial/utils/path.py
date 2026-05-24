from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# print(PROJECT_ROOT)

DLL_DIR = PROJECT_ROOT / "build"
DATA_DIR = PROJECT_ROOT / "data"
BENCHMARK_DIR = PROJECT_ROOT / "benchmarks"
CUDA_DIR = PROJECT_ROOT / "cuda"
SCRIPT_DIR = PROJECT_ROOT / "script"