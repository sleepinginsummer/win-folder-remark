#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows文件夹备注工具 - 基于desktop.ini实现
直接修改文件夹的desktop.ini文件来存储备注信息
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import argparse
import configparser
import subprocess
from pathlib import Path
import tempfile
import shutil
import datetime

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

class Logger:
    """日志记录器"""
    def __init__(self):
        self.log_text = None
        self.pending_logs = []  # 存储早期日志消息
    
    def set_text_widget(self, text_widget):
        """设置日志文本控件"""
        self.log_text = text_widget
        # 输出所有待处理的日志
        if self.pending_logs:
            for log_entry in self.pending_logs:
                try:
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, log_entry)
                    self.log_text.see(tk.END)
                    self.log_text.update_idletasks()
                except:
                    pass
            self.pending_logs.clear()  # 清空待处理日志
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        if self.log_text:
            try:
                # 在GUI中显示
                current_state = self.log_text.cget('state')
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)  # 自动滚动到底部
                # 强制刷新界面
                self.log_text.update_idletasks()
                # 恢复只读状态（如果原来是只读的）
                if current_state == tk.DISABLED:
                    self.log_text.config(state=tk.DISABLED)
            except Exception as e:
                # 如果GUI日志失败，回退到控制台
                print(t('error_gui_log_failed', e))
                print(f"{level}: {message}")
        else:
            # 如果GUI还没准备好，存储到待处理列表
            self.pending_logs.append(log_entry)
            # 同时在控制台输出
            print(f"{level}: {message}")
    
    def info(self, message):
        """信息日志"""
        self.log(message, "INFO")
    
    def success(self, message):
        """成功日志"""
        self.log(message, "✅ SUCCESS")
    
    def warning(self, message):
        """警告日志"""
        self.log(message, "⚠️ WARNING")
    
    def error(self, message):
        """错误日志"""
        self.log(message, "❌ ERROR")

# 创建全局日志器
logger = Logger()

