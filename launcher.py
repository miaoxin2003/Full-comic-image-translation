# -*- coding: utf-8 -*-
"""
漫画翻译器启动器
确保在打包环境中正确启动应用
"""

import sys
import os
import traceback

def setup_environment():
    """设置运行环境"""
    try:
        # 如果是打包后的exe，设置正确的路径
        if getattr(sys, 'frozen', False):
            # 运行在PyInstaller打包的exe中
            application_path = sys._MEIPASS
        else:
            # 运行在开发环境中
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # 添加到系统路径
        if application_path not in sys.path:
            sys.path.insert(0, application_path)
        
        # 设置工作目录
        os.chdir(application_path)
        
        return True
    except Exception as e:
        print(f"环境设置失败: {e}")
        return False

def main():
    """主启动函数"""
    try:
        # 设置环境
        if not setup_environment():
            input("按回车键退出...")
            return
        
        # 导入并启动主应用
        print("正在启动漫画翻译器...")
        
        # 导入主应用模块
        from comic_full_translator import ComicFullTranslatorApp
        import tkinter as tk
        
        # 创建主窗口
        root = tk.Tk()
        
        # 设置窗口图标和属性
        root.title("漫画翻译器 v2.1")
        
        # 创建应用实例
        app = ComicFullTranslatorApp(root)
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        print(f"模块导入失败: {e}")
        print("请确保所有必要的文件都在同一目录中")
        traceback.print_exc()
        input("按回车键退出...")
    except Exception as e:
        print(f"应用启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
