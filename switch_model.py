# -*- coding: utf-8 -*-
"""
快速切换模型工具
用于解决模型提供商故障问题
"""

from config import ConfigManager

def get_available_free_models():
    """获取可用的免费视觉模型"""
    return {
        "1": {
            "name": "google/gemini-flash-1.5:free",
            "description": "Google Gemini Flash 1.5 (免费，稳定)",
            "provider": "Google"
        },
        "2": {
            "name": "qwen/qwen-2-vl-7b-instruct:free", 
            "description": "Qwen 2 VL 7B (免费，中文友好)",
            "provider": "Alibaba"
        },
        "3": {
            "name": "opengvlab/internvl3-14b:free",
            "description": "InternVL3 14B (免费，可能不稳定)",
            "provider": "Nineteen"
        },
        "4": {
            "name": "meta-llama/llama-3.2-11b-vision-instruct:free",
            "description": "Llama 3.2 Vision (免费)",
            "provider": "Meta"
        }
    }

def get_available_paid_models():
    """获取可用的付费视觉模型"""
    return {
        "1": {
            "name": "gpt-4o-mini",
            "description": "GPT-4o Mini (付费，高质量)",
            "provider": "OpenAI",
            "service": "openai"
        },
        "2": {
            "name": "gpt-4o",
            "description": "GPT-4o (付费，最高质量)",
            "provider": "OpenAI", 
            "service": "openai"
        },
        "3": {
            "name": "claude-3-5-sonnet-20241022",
            "description": "Claude 3.5 Sonnet (付费，理解力强)",
            "provider": "Anthropic",
            "service": "anthropic"
        }
    }

def switch_to_free_model():
    """切换到免费模型"""
    print("🆓 可用的免费视觉模型:")
    print("=" * 50)
    
    models = get_available_free_models()
    
    for key, model in models.items():
        print(f"{key}. {model['description']}")
        print(f"   模型: {model['name']}")
        print(f"   提供商: {model['provider']}")
        print()
    
    choice = input("请选择模型 (1-4): ").strip()
    
    if choice in models:
        selected_model = models[choice]
        
        config_manager = ConfigManager()
        
        # 确保使用OpenRouter
        config_manager.update_provider("openrouter")
        
        # 更新模型
        current_config = config_manager.get_current_provider_config()
        current_config["model_name"] = selected_model["name"]
        config_manager.update_provider_config("openrouter", current_config)
        
        print(f"✅ 已切换到: {selected_model['description']}")
        print(f"🤖 模型名称: {selected_model['name']}")
        return True
    else:
        print("❌ 无效选择")
        return False

def switch_to_paid_model():
    """切换到付费模型"""
    print("💰 可用的付费视觉模型:")
    print("=" * 50)
    
    models = get_available_paid_models()
    
    for key, model in models.items():
        print(f"{key}. {model['description']}")
        print(f"   模型: {model['name']}")
        print(f"   服务: {model['service']}")
        print()
    
    choice = input("请选择模型 (1-3): ").strip()
    
    if choice in models:
        selected_model = models[choice]
        service = selected_model["service"]
        
        config_manager = ConfigManager()
        
        # 检查对应服务的配置
        service_config = config_manager.config.get(service, {})
        api_key = service_config.get("api_key", "")
        
        if not api_key or api_key.startswith("<"):
            print(f"⚠️ {service.upper()} API密钥未配置")
            api_key = input(f"请输入{service.upper()} API密钥: ").strip()
            
            if service == "openai":
                service_config.update({
                    "api_key": api_key,
                    "base_url": "https://api.openai.com/v1",
                    "model_name": selected_model["name"]
                })
            elif service == "anthropic":
                service_config.update({
                    "api_key": api_key,
                    "base_url": "https://api.anthropic.com/v1", 
                    "model_name": selected_model["name"],
                    "version": "2023-06-01"
                })
            
            config_manager.update_provider_config(service, service_config)
        
        # 切换到对应服务
        config_manager.update_provider(service)
        
        # 更新模型
        service_config["model_name"] = selected_model["name"]
        config_manager.update_provider_config(service, service_config)
        
        print(f"✅ 已切换到: {selected_model['description']}")
        print(f"🤖 模型名称: {selected_model['name']}")
        print(f"🔧 服务商: {service.upper()}")
        return True
    else:
        print("❌ 无效选择")
        return False

def show_current_model():
    """显示当前模型"""
    config_manager = ConfigManager()
    
    provider = config_manager.config.get("api_provider", "未设置")
    model = config_manager.get_current_model()
    
    print(f"📋 当前配置:")
    print(f"   服务商: {provider}")
    print(f"   模型: {model}")

def test_current_model():
    """测试当前模型"""
    print("🧪 测试当前模型...")
    
    try:
        from api_diagnostic import test_api_connection
        success = test_api_connection()
        
        if success:
            print("✅ 当前模型工作正常")
        else:
            print("❌ 当前模型有问题，建议切换")
            
        return success
    except ImportError:
        print("⚠️ 无法运行测试，请手动验证")
        return False

def main():
    """主函数"""
    print("🔄 模型切换工具")
    print("=" * 30)
    print("解决模型提供商故障问题")
    print()
    
    while True:
        show_current_model()
        print("\n请选择操作:")
        print("1. 切换到免费模型")
        print("2. 切换到付费模型") 
        print("3. 测试当前模型")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            success = switch_to_free_model()
            if success:
                print("\n🎉 切换成功！请重新尝试翻译")
                test_choice = input("是否测试新模型？(y/n): ").strip().lower()
                if test_choice == 'y':
                    test_current_model()
        elif choice == "2":
            success = switch_to_paid_model()
            if success:
                print("\n🎉 切换成功！请重新尝试翻译")
                test_choice = input("是否测试新模型？(y/n): ").strip().lower()
                if test_choice == 'y':
                    test_current_model()
        elif choice == "3":
            test_current_model()
        elif choice == "4":
            print("👋 退出")
            break
        else:
            print("❌ 无效选择")
        
        print("\n" + "=" * 30)

if __name__ == "__main__":
    main()
