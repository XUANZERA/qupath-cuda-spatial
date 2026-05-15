mod cli;
mod engine;
mod io;
mod benchmark;
mod primitive;
mod registry;

mod distance_to_polygon;
mod nearest_neighbor;

use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    engine::run()
}