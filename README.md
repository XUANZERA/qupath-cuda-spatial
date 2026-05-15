# QuPath-CUDA-Spatial

### High-Performance GPU Spatial Primitives for Computational Pathology

[![Rust](https://img.shields.io/badge/rust-1.70%2B-orange.svg)](https://www.rust-lang.org)
[![CUDA](https://img.shields.io/badge/CUDA-11.0%2B-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![QuPath](https://img.shields.io/badge/QuPath-0.5.1-blue.svg)](https://qupath.github.io/)
[![License](https://img.shields.io/badge/license-research-blue.svg)](#license)

---

# 1. Project Overview

QuPath-CUDA-Spatial is a GPU-accelerated spatial analysis toolkit for computational pathology and multiplex imaging workflows.

The project provides:

- High-performance CUDA spatial primitives
- Rust-based CLI infrastructure
- QuPath Groovy integration
- Unified spatial primitive abstraction
- Reproducible benchmarking pipeline

The toolkit is designed for large-scale whole-slide image (WSI) spatial analysis, particularly:

- Tumor microenvironment (TME)
- Neuroimmune interactions
- Perineural invasion (PNI)
- Multiplex immunofluorescence (MxIF)
- Spatial cell graph construction
- Large-scale distance computation

---

# 2. Core Design Philosophy

Instead of writing task-specific QuPath scripts repeatedly, this project abstracts spatial analysis into reusable GPU spatial primitives.

Current abstraction:

| Concept | Meaning |
|---|---|
| source | objects being measured |
| target | reference spatial objects |
| mode | spatial primitive |
| output | numerical spatial result |

This design allows different spatial algorithms to share:

- identical CLI interfaces
- identical IO pipelines
- identical benchmark infrastructure
- identical QuPath bridge logic

---

# 3. Current Spatial Primitives

## 3.1 nearest-neighbor

Computes the nearest Euclidean distance:

```text
point -> nearest point
```

Typical use cases:

- immune cell -> nearest immune cell
- tumor cell -> nearest vessel
- cell density estimation
- local spatial interaction analysis

---

## 3.2 distance-to-polygon

Computes minimum distance from points to polygon boundaries using vector projection.

```text
point -> nearest polygon edge
```

Typical use cases:

- cell -> nerve boundary
- cell -> tumor boundary
- cell -> annotation edge
- spatial shell analysis

---

# 4. Technical Architecture

## 4.1 CUDA Layer

Implements GPU kernels:

- point-to-point nearest distance
- point-to-segment distance
- polygon edge traversal
- massively parallel spatial computation

---

## 4.2 Rust Engine Layer

Responsible for:

- CLI dispatch
- primitive registry
- CSV IO
- benchmark execution
- FFI integration
- pipeline orchestration

---

## 4.3 QuPath Bridge Layer

Groovy bridge scripts provide:

- object export
- annotation export
- GPU invocation
- result re-import
- measurement update

This enables seamless integration into QuPath workflows.

---

# 5. Current Project Structure

```text
.
├── Cargo.toml
├── build.rs
│
├── cuda/
│   ├── nearest_neighbor.cu
│   └── distance_to_polygon.cu
│
├── src/
│   ├── main.rs
│   ├── engine.rs
│   ├── registry.rs
│   ├── primitive.rs
│   ├── benchmark.rs
│   ├── io.rs
│   ├── nearest_neighbor.rs
│   └── distance_to_polygon.rs
│
├── scripts/
│   └── qupath_bridge.groovy
│
├── benchmark/
│   ├── benchmark_generator.py
│   ├── benchmark_runner.py
│   └── benchmark_results/
│
└── data/
```

---

# 6. Installation

## 6.1 Requirements

- Windows 10/11
- NVIDIA GPU
- CUDA Toolkit 11+
- Rust 1.70+
- QuPath 0.5.1+
- Visual Studio Build Tools

---

## 6.2 Clone Repository

```bash
git clone https://github.com/XUANZERA/qupath-cuda-spatial.git

cd qupath-cuda-spatial
```

---

## 6.3 Build

```bash
cargo build --release
```

Executable:

```text
target/release/qupath_gpu_tool.exe
```

---

# 7. CLI Usage

## 7.1 nearest-neighbor

```bash
qupath_gpu_tool.exe ^
  --mode nearest-neighbor ^
  --source source.csv ^
  --target target.csv ^
  --output result.csv
```

---

## 7.2 distance-to-polygon

```bash
qupath_gpu_tool.exe ^
  --mode distance-to-polygon ^
  --source source.csv ^
  --target target.csv ^
  --output result.csv
```

---

# 8. Benchmark Infrastructure

The project includes:

- synthetic benchmark generation
- automated subprocess execution
- CPU/GPU comparison
- throughput analysis
- scalability visualization

Metrics:

| Metric | Meaning |
|---|---|
| wallclock_time | full program runtime |
| gpu_time | GPU pipeline runtime |
| cpu_time | CPU reference runtime |
| speedup | CPU/GPU acceleration |
| throughput | processed points per second |

---

# 9. Benchmark Results

## nearest-neighbor

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.08 s | ~9.47 s | ~113× |

---

## distance-to-polygon

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.30 s | ~25.50 s | ~84× |

Benchmarked on:

- NVIDIA RTX 3070 Ti Laptop
- 12th Gen Intel(R) Core(TM) i9-12900H

---

# 10. QuPath Workflow

## Step 1

Prepare annotations and detections:

- immune_cell
- nerve_regions
- tumor_regions
- vessel_regions

---

## Step 2

Run:

```text
scripts/qupath_bridge.groovy
```

---

## Step 3

Results are automatically imported back into QuPath measurement tables.

---

# 11. Research Context

This project was originally developed for:

- computational pathology
- multiplex immunofluorescence spatial analysis
- neuroimmune microenvironment analysis
- pancreatic ductal adenocarcinoma (PDAC) research

The toolkit is currently being used in experimental workflows involving:

- spatial graph analysis
- immune infiltration analysis
- nerve-tumor interaction modeling
- large-scale WSI spatial computation

---

# 12. Future Roadmap

Planned primitives:

- radius-query
- shell-query
- point-in-polygon
- graph-edge construction
- spatial density estimation
- GPU spatial graph primitives

Planned infrastructure:

- persistent GPU memory pool
- kernel-only benchmark mode
- multi-column outputs
- batch primitive execution
- spatial primitive chaining

---

# 13. Disclaimer

This project is:

- research-oriented
- experimental
- not intended for clinical diagnosis
- not validated for medical deployment

---

# 14. Author

Zixuan Liang

School of Information Science and Technology  
Jinan University

GitHub:

```text
https://github.com/XUANZERA
```

---

# 15. License

This repository is currently released for:

- academic research
- educational usage
- computational pathology development

Please contact the author for commercial or clinical usage.