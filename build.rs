use std::process::Command;

fn main() {

    println!("cargo:rerun-if-changed=cuda/distance_to_polygon.cu");
    println!("cargo:rerun-if-changed=cuda/nearest_neighbor.cu");

    // ------------------------------------------------
    // CUDA LIB PATH
    // ------------------------------------------------

    println!(
        "cargo:rustc-link-search=native=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6/lib/x64"
    );

    println!("cargo:rustc-link-lib=cudart");

    // --------------------------------
    // distance_to_polygon
    // --------------------------------

    let status = Command::new("nvcc")
        .args([
            "-c",

            "-allow-unsupported-compiler",

            "cuda/distance_to_polygon.cu",

            "-o",
            "cuda/distance_to_polygon.obj",

            "-Xcompiler",
            "/MD",
        ])
        .status()
        .expect("Failed to compile distance_to_polygon.cu");

    assert!(
        status.success(),
        "distance_to_polygon CUDA compilation failed"
    );

    // --------------------------------
    // nearest_neighbor
    // --------------------------------

    let status = Command::new("nvcc")
        .args([
            "-c",

            "-allow-unsupported-compiler",

            "cuda/nearest_neighbor.cu",

            "-o",
            "cuda/nearest_neighbor.obj",

            "-Xcompiler",
            "/MD",
        ])
        .status()
        .expect("Failed to compile nearest_neighbor.cu");

    assert!(
        status.success(),
        "nearest_neighbor CUDA compilation failed"
    );

    // --------------------------------
    // Link CUDA objects
    // --------------------------------

    println!("cargo:rustc-link-search=native=cuda");

    println!("cargo:rustc-link-lib=dylib=cudart");

    println!("cargo:rustc-link-arg=cuda/distance_to_polygon.obj");

    println!("cargo:rustc-link-arg=cuda/nearest_neighbor.obj");
}