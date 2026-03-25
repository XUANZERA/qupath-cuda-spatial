use serde::Deserialize;
use std::error::Error;
use std::time::Instant;
use clap::Parser;

// 定义命令行参数结构
#[derive(Parser, Debug)]
#[command(author, version, about = "GPU distance calculator")]
struct Args {
    #[arg(short, long)]
    cells: String,       // 对应 --cells

    #[arg(short, long)]
    boundary: String,    // 对应 --boundary

    #[arg(short, long)]
    output: String,      // 对应 --output
}


#[derive(Deserialize)]
struct Point { x: f32, y: f32 }

unsafe extern "C" {
    fn launch_gpu_kernel(cx: *const f32, cy: *const f32, n_c: i32, bx: *const f32, by: *const f32, n_v: i32, res: *mut f32);
}

const cell_csv: &str = "D:/code/qupath_gpu_tool/data/cells_input.csv";
const boundary_csv: &str = "D:/code/qupath_gpu_tool/data/boundary_input.csv";
const result_csv: &str = "D:/code/qupath_gpu_tool/data/result.csv";

fn read_csv(path: &str) -> (Vec<f32>, Vec<f32>) {
    let mut rdr = csv::Reader::from_path(path).unwrap();
    let (mut xs, mut ys) = (Vec::new(), Vec::new());
    for result in rdr.deserialize::<Point>() {
        let p: Point = result.unwrap();
        xs.push(p.x); ys.push(p.y);
    }
    (xs, ys)
}

fn point_to_segment_dist(px: f32, py: f32, x1: f32, y1: f32, x2: f32, y2: f32) -> f32 {
    let dx = x2 - x1;
    let dy = y2 - y1;
    let l2 = dx * dx + dy * dy;
    if l2 == 0.0 {
        return ((px - x1).powi(2) + (py - y1).powi(2)).sqrt();
    }
    let mut t = ((px - x1) * dx + (py - y1) * dy) / l2;
    t = t.max(0.0).min(1.0);
    let proj_x = x1 + t * dx;
    let proj_y = y1 + t * dy;
    ((px - proj_x).powi(2) + (py - proj_y).powi(2)).sqrt()
}

fn point_to_polygon_edge_distance(px: f32, py: f32, poly_x: &[f32], poly_y: &[f32]) -> f32 {
    let mut min_d = f32::INFINITY;
    for i in 0..poly_x.len() - 1 {
        let d = point_to_segment_dist(px, py, poly_x[i], poly_y[i], poly_x[i+1], poly_y[i+1]);
        if d < min_d {
            min_d = d;
        }
    }
    min_d
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();

    println!("1. Reading CSVs...");
    let (cx_orig, cy_orig) = read_csv(&args.cells);
    let (bx, by) = read_csv(&args.boundary);

    // 拼接数据点梯度评测性能 default=1
    let repeat_times = 1;
    let mut cx = Vec::with_capacity(cx_orig.len() * repeat_times);
    let mut cy = Vec::with_capacity(cy_orig.len() * repeat_times);
    for _ in 0..repeat_times {
        cx.extend_from_slice(&cx_orig);
        cy.extend_from_slice(&cy_orig);
    }
    println!("Original points: {}, Replicated: {}", cx_orig.len(), cx.len());

    let mut results = vec![0.0f32; cx.len()];

    println!("2. Launching CUDA...");
    let gpu_start = Instant::now();
    unsafe {
        launch_gpu_kernel(cx.as_ptr(), cy.as_ptr(), cx.len() as i32,
                          bx.as_ptr(), by.as_ptr(), bx.len() as i32,
                          results.as_mut_ptr());
    }
    let gpu_duration = gpu_start.elapsed();
    println!("GPU time: {:?}", gpu_duration);

    println!("3. CPU computation...");
    let cpu_start = Instant::now();
    let mut cpu_results = Vec::with_capacity(cx.len());
    for i in 0..cx.len() {
        let d = point_to_polygon_edge_distance(cx[i], cy[i], &bx, &by);
        cpu_results.push(d);
    }
    let cpu_duration = cpu_start.elapsed();
    println!("CPU time: {:?}", cpu_duration);

    println!("4. Saving GPU results...");
    let mut wtr = csv::Writer::from_path(&args.output)?;
    wtr.write_record(&["distance"])?;
    for d in &results {
        wtr.write_record(&[d.to_string()])?;
    }
    wtr.flush()?;

    // 只检查前5个结果（因为拼接后数据重复）
    println!("Comparison (first 5):");
    for i in 0..5.min(cx_orig.len()) {
        println!("  point {}: GPU={:.6}, CPU={:.6}", i, results[i], cpu_results[i]);
    }

    println!("All done!");
    Ok(())
}