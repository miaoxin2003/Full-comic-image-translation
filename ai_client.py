# -*- coding: utf-8 -*-
"""
AI客户端模块
负责调用OpenRouter API进行图像识别
"""

import json
import base64
import re
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from PIL import Image
import config


class AIClient:
    """AI客户端类，用于调用OpenRouter API识别图片中的英文对话区域"""
    
    def __init__(self, api_key: str = None):
        """
        初始化AI客户端
        
        Args:
            api_key: OpenRouter API密钥，如果不提供则使用config中的默认值
        """
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=self.api_key,
        )
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将图片文件编码为base64字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_image_size(self, image_path: str) -> Tuple[int, int]:
        """
        获取图片的实际尺寸
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            (width, height) 图片宽度和高度
        """
        with Image.open(image_path) as img:
            return img.size
    
    def create_prompt(self, image_path: str) -> str:
        """
        根据图片尺寸创建提示词
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            格式化的提示词
        """
        width, height = self.get_image_size(image_path)
        return config.PROMPT_TEMPLATE.format(width=width, height=height)
    
    def detect_text_regions(self, image_path: str) -> List[Dict]:
        """
        调用AI模型检测图片中的英文对话区域
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            检测结果列表，每个元素包含box_2d和text_content
        """
        try:
            # 编码图片
            base64_image = self.encode_image_to_base64(image_path)
            image_url = f"data:image/jpeg;base64,{base64_image}"
            
            # 创建提示词
            prompt = self.create_prompt(image_path)
            
            # 调用API
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": config.HTTP_REFERER,
                    "X-Title": config.X_TITLE,
                },
                extra_body={},
                model=config.MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            )
            
            # 解析响应
            response_content = completion.choices[0].message.content
            return self.parse_response(response_content)
            
        except Exception as e:
            print(f"AI检测过程中发生错误: {e}")
            return []
    
    def parse_response(self, response_content: str) -> List[Dict]:
        """
        解析AI响应内容，提取JSON格式的检测结果

        Args:
            response_content: AI返回的原始响应内容

        Returns:
            解析后的检测结果列表
        """
        try:
            # 清理响应内容，移除markdown代码块标记
            cleaned_content = response_content.strip()

            # 移除```json和```标记
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]  # 移除```json
            elif cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]   # 移除```

            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]  # 移除结尾的```

            cleaned_content = cleaned_content.strip()

            # 尝试直接解析JSON
            if cleaned_content.startswith('['):
                return json.loads(cleaned_content)

            # 如果不是直接的JSON，尝试从文本中提取JSON部分
            json_pattern = r'\[.*?\]'
            json_matches = re.findall(json_pattern, cleaned_content, re.DOTALL)

            if json_matches:
                # 取最长的匹配项（通常是完整的JSON）
                json_str = max(json_matches, key=len)
                return json.loads(json_str)

            # 如果找不到JSON格式，返回空列表
            print("警告: 无法从AI响应中解析出有效的JSON格式")
            print(f"原始响应: {response_content}")
            return []

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始响应: {response_content}")
            return []
        except Exception as e:
            print(f"响应解析过程中发生错误: {e}")
            return []