class FolderRemarkManager:
    """文件夹备注管理器"""
    
    def __init__(self):
        pass
    
    def get_desktop_ini_path(self, folder_path):
        """获取desktop.ini文件路径"""
        return os.path.join(folder_path, "desktop.ini")
    
    def read_remark(self, folder_path):
        """读取文件夹备注"""
        if not os.path.exists(folder_path):
            return ""
        
        desktop_ini_path = self.get_desktop_ini_path(folder_path)
        
        if not os.path.exists(desktop_ini_path):
            return ""
        
        try:
            config = configparser.ConfigParser()
            config.read(desktop_ini_path, encoding='utf-16')
            
            if config.has_section('.ShellClassInfo'):
                return config.get('.ShellClassInfo', 'InfoTip', fallback='')
            
            return ""
        except Exception as e:
            logger.error(t('error_read_failed', e))
            return ""
    
    def write_remark(self, folder_path, remark):
        """写入文件夹备注"""
        if not os.path.exists(folder_path):
            raise Exception(t('error_folder_not_exist'))
        
        desktop_ini_path = self.get_desktop_ini_path(folder_path)
        
        # 读取现有配置
        config = configparser.ConfigParser()
        if os.path.exists(desktop_ini_path):
            try:
                config.read(desktop_ini_path, encoding='utf-16')
            except:
                pass  # 如果读取失败，使用空配置
        
        # 确保有.ShellClassInfo节
        if not config.has_section('.ShellClassInfo'):
            config.add_section('.ShellClassInfo')
        
        # 设置备注
        if remark.strip():
            config.set('.ShellClassInfo', 'InfoTip', remark.strip())
            logger.info(t('log_writing_remark', folder_path))
        else:
            # 如果备注为空，删除InfoTip
            if config.has_option('.ShellClassInfo', 'InfoTip'):
                config.remove_option('.ShellClassInfo', 'InfoTip')
            logger.info(t('log_clearing_remark', folder_path))
        
        # 写入文件前先处理权限问题
        if os.path.exists(desktop_ini_path):
            try:
                # 移除只读和隐藏属性，以便写入
                subprocess.run(['attrib', '-R', '-H', '-S', desktop_ini_path], 
                             check=False, capture_output=True)
                logger.info(t('log_file_attrs_removed'))
            except Exception as e:
                logger.warning(t('log_file_attrs_failed', e))
        
        # 使用UTF-16编码写入文件
        try:
            with open(desktop_ini_path, 'w', encoding='utf-16') as f:
                # UTF-16会自动添加BOM，不需要手动写入
                config.write(f, space_around_delimiters=False)
            logger.success(t('log_write_success'))
        except Exception as e:
            raise Exception(t('error_write_failed', e))
        
        try:
            # 设置文件属性
            self._set_file_attributes(folder_path, desktop_ini_path)
            logger.success(t('log_attrs_set'))
            
            # 刷新文件夹显示
            self._refresh_folder(folder_path)
            
        except Exception as e:
            raise Exception(t('error_attrs_failed', e))
    
    def delete_remark(self, folder_path):
        """删除文件夹备注"""
        desktop_ini_path = self.get_desktop_ini_path(folder_path)
        
        if not os.path.exists(desktop_ini_path):
            return True
        
        try:
            # 先移除文件属性以便操作
            subprocess.run(['attrib', '-R', '-H', '-S', desktop_ini_path], 
                         check=False, capture_output=True)
            logger.info(t('log_deleting_remark'))
            
            # 读取现有文件
            config = configparser.ConfigParser()
            config.read(desktop_ini_path, encoding='utf-16')
            
            # 只删除InfoTip选项，保留desktop.ini文件和其他设置
            if config.has_section('.ShellClassInfo'):
                if config.has_option('.ShellClassInfo', 'InfoTip'):
                    config.remove_option('.ShellClassInfo', 'InfoTip')
                    logger.info(t('log_infotip_removed'))
                else:
                    logger.info(t('log_no_infotip'))
            else:
                logger.info(t('log_no_shellclass'))
            
            # 始终保留desktop.ini文件，只写入更新后的配置
            with open(desktop_ini_path, 'w', encoding='utf-16') as f:
                # UTF-16会自动添加BOM，不需要手动写入
                config.write(f, space_around_delimiters=False)
            logger.info(t('log_desktop_updated'))
            
            # 重新设置文件属性
            self._set_file_attributes(folder_path, desktop_ini_path)
            
            # 刷新文件夹显示
            self._refresh_folder(folder_path)
            logger.success(t('log_delete_completed'))
            
            return True
            
        except Exception as e:
            raise Exception(t('error_delete_failed', e))
    
    def _set_file_attributes(self, folder_path, desktop_ini_path):
        """设置文件属性"""
        try:
            # 设置desktop.ini为隐藏+系统文件
            subprocess.run(['attrib', '+H', '+S', desktop_ini_path], 
                         check=False, capture_output=True)
            
            # 设置文件夹为系统文件夹（这样desktop.ini才会生效）
            subprocess.run(['attrib', '+S', folder_path], 
                         check=False, capture_output=True)
            logger.info(t('log_attrs_set_detailed'))
        except Exception as e:
            logger.warning(t('warning_attrs_failed', e))
    
    def _refresh_folder(self, folder_path):
        """刷新文件夹显示"""
        try:
            import ctypes
            import time
            
            # 关键方法: 使用SHCNE_ASSOCCHANGED强制刷新桌面和文件关联
            try:
                shell32 = ctypes.windll.shell32
                
                # 这个是最有效的方法 - 强制刷新整个桌面
                SHCNE_ASSOCCHANGED = 0x8000000
                shell32.SHChangeNotifyW(SHCNE_ASSOCCHANGED, 0, None, None)
                logger.info(t('log_desktop_refresh'))
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(t('warning_desktop_refresh_failed', e))
            
            # 方法1: 针对具体文件夹的刷新
            try:
                # 定义刷新常量
                SHCNE_UPDATEDIR = 0x00001000      # 目录内容已更改
                SHCNE_UPDATEITEM = 0x00002000     # 文件/文件夹属性已更改
                SHCNE_ATTRIBUTES = 0x00000800     # 属性已更改
                SHCNF_PATH = 0x0001               # 路径格式
                SHCNF_FLUSH = 0x1000              # 立即刷新
                
                shell32 = ctypes.windll.shell32
                
                # 通知文件夹属性更改
                shell32.SHChangeNotifyW(SHCNE_ATTRIBUTES, SHCNF_PATH | SHCNF_FLUSH, folder_path, None)
                
                # 通知目录内容更改
                shell32.SHChangeNotifyW(SHCNE_UPDATEDIR, SHCNF_PATH | SHCNF_FLUSH, folder_path, None)
                
                # 通知项目更新
                shell32.SHChangeNotifyW(SHCNE_UPDATEITEM, SHCNF_PATH | SHCNF_FLUSH, folder_path, None)
                
                logger.info(t('log_folder_refresh_sent'))
            except Exception as e:
                logger.warning(t('warning_folder_refresh_failed', e))
            
            # 方法2: 刷新桌面（如果文件夹在桌面上）
            try:
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                if folder_path.startswith(desktop_path):
                    # 刷新桌面
                    user32 = ctypes.windll.user32
                    user32.InvalidateRect(None, None, True)
                    logger.info(t('log_desktop_refreshed'))
            except Exception as e:
                logger.warning(t('warning_desktop_failed', e))
            
            # 方法3: 使用COM接口刷新资源管理器窗口
            try:
                import win32com.client
                shell = win32com.client.Dispatch("Shell.Application")
                
                # 刷新所有资源管理器窗口
                windows = shell.Windows()
                for window in windows:
                    try:
                        if hasattr(window, 'LocationURL') and window.LocationURL:
                            window_path = window.LocationURL.replace('file:///', '').replace('/', '\\')
                            if window_path.lower() == folder_path.lower():
                                window.Refresh()
                                logger.info(t('log_explorer_window_refreshed'))
                    except:
                        pass
                        
            except ImportError:
                logger.info(t('log_win32com_unavailable'))
            except Exception as e:
                logger.warning(t('warning_com_refresh_failed', e))
            
            # 方法4: 临时修改文件夹时间戳
            try:
                import time
                current_time = time.time()
                # 稍微修改时间戳来触发文件系统事件
                os.utime(folder_path, (current_time, current_time))
                logger.info(t('log_timestamp_updated'))
            except Exception as e:
                logger.warning(t('warning_timestamp_failed', e))
            
            # 方法5: 强制重绘桌面和所有窗口
            try:
                user32 = ctypes.windll.user32
                # 重绘所有窗口
                user32.RedrawWindow(None, None, None, 0x0001 | 0x0004)  # RDW_INVALIDATE | RDW_UPDATENOW
                logger.info(t('log_global_redraw'))
            except Exception as e:
                logger.warning(t('warning_redraw_failed', e))
                
        except Exception as e:
            logger.warning(t('warning_refresh_error', e))
        
        # 给用户一些手动刷新的提示
        logger.info(t('tip_refresh_manual'))
        logger.info(t('tip_press_f5'))
        logger.info(t('tip_reopen_explorer'))
        logger.info(t('tip_wait_update'))

