

<div align="center">

# QuPath-CUDA-Spatial

## High-Performance GPU Spatial Primitives for Computational Pathology

<br>

<a href="#english-version">🇺🇸 English</a>
&nbsp;&nbsp;&nbsp;&nbsp;
<a href="#中文版本">🇨🇳 中文</a>

<br><br>

[![Rust](https://img.shields.io/badge/rust-1.70%2B-orange.svg)](https://www.rust-lang.org)
[![CUDA](https://img.shields.io/badge/CUDA-11.0%2B-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![QuPath](https://img.shields.io/badge/QuPath-0.5.1-blue.svg)](https://qupath.github.io/)
[![License](https://img.shields.io/badge/license-research-blue.svg)](#license)

🎥 Video tutorial:
https://youtu.be/iA-HR2wv8Vo
</div>

---

<a id="english-version"></a>

# 🇺🇸 English

## 1. Overview

QuPath-CUDA-Spatial is an experimental GPU-accelerated spatial analysis toolkit designed for computational pathology and multiplex imaging workflows.

The project focuses on accelerating large-scale whole-slide image (WSI) spatial computation bottlenecks commonly encountered in QuPath workflows.

<br>

### Current GPU Spatial Primitives

| Primitive | Description |
|---|---|
| `nearest-neighbor` | Fast nearest-point distance computation |
| `distance-to-polygon` | Fast point-to-boundary distance computation |

<br>

### Current Features

- CUDA spatial kernels
- Rust CLI infrastructure
- QuPath Groovy bridge scripts
- Early spatial primitive abstraction
- Reproducible benchmark pipeline

<br>

### Target Applications

- Tumor microenvironment (TME)
- Neuroimmune interactions
- Perineural invasion (PNI)
- Multiplex immunofluorescence (MxIF)
- Spatial graph construction
- Large-scale distance computation

---

## 2. Core Design Philosophy

Instead of repeatedly implementing task-specific QuPath scripts, this project attempts to abstract spatial computation into reusable GPU spatial primitives.

<br>

### Current Abstraction Model

| Concept | Meaning |
|---|---|
| `source` | objects being measured |
| `target` | reference spatial objects |
| `mode` | spatial primitive |
| `output` | numerical spatial result |

<br>

The current prototype allows different spatial primitives to share:

- unified CLI interfaces
- identical IO pipelines
- benchmark infrastructure
- QuPath bridge logic

---

## 3. Current Spatial Primitives

### 3.1 nearest-neighbor

Computes nearest Euclidean distance:

```text
point -> nearest point
```

<br>

#### Typical Use Cases

- immune cell -> nearest immune cell
- tumor cell -> nearest vessel
- local density estimation
- neighborhood interaction analysis

---

### 3.2 distance-to-polygon

Computes minimum distance from points to polygon boundaries using vector projection.

```text
point -> nearest polygon edge
```

<br>

#### Typical Use Cases

- cell -> nerve boundary
- cell -> tumor boundary
- cell -> annotation edge
- spatial shell analysis

---

## 4. Benchmark Results

### nearest-neighbor

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.08 s | ~9.47 s | ~113× |

<br>

### distance-to-polygon

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.30 s | ~25.50 s | ~84× |

<br>

### Benchmark Environment

- NVIDIA RTX 3070 Ti Laptop
- Intel i9-12900H

---

## 5. Quick Start

### Video Tutorial

A full workflow tutorial is available here:

🎥 https://youtu.be/iA-HR2wv8Vo

The tutorial demonstrates:

- exporting QuPath detections
- exporting polygon annotations
- GPU distance-to-polygon computation
- importing results back into QuPath
- visualization of spatial measurements

---

### Step 1 — Export Data from QuPath

Export:

- detections as CSV
- annotation polygons as CSV

Example:

```text
source.csv
target.csv
```

<br>

#### Typical Source Objects

- immune cells
- tumor cells
- nuclei centroids

#### Typical Target Objects

- nerve annotations
- tumor boundaries
- vessel regions

---

### Step 2 — Build

```bash
cargo build --release
```

Executable:

```text
target/release/qupath_gpu_tool.exe
```

---

### Step 3 — Run GPU Primitive

#### nearest-neighbor

```bash
qupath_gpu_tool.exe ^
  --mode nearest-neighbor ^
  --source source.csv ^
  --target target.csv ^
  --output result.csv
```

---

#### distance-to-polygon

```bash
qupath_gpu_tool.exe ^
  --mode distance-to-polygon ^
  --source source.csv ^
  --target polygon.csv ^
  --output result.csv
```

---

### Step 4 — Import Back into QuPath

Output CSV files can be:

- re-imported into QuPath
- merged into measurement tables
- used for downstream spatial analysis

<br>

#### Typical Downstream Analyses

- immune infiltration analysis
- nerve proximity analysis
- spatial shell analysis
- spatial graph construction

---

## 6. QuPath Workflow

<div align="center">

```text
QuPath
   ↓
Export CSV
   ↓
GPU Spatial Primitive
   ↓
Result CSV
   ↓
Re-import into QuPath
   ↓
Spatial statistics / visualization
```

</div>

---

## 7. Technical Architecture

### CUDA Layer

Current kernels include:

- point-to-point nearest distance
- point-to-segment distance
- polygon edge traversal

---

### Rust Engine Layer

Responsible for:

- CLI dispatch
- primitive registry
- CSV IO
- benchmark execution
- FFI integration

---

### QuPath Bridge Layer

Groovy scripts provide:

- object export
- annotation export
- GPU invocation
- result re-import
- measurement update

---

## 8. Current Limitations

Current limitations include:

- CSV-based IO overhead
- no persistent GPU memory pool
- limited primitive coverage
- Windows-focused build pipeline
- no multi-GPU support
- QuPath bridge is currently experimental

<br>

> The project is still in an early research-engineering stage.

---

## 9. Future Roadmap

### Planned Primitives

- radius-query
- shell-query
- point-in-polygon
- graph-edge construction
- spatial density estimation

<br>

### Planned Infrastructure

- persistent GPU memory pool
- batch primitive execution
- primitive chaining
- kernel-only benchmark mode

---

## 10. Disclaimer

This project is:

- research-oriented
- experimental
- not intended for clinical diagnosis
- not validated for medical deployment

---

## 11. Author

<div align="center">

### Zixuan Liang

School of Information Science and Technology  
Jinan University

<br>

GitHub:

```text
https://github.com/XUANZERA
```

</div>

---

## 12. License

This repository is currently released for:

- academic research
- educational usage
- computational pathology development

<br>

Please contact the author for commercial or clinical usage.

---

---

<a id="中文版本"></a>

# 🇨🇳 中文版本

## 1. 项目简介

QuPath-CUDA-Spatial 是一个面向计算病理学（Computational Pathology）的实验性 GPU 空间分析工具包。

该项目主要用于解决 QuPath 大规模全切片图像（WSI）空间分析中的计算瓶颈问题。

<br>

### 当前已实现的 GPU 空间原语

| Primitive | 功能 |
|---|---|
| `nearest-neighbor` | 最近邻距离计算 |
| `distance-to-polygon` | 点到边界最短距离计算 |

<br>

### 当前提供

- CUDA 空间计算 Kernel
- Rust CLI 基础设施
- QuPath Groovy 桥接脚本
- 初步统一的空间原语抽象
- 可复现 Benchmark 管线

<br>

### 主要目标应用场景

- 肿瘤微环境（TME）
- 神经免疫分析
- 神经侵犯（PNI）
- 多重免疫荧光（MxIF）
- 空间图构建
- 大规模距离计算

---

## 2. 核心设计思想

本项目尝试将大量重复的 QuPath 空间分析脚本，抽象为可复用 GPU 空间原语。

<br>

### 当前抽象模型

| 概念 | 含义 |
|---|---|
| `source` | 被测量对象 |
| `target` | 参考空间对象 |
| `mode` | 空间原语 |
| `output` | 数值空间结果 |

<br>

目前不同空间原语共享：

- 统一 CLI 接口
- 相同 IO 流程
- Benchmark 基础设施
- QuPath 桥接逻辑

---

## 3. 当前实现的空间原语

### 3.1 nearest-neighbor

计算最近欧氏距离：

```text
point -> nearest point
```

<br>

#### 典型应用

- immune cell -> nearest immune cell
- tumor cell -> nearest vessel
- 局部密度估计
- 空间邻域分析

---

### 3.2 distance-to-polygon

计算点到 Polygon 边界的最短距离。

```text
point -> nearest polygon edge
```

<br>

#### 典型应用

- cell -> nerve boundary
- cell -> tumor boundary
- cell -> annotation edge
- 空间 shell 分析

---

## 4. Benchmark 结果

### nearest_neighbor

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.08 s | ~9.47 s | ~113× |

<br>

### distance_to_polygon

| Source Size | Target Size | GPU Time | CPU Time | Speedup |
|---|---|---|---|---|
| 1e6 | 1e4 | ~0.30 s | ~25.50 s | ~84× |

<br>

### 测试环境

- NVIDIA RTX 3070 Ti Laptop
- Intel i9-12900H

---

## 5. 快速开始

### 视频教程

完整工作流视频教程：

🎥 https://youtu.be/iA-HR2wv8Vo

视频内容包括：

- QuPath detection 导出
- polygon annotation 导出
- GPU distance-to-polygon 空间计算
- result.csv 导回 QuPath
- 空间测量结果可视化

---

### Step 1 — QuPath 导出数据

导出：

- detection CSV
- polygon annotation CSV

示例：

```text
source.csv
target.csv
```

---

### Step 2 — 编译

```bash
cargo build --release
```

---

### Step 3 — 运行 GPU 原语

```bash
qupath_gpu_tool.exe ^
  --mode nearest_neighbor ^
  --source source.csv ^
  --target target.csv ^
  --output result.csv
```

---

### Step 4 — 导回 QuPath

结果 CSV 可以：

- 导回 QuPath
- 合并 measurement table
- 用于后续空间统计分析

---

## 6. 当前局限性

当前限制包括：

- CSV IO 开销较大
- 暂无 GPU memory pool
- 空间原语数量有限
- 主要针对 Windows 构建
- 暂无多 GPU 支持
- QuPath bridge 仍为实验阶段

<br>

> 项目目前仍属于早期研究工程阶段。

---

## 7. 作者

<div align="center">

### Zixuan Liang

暨南大学  
信息科学技术学院

<br>

GitHub：

```text
https://github.com/XUANZERA
```

</div>