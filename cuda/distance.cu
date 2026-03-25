#include <cuda_runtime.h>
#include <math.h>


__device__ float dist_to_segment_sq(
    float px, float py,
    float x1, float y1,
    float x2, float y2
) {
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


extern "C" __global__ void compute_distances(
    const float* cx, const float* cy, int n_cells,
    const float* bx, const float* by, int n_verts,
    float* out_dist
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < n_cells) {
        float min_d = 1e20f;
        
        float px = cx[i];
        float py = cy[i];

        for (int j = 0; j < n_verts - 1; j ++) {
            float d2 = dist_to_segment_sq(px, py, bx[j], by[j], bx[j+1], by[j+1]);

            if (d2 < min_d) min_d = d2;
        }
        out_dist[i] = sqrtf(min_d);  
    }
}


extern "C" void launch_gpu_kernel(
    const float* cx, const float* cy, int n_cells,
    const float* bx, const float* by, int n_verts,
    float* results) {
    float *d_cx, *d_cy, *d_bx, *d_by, *d_res;
    cudaMalloc(&d_cx, n_cells * sizeof(float));
    cudaMalloc(&d_cy, n_cells * sizeof(float));
    cudaMalloc(&d_bx, n_verts * sizeof(float));
    cudaMalloc(&d_by, n_verts * sizeof(float));
    cudaMalloc(&d_res, n_cells * sizeof(float));

    cudaMemcpy(d_cx, cx, n_cells * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_cy, cy, n_cells * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_bx, bx, n_verts * sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy(d_by, by, n_verts * sizeof(float), cudaMemcpyHostToDevice);

    int threads = 256;
    int blocks = (n_cells + threads - 1) / threads;
    compute_distances<<<blocks, threads>>>(d_cx, d_cy, n_cells, d_bx, d_by, n_verts, d_res);

    cudaMemcpy(results, d_res, n_cells * sizeof(float), cudaMemcpyDeviceToHost);

    cudaFree(d_cx); cudaFree(d_cy); cudaFree(d_bx); cudaFree(d_by); cudaFree(d_res);
}