pub fn nearest_neighbor_cpu(
    source_x: &[f32],
    source_y: &[f32],

    target_x: &[f32],
    target_y: &[f32],    
) -> Vec<f32> {

    let mut output = Vec::with_capacity(source_x.len());

    for i in 0..source_x.len() {

        let sx = source_x[i];
        let sy = source_y[i];

        let mut min_distance = f32::INFINITY;

        for j in 0..target_x.len() {
            let dx = target_x[j] - sx;
            let dy = target_y[j] - sy;

            let distance = (dx * dx + dy * dy).sqrt();

            if distance < min_distance {
                min_distance = distance;
            }
        }
        output.push(min_distance);
    }
    output
}


unsafe extern "C" {
    pub fn launch_nearest_neighbor_kernel(
        source_x: *const f32,
        source_y: *const f32,
        num_source: i32,

        target_x: *const f32,
        target_y: *const f32,
        num_target: i32,

        output: *mut f32,
    );
}

pub fn nearest_neighbor_gpu(
    source_x: &[f32],
    source_y: &[f32],

    target_x: &[f32],
    target_y: &[f32],    
) -> Vec<f32> {

    let mut output = vec![0.0f32; source_x.len()];

    unsafe {
        launch_nearest_neighbor_kernel(
            source_x.as_ptr(),
            source_y.as_ptr(),
            source_x.len() as i32,

            target_x.as_ptr(),
            target_y.as_ptr(),
            target_x.len() as i32,

            output.as_mut_ptr(),
        );
    }
    output
}