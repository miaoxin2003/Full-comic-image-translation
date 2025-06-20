# -*- coding: utf-8 -*-
"""
快速测试改进后的漫画翻译器
"""

import tkinter as tk
import sys
import os

def main():
    print("🚀 启动改进版漫画翻译器...")
    
    try:
        # 检查文件是否存在
        if not os.path.exists("comic_full_translator.py"):
            print("❌ 找不到 comic_full_translator.py 文件")
            return
        
        # 导入并运行主程序
        from comic_full_translator import ComicFullTranslatorApp
        
        # 创建主窗口
        root = tk.Tk()
        
        # 创建应用实例
        app = ComicFullTranslatorApp(root)
        
        print("✅ 应用启动成功！")
        print("\n📋 改进功能测试清单：")
        print("1. 加载图片 - 检查是否自动适应画布大小")
        print("2. 拖拽面板分隔线 - 检查是否可以调整宽度")
        print("3. 缩放图片 - 检查是否流畅无卡顿")
        print("4. 拖拽图片 - 检查移动是否流畅")
        print("5. 调整窗口大小 - 检查图片是否自动适应")
        print("6. 点击'适应窗口'按钮 - 检查是否重新适应")
        print("7. 点击'原始大小'按钮 - 检查是否显示原始大小")
        
        # 运行应用
        root.mainloop()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
