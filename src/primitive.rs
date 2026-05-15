pub type PrimitiveFn = fn(
    source_x: &[f32],
    source_y: &[f32],
    target_x: &[f32],
    target_y: &[f32],
) -> Vec<f32>;

pub struct SpatialPrimitive {
    pub name: &'static str,

    pub gpu: PrimitiveFn,

    pub cpu: PrimitiveFn,
}