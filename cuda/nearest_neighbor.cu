// 计算 Point to Point 最近距离
#include <stdio.h>
#include <cuda_runtime.h>
#include <math.h>
#include <float.h>

#include "cuda_utils.cuh"


/*
=========================================
功能：内核 计算两类点的最近距离
输入：两类点的[x...x] [y...]
输出：source类每个点到target类点的最短集合

=========================================
*/
extern "C" __global__ void nearest_neighbor_kernel(
    const float* source_x,
    const float* source_y,
    int num_source,

    const float* target_x,
    const float* target_y,
    int num_target,

    float* output
)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    if (idx >= num_source) return;

    float sx = source_x[idx];
    float sy = source_y[idx];

    float min_distance = FLT_MAX;

    for (int i = 0; i < num_target; i ++) {
        float tx = target_x[i];
        float ty = target_y[i];

        float dx = tx - sx;
        float dy = ty - sy;

        float distance = dx * dx + dy * dy;

        if (distance < min_distance) min_distance = distance;
    }

    output[idx] = sqrtf(min_distance);
}

extern "C" void launch_nearest_neighbor_kernel(
    const float* source_x,
    const float* source_y,
    int num_source,

    const float* target_x,
    const float* target_y,
    int num_target,

    float* output
)
{
    float *d_source_x, *d_source_y, *d_target_x, *d_target_y, *d_output;

    cudaMalloc(&d_source_x, num_source * sizeof(float));
    cudaMalloc(&d_source_y, num_source * sizeof(float));
    cudaMalloc(&d_target_x, num_target * sizeof(float));
    cudaMalloc(&d_target_y, num_target * sizeof(float));
    cudaMalloc(&d_output, num_source * sizeof(float));

    cudaMemcpy(d_source_x, source_x, num_source * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_source_y, source_y, num_source * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_target_x, target_x, num_target * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_target_y, target_y, num_target * sizeof(float), cudaMemcpyHostToDevice);

    int threads_per_block = 256;
    int blocks_per_grid = (num_source + threads_per_block - 1) / threads_per_block;

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    nearest_neighbor_kernel<<<blocks_per_grid, threads_per_block>>>(
        d_source_x, d_source_y, num_source,
        d_target_x, d_target_y, num_target,
        d_output
    );

    // launch error
    check_cuda_error(
        "nearest_neighbor_kernel launch"
    );

    float kernel_ms = benchmark_kernel_ms(
        start,
        stop
    );

    // runtime error
    check_cuda_error(
        "nearest_neighbor_kernel runtime"
    );

    printf(
        "[CUDA] nearest_neighbor kernel: %.6f ms\n",
        kernel_ms
    );

    cudaMemcpy(output, d_output, num_source * sizeof(float), cudaMemcpyDeviceToHost);

    cudaFree(d_source_x);
    cudaFree(d_source_y);
    cudaFree(d_target_x);
    cudaFree(d_target_y);
    cudaFree(d_output);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
}
