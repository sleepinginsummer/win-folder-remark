#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows右键菜单安装器 - 文件夹备注工具
用于安装和卸载文件夹备注功能到右键菜单
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path

# 添加当前目录到Python路径以导入i18n模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from i18n import i18n, t, _
except ImportError:
    # 如果导入失败，创建一个简单的备用函数
    def t(key, *args):
        return key
    def _(key, *args):
        return key

def get_python_executable():
    """获取Python可执行文件路径"""
    return sys.executable

def get_script_path():
    """获取脚本路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查是否在exe环境中运行
    if getattr(sys, 'frozen', False):
        # 在exe环境中，返回exe文件路径
        return sys.executable
    else:
        # 在开发环境中，返回Python脚本路径
        return os.path.join(current_dir, 'folder_remark.py')



def install_context_menu():
    """安装右键菜单"""
    try:
        python_exe = get_python_executable()
        script_path = get_script_path()
        
        # 检查文件是否存在
        if not os.path.exists(script_path):
            print(f"❌ 错误: 找不到脚本文件 {script_path}")
            return False
        
        # 注册表路径
        reg_path = r"Directory\shell\FolderRemark"
        reg_command_path = r"Directory\shell\FolderRemark\command"
        
        # 创建主菜单项 - 使用系统编辑相关图标
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, reg_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, t('installer_menu_text'))
            # 使用系统图标 - 编辑相关的图标选项：
            # shell32.dll,70  - 记事本/编辑图标
            # shell32.dll,269 - 编辑/铅笔图标 
            # shell32.dll,134 - 文档编辑图标
            # shell32.dll,1   - 文件图标
            # imageres.dll,5  - 文档编辑图标
            # imageres.dll,247 - 编辑图标
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "shell32.dll,269")  # 编辑/铅笔图标
        
        # 创建命令 - 使用pythonw.exe隐藏控制台窗口
        if getattr(sys, 'frozen', False):
            # 在exe环境中，直接使用exe文件
            command = f'"{script_path}" "%1"'
        else:
            # 在开发环境中，使用Python解释器
            pythonw_exe = python_exe.replace('python.exe', 'pythonw.exe')
            if not os.path.exists(pythonw_exe):
                pythonw_exe = python_exe  # 如果找不到pythonw.exe，回退到python.exe
            command = f'"{pythonw_exe}" "{script_path}" "%1"'
        
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, reg_command_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
        
        print(t('installer_success'))
        print(t('installer_success_detail'))
        print("💡 备注将通过desktop.ini文件存储，鼠标悬停在文件夹上即可查看。")
        return True
        
    except PermissionError:
        print("❌ 权限不足！请以管理员身份运行此程序。")
        print("\n🔧 解决方法：")
        print("1. 按 Win+R 打开运行对话框")
        print("2. 输入 'cmd' 并按 Ctrl+Shift+Enter 以管理员身份打开")
        print("3. 切换到程序目录并重新运行安装命令")
        print(f"4. 或者运行: python \"{get_script_path()}\" --install")
        return False
    except Exception as e:
        print(f"❌ 安装失败: {str(e)}")
        return False

def uninstall_context_menu():
    """卸载右键菜单"""
    try:
        reg_path = r"Directory\shell\FolderRemark"
        
        # 删除注册表项
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\FolderRemark\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, reg_path)
            print(t('installer_uninstall_success'))
            print(t('installer_uninstall_detail'))
            return True
        except FileNotFoundError:
            print("⚠️  右键菜单未安装或已被删除。")
            return True
            
    except PermissionError:
        print("❌ 权限不足！请以管理员身份运行此程序。")
        print("\n🔧 解决方法：")
        print("1. 按 Win+R 打开运行对话框")
        print("2. 输入 'cmd' 并按 Ctrl+Shift+Enter 以管理员身份打开")
        print("3. 切换到程序目录并重新运行卸载命令")
        return False
    except Exception as e:
        print(f"❌ 卸载失败: {str(e)}")
        return False

def check_installation():
    """检查是否已安装"""
    try:
        reg_path = r"Directory\shell\FolderRemark"
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, reg_path):
            return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def create_batch_installer():
    """创建批处理安装文件"""
    python_exe = get_python_executable()
    script_path = get_script_path()
    
    batch_content = f'''@echo off
chcp 65001 >nul
title 文件夹备注工具 - 安装程序

echo.
echo ==========================================
echo    文件夹备注工具 - 右键菜单安装程序
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

REM 运行Python安装脚本
echo 🚀 正在安装右键菜单...
"{python_exe}" "{script_path}" --install

echo.
echo 📋 安装完成！按任意键退出...
pause >nul
'''
    
    batch_path = "安装右键菜单.bat"
    try:
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ 已创建批处理安装文件: {batch_path}")
        print("💡 您可以右键点击此文件，选择'以管理员身份运行'来安装右键菜单。")
        return True
    except Exception as e:
        print(f"❌ 创建批处理文件失败: {e}")
        return False

def create_batch_uninstaller():
    """创建批处理卸载文件"""
    python_exe = get_python_executable()
    script_path = get_script_path()
    
    batch_content = f'''@echo off
chcp 65001 >nul
title 文件夹备注工具 - 卸载程序

echo.
echo ==========================================
echo    文件夹备注工具 - 右键菜单卸载程序
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

REM 运行Python卸载脚本
echo 🗑️ 正在卸载右键菜单...
"{python_exe}" "{script_path}" --uninstall

echo.
echo 📋 卸载完成！按任意键退出...
pause >nul
'''
    
    batch_path = "卸载右键菜单.bat"
    try:
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ 已创建批处理卸载文件: {batch_path}")
        return True
    except Exception as e:
        print(f"❌ 创建批处理文件失败: {e}")
        return False

def show_help():
    """显示帮助信息"""
    print("📝 文件夹备注工具 - 右键菜单安装器")
    print("=" * 50)
    print()
    
    # 检查当前安装状态
    if check_installation():
        print("✅ 右键菜单已安装")
    else:
        print("❌ 右键菜单未安装")
    
    print()
    print("🔧 使用方法:")
    print("  python installer.py install    - 安装右键菜单")
    print("  python installer.py uninstall  - 卸载右键菜单")
    print("  python installer.py batch      - 创建批处理安装/卸载文件")
    print("  python installer.py help       - 显示此帮助信息")
    print()
    print("💡 功能说明:")
    print("  • 安装后可在文件夹右键菜单中看到'📝 添加文件夹备注'选项")
    print("  • 备注信息存储在文件夹的desktop.ini文件中")
    print("  • 鼠标悬停在文件夹上即可查看备注内容")
    print("  • 备注会随文件夹一起移动，不会丢失")
    print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        
        print("请选择操作:")
        print("1. 安装右键菜单")
        print("2. 卸载右键菜单") 
        print("3. 创建批处理文件")
        print("4. 退出")
        
        while True:
            try:
                choice = input("\n请输入选项 (1-4): ").strip()
                
                if choice == '1':
                    install_context_menu()
                    break
                elif choice == '2':
                    uninstall_context_menu()
                    break
                elif choice == '3':
                    create_batch_installer()
                    create_batch_uninstaller()
                    break
                elif choice == '4':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效的选择，请输入1-4")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
    else:
        action = sys.argv[1].lower()
        if action == 'install':
            install_context_menu()
        elif action == 'uninstall':
            uninstall_context_menu()
        elif action == 'batch':
            create_batch_installer()
            create_batch_uninstaller()
        elif action == 'help':
            show_help()
        else:
            print(f"❌ 未知的操作: {action}")
            print("💡 使用 'python installer.py help' 查看帮助信息")

if __name__ == "__main__":
    main() 