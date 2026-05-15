// 计算 Point to Point 最近距离
#include <stdio.h>
#include <cuda_runtime.h>
#include <math.h>
#include <float.h>


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

    float* output_dist
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

    output_dist[idx] = sqrtf(min_distance);
}

extern "C" void launch_nearest_neighbor_kernel(
    const float* source_x,
    const float* source_y,
    int num_source,

    const float* target_x,
    const float* target_y,
    int num_target,

    float* output_dist
)
{
    float *d_source_x, *d_source_y, *d_target_x, *d_target_y, *d_output;

    cudaMalloc(&d_su_x, num_source * sizeof(float));
    cudaMalloc(&d_src_y, num_source * sizeof(float));
    cudaMalloc(&d_tar_x, num_target * sizeof(float));
    cudaMalloc(&d_tar_y, num_target * sizeof(float));
    cudaMalloc(&d_output, num_source * sizeof(float));

    cudaMemcpy(d_source_x, source_x, num_source * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_source_y, source_y, num_source * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_target_x, target_x, num_target * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_target_y, target_y, num_target * sizeof(float), cudaMemcpyHostToDevice);

    int threads_per_block = 256;
    int blocks_per_grid = (num_src + threads_per_block - 1) / threads_per_block;

    nearest_neighbor_kernel<<<blocks_per_grid, threads_per_block>>>(
        d_src_x, d_src_y, num_src,
        d_tar_x, d_tar_y, num_tar,
        d_output
    );

    float* output_dist = (float*) malloc(num_src * sizeof(float));
    cudaMemcpy(output_dist, d_output, num_src * sizeof(float), cudaMemcpyDeviceToHost);

    cudaFree(d_src_x);
    cudaFree(d_src_y);
    cudaFree(d_tar_x);
    cudaFree(d_tar_y);
    cudaFree(d_output);
}

// int main() {

// /*
// =========================================
// 测试数据
// =========================================
// */

//     float src_x[] = {0.0f, 1.0f, 2.0f};
//     float src_y[] = {0.0f, 1.0f, 2.0f};
//     int num_src = sizeof(src_x) / sizeof(src_x[0]);

//     float tar_x[] = {10.0f, 20.0f, 30.0f};
//     float tar_y[] = {10.0f, 20.0f, 30.0f};
//     int num_tar = sizeof(tar_x) / sizeof(tar_x[0]);

//     float *d_src_x, *d_src_y, *d_tar_x, *d_tar_y, *d_output;

//     cudaMalloc(&d_src_x, num_src * sizeof(float));
//     cudaMalloc(&d_src_y, num_src * sizeof(float));
//     cudaMalloc(&d_tar_x, num_tar * sizeof(float));
//     cudaMalloc(&d_tar_y, num_tar * sizeof(float));
//     cudaMalloc(&d_output, num_src * sizeof(float));

//     cudaMemcpy(d_src_x, src_x, num_src * sizeof(float), cudaMemcpyHostToDevice);
//     cudaMemcpy(d_src_y, src_y, num_src * sizeof(float), cudaMemcpyHostToDevice);
//     cudaMemcpy(d_tar_x, tar_x, num_tar * sizeof(float), cudaMemcpyHostToDevice);
//     cudaMemcpy(d_tar_y, tar_y, num_tar * sizeof(float), cudaMemcpyHostToDevice);

//     int threads_per_block = 256;
//     int blocks_per_grid = (num_src + threads_per_block - 1) / threads_per_block;

//     nearest_neighbor_kernel<<<blocks_per_grid, threads_per_block>>>(
//         d_src_x, d_src_y, num_src,
//         d_tar_x, d_tar_y, num_tar,
//         d_output
//     );

//     cudaDeviceSynchronize();
//     cudaError_t err = cudaGetLastError();
//     if (err != cudaSuccess) {
//         printf("CUDA Error: %s\n", cudaGetErrorString(err));
//         return -1;
//     }

//     float* output_dist = (float*) malloc(num_src * sizeof(float));
//     cudaMemcpy(output_dist, d_output, num_src * sizeof(float), cudaMemcpyDeviceToHost);

//     printf("Nearest distances from source points to target points:\n");
//     for (int i = 0; i < num_src; i ++) {
//         printf("Source point %d (%.1f, %.1f) -> closest target distance: %.4f\n", 
//                i, src_x[i], src_y[i], output_dist[i]);
//     }

//     cudaFree(d_src_x);
//     cudaFree(d_src_y);
//     cudaFree(d_tar_x);
//     cudaFree(d_tar_y);
//     cudaFree(d_output);

//     return 0;
// }