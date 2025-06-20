# -*- coding: utf-8 -*-
"""
测试基本缩放功能是否恢复正常
"""

import tkinter as tk
from tkinter import messagebox

def test_basic_zoom():
    """测试基本缩放功能"""
    print("🧪 测试基本缩放功能...")
    
    try:
        from comic_full_translator import ComicFullTranslatorApp
        
        root = tk.Tk()
        app = ComicFullTranslatorApp(root)
        
        print("✅ 应用启动成功")
        print("\n📋 基本缩放功能测试:")
        print("1. 加载一张图片")
        print("2. 使用鼠标滚轮进行缩放")
        print("3. 检查是否能正常放大缩小")
        print("4. 观察状态栏是否显示缩放比例")
        print("5. 测试拖拽功能是否正常")
        
        print("\n⚠️ 如果出现错误:")
        print("- 检查控制台是否有错误信息")
        print("- 确认图片文件格式正确")
        print("- 尝试重启应用")
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🔧 基本缩放功能修复验证")
    print("=" * 40)
    
    print("🐛 问题描述:")
    print("- 修复跳动问题时意外破坏了基本缩放功能")
    print("- 出现 AttributeError: 'zoom_timer' 错误")
    
    print("\n✅ 修复内容:")
    print("- 移除了对已删除变量的引用")
    print("- 简化了缩放事件处理逻辑")
    print("- 保持立即更新机制")
    
    choice = input("\n是否开始测试基本缩放功能？(y/n): ").strip().lower()
    
    if choice == 'y':
        success = test_basic_zoom()
        
        if success:
            print("\n🎉 基本缩放功能测试完成！")
            
            # 询问功能是否正常
            zoom_works = input("缩放功能是否正常工作？(y/n): ").strip().lower()
            drag_works = input("拖拽功能是否正常工作？(y/n): ").strip().lower()
            
            if zoom_works == 'y' and drag_works == 'y':
                print("✅ 太好了！基本功能已恢复正常")
                print("🎯 现在可以继续测试跳动问题是否解决")
            elif zoom_works == 'y':
                print("✅ 缩放功能正常")
                print("⚠️ 拖拽功能可能还有问题")
            else:
                print("❌ 还有问题需要进一步修复")
        else:
            print("❌ 测试失败，需要检查错误")
    else:
        print("👋 测试结束")

if __name__ == "__main__":
    main()
