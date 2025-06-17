#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件脚本
生成包含安装和卸载右键菜单功能的exe文件
"""

import os
import subprocess
import sys
import shutil

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("🔧 正在安装PyInstaller...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller安装失败: {e}")
        return False

def create_main_exe_script():
    """检查主exe脚本是否存在（现在直接使用现有的main.py）"""
    if os.path.exists("main.py"):
        print("✅ 发现现有的main.py文件，将直接使用")
        return True
    
    print("❌ 找不到main.py文件")
    return False

def build_exe():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 生成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=文件夹备注工具",  # exe文件名
        "--add-data=folder_remark.py;.",  # 包含依赖文件
        "--add-data=installer.py;.",
        "--add-data=i18n.py;.",  # 包含国际化模块
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=configparser",
        "--hidden-import=subprocess",
        "--hidden-import=winreg",
        "--hidden-import=ctypes",
        "--hidden-import=datetime",
        "--hidden-import=json",  # i18n模块需要json
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 可执行文件构建成功！")
        
        # 检查生成的文件
        exe_path = os.path.join("dist", "文件夹备注工具.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📁 生成的exe文件: {exe_path}")
            print(f"📊 文件大小: {file_size:.1f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_installer_script():
    """创建安装脚本"""
    installer_content = '''@echo off
chcp 65001 >nul
title 文件夹备注工具 - 安装程序

echo.
echo ==========================================
echo    文件夹备注工具 - 安装程序
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 检测到管理员权限，继续安装...
    echo.
) else (
    echo ❌ 需要管理员权限才能安装右键菜单！
    echo.
    echo 🔧 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

REM 运行安装
echo 🚀 正在安装右键菜单...
"文件夹备注工具.exe" --install

echo.
echo 📋 安装完成！按任意键退出...
pause >nul
'''
    
    with open("安装右键菜单.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    
    print("✅ 已创建安装脚本: 安装右键菜单.bat")

def create_uninstaller_script():
    """创建卸载脚本"""
    uninstaller_content = '''@echo off
chcp 65001 >nul
title 文件夹备注工具 - 卸载程序

echo.
echo ==========================================
echo    文件夹备注工具 - 卸载程序
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 检测到管理员权限，继续卸载...
    echo.
) else (
    echo ❌ 需要管理员权限才能卸载右键菜单！
    echo.
    echo 🔧 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

REM 运行卸载
echo 🗑️ 正在卸载右键菜单...
"文件夹备注工具.exe" --uninstall

echo.
echo 📋 卸载完成！按任意键退出...
pause >nul
'''
    
    with open("卸载右键菜单.bat", "w", encoding="utf-8") as f:
        f.write(uninstaller_content)
    
    print("✅ 已创建卸载脚本: 卸载右键菜单.bat")

def create_readme():
    """创建使用说明"""
    readme_content = '''# 文件夹备注工具 / Folder Remark Tool

## 功能介绍 / Features
为Windows文件夹添加备注信息，鼠标悬停在文件夹上即可查看备注内容。
Add remark information to Windows folders, viewable on hover.

## 语言支持 / Language Support
- 支持中文简体和英文界面切换
- Support Chinese Simplified and English interface switching
- 在程序右上角可选择语言 / Language selector in top-right corner

## 使用方法 / Usage

### 方法一：使用GUI界面 / Method 1: GUI Interface
1. 双击运行 `文件夹备注工具.exe` / Double-click `文件夹备注工具.exe`
2. 在主界面中选择相应功能 / Select desired function in main interface
3. 右上角可切换中英文界面 / Switch language in top-right corner

### 方法二：安装右键菜单 / Method 2: Install Context Menu
1. 右键点击 `安装右键菜单.bat`，选择"以管理员身份运行"
   Right-click `安装右键菜单.bat`, select "Run as administrator"
2. 安装完成后，在任意文件夹上右键选择"📝 添加文件夹备注"
   After installation, right-click any folder and select "📝 Add Folder Remark"

### 方法三：命令行使用 / Method 3: Command Line
```
文件夹备注工具.exe [文件夹路径]     # 直接打开指定文件夹的备注编辑
文件夹备注工具.exe --install      # 安装右键菜单
文件夹备注工具.exe --uninstall    # 卸载右键菜单
```

## 卸载方法 / Uninstallation
1. 右键点击 `卸载右键菜单.bat`，选择"以管理员身份运行"
   Right-click `卸载右键菜单.bat`, select "Run as administrator"
2. 或在主界面中点击"卸载右键菜单"按钮
   Or click "Uninstall Context Menu" button in main interface

## 注意事项 / Notes
- 安装/卸载右键菜单需要管理员权限 / Administrator privileges required for context menu installation/uninstallation
- 备注信息保存在文件夹的desktop.ini文件中 / Remarks are saved in folder's desktop.ini file
- 备注会随文件夹一起移动，不会丢失 / Remarks move with folders and won't be lost
- 支持中文和特殊字符 / Supports Chinese and special characters
- 语言设置会自动保存 / Language preference is automatically saved

## 技术支持 / Technical Support
如有问题，请检查 / If you encounter issues, please check:
1. 是否以管理员身份运行安装程序 / Whether installer is run as administrator
2. 杀毒软件是否阻止了程序运行 / Whether antivirus software is blocking the program
3. Windows版本是否支持（支持Windows 7及以上版本） / Windows version compatibility (Windows 7 and above)
'''
    
    with open("使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 已创建使用说明: 使用说明.txt")

def main():
    """主函数"""
    print("🚀 文件夹备注工具 - 可执行文件构建器")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，构建失败")
            return
    
    # 检查主程序文件是否存在
    if not create_main_exe_script():
        print("❌ 缺少main.py文件，无法构建")
        return
    
    # 构建exe文件
    if build_exe():
        print("\n🎉 构建完成！")
        print("\n📦 生成的文件:")
        print("  - dist/文件夹备注工具.exe  (主程序)")
        
        print("\n💡 使用方法:")
        print("  1. 双击exe文件直接使用")
        print("  2. 在主界面中可以安装/卸载右键菜单")
        print("  3. 命令行使用: 文件夹备注工具.exe --install/--uninstall")
    else:
        print("❌ 构建失败")

if __name__ == "__main__":
    main() 