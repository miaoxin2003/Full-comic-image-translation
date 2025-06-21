#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设置保存功能
验证高级设置是否能正确保存和加载
"""

import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from config import config_manager

def test_config_save_load():
    """测试配置保存和加载"""
    print("🧪 开始测试配置保存和加载功能...")
    
    # 测试数据
    test_settings = {
        "target_language": "日文",
        "translation_style": "直译",
        "custom_prompt": "这是一个测试提示词，用于验证保存功能是否正常工作。"
    }
    
    print(f"📝 测试数据: {test_settings}")
    
    # 保存设置
    try:
        config_manager.update_advanced_settings(test_settings)
        print("✅ 高级设置保存成功")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    
    # 重新加载配置
    try:
        config_manager.config = config_manager.load_config()
        print("✅ 配置重新加载成功")
    except Exception as e:
        print(f"❌ 重新加载失败: {e}")
        return False
    
    # 验证保存的数据
    try:
        saved_language = config_manager.get_target_language()
        saved_style = config_manager.get_translation_style()
        saved_prompt = config_manager.get_custom_prompt()
        
        print(f"📖 读取的数据:")
        print(f"  目标语言: {saved_language}")
        print(f"  翻译风格: {saved_style}")
        print(f"  提示词长度: {len(saved_prompt)} 字符")
        
        # 验证数据是否正确
        if (saved_language == test_settings["target_language"] and
            saved_style == test_settings["translation_style"] and
            saved_prompt == test_settings["custom_prompt"]):
            print("✅ 数据验证成功，保存和读取功能正常")
            return True
        else:
            print("❌ 数据验证失败，保存的数据与预期不符")
            print(f"  预期语言: {test_settings['target_language']}, 实际: {saved_language}")
            print(f"  预期风格: {test_settings['translation_style']}, 实际: {saved_style}")
            return False
            
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return False

def test_gui_settings():
    """测试GUI设置窗口"""
    print("\n🖥️ 测试GUI设置窗口...")
    
    try:
        # 导入GUI组件
        from comic_full_translator import SettingsWindow
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        def on_test_complete():
            print("✅ 设置窗口测试完成")
            root.quit()
        
        # 创建设置窗口
        settings_window = SettingsWindow(root, callback=on_test_complete)
        
        print("✅ 设置窗口创建成功")
        print("💡 请在设置窗口中:")
        print("  1. 切换到'高级设置'标签页")
        print("  2. 修改目标语言和翻译风格")
        print("  3. 编辑自定义提示词")
        print("  4. 点击'保存'按钮")
        print("  5. 关闭设置窗口")
        
        # 运行GUI
        root.mainloop()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        return False

def check_config_file():
    """检查配置文件内容"""
    print("\n📄 检查配置文件内容...")
    
    config_file = "user_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            print(f"✅ 配置文件存在: {config_file}")
            print("📋 配置文件结构:")
            
            for key, value in config_data.items():
                if key == "advanced_settings":
                    print(f"  {key}:")
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key == "custom_prompt":
                                print(f"    {sub_key}: {len(str(sub_value))} 字符")
                            else:
                                print(f"    {sub_key}: {sub_value}")
                    else:
                        print(f"    {value}")
                elif isinstance(value, dict):
                    print(f"  {key}: {{...}} (字典)")
                elif isinstance(value, list):
                    print(f"  {key}: [...] (列表)")
                else:
                    print(f"  {key}: {value}")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            return False
    else:
        print(f"⚠️  配置文件不存在: {config_file}")
        return False

def main():
    """主测试函数"""
    print("🔧 高级设置保存功能测试")
    print("=" * 50)
    
    # 测试1: 配置保存和加载
    test1_result = test_config_save_load()
    
    # 测试2: 检查配置文件
    test2_result = check_config_file()
    
    # 测试3: GUI设置窗口（可选）
    if input("\n❓ 是否测试GUI设置窗口? (y/n): ").lower() == 'y':
        test3_result = test_gui_settings()
        
        # 测试GUI后再次检查配置
        print("\n🔄 GUI测试后重新检查配置...")
        test_config_save_load()
        check_config_file()
    else:
        test3_result = True
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"  配置保存/加载: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"  配置文件检查: {'✅ 通过' if test2_result else '❌ 失败'}")
    print(f"  GUI设置窗口: {'✅ 通过' if test3_result else '❌ 失败'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 所有测试通过！高级设置保存功能正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查相关功能。")

if __name__ == "__main__":
    main()
