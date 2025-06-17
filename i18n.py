#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际化模块 - 多语言支持
支持中文简体和英文
"""

import os
import json
from pathlib import Path

class I18n:
    """国际化管理器"""
    
    def __init__(self):
        self.current_language = 'zh_CN'  # 默认中文
        self.config_file = 'language_config.json'
        self.translations = {
            'zh_CN': {
                # 主界面
                'main_title': '文件夹备注工具',
                'main_description': '为Windows文件夹添加备注信息，鼠标悬停即可查看',
                'status_installed': '✅ 右键菜单已安装',
                'status_not_installed': '❌ 右键菜单未安装',
                'btn_install': '📥 安装右键菜单',
                'btn_uninstall': '🗑 卸载右键菜单',
                'btn_exit': '❌ 退出',
                'language_label': '语言/Language:',
                
                # 帮助文本
                'help_text': '''使用说明：
1. 点击"安装右键菜单"将功能集成到文件夹右键菜单
2. 安装后可在任意文件夹上右键选择"📝 添加文件夹备注"
3. 或直接点击"打开备注工具"使用GUI界面
4. 备注信息会保存在文件夹的desktop.ini文件中
5. 鼠标悬停在文件夹上即可查看备注内容''',
                
                # 消息框
                'msg_already_installed': '右键菜单已经安装',
                'msg_install_confirm': '安装右键菜单需要管理员权限。\n\n安装后可在文件夹右键菜单中看到\'📝 添加文件夹备注\'选项。\n\n确定要继续吗？',
                'msg_install_success': '右键菜单安装成功！\n\n现在您可以右键点击任何文件夹来添加备注了。',
                'msg_install_failed': '安装失败',
                'msg_uninstall_confirm': '确定要卸载右键菜单吗？\n\n这将从文件夹右键菜单中移除"📝 添加文件夹备注"选项。',
                'msg_uninstall_success': '右键菜单卸载成功！',
                'msg_uninstall_failed': '卸载失败',
                'msg_error': '错误',
                'msg_confirm': '确认安装',
                'msg_confirm_uninstall': '确认卸载',
                'msg_info': '提示',
                
                # 备注工具界面
                'remark_title': '文件夹备注工具',
                'folder_path_label': '文件夹路径:',
                'btn_browse': '📁 浏览',
                'remark_content_label': '备注内容:',
                'btn_save': '💾 保存备注',
                'btn_delete': '🗑 删除备注',
                'btn_refresh': '🔄 刷新',
                'btn_restart_explorer': '🔄 重启资源管理器',
                'btn_clear_log': '🧹 清空日志',
                'log_label': '操作日志:',
                'char_count': '字符数: {}/500',
                
                # 日志消息
                'log_reading_remark': '正在读取备注...',
                'log_no_remark': '此文件夹没有备注',
                'log_remark_loaded': '备注加载完成',
                'log_writing_remark': '正在写入备注到: {}',
                'log_clearing_remark': '正在清空备注: {}',
                'log_file_attrs_removed': '已移除文件属性限制',
                'log_file_attrs_failed': '移除文件属性失败: {}',
                'log_write_success': 'desktop.ini文件写入成功',
                'log_attrs_set': '文件属性设置完成',
                'log_deleting_remark': '正在删除备注...',
                'log_infotip_removed': '已从.ShellClassInfo节中移除InfoTip',
                'log_remark_saved': '备注保存成功！',
                'log_remark_deleted': '备注删除成功！',
                'log_explorer_restarting': '正在重启Windows资源管理器...',
                'log_explorer_restarted': 'Windows资源管理器已重启',
                'log_explorer_restart_failed': '重启资源管理器失败: {}',
                
                # 新增的翻译键
                'help_text_tip': '备注将显示在文件管理器中，鼠标悬停在文件夹上即可查看',
                'error_select_folder': '请选择一个文件夹，不是文件',
                'msg_confirm_delete': '确认删除',
                'msg_delete_confirm': '确定要删除这个文件夹的备注吗？',
                'log_refreshed': '已刷新备注内容',
                'msg_restart_explorer_confirm': '重启Windows资源管理器是解决desktop.ini刷新问题的最可靠方法。\n\n⚠️ 注意：这会关闭所有打开的资源管理器窗口！\n\n确定要继续吗？',
                'log_explorer_killed': '已结束explorer.exe进程',
                'log_explorer_started': '已重新启动explorer.exe',
                'log_cleared': '日志已清空',
                'log_closing': '正在关闭程序...',
                'log_started': '文件夹备注工具已启动',
                'log_welcome': '🎉 文件夹备注工具已启动，界面加载完成',
                'log_instruction': '💡 选择文件夹并输入备注，即可为文件夹添加说明信息',
                'warning_no_folder_path': '未选择文件夹路径',
                'warning_user_cancelled': '用户取消了文件夹选择',
                'log_no_infotip': '未找到InfoTip选项，无需删除',
                'log_no_shellclass': '未找到.ShellClassInfo节，无需删除',
                'log_desktop_updated': '已更新desktop.ini文件（保留其他设置）',
                'log_delete_completed': '备注删除完成',
                'log_attrs_set_detailed': '已设置desktop.ini和文件夹属性',
                'warning_attrs_failed': '设置文件属性失败: {}',
                'log_desktop_refresh': '已触发桌面强制刷新',
                'warning_desktop_refresh_failed': '桌面强制刷新失败: {}',
                'log_folder_refresh_sent': '已发送文件夹刷新通知',
                'warning_folder_refresh_failed': '文件夹刷新通知失败: {}',
                'log_desktop_refreshed': '已刷新桌面显示',
                'warning_desktop_failed': '桌面刷新失败: {}',
                'log_explorer_window_refreshed': '已刷新对应的资源管理器窗口',
                'log_win32com_unavailable': 'Win32com不可用，跳过COM刷新',
                'warning_com_refresh_failed': 'COM刷新失败: {}',
                'log_timestamp_updated': '已更新文件夹时间戳',
                'warning_timestamp_failed': '时间戳更新失败: {}',
                'log_global_redraw': '已触发全局窗口重绘',
                'warning_redraw_failed': '窗口重绘失败: {}',
                'warning_refresh_error': '文件夹刷新过程出错: {}',
                'tip_refresh_manual': '💡 如果备注未立即显示，请尝试：',
                'tip_press_f5': '   1. 按F5刷新当前文件夹',
                'tip_reopen_explorer': '   2. 重新打开资源管理器窗口',
                'tip_wait_update': '   3. 或稍等几秒钟让系统自动更新',
                'log_folder_selected': '用户选择了文件夹: {}',
                'log_pathvar_value': 'path_var当前值: \'{}\'',
                'log_pathentry_value': 'path_entry当前值: \'{}\'',
                'log_path_set': '文件夹路径已设置: {}',
                'error_set_path': '设置路径时出错: {}',
                'error_gui_log_failed': 'GUI日志失败: {}',
                'log_pathvar_init': '初始化path_var，初始值: \'{}\'',
                'error_program_error': '程序运行出错: {}',
                'log_language_changed': '语言已切换为: {}',
                'log_ui_updated': '界面文本已更新',
                
                # 错误消息
                'error_folder_not_exist': '文件夹不存在',
                'error_read_failed': '读取备注失败: {}',
                'error_write_failed': '写入desktop.ini文件失败: {}',
                'error_attrs_failed': '设置文件属性失败: {}',
                'error_delete_failed': '删除备注失败: {}',
                'error_remark_too_long': '备注内容过长！最多500个字符。',
                'error_no_folder': '请先选择一个文件夹',
                'error_open_failed': '打开备注工具失败: {}',
                
                # 安装器相关
                'installer_menu_text': '添加文件夹备注',
                'installer_success': '右键菜单安装成功！',
                'installer_success_detail': '现在您可以右键点击任何文件夹，选择\'📝 添加文件夹备注\'来使用此功能。',
                'installer_uninstall_success': '右键菜单卸载成功！',
                'installer_uninstall_detail': '文件夹右键菜单中的\'📝 添加文件夹备注\'选项已被移除。',
            },
            
            'en_US': {
                # Main interface
                'main_title': 'Folder Remark Tool',
                'main_description': 'Add remark information to Windows folders, viewable on hover',
                'status_installed': '✅ Context menu installed',
                'status_not_installed': '❌ Context menu not installed',
                'btn_install': '📥 Install Context Menu',
                'btn_uninstall': '🗑 Uninstall Context Menu',
                'btn_exit': '❌ Exit',
                'language_label': 'Language/语言:',
                
                # Help text
                'help_text': '''Instructions:
1. Click "Install Context Menu" to integrate into folder context menu
2. After installation, right-click any folder and select "📝 Add Folder Remark"
3. Or directly click "Open Remark Tool" to use GUI interface
4. Remark information is saved in the folder's desktop.ini file
5. Hover over folders to view remark content''',
                
                # Message boxes
                'msg_already_installed': 'Context menu is already installed',
                'msg_install_confirm': 'Installing context menu requires administrator privileges.\n\nAfter installation, you can see the \'📝 Add Folder Remark\' option in folder context menus.\n\nDo you want to continue?',
                'msg_install_success': 'Context menu installed successfully!\n\nYou can now right-click any folder to add remarks.',
                'msg_install_failed': 'Installation failed',
                'msg_uninstall_confirm': 'Are you sure you want to uninstall the context menu?\n\nThis will remove the "📝 Add Folder Remark" option from folder context menus.',
                'msg_uninstall_success': 'Context menu uninstalled successfully!',
                'msg_uninstall_failed': 'Uninstall failed',
                'msg_error': 'Error',
                'msg_confirm': 'Confirm Installation',
                'msg_confirm_uninstall': 'Confirm Uninstall',
                'msg_info': 'Info',
                
                # Remark tool interface
                'remark_title': 'Folder Remark Tool',
                'folder_path_label': 'Folder Path:',
                'btn_browse': '📁 Browse',
                'remark_content_label': 'Remark Content:',
                'btn_save': '💾 Save Remark',
                'btn_delete': '🗑 Delete Remark',
                'btn_refresh': '🔄 Refresh',
                'btn_restart_explorer': '🔄 Restart Explorer',
                'btn_clear_log': '🧹 Clear Log',
                'log_label': 'Operation Log:',
                'char_count': 'Characters: {}/500',
                
                # Log messages
                'log_reading_remark': 'Reading remark...',
                'log_no_remark': 'This folder has no remark',
                'log_remark_loaded': 'Remark loaded successfully',
                'log_writing_remark': 'Writing remark to: {}',
                'log_clearing_remark': 'Clearing remark: {}',
                'log_file_attrs_removed': 'File attribute restrictions removed',
                'log_file_attrs_failed': 'Failed to remove file attributes: {}',
                'log_write_success': 'desktop.ini file written successfully',
                'log_attrs_set': 'File attributes set successfully',
                'log_deleting_remark': 'Deleting remark...',
                'log_infotip_removed': 'Removed InfoTip from .ShellClassInfo section',
                'log_remark_saved': 'Remark saved successfully!',
                'log_remark_deleted': 'Remark deleted successfully!',
                'log_explorer_restarting': 'Restarting Windows Explorer...',
                'log_explorer_restarted': 'Windows Explorer restarted',
                'log_explorer_restart_failed': 'Failed to restart Explorer: {}',
                
                # New translation keys
                'help_text_tip': 'Remarks will be displayed in File Explorer when hovering over the folder',
                'error_select_folder': 'Please select a folder, not a file',
                'msg_confirm_delete': 'Confirm Deletion',
                'msg_delete_confirm': 'Are you sure you want to delete the remark for this folder?',
                'log_refreshed': 'Remark content refreshed',
                'msg_restart_explorer_confirm': 'Restarting Windows Explorer is the most reliable way to solve desktop.ini refresh issues.\n\n⚠️ Warning: This will close all open File Explorer windows!\n\nDo you want to continue?',
                'log_explorer_killed': 'Terminated explorer.exe process',
                'log_explorer_started': 'Restarted explorer.exe',
                'log_cleared': 'Log cleared',
                'log_closing': 'Closing application...',
                'log_started': 'Folder Remark Tool started',
                'log_welcome': '🎉 Folder Remark Tool started, interface loaded successfully',
                'log_instruction': '💡 Select a folder and enter remarks to add description information',
                'warning_no_folder_path': 'No folder path selected',
                'warning_user_cancelled': 'User cancelled folder selection',
                'log_no_infotip': 'InfoTip option not found, no need to delete',
                'log_no_shellclass': '.ShellClassInfo section not found, no need to delete',
                'log_desktop_updated': 'Updated desktop.ini file (keeping other settings)',
                'log_delete_completed': 'Remark deletion completed',
                'log_attrs_set_detailed': 'Set desktop.ini and folder attributes',
                'warning_attrs_failed': 'Failed to set file attributes: {}',
                'log_desktop_refresh': 'Triggered desktop force refresh',
                'warning_desktop_refresh_failed': 'Desktop force refresh failed: {}',
                'log_folder_refresh_sent': 'Sent folder refresh notification',
                'warning_folder_refresh_failed': 'Folder refresh notification failed: {}',
                'log_desktop_refreshed': 'Desktop display refreshed',
                'warning_desktop_failed': 'Desktop refresh failed: {}',
                'log_explorer_window_refreshed': 'Refreshed corresponding File Explorer window',
                'log_win32com_unavailable': 'Win32com not available, skipping COM refresh',
                'warning_com_refresh_failed': 'COM refresh failed: {}',
                'log_timestamp_updated': 'Updated folder timestamp',
                'warning_timestamp_failed': 'Timestamp update failed: {}',
                'log_global_redraw': 'Triggered global window redraw',
                'warning_redraw_failed': 'Window redraw failed: {}',
                'warning_refresh_error': 'Error during folder refresh process: {}',
                'tip_refresh_manual': '💡 If remarks don\'t appear immediately, try:',
                'tip_press_f5': '   1. Press F5 to refresh current folder',
                'tip_reopen_explorer': '   2. Reopen File Explorer window',
                'tip_wait_update': '   3. Wait a few seconds for system to update automatically',
                'log_folder_selected': 'User selected folder: {}',
                'log_pathvar_value': 'path_var current value: \'{}\'',
                'log_pathentry_value': 'path_entry current value: \'{}\'',
                'log_path_set': 'Folder path set: {}',
                'error_set_path': 'Error setting path: {}',
                'error_gui_log_failed': 'GUI logging failed: {}',
                'log_pathvar_init': 'Initializing path_var, initial value: \'{}\'',
                'error_program_error': 'Program error: {}',
                'log_language_changed': 'Language changed to: {}',
                'log_ui_updated': 'UI text updated',
                
                # Error messages
                'error_folder_not_exist': 'Folder does not exist',
                'error_read_failed': 'Failed to read remark: {}',
                'error_write_failed': 'Failed to write desktop.ini file: {}',
                'error_attrs_failed': 'Failed to set file attributes: {}',
                'error_delete_failed': 'Failed to delete remark: {}',
                'error_remark_too_long': 'Remark content too long! Maximum 500 characters.',
                'error_no_folder': 'Please select a folder first',
                'error_open_failed': 'Failed to open remark tool: {}',
                
                # Installer related
                'installer_menu_text': 'Add Folder Remark',
                'installer_success': 'Context menu installed successfully!',
                'installer_success_detail': 'You can now right-click any folder and select \'📝 Add Folder Remark\' to use this feature.',
                'installer_uninstall_success': 'Context menu uninstalled successfully!',
                'installer_uninstall_detail': 'The \'📝 Add Folder Remark\' option has been removed from folder context menus.',
            }
        }
        self.load_language_config()
    
    def load_language_config(self):
        """加载语言配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_language = config.get('language', 'zh_CN')
        except Exception:
            pass  # 使用默认语言
    
    def save_language_config(self):
        """保存语言配置"""
        try:
            config = {'language': self.current_language}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 保存失败不影响使用
    
    def set_language(self, language):
        """设置当前语言"""
        if language in self.translations:
            self.current_language = language
            self.save_language_config()
    
    def get_language(self):
        """获取当前语言"""
        return self.current_language
    
    def get_available_languages(self):
        """获取可用语言列表"""
        return {
            'zh_CN': '中文',
            'en_US': 'English'
        }
    
    def t(self, key, *args):
        """翻译函数"""
        translation = self.translations.get(self.current_language, {}).get(key, key)
        if args:
            try:
                return translation.format(*args)
            except:
                return translation
        return translation
    
    def _(self, key, *args):
        """翻译函数的简写版本"""
        return self.t(key, *args)

# 创建全局国际化实例
i18n = I18n()

# 导出常用函数
t = i18n.t
_ = i18n._ 