//! 将 PNG 转换为 ICO 的一次性工具

use std::env;
use std::fs::File;
use std::path::Path;

use ico::IconDir;
use image::imageops::FilterType;
use image::GenericImageView;

/// 入口：`cargo run --bin icongen -- assets/1.png assets/remark.ico`
fn main() -> Result<(), String> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        return Err("Usage: icongen <input_png> <output_ico>".to_string());
    }
    let src = Path::new(&args[1]);
    let dest = Path::new(&args[2]);
    convert_png_to_ico(src, dest)
}

/// 读取 PNG 并生成 32x32 ICO（保留透明）
fn convert_png_to_ico(src: &Path, dest: &Path) -> Result<(), String> {
    if !src.exists() {
        return Err(format!("missing source png: {}", src.display()));
    }
    let img = image::open(src).map_err(|e| e.to_string())?;
    let resized = img.resize_exact(32, 32, FilterType::Lanczos3);
    let rgba = resized.to_rgba8();
    let (w, h) = resized.dimensions();

    let mut dir = IconDir::new(ico::ResourceType::Icon);
    let icon_image = ico::IconImage::from_rgba_data(w, h, rgba.into_raw());
    dir.add_entry(ico::IconDirEntry::encode(&icon_image).map_err(|e| e.to_string())?);

    let mut file = File::create(dest).map_err(|e| e.to_string())?;
    dir.write(&mut file).map_err(|e| e.to_string())
}
