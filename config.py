# -*- coding: utf-8 -*-
"""
配置文件
包含API密钥、模型配置和提示词模板
"""

import json
import os
from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG = {
    # API服务商配置
    "api_provider": "openrouter",  # openrouter, openai, anthropic, custom

    # OpenRouter配置
    "openrouter": {
        "api_key": "*************************************************************",
        "base_url": "https://openrouter.ai/api/v1",
        "model_name": "google/gemini-2.5-pro-preview",
        "http_referer": "<YOUR_SITE_URL>",
        "x_title": "<YOUR_SITE_NAME>"
    },

    # OpenAI配置
    "openai": {
        "api_key": "<OPENAI_API_KEY>",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4-vision-preview",
        "organization": "",
        "project": ""
    },

    # Anthropic配置
    "anthropic": {
        "api_key": "<ANTHROPIC_API_KEY>",
        "base_url": "https://api.anthropic.com",
        "model_name": "claude-3-5-sonnet-20241022",
        "version": "2023-06-01"
    },

    # 自定义API配置
    "custom": {
        "api_key": "<CUSTOM_API_KEY>",
        "base_url": "https://your-api-endpoint.com/v1",
        "model_name": "your-model-name",
        "headers": {}
    },

    # 模型选项
    "available_models": {
        "openrouter": [
            "google/gemini-2.5-pro-preview",
            "google/gemini-pro-vision",
            "openai/gpt-4-vision-preview",
            "openai/gpt-4o",
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-3-opus",
            "meta-llama/llama-3.2-90b-vision-instruct",
            "qwen/qwen-2-vl-72b-instruct",
            "opengvlab/internvl3-14b:free",
            "opengvlab/internvl2-8b",
            "opengvlab/internvl2-26b",
            "opengvlab/internvl2-40b"
        ],
        "openai": [
            "gpt-4-vision-preview",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo"
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "custom": [
            "your-model-name"
        ]
    }
}

# 配置文件路径
CONFIG_FILE = "user_config.json"

class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # 合并默认配置和用户配置
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()

    def get_current_provider_config(self) -> Dict[str, Any]:
        """获取当前服务商的配置"""
        provider = self.config.get("api_provider", "openrouter")
        return self.config.get(provider, {})

    def get_current_api_key(self) -> str:
        """获取当前API密钥"""
        provider_config = self.get_current_provider_config()
        return provider_config.get("api_key", "")

    def get_current_base_url(self) -> str:
        """获取当前API基础URL"""
        provider_config = self.get_current_provider_config()
        return provider_config.get("base_url", "")

    def get_current_model(self) -> str:
        """获取当前模型名称"""
        provider_config = self.get_current_provider_config()
        return provider_config.get("model_name", "")

    def get_available_models(self) -> list:
        """获取当前服务商可用的模型列表"""
        provider = self.config.get("api_provider", "openrouter")
        return self.config.get("available_models", {}).get(provider, [])

    def update_provider(self, provider: str):
        """更新API服务商"""
        self.config["api_provider"] = provider
        self.save_config()

    def update_provider_config(self, provider: str, config_updates: Dict[str, Any]):
        """更新特定服务商的配置"""
        if provider not in self.config:
            self.config[provider] = {}
        self.config[provider].update(config_updates)
        self.save_config()

# 创建全局配置管理器实例
config_manager = ConfigManager()

# 为了向后兼容，保留原有的变量名
OPENROUTER_API_KEY = config_manager.get_current_api_key()
OPENROUTER_BASE_URL = config_manager.get_current_base_url()
MODEL_NAME = config_manager.get_current_model()
HTTP_REFERER = config_manager.get_current_provider_config().get("http_referer", "<YOUR_SITE_URL>")
X_TITLE = config_manager.get_current_provider_config().get("x_title", "<YOUR_SITE_NAME>")

# AI识别提示词模板
PROMPT_TEMPLATE = """请仔细识别这张漫画图片中的英文对话框区域。

重要要求：
1. 只识别有明确边界的对话气泡或对话框（通常有白色或浅色背景）
2. 不要识别叙述文本框（通常是黄色背景的说明文字）
3. 不要识别标题或作者信息
4. 每个对话框应该紧贴文字边界，不要包含过多空白区域
5. 确保坐标准确，基于图片实际像素大小：{width}x{height}

请以JSON格式返回结果：
[
    {{
        "box_2d": [x1, y1, x2, y2],
        "text_content": "对话框内的英文文本",
        "type": "dialogue"
    }}
]

其中：
- x1, y1 是对话框左上角坐标
- x2, y2 是对话框右下角坐标
- text_content 是对话框内的完整英文文本
- type 固定为 "dialogue"
- 坐标必须精确到文字边界
"""

# OpenCV绘制配置
BBOX_COLOR = (0, 0, 255)  # 红色边框 (BGR格式)
BBOX_THICKNESS = 2        # 边框粗细
FONT_SCALE = 0.6         # 文字大小
FONT_THICKNESS = 1       # 文字粗细
TEXT_COLOR = (0, 255, 0) # 绿色文字 (BGR格式)

# 输出文件配置
OUTPUT_SUFFIX = "_detected"  # 输出文件后缀
SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']  # 支持的图片格式
