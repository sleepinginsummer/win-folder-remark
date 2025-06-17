#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹备注工具 - 主程序
包含GUI界面和右键菜单安装/卸载功能
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import argparse

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from folder_remark import FolderRemarkGUI, FolderRemarkManager
    from installer import install_context_menu, uninstall_context_menu, check_installation
    from i18n import i18n, t, _
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

class MainApp:
    """主应用程序"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(t('main_title'))
        self.root.geometry("500x550")  # 增加高度以容纳语言选择器
        self.root.resizable(True, True)
        
        # 使用系统默认窗口样式
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置窗口图标
        try:
            # 如果有图标文件，可以在这里设置
            pass
        except:
            pass
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # 设置现代化样式
        self.setup_modern_style()
        
        # 语言选择器框架 - 放在右上角
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=0, column=0, sticky=(tk.E), pady=(0, 10))
        
        ttk.Label(lang_frame, text=t('language_label'), 
                 style='Section.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        
        # 语言选择器 - 使用语言名称作为显示值
        language_names = i18n.get_available_languages()
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var,
                                     values=list(language_names.values()),
                                     state='readonly', width=8)
        language_combo.pack(side=tk.LEFT)
        
        # 设置当前选中的语言
        current_lang_name = language_names[i18n.get_language()]
        self.language_var.set(current_lang_name)
        
        # 绑定语言切换事件
        language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # 标题
        self.title_label = ttk.Label(main_frame, text="📝 " + t('main_title'), 
                               style='Title.TLabel')
        self.title_label.grid(row=1, column=0, pady=(0, 20))
        
        # 描述
        self.desc_label = ttk.Label(main_frame, 
                              text=t('main_description'),
                              style='Section.TLabel')
        self.desc_label.grid(row=2, column=0, pady=(0, 30))
        
        # 检查安装状态
        self.status_var = tk.StringVar()
        self.update_status()
        
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                style='Status.TLabel')
        self.status_label.grid(row=3, column=0, pady=(0, 20))
        
        # 按钮框架
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.grid(row=4, column=0, pady=10)
        
        # 主要功能按钮
        self.install_btn = ttk.Button(self.button_frame, text=t('btn_install'), 
                  command=self.install_context_menu,
                  style='Success.TButton')
        self.install_btn.pack(pady=5, fill=tk.X)
        
        self.uninstall_btn = ttk.Button(self.button_frame, text=t('btn_uninstall'), 
                  command=self.uninstall_context_menu,
                  style='Danger.TButton')
        self.uninstall_btn.pack(pady=5, fill=tk.X)
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=20)
        
        # 帮助信息
        self.help_label = ttk.Label(main_frame, text=t('help_text'),
                              style='Tip.TLabel',
                              justify=tk.LEFT)
        self.help_label.grid(row=6, column=0, pady=10, sticky=tk.W)
        
        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=7, column=0, pady=20)
        
        self.exit_btn = ttk.Button(bottom_frame, text=t('btn_exit'), 
                  command=self.on_closing,
                  style='Tool.TButton')
        self.exit_btn.pack()
    
    def setup_modern_style(self):
        """设置简洁的原生样式"""
        style = ttk.Style()
        
        # 使用系统默认主题
        try:
            style.theme_use('default')
        except:
            pass
        
        # 简洁的按钮样式 - 仅设置字体和间距
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11),
                       padding=(20, 10))
        
        style.configure('Success.TButton',
                       font=('Segoe UI', 10),
                       padding=(15, 8))
        
        style.configure('Danger.TButton',
                       font=('Segoe UI', 10),
                       padding=(15, 8))
        
        style.configure('Tool.TButton',
                       font=('Segoe UI', 9),
                       padding=(12, 6))
        
        # 简洁的标签样式
        style.configure('Title.TLabel',
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Section.TLabel',
                       font=('Segoe UI', 10))
        
        style.configure('Tip.TLabel',
                       font=('Segoe UI', 9))
        
        style.configure('Status.TLabel',
                       font=('Segoe UI', 10, 'bold'))
    
    def on_language_change(self, event=None):
        """语言切换事件处理"""
        combo = event.widget
        selected_name = combo.get()
        
        # 根据显示名称找到语言代码
        language_names = i18n.get_available_languages()
        selected_lang = None
        for code, name in language_names.items():
            if name == selected_name:
                selected_lang = code
                break
        
        if selected_lang and selected_lang != i18n.get_language():
            i18n.set_language(selected_lang)
            self.update_ui_text()
    
    def update_ui_text(self):
        """更新界面文本"""
        # 更新窗口标题
        self.root.title(t('main_title'))
        
        # 更新标签文本
        self.title_label.config(text="📝 " + t('main_title'))
        self.desc_label.config(text=t('main_description'))
        self.help_label.config(text=t('help_text'))
        
        # 更新按钮文本
        self.install_btn.config(text=t('btn_install'))
        self.uninstall_btn.config(text=t('btn_uninstall'))
        self.exit_btn.config(text=t('btn_exit'))
        
        # 更新状态
        self.update_status()
    
    def update_status(self):
        """更新安装状态"""
        if check_installation():
            self.status_var.set(t('status_installed'))
        else:
            self.status_var.set(t('status_not_installed'))
    
    def open_remark_tool(self):
        """打开备注工具"""
        try:
            # 隐藏主窗口
            self.root.withdraw()
            
            # 打开备注工具（创建独立的实例，避免样式干扰）
            app = FolderRemarkGUI()
            app.run()
            
            # 备注工具关闭后显示主窗口
            self.root.deiconify()
            
            # 重新设置主界面样式（防止被备注工具影响）
            self.setup_modern_style()
            
            self.update_status()
        except Exception as e:
            messagebox.showerror(t('msg_error'), t('error_open_failed', str(e)))
    
    def install_context_menu(self):
        """安装右键菜单"""
        try:
            if check_installation():
                messagebox.showinfo(t('msg_info'), t('msg_already_installed'))
                return
            
            result = messagebox.askyesno(t('msg_confirm'), t('msg_install_confirm'))
            
            if result:
                success = install_context_menu()
                if success:
                    messagebox.showinfo(t('msg_info'), t('msg_install_success'))
                    self.update_status()
                else:
                    messagebox.showerror(t('msg_install_failed'), "❌ 右键菜单安装失败！\n\n请确保以管理员身份运行此程序")
        except Exception as e:
            messagebox.showerror(t('msg_error'), f"安装过程出错: {str(e)}")
    
    def uninstall_context_menu(self):
        """卸载右键菜单"""
        try:
            if not check_installation():
                messagebox.showinfo(t('msg_info'), "右键菜单未安装")
                return
            
            result = messagebox.askyesno(t('msg_confirm_uninstall'), t('msg_uninstall_confirm'))
            
            if result:
                success = uninstall_context_menu()
                if success:
                    messagebox.showinfo(t('msg_info'), t('msg_uninstall_success'))
                    self.update_status()
                else:
                    messagebox.showerror(t('msg_uninstall_failed'), "❌ 右键菜单卸载失败！\n\n请确保以管理员身份运行此程序")
        except Exception as e:
            messagebox.showerror(t('msg_error'), f"卸载过程出错: {str(e)}")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 销毁窗口并退出程序
            self.root.quit()      # 退出mainloop
            self.root.destroy()   # 销毁窗口
            
            # 强制退出程序（确保进程完全结束）
            import sys
            sys.exit(0)
            
        except Exception as e:
            # 如果正常关闭失败，强制退出
            import os
            os._exit(0)
    
    def run(self):
        """运行应用程序"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            print(f"程序运行出错: {e}")
            self.on_closing()

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="文件夹备注工具")
    parser.add_argument("folder_path", nargs="?", help="要添加备注的文件夹路径")
    parser.add_argument("--install", action="store_true", help="安装右键菜单")
    parser.add_argument("--uninstall", action="store_true", help="卸载右键菜单")
    
    args = parser.parse_args()
    
    # 处理命令行参数
    if args.install:
        success = install_context_menu()
        sys.exit(0 if success else 1)
    elif args.uninstall:
        success = uninstall_context_menu()
        sys.exit(0 if success else 1)
    elif args.folder_path:
        # 直接打开指定文件夹的备注工具
        app = FolderRemarkGUI(folder_path=args.folder_path)
        app.run()
    else:
        # 打开主界面
        app = MainApp()
        app.run()

if __name__ == "__main__":
    main()
