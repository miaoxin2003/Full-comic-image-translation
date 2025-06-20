# -*- coding: utf-8 -*-
"""
主程序文件
整合AI识别和图像处理功能
"""

import os
import sys
import argparse
import json
from typing import List, Dict
from ai_client import AIClient
from image_processor import ImageProcessor
import config


class TextDetectionApp:
    """文本检测应用主类"""
    
    def __init__(self, api_key: str = None):
        """
        初始化应用
        
        Args:
            api_key: OpenRouter API密钥
        """
        self.ai_client = AIClient(api_key)
        self.image_processor = ImageProcessor()
    
    def validate_image_file(self, image_path: str) -> bool:
        """
        验证图片文件是否有效
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            文件是否有效
        """
        if not os.path.exists(image_path):
            print(f"错误: 图片文件不存在: {image_path}")
            return False
        
        _, ext = os.path.splitext(image_path.lower())
        if ext not in config.SUPPORTED_FORMATS:
            print(f"错误: 不支持的图片格式: {ext}")
            print(f"支持的格式: {', '.join(config.SUPPORTED_FORMATS)}")
            return False
        
        return True
    
    def process_single_image(self, image_path: str, output_path: str = None, save_json: bool = False) -> Dict:
        """
        处理单张图片
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径（可选）
            save_json: 是否保存检测结果为JSON文件
            
        Returns:
            处理结果字典
        """
        result = {
            'success': False,
            'input_path': image_path,
            'output_path': None,
            'detections': [],
            'error': None
        }
        
        try:
            print(f"开始处理图片: {image_path}")
            
            # 验证输入文件
            if not self.validate_image_file(image_path):
                result['error'] = "输入文件验证失败"
                return result
            
            # AI检测文本区域
            print("正在调用AI模型检测文本区域...")
            detections = self.ai_client.detect_text_regions(image_path)
            
            if not detections:
                print("警告: 未检测到任何文本区域")
                result['error'] = "未检测到文本区域"
                return result
            
            print(f"检测到 {len(detections)} 个文本区域")
            result['detections'] = detections
            
            # 图像处理和绘制边框
            print("正在绘制检测结果...")
            output_image_path = self.image_processor.process_image(
                image_path, detections, output_path
            )
            result['output_path'] = output_image_path
            
            # 保存JSON结果（可选）
            if save_json:
                json_path = self.save_detection_results(image_path, detections)
                print(f"检测结果已保存到: {json_path}")
            
            result['success'] = True
            print("处理完成!")
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {e}"
            print(error_msg)
            result['error'] = error_msg
        
        return result
    
    def save_detection_results(self, image_path: str, detections: List[Dict]) -> str:
        """
        保存检测结果为JSON文件
        
        Args:
            image_path: 原始图片路径
            detections: 检测结果列表
            
        Returns:
            JSON文件路径
        """
        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        name, _ = os.path.splitext(base_name)
        
        json_path = os.path.join(dir_name, f"{name}_detections.json")
        
        # 准备保存的数据
        save_data = {
            'image_path': image_path,
            'image_size': self.ai_client.get_image_size(image_path),
            'detection_count': len(detections),
            'detections': detections,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return json_path
    
    def print_detection_summary(self, detections: List[Dict]):
        """
        打印检测结果摘要
        
        Args:
            detections: 检测结果列表
        """
        print("\n" + "="*50)
        print("检测结果摘要:")
        print("="*50)
        
        for i, detection in enumerate(detections, 1):
            box_2d = detection.get('box_2d', [])
            text_content = detection.get('text_content', '')
            
            print(f"\n区域 #{i}:")
            print(f"  坐标: {box_2d}")
            print(f"  文本: {text_content[:100]}...")  # 限制显示长度
        
        print("\n" + "="*50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI文本区域检测工具')
    parser.add_argument('image_path', help='输入图片路径')
    parser.add_argument('-o', '--output', help='输出图片路径（可选）')
    parser.add_argument('-k', '--api-key', help='OpenRouter API密钥')
    parser.add_argument('--save-json', action='store_true', help='保存检测结果为JSON文件')
    parser.add_argument('--no-summary', action='store_true', help='不显示检测结果摘要')
    
    args = parser.parse_args()
    
    # 检查API密钥
    api_key = args.api_key or config.OPENROUTER_API_KEY
    if api_key == "<OPENROUTER_API_KEY>":
        print("错误: 请在config.py中设置有效的OPENROUTER_API_KEY，或使用-k参数提供API密钥")
        sys.exit(1)
    
    # 创建应用实例
    app = TextDetectionApp(api_key)
    
    # 处理图片
    result = app.process_single_image(
        args.image_path,
        args.output,
        args.save_json
    )
    
    # 显示结果
    if result['success']:
        print(f"\n✅ 处理成功!")
        print(f"输入文件: {result['input_path']}")
        print(f"输出文件: {result['output_path']}")
        print(f"检测到 {len(result['detections'])} 个文本区域")
        
        if not args.no_summary and result['detections']:
            app.print_detection_summary(result['detections'])
    else:
        print(f"\n❌ 处理失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
