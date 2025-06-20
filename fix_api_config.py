# -*- coding: utf-8 -*-
"""
API配置快速修复工具
"""

import json
import os
from config import ConfigManager

def fix_openrouter_config():
    """修复OpenRouter配置"""
    print("🔧 配置OpenRouter...")
    
    config_manager = ConfigManager()
    
    print("推荐的免费视觉模型:")
    print("1. google/gemini-flash-1.5:free (推荐)")
    print("2. qwen/qwen-2-vl-7b-instruct:free")
    print("3. opengvlab/internvl3-14b:free")

    model_choice = input("选择模型 (1-3, 默认1): ").strip() or "1"

    model_map = {
        "1": "google/gemini-flash-1.5:free",
        "2": "qwen/qwen-2-vl-7b-instruct:free",
        "3": "opengvlab/internvl3-14b:free"
    }

    selected_model = model_map.get(model_choice, "google/gemini-flash-1.5:free")

    # 推荐的OpenRouter配置
    openrouter_config = {
        "api_key": input("请输入OpenRouter API密钥: ").strip(),
        "base_url": "https://openrouter.ai/api/v1",
        "model_name": selected_model,
        "http_referer": "https://github.com/your-username/comic-translator",
        "x_title": "Comic Translator"
    }
    
    # 更新配置
    config_manager.update_provider("openrouter")
    config_manager.update_provider_config("openrouter", openrouter_config)
    
    print("✅ OpenRouter配置已更新")
    print(f"🤖 使用模型: {openrouter_config['model_name']}")
    return True

def fix_openai_config():
    """修复OpenAI配置"""
    print("🔧 配置OpenAI...")
    
    config_manager = ConfigManager()
    
    openai_config = {
        "api_key": input("请输入OpenAI API密钥: ").strip(),
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o-mini"  # 支持视觉的模型
    }
    
    config_manager.update_provider("openai")
    config_manager.update_provider_config("openai", openai_config)
    
    print("✅ OpenAI配置已更新")
    print(f"🤖 使用模型: {openai_config['model_name']}")
    return True

def fix_anthropic_config():
    """修复Anthropic配置"""
    print("🔧 配置Anthropic...")
    
    config_manager = ConfigManager()
    
    anthropic_config = {
        "api_key": input("请输入Anthropic API密钥: ").strip(),
        "base_url": "https://api.anthropic.com/v1",
        "model_name": "claude-3-5-sonnet-20241022",
        "version": "2023-06-01"
    }
    
    config_manager.update_provider("anthropic")
    config_manager.update_provider_config("anthropic", anthropic_config)
    
    print("✅ Anthropic配置已更新")
    print(f"🤖 使用模型: {anthropic_config['model_name']}")
    return True

def show_recommended_configs():
    """显示推荐配置"""
    print("\n💡 推荐配置方案:")
    print("=" * 50)
    
    print("1. 🆓 免费方案 - OpenRouter + InternVL")
    print("   - 服务商: OpenRouter")
    print("   - 模型: opengvlab/internvl3-14b:free")
    print("   - 优点: 完全免费，支持视觉")
    print("   - 注册: https://openrouter.ai/")
    
    print("\n2. 💰 付费方案 - OpenAI + GPT-4o-mini")
    print("   - 服务商: OpenAI")
    print("   - 模型: gpt-4o-mini")
    print("   - 优点: 质量高，速度快")
    print("   - 注册: https://platform.openai.com/")
    
    print("\n3. 🎯 高质量方案 - Anthropic + Claude")
    print("   - 服务商: Anthropic")
    print("   - 模型: claude-3-5-sonnet")
    print("   - 优点: 理解能力强")
    print("   - 注册: https://console.anthropic.com/")

def interactive_setup():
    """交互式设置"""
    print("🎯 交互式API配置")
    print("=" * 30)
    
    show_recommended_configs()
    
    print("\n请选择配置方案:")
    print("1. OpenRouter (推荐，免费)")
    print("2. OpenAI (付费)")
    print("3. Anthropic (付费)")
    print("4. 查看当前配置")
    print("5. 退出")
    
    choice = input("\n请输入选择 (1-5): ").strip()
    
    if choice == "1":
        return fix_openrouter_config()
    elif choice == "2":
        return fix_openai_config()
    elif choice == "3":
        return fix_anthropic_config()
    elif choice == "4":
        show_current_config()
        return False
    elif choice == "5":
        print("👋 退出配置")
        return False
    else:
        print("❌ 无效选择")
        return False

def show_current_config():
    """显示当前配置"""
    print("\n📋 当前配置:")
    print("=" * 30)
    
    config_manager = ConfigManager()
    provider = config_manager.config.get("api_provider", "未设置")
    provider_config = config_manager.get_current_provider_config()
    
    print(f"服务商: {provider}")
    print(f"API密钥: {'已配置' if provider_config.get('api_key') and not provider_config.get('api_key').startswith('<') else '未配置'}")
    print(f"基础URL: {provider_config.get('base_url', '未设置')}")
    print(f"模型: {provider_config.get('model_name', '未设置')}")

def test_configuration():
    """测试配置"""
    print("\n🧪 测试API配置...")
    
    try:
        from api_diagnostic import test_api_connection, check_model_vision_support
        
        connection_ok = test_api_connection()
        vision_ok = check_model_vision_support()
        
        if connection_ok and vision_ok:
            print("🎉 配置测试成功！")
            return True
        else:
            print("⚠️ 配置可能有问题")
            return False
            
    except ImportError:
        print("⚠️ 无法导入诊断模块，请手动测试")
        return False

def main():
    """主函数"""
    print("🔧 API配置快速修复工具")
    print("=" * 40)
    
    while True:
        print("\n请选择操作:")
        print("1. 交互式配置API")
        print("2. 查看当前配置")
        print("3. 测试配置")
        print("4. 查看推荐方案")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            success = interactive_setup()
            if success:
                print("\n✅ 配置完成！")
                test_config = input("是否测试配置？(y/n): ").strip().lower()
                if test_config == 'y':
                    test_configuration()
        elif choice == "2":
            show_current_config()
        elif choice == "3":
            test_configuration()
        elif choice == "4":
            show_recommended_configs()
        elif choice == "5":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
