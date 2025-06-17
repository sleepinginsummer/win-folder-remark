# 文件夹备注工具 / Folder Remark Tool

一个为 Windows 文件夹添加备注信息的实用工具，支持中英文界面。

A practical tool for adding remark information to Windows folders with Chinese and English interface support.

## 功能特色 / Features

### 中文
- 🏷️ **文件夹备注** - 为任意文件夹添加备注信息，鼠标悬停即可查看
- 🎯 **右键菜单集成** - 安装后可直接通过文件夹右键菜单快速添加备注
- 🌍 **多语言支持** - 支持中文简体和英文界面切换
- 💾 **原生存储** - 基于 Windows desktop.ini 文件，无需额外数据库
- 🎨 **现代化界面** - 美观的图形用户界面，操作简单直观
- 🔧 **系统集成** - 深度集成 Windows 资源管理器
- 📋 **操作日志** - 详细的操作日志，便于问题排查

### English
- 🏷️ **Folder Remarks** - Add remark information to any folder, viewable on hover
- 🎯 **Context Menu Integration** - Quick access through folder right-click menu after installation
- 🌍 **Multi-language Support** - Switch between Simplified Chinese and English interfaces
- 💾 **Native Storage** - Based on Windows desktop.ini files, no additional database required
- 🎨 **Modern Interface** - Beautiful graphical user interface with intuitive operation
- 🔧 **System Integration** - Deep integration with Windows File Explorer
- 📋 **Operation Log** - Detailed operation logs for troubleshooting

## 系统要求 / System Requirements

- Windows 10/11
- Python 3.7+
- Tkinter (通常随 Python 一起安装 / Usually installed with Python)

## 安装方法 / Installation

### 方法一：使用打包版本 / Method 1: Using Packaged Version

1. 下载最新的 `.exe` 文件 / Download the latest `.exe` file
2. 运行 `build.exe` / Run `build.exe`
3. 点击"安装右键菜单" / Click "Install Context Menu"

### 方法二：从源码运行 / Method 2: Running from Source

```bash
# 克隆仓库 / Clone repository
git clone <repository-url>
cd folder_remark

# 安装依赖（如需要） / Install dependencies (if needed)
pip install -r requirements.txt

# 运行主程序 / Run main program
python main.py
```

## 使用说明 / Usage Instructions

### 中文使用说明

#### 1. 安装右键菜单
- 运行 exe
- 在右上角选择您偏好的语言
- 点击"📥 安装右键菜单"按钮
- 授予管理员权限（如果需要）

#### 2. 添加文件夹备注
**方法一：通过右键菜单**
- 右键点击任意文件夹
- 选择"📝 添加文件夹备注"
- 在打开的窗口中输入备注内容
- 点击"💾 保存备注"

**方法二：通过主界面**
- 运行主程序
- 点击"🚀 打开备注工具"
- 选择文件夹路径
- 输入备注内容并保存

#### 3. 查看备注
- 在文件管理器中，将鼠标悬停在有备注的文件夹上
- 备注内容将显示在提示框中

#### 4. 管理备注
- 修改备注：重新打开备注工具，编辑内容后保存
- 删除备注：在备注工具中点击"🗑 删除备注"

### English Usage Instructions

#### 1. Install Context Menu
- Run exe
- Select your preferred language in the top-right corner
- Click the "📥 Install Context Menu" button
- Grant administrator privileges if prompted

#### 2. Add Folder Remarks
**Method 1: Through Context Menu**
- Right-click on any folder
- Select "📝 Add Folder Remark"
- Enter remark content in the opened window
- Click "💾 Save Remark"

**Method 2: Through Main Interface**
- Run the main program
- Click "🚀 Open Remark Tool"
- Select folder path
- Enter remark content and save

#### 3. View Remarks
- In File Explorer, hover your mouse over folders with remarks
- Remark content will be displayed in a tooltip

#### 4. Manage Remarks
- Edit remarks: Reopen the remark tool, edit content and save
- Delete remarks: Click "🗑 Delete Remark" in the remark tool

