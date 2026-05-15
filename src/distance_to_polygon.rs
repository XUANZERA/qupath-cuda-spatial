fn point_to_segment_distance(
    px: f32, 
    py: f32, 
    
    x1: f32, 
    y1: f32, 

    x2: f32,
    y2: f32
) -> f32 
{
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


fn point_to_polygon_distance(
    px: f32, 
    py: f32, 
    
    polygon_x: &[f32], 
    polygon_y: &[f32]
) -> f32 {
    let mut min_distance = f32::INFINITY;

    for i in 0..polygon_x.len() - 1 {
        let distance = point_to_segment_distance(
            px, 
            py, 
            
            polygon_x[i], 
            polygon_y[i], 
            
            polygon_x[i+1], 
            polygon_y[i+1]);

        if distance < min_distance {
            min_distance = distance;
        }
    }

    min_distance
}


pub fn distance_to_polygon_cpu(
    source_x: &[f32],
    source_y: &[f32],

    polygon_x: &[f32],
    polygon_y: &[f32],
) -> Vec<f32>
{
    let mut output = Vec::with_capacity(source_x.len());

    for i in 0..source_x.len() {
        let distance = point_to_polygon_distance(
            source_x[i],
            source_y[i],

            polygon_x,
            polygon_y,
        );

        output.push(distance)
    }

    output
}


unsafe extern "C" {

    pub fn launch_distance_to_polygon_kernel(

        source_x: *const f32,
        source_y: *const f32,
        num_source: i32,

        target_x: *const f32,
        target_y: *const f32,
        num_target: i32,

        output: *mut f32,
    );
}

pub fn distance_to_polygon_gpu(
        source_x: &[f32],
        source_y: &[f32],

        target_x: &[f32],
        target_y: &[f32],
) -> Vec<f32>
{

    let mut output = vec![0.0f32; source_x.len()];

    unsafe {
        launch_distance_to_polygon_kernel(
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