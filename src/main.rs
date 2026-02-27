#![windows_subsystem = "windows"]
//! 应用入口与 UI 交互

mod config;
mod desktop_ini;
mod lang;

use crate::config::AppConfig;
use crate::desktop_ini::{load_infotip, save_infotip};
use crate::lang::LangPack;
use eframe::egui;
use std::path::PathBuf;
use std::fs;
use std::time::{Duration, Instant};

/// 程序入口：解析命令行参数、加载配置、启动 UI
fn main() {
    let target_dir = match parse_target_dir() {
        Ok(dir) => dir,
        Err(msg) => {
            eprintln!("{msg}");
            return;
        }
    };

    let config = AppConfig::load_or_default();
    let lang_pack = LangPack::new(config.language);
    let last_error = config.last_error.clone();

    let app = RemarkApp::new(target_dir, last_error, lang_pack);
    let native_options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([420.0, 220.0])
            .with_resizable(false),
        ..Default::default()
    };

    let _ = eframe::run_native(
        "Folder Remark",
        native_options,
        Box::new(|_cc| Box::new(app)),
    );
}

/// 解析命令行参数中的目标目录
fn parse_target_dir() -> Result<PathBuf, String> {
    let mut args = std::env::args().skip(1);
    let path = args.next().ok_or_else(|| "缺少目标目录参数".to_string())?;
    let dir = PathBuf::from(path);
    if !dir.is_dir() {
        return Err("目标路径不是文件夹".to_string());
    }
    Ok(dir)
}

/// 主窗口应用状态
struct RemarkApp {
    target_dir: PathBuf,
    input: String,
    status: String,
    font_diag: String,
    lang: LangPack,
    last_error: Option<String>,
    close_at: Option<Instant>,
    fonts_applied: bool,
}

impl RemarkApp {
    /// 初始化应用并回显已有备注
    fn new(target_dir: PathBuf, mut last_error: Option<String>, lang: LangPack) -> Self {
        let input = match load_infotip(&target_dir) {
            Ok(value) => value.unwrap_or_default(),
            Err(err) => {
                last_error = Some(err.to_string());
                String::new()
            }
        };
        let status = last_error.clone().unwrap_or_default();
        Self {
            target_dir,
            input,
            status,
            font_diag: String::new(),
            lang,
            last_error,
            close_at: None,
            fonts_applied: false,
        }
    }

    /// 执行保存逻辑
    fn handle_save(&mut self) {
        match save_infotip(&self.target_dir, &self.input) {
            Ok(_) => {
                self.status = self.lang.save_success.to_string();
                // 保存成功后延迟关闭窗口，保证提示可见
                self.close_at = Some(Instant::now() + Duration::from_millis(700));
            }
            Err(err) => self.status = format!("{}: {}", self.lang.save_failed, err),
        }
    }

    /// 执行清空逻辑（保留 desktop.ini）
    fn handle_clear(&mut self) {
        self.input.clear();
        match save_infotip(&self.target_dir, &self.input) {
            Ok(_) => self.status = self.lang.clear_success.to_string(),
            Err(err) => self.status = format!("{}: {}", self.lang.clear_failed, err),
        }
    }
}

impl eframe::App for RemarkApp {
    /// eframe UI 渲染主循环
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if !self.fonts_applied {
            apply_fonts(ctx);
            // 首帧生成字体诊断信息，便于定位是否真的加载到中文字体
            self.font_diag = build_font_diag(ctx);
            self.fonts_applied = true;
        }
        apply_theme(ctx);
        if let Some(deadline) = self.close_at {
            if Instant::now() >= deadline {
                ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                return;
            } else {
                let remaining = deadline.saturating_duration_since(Instant::now());
                ctx.request_repaint_after(remaining);
            }
        }
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(8.0);
            ui.heading(&self.lang.title);
            ui.add_space(10.0);

            egui::Frame::group(ui.style())
                .inner_margin(egui::Margin::same(10.0))
                .rounding(egui::Rounding::same(8.0))
                .show(ui, |ui| {
                    ui.label(&self.lang.remark_label);
                    ui.add(
                        egui::TextEdit::multiline(&mut self.input)
                            .desired_rows(4)
                            .desired_width(380.0),
                    );

                    ui.add_space(10.0);
                    ui.horizontal(|ui| {
                        if ui
                            .add_sized([90.0, 28.0], egui::Button::new(&self.lang.save_button))
                            .clicked()
                        {
                            self.handle_save();
                        }
                        if ui
                            .add_sized([90.0, 28.0], egui::Button::new(&self.lang.clear_button))
                            .clicked()
                        {
                            self.handle_clear();
                        }
                    });
                });

            if !self.status.is_empty() {
                ui.add_space(10.0);
                ui.colored_label(egui::Color32::from_rgb(110, 110, 110), &self.status);
            }
            if !self.font_diag.is_empty() {
                ui.add_space(6.0);
                ui.colored_label(egui::Color32::from_rgb(90, 90, 90), &self.font_diag);
            }
        });
    }
}

