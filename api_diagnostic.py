# -*- coding: utf-8 -*-
"""
API配置诊断工具
用于检查和诊断API配置问题
"""

import json
import requests
import base64
import os
from config import ConfigManager

def check_api_configuration():
    """检查API配置"""
    print("🔍 开始API配置诊断...")
    print("=" * 50)
    
    config_manager = ConfigManager()
    
    # 检查当前配置
    provider = config_manager.config.get("api_provider", "openrouter")
    provider_config = config_manager.get_current_provider_config()
    
    print(f"📋 当前API服务商: {provider}")
    print(f"🔑 API密钥: {'已配置' if provider_config.get('api_key') and not provider_config.get('api_key').startswith('<') else '未配置'}")
    print(f"🌐 基础URL: {provider_config.get('base_url', '未设置')}")
    print(f"🤖 模型名称: {provider_config.get('model_name', '未设置')}")
    
    # 检查API密钥
    api_key = provider_config.get("api_key", "")
    if not api_key or api_key.startswith("<"):
        print("\n❌ API密钥未正确配置！")
        print("💡 请在设置中配置正确的API密钥")
        return False
    
    # 检查基础URL
    base_url = provider_config.get("base_url", "")
    if not base_url:
        print("\n❌ 基础URL未配置！")
        return False
    
    # 检查模型名称
    model_name = provider_config.get("model_name", "")
    if not model_name:
        print("\n❌ 模型名称未配置！")
        return False
    
    print("\n✅ 基本配置检查通过")
    return True

def test_api_connection():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    
    config_manager = ConfigManager()
    provider = config_manager.config.get("api_provider", "openrouter")
    provider_config = config_manager.get_current_provider_config()
    
    # 构建请求头
    headers = {
        'Authorization': f'Bearer {provider_config.get("api_key", "")}',
        'Content-Type': 'application/json'
    }
    
    # 根据不同服务商添加特定头信息
    if provider == "openrouter":
        headers['HTTP-Referer'] = provider_config.get("http_referer", "")
        headers['X-Title'] = provider_config.get("x_title", "")
    elif provider == "anthropic":
        headers['anthropic-version'] = provider_config.get("version", "2023-06-01")
    
    # 构建简单的文本测试请求
    base_url = provider_config.get("base_url", "")
    model_name = provider_config.get("model_name", "")
    
    if provider == "anthropic":
        url = f"{base_url}/messages"
        data = {
            'model': model_name,
            'max_tokens': 100,
            'messages': [
                {
                    'role': 'user',
                    'content': '请回复"连接测试成功"'
                }
            ]
        }
    else:
        url = f"{base_url}/chat/completions"
        data = {
            'model': model_name,
            'messages': [
                {
                    'role': 'user',
                    'content': '请回复"连接测试成功"'
                }
            ],
            'max_tokens': 100
        }
    
    try:
        print(f"📡 发送测试请求到: {url}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API连接成功！")
            
            # 检查响应格式
            if provider == "anthropic":
                if 'content' in result:
                    print("✅ Anthropic API响应格式正确")
                    return True
                else:
                    print("❌ Anthropic API响应格式异常")
                    print(f"响应结构: {list(result.keys())}")
                    return False
            else:
                if 'choices' in result:
                    print("✅ OpenAI兼容API响应格式正确")
                    return True
                else:
                    print("❌ OpenAI兼容API响应格式异常")
                    print(f"响应结构: {list(result.keys())}")
                    print(f"完整响应: {result}")
                    return False
        else:
            print(f"❌ API连接失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_model_vision_support():
    """检查模型是否支持视觉功能"""
    print("\n👁️ 检查模型视觉支持...")
    
    config_manager = ConfigManager()
    model_name = config_manager.get_current_model()
    
    # 已知支持视觉的模型列表
    vision_models = [
        'gpt-4-vision-preview',
        'gpt-4o',
        'gpt-4o-mini',
        'claude-3-opus',
        'claude-3-sonnet',
        'claude-3-haiku',
        'claude-3-5-sonnet',
        'gemini-pro-vision',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'internvl',
        'qwen-vl'
    ]
    
    model_lower = model_name.lower()
    is_vision_model = any(vm in model_lower for vm in vision_models)
    
    if is_vision_model:
        print(f"✅ 模型 {model_name} 支持视觉功能")
        return True
    else:
        print(f"⚠️ 模型 {model_name} 可能不支持视觉功能")
        print("💡 建议使用支持视觉的模型，如：")
        print("   - GPT-4o, GPT-4o-mini")
        print("   - Claude-3.5-Sonnet")
        print("   - Gemini-1.5-Pro")
        print("   - InternVL系列")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n💡 常见问题解决方案:")
    print("=" * 50)
    
    print("1. 'choices' 字段缺失错误:")
    print("   - 检查模型是否支持视觉功能")
    print("   - 确认API密钥有效且有足够权限")
    print("   - 检查API端点URL是否正确")
    print("   - 尝试使用不同的模型")
    
    print("\n2. API连接失败:")
    print("   - 检查网络连接")
    print("   - 确认API密钥正确")
    print("   - 检查基础URL格式")
    print("   - 确认服务商选择正确")
    
    print("\n3. 模型不支持视觉:")
    print("   - 切换到支持视觉的模型")
    print("   - 检查模型名称是否正确")
    print("   - 确认API服务商支持该模型")
    
    print("\n4. 推荐配置:")
    print("   OpenRouter + InternVL3-14B:free (免费)")
    print("   OpenAI + GPT-4o-mini (付费)")
    print("   Anthropic + Claude-3.5-Sonnet (付费)")

def main():
    """主函数"""
    print("🔧 API配置诊断工具")
    print("=" * 50)
    
    # 步骤1: 检查配置
    config_ok = check_api_configuration()
    
    if not config_ok:
        print("\n❌ 配置检查失败，请先配置API")
        provide_solutions()
        return
    
    # 步骤2: 测试连接
    connection_ok = test_api_connection()
    
    # 步骤3: 检查模型支持
    vision_ok = check_model_vision_support()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 诊断总结:")
    print(f"配置检查: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"连接测试: {'✅ 通过' if connection_ok else '❌ 失败'}")
    print(f"视觉支持: {'✅ 支持' if vision_ok else '⚠️ 可能不支持'}")
    
    if config_ok and connection_ok and vision_ok:
        print("\n🎉 所有检查通过！API配置正常")
    else:
        print("\n⚠️ 发现问题，请参考解决方案")
        provide_solutions()

if __name__ == "__main__":
    main()
