use clap::Parser;

#[derive(Parser, Debug)]
#[command(author, version, about = "QuPath CUDA Spatial Toolkit")]
pub struct Args {
    #[arg(long)]
    pub mode: String,

    #[arg(long)]
    pub source: String,

    #[arg(long)]
    pub target: String,

    #[arg(long)]
    pub output: String,

    #[arg(long, default_value_t = true)]
    pub benchmark: bool,
}

pub fn parse_args() -> Args {
    Args::parse()
}