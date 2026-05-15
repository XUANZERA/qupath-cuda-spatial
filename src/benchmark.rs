use std::time::{Duration, Instant};

pub fn time_it<F>(
    func: F,
) -> (Vec<f32>, Duration)
where
    F: FnOnce() -> Vec<f32>,
{
    let start = Instant::now();

    let result = func();

    let elapsed = start.elapsed();

    (result, elapsed)
}

pub fn compare_results(
    gpu: &[f32],
    cpu: &[f32],
) {
    println!("=================================");
    println!("Result Comparison");
    println!("=================================");

    let n = 5.min(gpu.len()).min(cpu.len());

    for i in 0..n {
        let abs_err =
            (gpu[i] - cpu[i]).abs();

        println!(
            "Point {}: GPU={:.6}, CPU={:.6}, abs_err={:.6}",
            i,
            gpu[i],
            cpu[i],
            abs_err,
        );
    }
}