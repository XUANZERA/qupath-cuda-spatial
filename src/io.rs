use serde::Deserialize;
use std::error::Error;

#[derive(Deserialize)]
pub struct Point {
    pub x: f32,
    pub y: f32,
}

pub fn read_csv(
    path: &str,
) -> Result<(Vec<f32>, Vec<f32>), Box<dyn Error>> {
    let mut reader =
        csv::Reader::from_path(path)?;

    let mut xs = Vec::new();
    let mut ys = Vec::new();

    for row in reader.deserialize::<Point>() {
        let point = row?;

        xs.push(point.x);
        ys.push(point.y);
    }

    Ok((xs, ys))
}

pub fn save_distances(
    path: &str,
    distances: &[f32],
) -> Result<(), Box<dyn Error>> {
    let mut writer =
        csv::Writer::from_path(path)?;

    writer.write_record(["distance"])?;

    for distance in distances {
        writer.write_record([
            distance.to_string(),
        ])?;
    }

    writer.flush()?;

    Ok(())
}