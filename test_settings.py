# -*- coding: utf-8 -*-
"""
测试设置窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox

def test_settings_window():
    """测试设置窗口"""
    
    def create_settings():
        """创建设置窗口"""
        settings_window = tk.Toplevel(root)
        settings_window.title("设置测试")
        settings_window.geometry("600x500")
        
        # 创建主框架
        main_frame = ttk.Frame(settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 标签页1
        frame1 = ttk.Frame(notebook)
        notebook.add(frame1, text="API服务商")
        ttk.Label(frame1, text="这是API服务商标签页").pack(pady=20)
        
        # 标签页2
        frame2 = ttk.Frame(notebook)
        notebook.add(frame2, text="模型设置")
        ttk.Label(frame2, text="这是模型设置标签页").pack(pady=20)
        
        # 标签页3
        frame3 = ttk.Frame(notebook)
        notebook.add(frame3, text="高级设置")
        ttk.Label(frame3, text="这是高级设置标签页").pack(pady=20)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮
        ttk.Button(button_frame, text="重置默认", command=lambda: messagebox.showinfo("测试", "重置按钮")).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="保存", command=lambda: messagebox.showinfo("测试", "保存按钮")).pack(side=tk.RIGHT)
    
    # 创建主窗口
    root = tk.Tk()
    root.title("设置窗口测试")
    root.geometry("400x300")
    
    # 测试按钮
    ttk.Button(root, text="打开设置", command=create_settings).pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test_settings_window()
