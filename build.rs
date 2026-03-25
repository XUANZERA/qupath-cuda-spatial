use std::env;

fn main() {
    println!("cargo:rustc-link-search=native={}", r"D:\code\qupath_gpu_tool\cuda");

    if let Ok(cuda_path) = env::var("CUDA_PATH") {
        println!("cargo:rustc-link-search=native={}\\lib\\x64", cuda_path);
    } else {
        println!("cargo:warning=CUDA_PATH not set, cudart.lib may not be found");
    }

    println!("cargo:rustc-link-lib=static=gpu_kernel");
    println!("cargo:rustc-link-lib=cudart");
}