class FolderRemarkGUI:
    """文件夹备注GUI界面"""
    
    def __init__(self, folder_path=None):
        self.manager = FolderRemarkManager()
        self.folder_path = folder_path
        
        self.root = tk.Tk()
        self.root.title(t('remark_title'))
        self.root.geometry("800x750")  # 增加高度以显示日志区域
        self.root.resizable(True, True)
        
        # 使用系统默认窗口样式
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap(default="folder.ico")
        except:
            pass
        
        # 配置现代化样式
        self.setup_modern_style()
        self.setup_ui()
        
        # 如果指定了文件夹路径，直接加载备注
        if self.folder_path:
            self.load_folder_remark()
    
    def setup_modern_style(self):
        """设置现代化样式"""
        style = ttk.Style()
        
        # 使用vista主题（Windows 10/11风格）
        try:
            available_themes = style.theme_names()
            if 'vista' in available_themes:
                style.theme_use('vista')
            elif 'winnative' in available_themes:
                style.theme_use('winnative')
            else:
                style.theme_use('default')
        except:
            pass
        
        # 统一的现代按钮样式 - 所有按钮使用完全相同的样式
        button_font = ('Segoe UI', 10, 'normal')  # 统一字体：10号，正常粗细
        button_padding = (18, 10)  # 统一内边距
        button_width = 14  # 统一宽度
        
        # 所有按钮使用相同的基础样式
        base_button_style = {
            'font': button_font,
            'padding': button_padding,
            'width': button_width
        }
        
        style.configure('Uniform.TButton', **base_button_style)
        
        # 主要操作按钮（保存）- 现在也使用统一样式
        style.configure('Primary.TButton', **base_button_style)
        
        # 危险操作按钮（删除）
        style.configure('Danger.TButton', **base_button_style)
        
        # 工具按钮
        style.configure('Tool.TButton', **base_button_style)
        
        # 浏览按钮 - 现在也使用统一的字体和padding
        style.configure('Browse.TButton',
                       font=button_font,  # 统一为10号字体
                       padding=button_padding)  # 统一内边距
        
        # 现代化输入框样式
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       padding=(12, 8),
                       relief='flat',
                       borderwidth=1)
        
        # 卡片样式框架
        style.configure('Card.TFrame',
                       relief='solid',
                       borderwidth=1,
                       background='#f8f9fa')
        
        # 标题样式
        style.configure('Title.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       foreground='#2c3e50',
                       background='#ffffff')
        
        # 章节标题样式
        style.configure('Section.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#34495e',
                       background='#f8f9fa')
        
        # 提示文字样式
        style.configure('Tip.TLabel',
                       font=('Segoe UI', 9),
                       foreground='#7f8c8d',
                       background='#f8f9fa')
        
        # 状态标签样式
        style.configure('Status.TLabel',
                       font=('Segoe UI', 10, 'bold'),
                       foreground='#27ae60')
    
    def setup_ui(self):
        """设置现代化用户界面"""
        # 设置窗口背景色
        self.root.configure(bg='#ffffff')
        
        # 创建主滚动框架
        main_canvas = tk.Canvas(self.root, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 主容器 - 居中布局
        main_container = tk.Frame(scrollable_frame, bg='#ffffff')
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # 语言选择器 - 放在右上角
        self.setup_language_selector(main_container)
     
        
        # 文件夹选择卡片 - 增强视觉效果
        path_card = ttk.Frame(main_container, style='Card.TFrame', padding="25")
        path_card.pack(fill=tk.X, pady=(0, 25))
        
        # 文件夹路径标签
        path_label = ttk.Label(path_card, text="📂 " + t('folder_path_label'), 
                              style='Section.TLabel')
        path_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 路径输入框架
        path_input_frame = tk.Frame(path_card, bg='#f8f9fa')
        path_input_frame.pack(fill=tk.X)
        
        # 创建StringVar并设置初始值
        initial_path = self.folder_path or ""
        self.path_var = tk.StringVar(value=initial_path)
        logger.info(t('log_pathvar_init', initial_path))
        
        # 创建Entry控件并绑定StringVar
        self.path_entry = ttk.Entry(path_input_frame, textvariable=self.path_var, 
                                   style='Modern.TEntry',
                                   font=('Segoe UI', 11))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        # 浏览按钮
        ttk.Button(path_input_frame, text=t('btn_browse'), 
                  command=self.browse_folder,
                  style='Browse.TButton').pack(side=tk.RIGHT)
        
        # 备注编辑卡片 - 增强视觉层次
        remark_card = ttk.Frame(main_container, style='Card.TFrame', padding="25")
        remark_card.pack(fill=tk.X, pady=(0, 25))
        
        # 备注内容标签
        remark_label = ttk.Label(remark_card, text="✏️ " + t('remark_content_label'), 
                                style='Section.TLabel')
        remark_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 文本编辑区域 - 现代化设计
        text_frame = tk.Frame(remark_card, bg='#f8f9fa')
        text_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 文本框边框
        text_border = tk.Frame(text_frame, bg='#bdc3c7', padx=1, pady=1)
        text_border.pack(fill=tk.X)
        
        self.remark_text = scrolledtext.ScrolledText(text_border, height=6, wrap=tk.WORD,
                                                    font=('Segoe UI', 11),
                                                    relief='flat',
                                                    borderwidth=0,
                                                    padx=12, pady=12)
        self.remark_text.pack(fill=tk.X)
        
        # 提示信息 - 增强可读性
        tip_frame = tk.Frame(remark_card, bg='#f8f9fa')
        tip_frame.pack(fill=tk.X)
        
        tip_icon = tk.Label(tip_frame, text="💡", 
                           font=('Segoe UI', 12),
                           bg='#f8f9fa')
        tip_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        tip_label = ttk.Label(tip_frame, 
                             text=t('help_text_tip'),
                             style='Tip.TLabel')
        tip_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 操作按钮区域 - 现代化布局
        action_frame = tk.Frame(main_container, bg='#ffffff')
        action_frame.pack(fill=tk.X, pady=(0, 30))
        
        # 按钮容器 - 居中对齐，统一间距
        button_container = tk.Frame(action_frame, bg='#ffffff')
        button_container.pack(anchor=tk.CENTER)
        
        # 按钮间距配置 - 统一样式
        button_padding = 8
        
        # 单行布局：四个按钮在同一行
        ttk.Button(button_container, text=t('btn_save'), 
                  command=self.save_remark, 
                  style='Primary.TButton').grid(row=0, column=0, 
                                               padx=(0, button_padding), 
                                               pady=0,
                                               sticky='ew')
        
        ttk.Button(button_container, text=t('btn_delete'), 
                  command=self.delete_remark,
                  style='Danger.TButton').grid(row=0, column=1, 
                                              padx=(0, button_padding), 
                                              pady=0,
                                              sticky='ew')
        
        ttk.Button(button_container, text=t('btn_restart_explorer'), 
                  command=self.restart_explorer,
                  style='Tool.TButton').grid(row=0, column=2, 
                                            padx=(0, button_padding), 
                                            pady=0,
                                            sticky='ew')
        
        ttk.Button(button_container, text=t('btn_exit'), 
                  command=self.on_closing,
                  style='Tool.TButton').grid(row=0, column=3, 
                                            padx=0, 
                                            pady=0,
                                            sticky='ew')
        
        # 配置按钮列权重，使所有按钮等宽
        for i in range(4):
            button_container.grid_columnconfigure(i, weight=1)
        
        # 日志区域卡片 - 现代化日志面板
        log_card = ttk.Frame(main_container, style='Card.TFrame', padding="25")
        log_card.pack(fill=tk.BOTH, expand=True)
        
        # 日志标题栏 - 增强视觉效果
        log_header = tk.Frame(log_card, bg='#f8f9fa')
        log_header.pack(fill=tk.X, pady=(0, 15))
        
        log_icon = tk.Label(log_header, text="📋", 
                           font=('Segoe UI', 12),
                           bg='#f8f9fa')
        log_icon.pack(side=tk.LEFT, padx=(0, 8))
        
        log_label = ttk.Label(log_header, text=t('log_label'), 
                             style='Section.TLabel')
        log_label.pack(side=tk.LEFT)
        
        # 清空按钮 - 使用统一的ttk按钮样式
        ttk.Button(log_header, text=t('btn_clear_log'), 
                  command=self.clear_log,
                  style='Tool.TButton').pack(side=tk.RIGHT)
        
        # 日志文本区域 - 现代化边框设计
        log_frame = tk.Frame(log_card, bg='#f8f9fa')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志边框
        log_border = tk.Frame(log_frame, bg='#bdc3c7', padx=1, pady=1)
        log_border.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_border, height=8, wrap=tk.WORD,
                                                 font=('Consolas', 9), 
                                                 state=tk.NORMAL,
                                                 relief='flat',
                                                 borderwidth=0,
                                                 bg='#2c3e50',
                                                 fg='#ecf0f1',
                                                 insertbackground='#ecf0f1',
                                                 padx=12, pady=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 设置日志器的文本控件
        logger.set_text_widget(self.log_text)
        
        # 欢迎消息
        logger.info(t('log_welcome'))
        logger.info(t('log_instruction'))
    
    def setup_language_selector(self, parent):
        """设置语言选择器"""
        # 语言选择框架 - 右上角
        lang_frame = tk.Frame(parent, bg='#ffffff')
        lang_frame.pack(anchor=tk.NE, pady=(0, 20))
        
        # 语言标签
        lang_label = ttk.Label(lang_frame, text=t('language_label'), 
                              font=('Segoe UI', 9), 
                              background='#ffffff')
        lang_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 语言选择下拉框
        try:
            self.language_var = tk.StringVar()
            self.language_combo = ttk.Combobox(
                lang_frame, 
                textvariable=self.language_var,
                values=['中文', 'English'],
                state='readonly',
                width=10,
                font=('Segoe UI', 9)
            )
            
            # 设置当前语言显示
            current_lang = i18n.get_language()
            if current_lang == 'zh_CN':
                self.language_var.set('中文')
            else:
                self.language_var.set('English')
            
            self.language_combo.pack(side=tk.LEFT)
            
            # 绑定语言切换事件
            self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
            
        except Exception as e:
            logger.error(f"语言选择器初始化失败: {e}")
    
    def on_language_change(self, event=None):
        """语言切换事件处理"""
        try:
            selected = self.language_var.get()
            
            # 根据选择设置语言
            if selected == '中文':
                new_lang = 'zh_CN'
            elif selected == 'English':
                new_lang = 'en_US'
            else:
                return
            
            # 只有在语言真正改变时才更新
            if new_lang != i18n.get_language():
                i18n.set_language(new_lang)
                logger.info(t('log_language_changed', selected))
                
                # 更新界面文本
                self.update_ui_text()
                
        except Exception as e:
            logger.error(f"语言切换失败: {e}")
    
    def update_ui_text(self):
        """更新界面文本"""
        try:
            # 更新窗口标题
            self.root.title(t('remark_title'))
            
            # 保存当前状态
            current_folder = self.path_var.get() if hasattr(self, 'path_var') else ""
            current_remark = self.remark_text.get(1.0, tk.END).strip() if hasattr(self, 'remark_text') else ""
            
            # 清除现有界面
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # 重新设置样式和界面
            self.setup_modern_style()
            self.setup_ui()
            
            # 恢复状态
            if current_folder and hasattr(self, 'path_var'):
                self.path_var.set(current_folder)
                self.folder_path = current_folder
                if hasattr(self, 'path_entry'):
                    self.path_entry.delete(0, tk.END)
                    self.path_entry.insert(0, current_folder)
            
            if current_remark and hasattr(self, 'remark_text'):
                self.remark_text.delete(1.0, tk.END)
                self.remark_text.insert(1.0, current_remark)
            
            logger.info(t('log_ui_updated'))
            
        except Exception as e:
            logger.error(f"界面文本更新失败: {e}")
    
    def browse_folder(self):
        """浏览文件夹"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title=t('folder_path_label'))
        if folder:
            logger.info(t('log_folder_selected', folder))
            
            # 多种方式设置路径，确保显示
            try:
                # 方法1: 直接设置StringVar
                self.path_var.set(folder)
                self.folder_path = folder
                
                # 方法2: 直接操作Entry控件
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, folder)
                
                # 验证设置是否成功
                current_value = self.path_var.get()
                entry_value = self.path_entry.get()
                logger.info(t('log_pathvar_value', current_value))
                logger.info(t('log_pathentry_value', entry_value))
                
                # 强制刷新界面
                self.path_entry.update()
                self.root.update()
                
                logger.success(t('log_path_set', folder))
                self.load_folder_remark()
                
            except Exception as e:
                logger.error(t('error_set_path', e))
        else:
            logger.warning(t('warning_user_cancelled'))
    
    def load_folder_remark(self):
        """加载文件夹备注"""
        if not self.folder_path:
            logger.warning(t('warning_no_folder_path'))
            return
        
        try:
            logger.info(t('log_reading_remark'))
            remark = self.manager.read_remark(self.folder_path)
            self.remark_text.delete(1.0, tk.END)
            self.remark_text.insert(1.0, remark)
            if remark:
                logger.success(t('log_remark_loaded'))
            else:
                logger.info(t('log_no_remark'))
        except Exception as e:
            logger.error(t('error_read_failed', str(e)))
            messagebox.showerror(t('msg_error'), t('error_read_failed', str(e)))
    
    def save_remark(self):
        """保存备注"""
        folder_path = self.path_var.get().strip()
        if not folder_path:
            messagebox.showerror(t('msg_error'), t('error_no_folder'))
            return
        
        if not os.path.exists(folder_path):
            messagebox.showerror(t('msg_error'), t('error_folder_not_exist'))
            return
        
        if not os.path.isdir(folder_path):
            messagebox.showerror(t('msg_error'), t('error_select_folder'))
            return
        
        remark = self.remark_text.get(1.0, tk.END).strip()
        
        # 检查字符长度
        if len(remark) > 500:
            messagebox.showerror(t('msg_error'), t('error_remark_too_long'))
            return
        
        try:
            self.manager.write_remark(folder_path, remark)
            if remark:
                logger.success(t('log_remark_saved'))
                messagebox.showinfo(t('msg_info'), t('log_remark_saved'))
            else:
                logger.success(t('log_remark_deleted'))
                messagebox.showinfo(t('msg_info'), t('log_remark_deleted'))
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            messagebox.showerror(t('msg_error'), f"保存失败: {str(e)}")
    
    def delete_remark(self):
        """删除备注"""
        folder_path = self.path_var.get().strip()
        if not folder_path:
            messagebox.showerror(t('msg_error'), t('error_no_folder'))
            return
        
        if messagebox.askyesno(t('msg_confirm_delete'), t('msg_delete_confirm')):
            try:
                self.manager.delete_remark(folder_path)
                self.remark_text.delete(1.0, tk.END)
                logger.success(t('log_remark_deleted'))
                messagebox.showinfo(t('msg_info'), t('log_remark_deleted'))
            except Exception as e:
                logger.error(t('error_delete_failed', str(e)))
                messagebox.showerror(t('msg_error'), t('error_delete_failed', str(e)))
    
    def refresh_remark(self):
        """刷新备注"""
        if self.folder_path:
            self.load_folder_remark()
            self.manager._refresh_folder(self.folder_path)
            logger.info(t('log_refreshed'))
        else:
            messagebox.showinfo(t('msg_info'), t('error_no_folder'))
    
    def restart_explorer(self):
        """重启Windows资源管理器"""
        result = messagebox.askyesno(
            t('btn_restart_explorer'), 
            t('msg_restart_explorer_confirm')
        )
        
        if result:
            try:
                logger.info(t('log_explorer_restarting'))
                
                # 结束explorer.exe进程
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                              check=False, capture_output=True)
                logger.info(t('log_explorer_killed'))
                
                # 等待进程结束
                import time
                time.sleep(1)
                
                # 重新启动explorer.exe
                subprocess.Popen(['explorer.exe'])
                logger.success(t('log_explorer_started'))
                
                # 等待资源管理器启动
                time.sleep(2)
                
                logger.success(t('log_explorer_restarted'))
                messagebox.showinfo(t('msg_info'), t('log_explorer_restarted'))
                
            except Exception as e:
                logger.error(t('log_explorer_restart_failed', e))
                messagebox.showerror(t('msg_error'), t('log_explorer_restart_failed', str(e)))
    
    def clear_log(self):
        """清空日志"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            logger.info(t('log_cleared'))
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            logger.info(t('log_closing'))
            # 清理资源
            if hasattr(self, 'log_text'):
                self.log_text = None
            if hasattr(self, 'manager'):
                self.manager = None
            
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
        """运行GUI"""
        logger.info(t('log_started'))
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            logger.error(t('error_program_error', e))
            self.on_closing()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Windows文件夹备注工具 - 基于desktop.ini")
    parser.add_argument("folder_path", nargs="?", help="文件夹路径")
    parser.add_argument("--install", action="store_true", help="安装右键菜单")
    parser.add_argument("--uninstall", action="store_true", help="卸载右键菜单")
    
    args = parser.parse_args()
    
    if args.install:
        from installer import install_context_menu
        install_context_menu()
        return
    
    if args.uninstall:
        from installer import uninstall_context_menu
        uninstall_context_menu()
        return
    
    # 启动GUI
    app = FolderRemarkGUI(args.folder_path)
    app.run()

if __name__ == "__main__":
    main() 