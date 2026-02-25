//! 配置读写模块

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

/// 支持的语言
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum Language {
    #[serde(rename = "zh-CN")]
    ZhCn,
    #[serde(rename = "en-US")]
    EnUs,
}

/// 应用配置结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub language: Language,
    pub last_error: Option<String>,
}

impl Default for AppConfig {
    /// 默认配置：中文
    fn default() -> Self {
        Self {
            language: Language::EnUs,
            last_error: None,
        }
    }
}

impl AppConfig {
    /// 加载配置，不存在时返回默认值
    pub fn load_or_default() -> Self {
        let path = config_path();
        let content = fs::read_to_string(&path).ok();
        if let Some(text) = content {
            if let Ok(cfg) = serde_json::from_str::<AppConfig>(&text) {
                return cfg;
            }
        }
        AppConfig::default()
    }

    /// 保存配置到磁盘
    pub fn save(&self) -> Result<(), String> {
        let path = config_path();
        if let Some(dir) = path.parent() {
            fs::create_dir_all(dir).map_err(|e| e.to_string())?;
        }
        let text = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        fs::write(path, text).map_err(|e| e.to_string())
    }
}

/// 获取配置文件路径
fn config_path() -> PathBuf {
    let base = std::env::var_os("APPDATA")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    base.join("FolderRemark").join("config.json")
}
