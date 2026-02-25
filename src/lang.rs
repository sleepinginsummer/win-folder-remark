//! 语言文本管理

use crate::config::Language;

/// 语言包结构
#[derive(Clone)]
pub struct LangPack {
    pub title: String,
    pub remark_label: String,
    pub save_button: String,
    pub clear_button: String,
    pub save_success: String,
    pub save_failed: String,
    pub clear_success: String,
    pub clear_failed: String,
    pub save_config_failed: String,
}

impl LangPack {
    /// 创建语言包
    pub fn new(lang: Language) -> Self {
        let _ = lang;
        Self {
            title: "Folder Remark".to_string(),
            remark_label: "Remark:".to_string(),
            save_button: "Save".to_string(),
            clear_button: "Clear".to_string(),
            save_success: "Saved".to_string(),
            save_failed: "Save failed".to_string(),
            clear_success: "Cleared".to_string(),
            clear_failed: "Clear failed".to_string(),
            save_config_failed: "Save config failed".to_string(),
        }
    }
}