## 构建可执行文件 / Building Executable

使用 PyInstaller 构建独立的可执行文件：

Use PyInstaller to build standalone executable files:

```bash
# 安装 PyInstaller / Install PyInstaller
pip install pyinstaller

# 构建主程序 / Build main program
python build_exe.py

# 生成的文件在 dist 目录中 / Generated files are in the dist directory
```

## 文件结构 / File Structure

```
folder_remark/
├── main.py                 # 主界面程序 / Main interface program
├── folder_remark.py        # 备注工具核心 / Remark tool core
├── installer.py            # 右键菜单安装器 / Context menu installer
├── i18n.py                 # 国际化模块 / Internationalization module
├── build_exe.py            # 构建脚本 / Build script
├── requirements.txt        # 依赖列表 / Dependencies list
└── README.md              # 说明文档 / Documentation
```

## 技术原理 / Technical Principles

### 中文
本工具基于 Windows 的 `desktop.ini` 文件机制工作：

1. **存储机制**：备注信息存储在文件夹的 `desktop.ini` 文件中的 `InfoTip` 字段
2. **显示机制**：Windows 资源管理器原生支持读取 `InfoTip` 并在鼠标悬停时显示
3. **文件属性**：自动设置 `desktop.ini` 为隐藏+系统文件，文件夹为系统文件夹
4. **编码格式**：使用 UTF-16 编码确保中文等字符正确显示

### English
This tool works based on Windows' `desktop.ini` file mechanism:

1. **Storage Mechanism**: Remark information is stored in the `InfoTip` field of the folder's `desktop.ini` file
2. **Display Mechanism**: Windows File Explorer natively supports reading `InfoTip` and displaying it on hover
3. **File Attributes**: Automatically sets `desktop.ini` as hidden+system file, and folder as system folder
4. **Encoding Format**: Uses UTF-16 encoding to ensure proper display of Chinese and other characters

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

#### 备注不显示 / Remarks Not Showing

**中文解决方案：**
1. 按 F5 刷新文件夹
2. 使用工具中的"🔄 重启资源管理器"功能
3. 重新打开文件管理器窗口
4. 检查 `desktop.ini` 文件是否存在且有正确的属性

**English Solutions:**
1. Press F5 to refresh the folder
2. Use the "🔄 Restart Explorer" function in the tool
3. Reopen File Explorer window
4. Check if `desktop.ini` file exists with correct attributes

#### 权限问题 / Permission Issues

**中文解决方案：**
- 以管理员身份运行程序
- 检查文件夹是否有写入权限
- 确保不在系统保护的目录中操作

**English Solutions:**
- Run the program as administrator
- Check if the folder has write permissions
- Ensure not operating in system-protected directories

#### 右键菜单未出现 / Context Menu Not Appearing

**中文解决方案：**
1. 确认安装过程中授予了管理员权限
2. 重新安装右键菜单
3. 重启 Windows 资源管理器
4. 检查注册表项是否正确创建

**English Solutions:**
1. Confirm administrator privileges were granted during installation
2. Reinstall the context menu
3. Restart Windows Explorer
4. Check if registry entries were created correctly

## 更新日志 / Changelog

### v1.0.0
- ✨ 初始版本发布 / Initial release
- 🌍 添加多语言支持 / Added multi-language support
- 🎨 现代化界面设计 / Modern interface design
- 🔧 完整的右键菜单集成 / Complete context menu integration

## 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

Welcome to submit Issues and Pull Requests!

### 开发指南 / Development Guidelines

1. Fork 项目 / Fork the project
2. 创建功能分支 / Create feature branch (`git checkout -b feature/AmazingFeature`)
3. 提交更改 / Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 / Push to branch (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request / Open a Pull Request

## 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**注意 / Note**: 本工具仅修改文件夹的 `desktop.ini` 文件，不会影响文件夹内的其他文件或系统稳定性。/ This tool only modifies the folder's `desktop.ini` file and will not affect other files in the folder or system stability. 