#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI响应调试工具
帮助诊断翻译响应解析问题
"""

import json
import re
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyze_response(content):
    """分析AI响应内容"""
    print("🔍 AI响应内容分析")
    print("=" * 60)
    
    print(f"📊 基本信息:")
    print(f"  内容长度: {len(content)} 字符")
    print(f"  行数: {len(content.splitlines())}")
    print(f"  是否包含JSON标记: {'```json' in content}")
    print(f"  是否包含数组: {content.strip().startswith('[') and content.strip().endswith(']')}")
    print(f"  是否包含大括号: {'{' in content and '}' in content}")
    
    print(f"\n📄 内容预览 (前500字符):")
    print("-" * 40)
    print(content[:500])
    if len(content) > 500:
        print("...")
    print("-" * 40)
    
    # 尝试各种解析方法
    print(f"\n🔧 解析尝试:")
    
    # 方法1: JSON代码块
    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
    if json_match:
        json_content = json_match.group(1)
        print(f"✅ 方法1 - 找到JSON代码块，长度: {len(json_content)}")
        print(f"   内容预览: {json_content[:100]}...")
        try:
            parsed = json.loads(json_content)
            print(f"   ✅ JSON解析成功，类型: {type(parsed)}")
            if isinstance(parsed, list):
                print(f"   📋 数组长度: {len(parsed)}")
                for i, item in enumerate(parsed[:3]):  # 只显示前3个
                    if isinstance(item, dict):
                        print(f"   [{i}] 键: {list(item.keys())}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
    else:
        print("❌ 方法1 - 未找到JSON代码块")
    
    # 方法2: 数组格式
    array_match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
    if array_match:
        array_content = array_match.group(0)
        print(f"✅ 方法2 - 找到JSON数组，长度: {len(array_content)}")
        print(f"   内容预览: {array_content[:100]}...")
        try:
            parsed = json.loads(array_content)
            print(f"   ✅ JSON解析成功，类型: {type(parsed)}")
            if isinstance(parsed, list):
                print(f"   📋 数组长度: {len(parsed)}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
    else:
        print("❌ 方法2 - 未找到JSON数组")
    
    # 方法3: 直接解析
    content_clean = content.strip()
    if content_clean.startswith('[') or content_clean.startswith('{'):
        print(f"✅ 方法3 - 尝试直接解析，长度: {len(content_clean)}")
        try:
            parsed = json.loads(content_clean)
            print(f"   ✅ JSON解析成功，类型: {type(parsed)}")
            return parsed
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
            print(f"   错误位置: 第{e.lineno}行，第{e.colno}列")
    else:
        print("❌ 方法3 - 内容不以JSON字符开始")
    
    print("\n❌ 所有JSON解析方法都失败了")
    return None

def suggest_fixes(content):
    """建议修复方案"""
    print("\n💡 修复建议:")
    print("=" * 60)
    
    if '```json' not in content and '[' not in content and '{' not in content:
        print("1. 🎯 提示词问题 - AI没有返回JSON格式")
        print("   建议: 检查并优化提示词，确保明确要求JSON格式")
        print("   示例提示词:")
        print("   '请严格按照以下JSON格式返回，不要添加任何其他文字：'")
        
    elif '```json' in content:
        print("1. 📝 JSON代码块格式问题")
        print("   建议: 检查JSON代码块内容是否完整和正确")
        
    elif len(content) > 1000:
        print("1. 📏 响应内容过长")
        print("   建议: 可能包含多余的解释文字，需要优化提示词")
        
    else:
        print("1. 🔧 JSON格式错误")
        print("   建议: 检查JSON语法是否正确")
    
    print("\n2. 🛠️ 通用解决方案:")
    print("   - 尝试更换AI模型")
    print("   - 简化提示词")
    print("   - 检查API配置")
    print("   - 重试翻译")

def test_with_sample():
    """使用示例数据测试"""
    print("\n🧪 使用示例数据测试解析功能:")
    print("=" * 60)
    
    # 正确格式示例
    good_example = '''```json
[
  {
    "type": "对话气泡",
    "original_text": "Hello world",
    "translation": "你好世界"
  }
]
```'''
    
    print("测试正确格式:")
    result = analyze_response(good_example)
    if result:
        print("✅ 正确格式解析成功")
    else:
        print("❌ 正确格式解析失败")

def main():
    """主函数"""
    print("🔧 AI响应调试工具")
    print("帮助诊断翻译响应解析问题")
    print("=" * 60)
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 从文件读取
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"📁 从文件读取: {file_path}")
        else:
            print(f"❌ 文件不存在: {file_path}")
            return
    else:
        # 交互式输入
        print("请输入AI响应内容 (输入'END'结束):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n用户取消输入")
                return
            except EOFError:
                break
        
        content = '\n'.join(lines)
        
        if not content.strip():
            print("❌ 没有输入内容")
            return
    
    # 分析响应
    result = analyze_response(content)
    
    # 提供建议
    suggest_fixes(content)
    
    # 测试示例
    test_with_sample()
    
    print(f"\n{'='*60}")
    if result:
        print("🎉 解析成功！问题可能已解决。")
    else:
        print("❌ 解析失败，请根据上述建议进行修复。")

if __name__ == "__main__":
    main()
