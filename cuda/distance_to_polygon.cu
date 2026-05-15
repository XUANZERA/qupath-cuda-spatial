#include <cuda_runtime.h>
#include <math.h>
#include <stdio.h>

#include "cuda_utils.cuh"


__device__ float dist_to_segment_sq(
    float px, 
    float py,

    float x1, 
    float y1,

    float x2, 
    float y2
) 
{
    float dx = x2 - x1;
    float dy = y2 - y1;

    float l2 = dx * dx + dy * dy;
    if (l2 == 0.0f) return powf(px - x1, 2) + powf(py - y1, 2);

    float t = ((px - x1) * dx + (py - y1) * dy) / l2;
    t = fmaxf(0.0f, fminf(1.0f, t));

    float x_proj = x1 + t * dx;
    float y_proj = y1 + t * dy;

    return powf(px - x_proj, 2) + powf(py - y_proj, 2);
}


extern "C" __global__ void distance_to_polygon_kernel(
    const float* source_x, 
    const float* source_y, 
    int num_source,

    const float* target_x, 
    const float* target_y, 
    int num_target,

    float* output
) 
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < num_source) {
        float min_d = 1e20f;
        
        float px = source_x[i];
        float py = source_y[i];

        for (int j = 0; j < num_target - 1; j ++) {
            float d2 = dist_to_segment_sq(
                px, py, target_x[j], 
                target_y[j], target_x[j+1], target_y[j+1]
            );

            if (d2 < min_d) min_d = d2;
        }
        output[i] = sqrtf(min_d);  
    }
}


extern "C" void launch_distance_to_polygon_kernel(
    const float* source_x, 
    const float* source_y, 
    int num_source,

    const float* target_x, 
    const float* target_y, 
    int num_target,

    float* results
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

    int threads = 256;
    int blocks = (num_source + threads - 1) / threads;

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    distance_to_polygon_kernel<<<blocks, threads>>>(
        d_source_x, d_source_y, num_source, 
        d_target_x, d_target_y, num_target, 
        d_output);

    // launch error
    check_cuda_error(
        "distance_to_polygon_kernel launch"
    );

    float kernel_ms = benchmark_kernel_ms(
        start,
        stop
    );

    // runtime error
    check_cuda_error(
        "distance_to_polygon_kernel runtime"
    );

    printf(
        "[CUDA] distance_to_polygon kernel: %.6f ms\n",
        kernel_ms
    );

    cudaMemcpy(results, d_output, num_source * sizeof(float), cudaMemcpyDeviceToHost);

    cudaFree(d_source_x); 
    cudaFree(d_source_y); 
    cudaFree(d_target_x); 
    cudaFree(d_target_y); 
    cudaFree(d_output);

    cudaEventDestroy(start);
    cudaEventDestroy(stop);
}