/// 设置应用主题与控件样式
fn apply_theme(ctx: &egui::Context) {
    let mut visuals = egui::Visuals::light();
    visuals.override_text_color = Some(egui::Color32::from_rgb(24, 24, 24));
    visuals.widgets.noninteractive.bg_fill = egui::Color32::from_rgb(250, 250, 250);
    visuals.widgets.inactive.bg_fill = egui::Color32::from_rgb(246, 246, 246);
    visuals.widgets.hovered.bg_fill = egui::Color32::from_rgb(238, 242, 246);
    visuals.widgets.active.bg_fill = egui::Color32::from_rgb(228, 235, 242);
    visuals.widgets.inactive.fg_stroke.color = egui::Color32::from_rgb(36, 36, 36);
    visuals.widgets.inactive.bg_stroke.color = egui::Color32::from_rgb(222, 222, 222);
    visuals.widgets.hovered.bg_stroke.color = egui::Color32::from_rgb(200, 210, 220);
    visuals.widgets.active.bg_stroke.color = egui::Color32::from_rgb(190, 205, 220);
    visuals.widgets.inactive.rounding = egui::Rounding::same(8.0);
    visuals.widgets.hovered.rounding = egui::Rounding::same(8.0);
    visuals.widgets.active.rounding = egui::Rounding::same(8.0);
    visuals.window_rounding = egui::Rounding::same(12.0);
    visuals.window_fill = egui::Color32::from_rgb(252, 252, 252);
    ctx.set_visuals(visuals);

    let mut style = (*ctx.style()).clone();
    style.spacing.item_spacing = egui::vec2(10.0, 10.0);
    style.spacing.button_padding = egui::vec2(12.0, 7.0);
    style.spacing.text_edit_width = 380.0;
    style.visuals.widgets.hovered.fg_stroke.color = egui::Color32::from_rgb(16, 16, 16);
    ctx.set_style(style);
}

/// 应用中文字体，避免输入中文显示方块
fn apply_fonts(ctx: &egui::Context) {
    let mut fonts = egui::FontDefinitions::default();
    // 仅使用内置字体，避免系统字体解析异常导致崩溃
    if let Some((name, data)) = load_builtin_font() {
        // 内置字体作为最终兜底，避免系统字体缺失导致乱码
        fonts.font_data.insert(name.clone(), data);
        if let Some(family) = fonts.families.get_mut(&egui::FontFamily::Proportional) {
            family.push(name.clone());
        }
        if let Some(family) = fonts.families.get_mut(&egui::FontFamily::Monospace) {
            family.push(name);
        }
    }
    ctx.set_fonts(fonts);
}

/// 从系统字体目录加载可用的中文字体集合
fn load_system_fonts() -> Vec<(String, egui::FontData)> {
    let candidates = [
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simfang.ttf",
        r"C:\Windows\Fonts\msyh.ttf",
        r"C:\Windows\Fonts\msyhl.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
    ];
    let mut fonts = Vec::new();
    for path in candidates {
        match fs::read(path) {
            Ok(bytes) => {
                let is_ttc = path.to_ascii_lowercase().ends_with(".ttc");
                if is_ttc {
                    // ttc 可能包含多个字体面，依次尝试前几个索引
                    for index in 0..4 {
                        let name = format!(
                            "sys_cn_{}_{}",
                            path.replace(['\\', ':', '.'], "_"),
                            index
                        );
                        let mut data = egui::FontData::from_owned(bytes.clone());
                        data.index = index;
                        fonts.push((name, data));
                    }
                } else {
                    let name = format!("sys_cn_{}", path.replace(['\\', ':', '.'], "_"));
                    fonts.push((name, egui::FontData::from_owned(bytes)));
                }
            }
            Err(err) => {
                // 如果读取失败则尝试下一个字体
                let _ = err;
            }
        }
    }
    fonts
}

/// 加载内置中文字体作为兜底
fn load_builtin_font() -> Option<(String, egui::FontData)> {
    let bytes = include_bytes!("../assets/爱点风雅黑.ttf").to_vec();
    if bytes.is_empty() {
        return None;
    }
    let name = "builtin_cn_aidian_fangyahei".to_string();
    Some((name, egui::FontData::from_owned(bytes)))
}

/// 构建字体诊断信息（检测中文字符是否可被当前字体渲染）
fn build_font_diag(ctx: &egui::Context) -> String {
    let sample = "中文测试";
    let (prop_ok, mono_ok) = ctx.fonts(|fonts| {
        let prop = fonts.has_glyphs(&egui::FontId::proportional(14.0), sample);
        let mono = fonts.has_glyphs(&egui::FontId::monospace(14.0), sample);
        (prop, mono)
    });
    format!("字体诊断：比例字体中文={}，等宽字体中文={}", prop_ok, mono_ok)
}
