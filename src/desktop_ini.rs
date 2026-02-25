//! desktop.ini 读写与属性处理

use std::fs;
use std::os::windows::ffi::OsStrExt;
use std::path::Path;
use windows::Win32::Storage::FileSystem::{
    GetFileAttributesW, SetFileAttributesW, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_READONLY,
    FILE_ATTRIBUTE_SYSTEM, INVALID_FILE_ATTRIBUTES,
};

/// desktop.ini 处理错误类型
#[derive(Debug)]
pub enum DesktopIniError {
    Io(String),
    Attr(String),
}

impl std::fmt::Display for DesktopIniError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DesktopIniError::Io(msg) => write!(f, "IO 错误: {}", msg),
            DesktopIniError::Attr(msg) => write!(f, "属性错误: {}", msg),
        }
    }
}

impl std::error::Error for DesktopIniError {}

/// 读取 desktop.ini 中的 InfoTip 备注
pub fn load_infotip(dir: &Path) -> Result<Option<String>, DesktopIniError> {
    let ini_path = dir.join("desktop.ini");
    if !ini_path.exists() {
        return Ok(None);
    }
    let content = read_utf16le(&ini_path).map_err(DesktopIniError::Io)?;
    Ok(extract_infotip(&content))
}

/// 写入 desktop.ini 的 InfoTip 备注
pub fn save_infotip(dir: &Path, value: &str) -> Result<(), DesktopIniError> {
    let ini_path = dir.join("desktop.ini");
    let content = if ini_path.exists() {
        read_utf16le(&ini_path).map_err(DesktopIniError::Io)?
    } else {
        String::new()
    };
    let text = update_infotip(&content, value);
    write_utf16le(&ini_path, &text).map_err(DesktopIniError::Io)?;

    set_file_attributes(
        &ini_path,
        FILE_ATTRIBUTE_HIDDEN.0 | FILE_ATTRIBUTE_SYSTEM.0,
    )?;
    set_folder_readonly(dir)?;

    Ok(())
}

/// 读取 UTF-16LE BOM 文本
fn read_utf16le(path: &Path) -> Result<String, String> {
    let bytes = fs::read(path).map_err(|e| e.to_string())?;
    if bytes.len() >= 2 && bytes[0] == 0xFF && bytes[1] == 0xFE {
        let utf16: Vec<u16> = bytes[2..]
            .chunks(2)
            .map(|c| u16::from_le_bytes([c[0], *c.get(1).unwrap_or(&0)]))
            .collect();
        String::from_utf16(&utf16).map_err(|e| e.to_string())
    } else {
        // 兼容非 UTF-16 的历史文件
        String::from_utf8(bytes).map_err(|e| e.to_string())
    }
}

/// 写入 UTF-16LE BOM 文本
fn write_utf16le(path: &Path, text: &str) -> Result<(), String> {
    let mut bytes = Vec::with_capacity(text.len() * 2 + 2);
    bytes.extend_from_slice(&[0xFF, 0xFE]);
    for code in text.encode_utf16() {
        bytes.extend_from_slice(&code.to_le_bytes());
    }
    fs::write(path, bytes).map_err(|e| e.to_string())
}

/// 设置文件属性（隐藏 + 系统）
fn set_file_attributes(path: &Path, attrs: u32) -> Result<(), DesktopIniError> {
    let wide = to_wide(path);
    unsafe {
        SetFileAttributesW(
            windows::core::PCWSTR(wide.as_ptr()),
            windows::Win32::Storage::FileSystem::FILE_FLAGS_AND_ATTRIBUTES(attrs),
        )
        .map_err(|_| DesktopIniError::Attr("设置文件属性失败".to_string()))?;
    }
    Ok(())
}

/// 设置目录为只读以触发系统读取 desktop.ini
fn set_folder_readonly(dir: &Path) -> Result<(), DesktopIniError> {
    let wide = to_wide(dir);
    unsafe {
        let current = GetFileAttributesW(windows::core::PCWSTR(wide.as_ptr()));
        if current == INVALID_FILE_ATTRIBUTES {
            return Err(DesktopIniError::Attr("读取目录属性失败".to_string()));
        }
        let new_attrs = current | FILE_ATTRIBUTE_READONLY.0;
        SetFileAttributesW(
            windows::core::PCWSTR(wide.as_ptr()),
            windows::Win32::Storage::FileSystem::FILE_FLAGS_AND_ATTRIBUTES(new_attrs),
        )
        .map_err(|_| DesktopIniError::Attr("设置目录只读失败".to_string()))?;
    }
    Ok(())
}

/// Windows 宽字符串转换
fn to_wide(path: &Path) -> Vec<u16> {
    let mut wide: Vec<u16> = path.as_os_str().encode_wide().collect();
    wide.push(0);
    wide
}

/// 提取 .ShellClassInfo 的 InfoTip 内容
fn extract_infotip(content: &str) -> Option<String> {
    let mut in_section = false;
    for line in content.lines() {
        let trimmed = line.trim();
        if is_section_header(trimmed) {
            in_section = is_shell_class_info(trimmed);
            continue;
        }
        if in_section {
            if let Some((key, value)) = split_key_value(trimmed) {
                if key.eq_ignore_ascii_case("InfoTip") {
                    return Some(unescape_value(value));
                }
            }
        }
    }
    None
}

/// 更新 InfoTip 字段并尽量保留原有内容
fn update_infotip(content: &str, value: &str) -> String {
    let mut out: Vec<String> = Vec::new();
    let mut in_section = false;
    let mut found_section = false;
    let mut updated = false;
    let escaped = escape_value(value);

    for line in content.lines() {
        let trimmed = line.trim();
        if is_section_header(trimmed) {
            if in_section && !updated {
                out.push(format!("InfoTip={}", escaped));
                updated = true;
            }
            in_section = is_shell_class_info(trimmed);
            if in_section {
                found_section = true;
            }
            out.push(line.to_string());
            continue;
        }
        if in_section {
            if let Some((key, _)) = split_key_value(trimmed) {
                if key.eq_ignore_ascii_case("InfoTip") {
                    out.push(format!("InfoTip={}", escaped));
                    updated = true;
                    continue;
                }
            }
        }
        out.push(line.to_string());
    }

    if found_section {
        if in_section && !updated {
            out.push(format!("InfoTip={}", escaped));
        }
    } else {
        if !out.is_empty() {
            out.push(String::new());
        }
        out.push("[.ShellClassInfo]".to_string());
        out.push(format!("InfoTip={}", escaped));
    }

    out.join("\r\n")
}

/// 判断是否为节标题
fn is_section_header(line: &str) -> bool {
    line.starts_with('[') && line.ends_with(']')
}

/// 判断是否为 .ShellClassInfo 节
fn is_shell_class_info(line: &str) -> bool {
    line.eq_ignore_ascii_case("[.ShellClassInfo]")
}

/// 拆分 key=value
fn split_key_value(line: &str) -> Option<(&str, &str)> {
    let mut parts = line.splitn(2, '=');
    let key = parts.next()?.trim();
    let value = parts.next()?.trim();
    if key.is_empty() {
        None
    } else {
        Some((key, value))
    }
}

/// 处理换行转义
fn escape_value(value: &str) -> String {
    value
        .replace("\r\n", "\\n")
        .replace('\n', "\\n")
        .replace('\r', "\\n")
}

/// 还原换行转义
fn unescape_value(value: &str) -> String {
    value.replace("\\n", "\n")
}
