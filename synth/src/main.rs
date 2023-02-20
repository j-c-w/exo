use clap::Parser;

#[derive(Parser)]
struct Args {
	exo: std::path::PathBuf,
	sketch: std::path::PathBuf,
}

fn main() {
	let args = Args::parse();

	println!("Generating Schedules for {} from sketch in {}", args.exo.display(), args.sketch.display());

}
