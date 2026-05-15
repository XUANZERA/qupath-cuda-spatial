#pragma once

#include <cuda_runtime.h>
#include <stdio.h>

// ============================================================
// CUDA CONFIG
// ============================================================

#define THREADS_PER_BLOCK 256

// ============================================================
// CUDA ERROR CHECK
// ============================================================

static inline void check_cuda_error(
    const char* stage
)
{
    cudaError_t err = cudaGetLastError();

    if (err != cudaSuccess) {

        printf(
            "[CUDA ERROR] %s: %s\n",
            stage,
            cudaGetErrorString(err)
        );
    }
}

// ============================================================
// CUDA KERNEL BENCHMARK
// ============================================================

static inline float benchmark_kernel_ms(
    cudaEvent_t start,
    cudaEvent_t stop
)
{
    cudaEventRecord(stop);

    cudaEventSynchronize(stop);

    float ms = 0.0f;

    cudaEventElapsedTime(
        &ms,
        start,
        stop
    );

    return ms;
}