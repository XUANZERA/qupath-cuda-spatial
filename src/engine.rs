use std::error::Error;

use crate::benchmark;
use crate::cli;
use crate::io;
use crate::registry;

struct SpatialInput {
    source_x: Vec<f32>,
    source_y: Vec<f32>,

    target_x: Vec<f32>,
    target_y: Vec<f32>,
}

pub fn run() -> Result<(), Box<dyn Error>> {
    let args = cli::parse_args();

    print_banner(&args.mode);

    let input =
        load_input(&args.source, &args.target)?;

    let registry =
        registry::build_registry();

    let primitive =
        registry
            .get(args.mode.as_str())
            .ok_or_else(|| {
                format!(
                    "Unknown mode: {}. Available modes: {:?}",
                    args.mode,
                    registry.keys().collect::<Vec<_>>()
                )
            })?;

    println!("Running GPU primitive: {}", primitive.name);

    let (gpu_results, gpu_time) =
        benchmark::time_it(|| {
            (primitive.gpu)(
                &input.source_x,
                &input.source_y,
                &input.target_x,
                &input.target_y,
            )
        });

    println!("GPU time: {:?}", gpu_time);

    if args.benchmark {
        println!("Running CPU reference: {}", primitive.name);

        let (cpu_results, cpu_time) =
            benchmark::time_it(|| {
                (primitive.cpu)(
                    &input.source_x,
                    &input.source_y,
                    &input.target_x,
                    &input.target_y,
                )
            });

        println!("CPU time: {:?}", cpu_time);

        benchmark::compare_results(
            &gpu_results,
            &cpu_results,
        );
    }

    io::save_distances(
        &args.output,
        &gpu_results,
    )?;

    println!("Done.");

    Ok(())
}

fn load_input(
    source_path: &str,
    target_path: &str,
) -> Result<SpatialInput, Box<dyn Error>> {
    println!("Reading CSV files...");

    let (source_x, source_y) =
        io::read_csv(source_path)?;

    let (target_x, target_y) =
        io::read_csv(target_path)?;

    println!(
        "Loaded {} source points, {} target points",
        source_x.len(),
        target_x.len()
    );

    Ok(SpatialInput {
        source_x,
        source_y,
        target_x,
        target_y,
    })
}

fn print_banner(mode: &str) {
    println!("=================================");
    println!("QuPath CUDA Spatial Toolkit");
    println!("Mode: {}", mode);
    println!("=================================");
}