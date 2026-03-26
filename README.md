# QuPath-CUDA-Spatial 
### High-Performance Spatial Analysis for Neuroimmunopathology

[![Rust](https://img.shields.io/badge/rust-1.70%2B-orange.svg)](https://www.rust-lang.org)
[![CUDA](https://img.shields.io/badge/CUDA-11.0%2B-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![QuPath](https://img.shields.io/badge/QuPath-0.4.0%2B-blue.svg)](https://qupath.github.io/)

## 1. Project Overview
This project provides a **GPU-accelerated CLI tool** to solve the computational bottleneck in digital pathology spatial analysis. Specifically, it calculates the **minimum distance from thousands of cells to complex annotation boundaries** (e.g., nerve regions) within QuPath.

By leveraging **Rust**'s memory safety and **CUDA**'s parallel computing power, this tool achieves a **200x+ speedup** compared to QuPath's native single-threaded CPU implementation, enabling real-time spatial analysis of whole-slide images (WSI) with tens of thousands of cells.

### Key Features
*   **CUDA Core**: Implements a high-precision point-to-segment distance algorithm using vector projection.
*   **Rust CLI**: Provides a robust command-line interface with safe FFI (Foreign Function Interface) to manage GPU resources.
*   **QuPath Integration**: Seamless workflow integration via Groovy scripts (Export -> GPU Calc -> Import).
*   **Unit Conversion**: Automatically handles pixel-to-micron calibration based on image metadata.

## 2. System Requirements
*   **OS**: Windows 10/11 (Tested)
*   **GPU**: NVIDIA GPU (Compute Capability 6.0+)
*   **Software**:
    *   CUDA Toolkit 11.x or 12.x
    *   Rust 1.70+
    *   QuPath 0.4.0 or later
    *   Visual Studio Build Tools (C++ compiler)

## 3. Installation & Building

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/qupath-cuda-spatial.git
    cd qupath-cuda-spatial
    ```

2.  **Build the project**:
    The `build.rs` script will automatically compile the CUDA kernel and link it to the Rust binary.
    ```bash
    cargo build --release
    ```
    The executable will be generated at `target/release/qupath_gpu_tool.exe`.

## 4. Usage

### Step 1: Prepare QuPath Data
1. Open your image in QuPath.
2. Ensure you have objects classified as `immune_cell` and `nerve_regions` (or modify the Groovy script classes).
3. Select the parent annotation containing these objects.

### Step 2: Run the Groovy Bridge
1. Open the **Script Editor** in QuPath.
2. Load `scripts/qupath_bridge.groovy`.
3. Update the `exePath` and data folder paths in the script.
4. Click **Run**.

### Step 3: View Results
1. Results are saved in the `Distance_to_Nerve_um` column in the Measurement List.
2. Use **Measure -> Show measurement maps** to visualize the spatial distribution.

## 5. Mathematical Logic
The tool implements the **Vector Projection Method** to find the minimum distance from a point $P$ to a line segment $AB$.

1.  **Projection Ratio ($t$)**: 
    $$t = \frac{\vec{AP} \cdot \vec{AB}}{|\vec{AB}|^2}$$
2.  **Clamping**: To ensure the closest point $Q$ lies on the segment, $t$ is clamped to $[0, 1]$.
3.  **Distance**: 
    $$Distance = \sqrt{|P - (A + t \cdot \vec{AB})|^2}$$

This approach avoids slope-intercept form ($y=mx+b$), preventing division-by-zero errors for vertical lines and significantly improving numerical stability on GPU hardware.

## 6. Performance Benchmark
| Cell Count | Target Vertices | Native QuPath (CPU) | This Tool (GPU) | Speedup |
| :--- | :--- | :--- | :--- | :--- |
| 10,000 | 5,000 | ~15.2 s | ~0.06 s | **~250x** |
| 50,000 | 20,000 | ~240.5 s | ~0.85 s | **~280x** |

*Note: Benchmarked on NVIDIA RTX 3070Ti Laptop vs Intel i9-12900H. Speedup includes data I/O overhead.*

## 7. Project Structure
```text
.
├── Cargo.toml            # Rust dependencies & metadata
├── build.rs              # CUDA compilation script
├── cuda/
│   └── distance.cu       # CUDA kernel implementation
├── src/
│   └── main.rs           # CLI logic & GPU FFI wrapper
├── scripts/
│   └── qupath_bridge.groovy # QuPath integration script
└── data/                 # (Git-ignored) Temporary CSV files
```

## 8. License
This project is developed for the software engineering project and for neuroimmunopathology research at Jinan University.

**Author**: Zixuan Liang
**Contact**: liangzixuan@stu2023.jnu.edu.cn
