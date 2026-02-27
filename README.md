# Folder Remark Rust 项目说明

## 项目框架
- 语言与版本：Rust 2024 Edition
- UI 框架：`eframe` / `egui`
- 主要模块：
  - `src/main.rs`：程序入口与 UI 渲染
  - `src/desktop_ini.rs`：读写 `desktop.ini` 备注
  - `src/config.rs`：配置读写
  - `src/lang.rs`：多语言文本
  - `src/bin/icongen.rs`：图标生成工具（如需）

## 运行
```bash
cargo run -- <目标文件夹路径>
```
示例：
```bash
cargo run -- "D:\demo\test-folder"
```

## 测试
当前项目的“测试”就是运行程序验证功能：
```bash
cargo run -- <目标文件夹路径>
```

## 打包
1. 生成 Release 可执行文件：
```bash
cargo build --release
```

2. 使用 Inno Setup 脚本打包（脚本位于 `installer/FolderRemark.iss`）
   - 确认脚本引用的可执行文件为：
     `target\release\folder-remark-rust.exe`
   - 在 Inno Setup 中编译 `FolderRemark.iss` 生成安装包
