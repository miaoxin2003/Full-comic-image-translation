# -*- coding: utf-8 -*-
"""
漫画全图翻译器 v2.1 - 稳定版
移除拖拽功能，确保稳定运行，保留所有其他功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
from PIL import Image, ImageTk
import json
import os
import requests
import base64
import threading
import datetime
import re

# 导入配置
import config
from config import config_manager

# 导入设置窗口（从原文件复制）
class SettingsWindow:
    """设置窗口"""
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.window = None
        self.create_window()
    
    def create_window(self):
        """创建设置窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("设置 - 漫画翻译器")
        self.window.geometry("700x600")
        self.window.resizable(True, True)
        
        # 设置窗口属性
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.create_all_tabs()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮
        ttk.Button(button_frame, text="重置默认", command=self.reset_defaults).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="保存", command=self.save_settings).pack(side=tk.RIGHT)
        
        # 居中显示窗口
        self.center_window()
    
    def create_all_tabs(self):
        """创建所有标签页"""
        try:
            # 标签页1: API服务商
            self.create_provider_tab()
            print("✅ API服务商标签页创建成功")
            
            # 标签页2: 模型设置
            self.create_model_tab()
            print("✅ 模型设置标签页创建成功")
            
            # 标签页3: 高级设置
            self.create_advanced_tab()
            print("✅ 高级设置标签页创建成功")
            
        except Exception as e:
            print(f"❌ 创建标签页时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def create_provider_tab(self):
        """创建API服务商标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="API服务商")
        
        # 服务商选择
        provider_frame = ttk.LabelFrame(frame, text="选择API服务商", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.provider_var = tk.StringVar(value=config_manager.config.get("api_provider", "openrouter"))
        
        providers = [
            ("OpenRouter", "openrouter"),
            ("OpenAI", "openai"),
            ("Anthropic", "anthropic"),
            ("自定义API", "custom")
        ]
        
        for text, value in providers:
            ttk.Radiobutton(provider_frame, text=text, variable=self.provider_var, 
                           value=value, command=self.on_provider_change).pack(anchor=tk.W, pady=2)
        
        # API配置框架
        self.config_frame = ttk.LabelFrame(frame, text="API配置", padding=10)
        self.config_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建配置输入框
        self.create_config_inputs()
    
    def create_model_tab(self):
        """创建模型设置标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="模型设置")
        
        # 模型选择区域
        model_frame = ttk.LabelFrame(frame, text="选择模型", padding=10)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 预设模型
        ttk.Label(model_frame, text="预设模型:").pack(anchor=tk.W)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       state="readonly", width=60)
        self.model_combo.pack(fill=tk.X, pady=(5, 10))
        
        # 自定义模型
        ttk.Label(model_frame, text="自定义模型 (输入完整模型名称):").pack(anchor=tk.W)
        self.custom_model_var = tk.StringVar()
        custom_entry = ttk.Entry(model_frame, textvariable=self.custom_model_var, width=60)
        custom_entry.pack(fill=tk.X, pady=(5, 10))
        
        # 提示文本
        tip_label = ttk.Label(model_frame, text="💡 提示: 可以输入任何OpenRouter支持的模型，如 opengvlab/internvl3-14b:free", 
                             foreground="blue")
        tip_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 模型信息
        info_frame = ttk.LabelFrame(frame, text="模型信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.model_info = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.model_info.pack(fill=tk.BOTH, expand=True)
        
        # 初始化模型列表
        self.update_model_list()
    
    def create_advanced_tab(self):
        """创建高级设置标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="高级设置")
        
        # 翻译设置
        translate_frame = ttk.LabelFrame(frame, text="翻译设置", padding=10)
        translate_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 目标语言
        ttk.Label(translate_frame, text="目标语言:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_lang_var = tk.StringVar(value="中文")
        lang_combo = ttk.Combobox(translate_frame, textvariable=self.target_lang_var,
                                 values=["中文", "日文", "韩文", "法文", "德文", "西班牙文"], 
                                 state="readonly", width=20)
        lang_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 翻译风格
        ttk.Label(translate_frame, text="翻译风格:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.style_var = tk.StringVar(value="自然")
        style_combo = ttk.Combobox(translate_frame, textvariable=self.style_var,
                                  values=["自然", "直译", "意译", "口语化", "正式"], 
                                  state="readonly", width=20)
        style_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 提示词设置
        prompt_frame = ttk.LabelFrame(frame, text="自定义提示词", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        
        # 设置默认提示词
        default_prompt = """请分析这张图片中的所有文本内容，包括对话气泡、标题、旁白、音效文字等。

要求：
1. 识别图片中的每一个文本块
2. 对每个文本块进行分类（如：对话、旁白、标题、音效等）
3. 将所有文本翻译成中文
4. 保持原文的语气和风格

请按以下JSON格式返回结果：
```json
[
  {
    "type": "对话气泡",
    "original_text": "原文内容",
    "translation": "中文翻译"
  }
]
```"""
        self.prompt_text.insert(1.0, default_prompt)
    
    def create_config_inputs(self):
        """创建配置输入框"""
        # 清空现有控件
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        
        provider = self.provider_var.get()
        provider_config = config_manager.config.get(provider, {})
        
        self.config_vars = {}
        
        if provider == "openrouter":
            fields = [
                ("API密钥", "api_key", True),
                ("基础URL", "base_url", False),
                ("HTTP Referer", "http_referer", False),
                ("X-Title", "x_title", False)
            ]
        elif provider == "openai":
            fields = [
                ("API密钥", "api_key", True),
                ("基础URL", "base_url", False),
                ("组织ID", "organization", False),
                ("项目ID", "project", False)
            ]
        elif provider == "anthropic":
            fields = [
                ("API密钥", "api_key", True),
                ("基础URL", "base_url", False),
                ("API版本", "version", False)
            ]
        else:  # custom
            fields = [
                ("API密钥", "api_key", True),
                ("基础URL", "base_url", True),
                ("自定义头信息", "headers", False)
            ]
        
        for i, (label, key, required) in enumerate(fields):
            ttk.Label(self.config_frame, text=f"{label}{'*' if required else ''}:").grid(
                row=i, column=0, sticky=tk.W, pady=5)
            
            if key == "headers":
                var = tk.StringVar(value=json.dumps(provider_config.get(key, {}), indent=2))
                entry = tk.Text(self.config_frame, height=3, width=40)
                entry.insert(1.0, var.get())
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
                self.config_vars[key] = entry
            else:
                var = tk.StringVar(value=provider_config.get(key, ""))
                entry = ttk.Entry(self.config_frame, textvariable=var, width=40)
                if key == "api_key":
                    entry.config(show="*")
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
                self.config_vars[key] = var
        
        self.config_frame.columnconfigure(1, weight=1)
    
    def on_provider_change(self):
        """服务商改变时的处理"""
        self.create_config_inputs()
        self.update_model_list()
    
    def update_model_list(self):
        """更新模型列表"""
        try:
            provider = self.provider_var.get()
            models = config_manager.config.get("available_models", {}).get(provider, [])
            
            if hasattr(self, 'model_combo'):
                self.model_combo['values'] = models
                
                # 设置当前模型
                current_model = config_manager.config.get(provider, {}).get("model_name", "")
                if current_model in models:
                    self.model_var.set(current_model)
                    self.custom_model_var.set("")
                elif models:
                    self.model_var.set(models[0])
                    self.custom_model_var.set("")
                else:
                    self.custom_model_var.set(current_model)
                    self.model_var.set("")
                
                self.show_model_info()
        except Exception as e:
            print(f"更新模型列表时出错: {e}")
    
    def show_model_info(self):
        """显示模型信息"""
        try:
            provider = self.provider_var.get()
            model = self.custom_model_var.get().strip() or self.model_var.get()
            
            info_text = f"当前配置:\n"
            info_text += f"服务商: {provider}\n"
            info_text += f"模型: {model}\n\n"
            
            if "internvl" in model.lower():
                info_text += "🎯 InternVL 系列模型:\n"
                info_text += "• 强大的视觉语言理解能力\n"
                info_text += "• 专为多模态任务优化\n"
                info_text += "• 适合漫画全图翻译\n"
                info_text += "• :free 后缀表示免费使用\n"
            elif "gemini" in model.lower():
                info_text += "🎯 Google Gemini 系列:\n"
                info_text += "• 支持图像和文本理解\n"
                info_text += "• 多语言支持良好\n"
                info_text += "• 适合全图翻译\n"
            else:
                info_text += "ℹ️ 自定义模型\n"
                info_text += "请确保模型支持视觉理解功能\n"
            
            if hasattr(self, 'model_info'):
                self.model_info.delete(1.0, tk.END)
                self.model_info.insert(1.0, info_text)
        except Exception as e:
            print(f"显示模型信息时出错: {e}")
    
    def get_selected_model(self):
        """获取当前选择的模型"""
        custom = self.custom_model_var.get().strip()
        return custom if custom else self.model_var.get()
    
    def center_window(self):
        """居中显示窗口"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def reset_defaults(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认重置", "确定要重置所有设置为默认值吗？\n这将清除所有自定义配置。"):
            config_manager.reset_to_default()
            messagebox.showinfo("重置完成", "设置已重置为默认值，请重新启动应用以生效。")
            self.window.destroy()
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存API服务商
            provider = self.provider_var.get()
            config_manager.update_provider(provider)
            
            # 保存API配置
            provider_updates = {}
            for key, var in self.config_vars.items():
                if isinstance(var, tk.Text):
                    value = var.get(1.0, tk.END).strip()
                    if key == "headers":
                        try:
                            provider_updates[key] = json.loads(value) if value else {}
                        except json.JSONDecodeError:
                            messagebox.showerror("错误", "自定义头信息格式错误，请使用有效的JSON格式")
                            return
                    else:
                        provider_updates[key] = value
                else:
                    provider_updates[key] = var.get()
            
            # 保存模型选择
            selected_model = self.get_selected_model()
            if selected_model:
                provider_updates["model_name"] = selected_model
            
            config_manager.update_provider_config(provider, provider_updates)
            
            messagebox.showinfo("保存成功", "设置已保存！")
            
            if self.callback:
                self.callback()
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("保存失败", f"保存设置时发生错误: {e}")
    
    def cancel(self):
        """取消设置"""
        self.window.destroy()


class ComicTranslatorStableApp:
    """漫画全图翻译器主应用 - 稳定版（无拖拽功能）"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("漫画全图翻译器 v2.1 - 稳定版")
        self.root.geometry("1600x1000")
        
        # 应用状态
        self.image_list = []  # 存储所有图片路径
        self.current_image_index = 0  # 当前显示的图片索引
        self.current_image = None
        self.all_translation_results = {}  # 存储所有图片的翻译结果 {image_path: results}
        self.is_translating = False
        self.is_batch_translating = False
        
        # 图片显示相关状态
        self.photo = None  # 当前显示的图片对象
        self.image_scale = 1.0  # 图片缩放比例
        self.image_offset_x = 0  # 图片X偏移
        self.image_offset_y = 0  # 图片Y偏移
        self.drag_start_x = 0  # 拖拽起始X坐标
        self.drag_start_y = 0  # 拖拽起始Y坐标
        self.original_pil_image = None  # 原始PIL图片对象

        # 创建UI
        self.create_ui()

        # 显示当前配置
        self.update_status_with_config()
        
        print("✅ 稳定版漫画翻译器启动成功")
        print("💡 使用 '选择多张图片' 按钮批量添加图片")
