#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试响应解析功能
验证翻译响应解析是否正确
"""

import json
import re

def parse_translation_response(content):
    """解析翻译响应 - 测试版本"""
    try:
        print(f"🔍 开始解析响应，内容长度: {len(content)}")
        
        # 尝试多种方式提取JSON部分
        json_str = None
        
        # 方法1: 查找JSON代码块
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("✅ 找到JSON代码块")
        else:
            # 方法2: 查找数组格式 [...]
            array_match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
            if array_match:
                json_str = array_match.group(0)
                print("✅ 找到JSON数组")
            else:
                # 方法3: 尝试直接解析整个内容
                json_str = content.strip()
                print("⚠️ 尝试直接解析内容")

        if not json_str:
            print("❌ 无法找到JSON内容")
            return []

        # 清理JSON字符串
        json_str = json_str.strip()
        
        # 解析JSON
        results = json.loads(json_str)
        print(f"✅ JSON解析成功，找到 {len(results) if isinstance(results, list) else 1} 个项目")

        # 验证结果格式
        if isinstance(results, list):
            validated_results = []
            for item in results:
                if isinstance(item, dict) and 'original_text' in item and 'translation' in item:
                    validated_results.append({
                        'type': item.get('type', '未分类'),
                        'original_text': item.get('original_text', ''),
                        'translation': item.get('translation', '')
                    })
            print(f"✅ 验证完成，有效项目: {len(validated_results)}")
            return validated_results
        else:
            # 如果不是列表格式，尝试转换
            if isinstance(results, dict):
                return [results]

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"📄 尝试解析的内容: {json_str[:200]}...")
        return []

    except Exception as e:
        print(f"❌ 解析响应时出错: {e}")
        return []

def test_cases():
    """测试用例"""
    
    # 测试用例1: 正确的JSON格式
    test1 = '''```json
[
  {
    "type": "对话气泡",
    "original_text": "Hello world",
    "translation": "你好世界"
  },
  {
    "type": "旁白",
    "original_text": "This is a test",
    "translation": "这是一个测试"
  }
]
```'''
    
    # 测试用例2: 您遇到的错误格式
    test2 = '''【文本块 1】 - 翻译结果
原文: 图片内容
译文: ```json
[
  {
    "type": "对话气泡",
    "original_text": "D-DON'T MOVE, PELLA!",
    "translation": "不要动，佩拉！"
  },
  {
    "type": "对话气泡",
    "original_text": "ONLY ONE'S LEFT.",
    "translation": "只剩下一个了。"
  }
]
```'''
    
    # 测试用例3: 直接的JSON数组
    test3 = '''[
  {
    "type": "对话气泡",
    "original_text": "Test message",
    "translation": "测试消息"
  }
]'''
    
    test_cases = [
        ("正确的JSON格式", test1),
        ("错误的包装格式", test2),
        ("直接JSON数组", test3)
    ]
    
    for name, content in test_cases:
        print(f"\n{'='*50}")
        print(f"🧪 测试: {name}")
        print(f"{'='*50}")
        
        results = parse_translation_response(content)
        
        print(f"\n📊 解析结果:")
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. 类型: {result['type']}")
                print(f"     原文: {result['original_text']}")
                print(f"     译文: {result['translation']}")
        else:
            print("  ❌ 没有解析到有效结果")

def main():
    """主函数"""
    print("🔧 翻译响应解析测试")
    print("测试修复后的解析逻辑是否能正确处理各种格式")
    
    test_cases()
    
    print(f"\n{'='*50}")
    print("📋 测试总结:")
    print("1. 正确的JSON格式应该能正常解析")
    print("2. 错误的包装格式应该能提取内部JSON")
    print("3. 直接JSON数组应该能直接解析")
    print("\n💡 如果所有测试都通过，说明修复成功！")

if __name__ == "__main__":
    main()
