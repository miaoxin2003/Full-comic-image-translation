# -*- coding: utf-8 -*-
"""
漫画翻译器 - 完整的GUI应用
整合AI识别、手动调整、翻译等所有功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os
import requests
import base64
from typing import List, Dict, Tuple
import threading
import datetime

# 导入配置
import config
from config import config_manager

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
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # 设置窗口图标和属性
        self.window.transient(self.parent)
        self.window.grab_set()

        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 创建所有标签页（带异常处理）
        try:
            # API服务商标签页
            self.create_provider_tab(notebook)
            print("✅ API服务商标签页创建成功")

            # 模型设置标签页
            self.create_model_tab(notebook)
            print("✅ 模型设置标签页创建成功")

            # 高级设置标签页
            self.create_advanced_tab(notebook)
            print("✅ 高级设置标签页创建成功")
        except Exception as e:
            print(f"❌ 创建标签页时出错: {e}")
            import traceback
            traceback.print_exc()
            # 创建一个错误提示标签页
            error_frame = ttk.Frame(notebook)
            notebook.add(error_frame, text="错误信息")
            ttk.Label(error_frame, text=f"创建设置界面时出错: {e}").pack(pady=20)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 按钮
        ttk.Button(button_frame, text="重置默认", command=self.reset_defaults).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="保存", command=self.save_settings).pack(side=tk.RIGHT)

        # 居中显示窗口
        self.center_window()

    def create_provider_tab(self, notebook):
        """创建API服务商标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="API服务商")

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

        # 初始化显示
        self.on_provider_change()

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
                row=i, column=0, sticky=tk.W, pady=2)

            if key == "headers":
                # 特殊处理headers字段
                var = tk.StringVar(value=json.dumps(provider_config.get(key, {}), indent=2))
                entry = tk.Text(self.config_frame, height=3, width=40)
                entry.insert(1.0, var.get())
                entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
                self.config_vars[key] = entry
            else:
                var = tk.StringVar(value=provider_config.get(key, ""))
                entry = ttk.Entry(self.config_frame, textvariable=var, width=40)
                if key == "api_key":
                    entry.config(show="*")  # 隐藏API密钥
                entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
                self.config_vars[key] = var

        # 配置列权重
        self.config_frame.columnconfigure(1, weight=1)

    def create_model_tab(self, notebook):
        """创建模型设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="模型设置")

        # 模型选择
        model_frame = ttk.LabelFrame(frame, text="选择模型", padding=10)
        model_frame.pack(fill=tk.X, pady=(0, 10))

        # 预设模型选择
        ttk.Label(model_frame, text="预设模型:").pack(anchor=tk.W)

        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                       state="readonly", width=50)
        self.model_combo.pack(fill=tk.X, pady=(5, 0))
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_select)

        # 自定义模型输入
        ttk.Label(model_frame, text="或输入自定义模型名称:").pack(anchor=tk.W, pady=(10, 0))

        self.custom_model_var = tk.StringVar()
        custom_model_entry = ttk.Entry(model_frame, textvariable=self.custom_model_var, width=50)
        custom_model_entry.pack(fill=tk.X, pady=(5, 0))
        custom_model_entry.bind("<KeyRelease>", self.on_custom_model_change)

        # 使用自定义模型按钮
        ttk.Button(model_frame, text="使用自定义模型",
                  command=self.use_custom_model).pack(pady=(5, 0))

        # 模型信息
        info_frame = ttk.LabelFrame(frame, text="模型信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.model_info = scrolledtext.ScrolledText(info_frame, height=8, wrap=tk.WORD)
        self.model_info.pack(fill=tk.BOTH, expand=True)

        # 更新模型列表（放在最后，避免在控件创建前调用）
        try:
            self.update_model_list()
            # 显示模型信息
            self.show_model_info()
        except Exception as e:
            print(f"初始化模型设置时出错: {e}")
            # 显示错误信息
            if hasattr(self, 'model_info'):
                self.model_info.insert(1.0, f"初始化出错: {e}")

    def create_advanced_tab(self, notebook):
        """创建高级设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="高级设置")

        # 提示词设置
        prompt_frame = ttk.LabelFrame(frame, text="AI检测提示词", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)
        self.prompt_text.insert(1.0, config.PROMPT_TEMPLATE)

        # 翻译设置
        translate_frame = ttk.LabelFrame(frame, text="翻译设置", padding=10)
        translate_frame.pack(fill=tk.X)

        # 目标语言
        ttk.Label(translate_frame, text="目标语言:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.target_lang_var = tk.StringVar(value="中文")
        lang_combo = ttk.Combobox(translate_frame, textvariable=self.target_lang_var,
                                 values=["中文", "日文", "韩文", "法文", "德文", "西班牙文"],
                                 state="readonly", width=20)
        lang_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))

        # 翻译风格
        ttk.Label(translate_frame, text="翻译风格:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.style_var = tk.StringVar(value="自然")
        style_combo = ttk.Combobox(translate_frame, textvariable=self.style_var,
                                  values=["自然", "直译", "意译", "口语化", "正式"],
                                  state="readonly", width=20)
        style_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))

    def on_provider_change(self):
        """服务商改变时的处理"""
        self.create_config_inputs()
        self.update_model_list()

    def update_model_list(self):
        """更新模型列表"""
        try:
            provider = self.provider_var.get()
            models = config_manager.config.get("available_models", {}).get(provider, [])

            # 确保model_combo存在
            if hasattr(self, 'model_combo'):
                self.model_combo['values'] = models

            # 设置当前模型
            current_model = config_manager.config.get(provider, {}).get("model_name", "")
            if current_model in models:
                if hasattr(self, 'model_var'):
                    self.model_var.set(current_model)
                if hasattr(self, 'custom_model_var'):
                    self.custom_model_var.set("")  # 清空自定义模型输入
            elif models:
                if hasattr(self, 'model_var'):
                    self.model_var.set(models[0])
                if hasattr(self, 'custom_model_var'):
                    self.custom_model_var.set("")
            else:
                # 如果当前模型不在预设列表中，显示在自定义输入框中
                if hasattr(self, 'custom_model_var'):
                    self.custom_model_var.set(current_model)
                if hasattr(self, 'model_var'):
                    self.model_var.set("")
        except Exception as e:
            print(f"更新模型列表时出错: {e}")
            # 继续执行，不中断标签页创建

    def on_model_select(self, event=None):
        """预设模型选择事件"""
        if self.model_var.get():
            self.custom_model_var.set("")  # 清空自定义输入
            self.show_model_info()

    def on_custom_model_change(self, event=None):
        """自定义模型输入变化事件"""
        if self.custom_model_var.get():
            self.model_var.set("")  # 清空预设选择
            self.show_model_info()

    def use_custom_model(self):
        """使用自定义模型"""
        custom_model = self.custom_model_var.get().strip()
        if not custom_model:
            messagebox.showwarning("警告", "请输入自定义模型名称")
            return

        # 清空预设选择
        self.model_var.set("")

        # 显示确认信息
        messagebox.showinfo("自定义模型", f"已设置自定义模型: {custom_model}")
        self.show_model_info()

    def get_selected_model(self):
        """获取当前选择的模型"""
        if self.custom_model_var.get().strip():
            return self.custom_model_var.get().strip()
        else:
            return self.model_var.get()

    def show_model_info(self):
        """显示模型信息"""
        try:
            provider = self.provider_var.get()
            model = self.get_selected_model()

            info_text = f"服务商: {provider}\n"
            info_text += f"模型: {model}\n\n"

            # 根据不同服务商和模型显示相关信息
            if provider == "openrouter":
                info_text += "OpenRouter 是一个AI模型聚合平台，提供多种模型选择。\n\n"
                if "gemini" in model.lower():
                    info_text += "Google Gemini 系列模型:\n"
                    info_text += "- 支持图像和文本理解\n"
                    info_text += "- 适合漫画对话框检测\n"
                    info_text += "- 多语言支持良好\n"
                elif "gpt" in model.lower():
                    info_text += "OpenAI GPT 系列模型:\n"
                    info_text += "- 强大的文本理解能力\n"
                    info_text += "- 优秀的翻译质量\n"
                    info_text += "- 支持视觉理解\n"
                elif "claude" in model.lower():
                    info_text += "Anthropic Claude 系列模型:\n"
                    info_text += "- 安全可靠的AI助手\n"
                    info_text += "- 优秀的推理能力\n"
                    info_text += "- 支持长文本处理\n"
                elif "internvl" in model.lower():
                    info_text += "OpenGVLab InternVL 系列模型:\n"
                    info_text += "- 强大的视觉语言理解能力\n"
                    info_text += "- 支持多模态任务\n"
                    info_text += "- 适合图像分析和对话框检测\n"
                    info_text += "- 免费模型，性价比高\n"
                elif "llama" in model.lower():
                    info_text += "Meta Llama 系列模型:\n"
                    info_text += "- 开源大语言模型\n"
                    info_text += "- 支持视觉理解\n"
                    info_text += "- 多语言支持\n"
                elif "qwen" in model.lower():
                    info_text += "阿里巴巴 Qwen 系列模型:\n"
                    info_text += "- 中文理解能力强\n"
                    info_text += "- 支持视觉语言任务\n"
                    info_text += "- 适合中文翻译\n"
                else:
                    info_text += "自定义模型:\n"
                    info_text += "- 请确保模型支持视觉理解\n"
                    info_text += "- 检查API兼容性\n"
            elif provider == "openai":
                info_text += "OpenAI 官方API，提供最新的GPT模型。\n"
                info_text += "需要OpenAI账户和API密钥。\n"
            elif provider == "anthropic":
                info_text += "Anthropic 官方API，提供Claude系列模型。\n"
                info_text += "需要Anthropic账户和API密钥。\n"
            else:
                info_text += "自定义API配置，请确保API兼容OpenAI格式。\n"

            if hasattr(self, 'model_info'):
                self.model_info.delete(1.0, tk.END)
                self.model_info.insert(1.0, info_text)
        except Exception as e:
            print(f"显示模型信息时出错: {e}")
            # 继续执行，不中断程序

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
                    # 处理Text控件（如headers）
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
                    # 处理StringVar
                    provider_updates[key] = var.get()

            # 保存模型选择（支持自定义模型）
            if hasattr(self, 'model_var'):
                selected_model = self.get_selected_model()
                provider_updates["model_name"] = selected_model

            config_manager.update_provider_config(provider, provider_updates)

            # 保存提示词
            if hasattr(self, 'prompt_text'):
                new_prompt = self.prompt_text.get(1.0, tk.END).strip()
                if new_prompt:
                    config.PROMPT_TEMPLATE = new_prompt

            messagebox.showinfo("保存成功", "设置已保存！")

            # 调用回调函数通知主应用
            if self.callback:
                self.callback()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("保存失败", f"保存设置时发生错误: {e}")

    def cancel(self):
        """取消设置"""
        self.window.destroy()

class ComicTranslatorApp:
    """漫画翻译器主应用 - 全图翻译版"""

    def __init__(self, root):
        self.root = root
        self.root.title("漫画翻译器 v2.0 - 全图翻译版")
        self.root.geometry("1400x900")

        # 应用状态
        self.current_image_path = None
        self.current_image = None
        self.translation_results = []  # 存储翻译结果
        self.is_translating = False

        # 创建UI
        self.create_ui()

        # 显示当前配置
        self.update_status_with_config()
    
    def create_ui(self):
        """创建用户界面 - 全图翻译版"""

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部控制面板
        top_panel = ttk.Frame(main_frame, height=80)
        top_panel.pack(fill=tk.X, pady=(0, 10))
        top_panel.pack_propagate(False)

        # 中间内容区域 - 分为左右两部分
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧 - 图片显示区域
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 右侧 - 翻译结果区域
        right_panel = ttk.Frame(content_frame, width=500)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)

        self.create_top_panel(top_panel)
        self.create_image_panel(left_panel)
        self.create_translation_panel(right_panel)
    
    def create_top_panel(self, parent):
        """创建顶部控制面板"""

        # 文件操作区域
        file_frame = ttk.LabelFrame(parent, text="文件操作", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(file_frame, text="选择图片", command=self.select_image, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="设置", command=self.open_settings, width=8).pack(side=tk.LEFT, padx=2)

        # AI翻译区域
        ai_frame = ttk.LabelFrame(parent, text="AI翻译", padding=10)
        ai_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.translate_btn = ttk.Button(ai_frame, text="开始全图翻译", command=self.start_full_translation, width=15)
        self.translate_btn.pack(side=tk.LEFT, padx=2)

        self.progress = ttk.Progressbar(ai_frame, mode='indeterminate', width=200)
        self.progress.pack(side=tk.LEFT, padx=2)

        # 导出区域
        export_frame = ttk.LabelFrame(parent, text="导出结果", padding=10)
        export_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(export_frame, text="保存翻译", command=self.save_translation_results, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="清空结果", command=self.clear_results, width=12).pack(side=tk.LEFT, padx=2)

        # 状态显示
        status_frame = ttk.LabelFrame(parent, text="状态", padding=10)
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar()
        self.status_var.set("请选择图片文件")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(expand=True)
    
    def create_image_panel(self, parent):
        """创建图片显示面板"""

        # 图片显示标题
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(title_frame, text="原图预览", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # 图片显示区域
        self.image_frame = ttk.Frame(parent)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布
        self.canvas = tk.Canvas(self.image_frame, bg='white', relief=tk.SUNKEN, bd=2)

        # 添加滚动条
        h_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # 布局
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)

    def create_translation_panel(self, parent):
        """创建翻译结果面板"""

        # 翻译结果标题
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(title_frame, text="翻译结果", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # 结果计数
        self.result_count_var = tk.StringVar()
        self.result_count_var.set("(0 个文本块)")
        ttk.Label(title_frame, textvariable=self.result_count_var, foreground="gray").pack(side=tk.LEFT, padx=(10, 0))

        # 翻译结果显示区域
        self.translation_frame = ttk.Frame(parent)
        self.translation_frame.pack(fill=tk.BOTH, expand=True)

        # 创建滚动文本区域
        self.translation_text = scrolledtext.ScrolledText(
            self.translation_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            relief=tk.SUNKEN,
            bd=2
        )
        self.translation_text.pack(fill=tk.BOTH, expand=True)

        # 配置文本标签样式
        self.translation_text.tag_configure("header", font=("Arial", 11, "bold"), foreground="blue")
        self.translation_text.tag_configure("original", font=("Arial", 10), foreground="black", background="#f0f0f0")
        self.translation_text.tag_configure("translation", font=("Arial", 10), foreground="darkgreen")
        self.translation_text.tag_configure("separator", font=("Arial", 8), foreground="gray")
    
    def start_full_translation(self):
        """开始全图翻译"""
        if self.current_image_path is None:
            messagebox.showwarning("警告", "请先选择图片文件")
            return

        if self.is_translating:
            messagebox.showinfo("提示", "翻译正在进行中，请稍候...")
            return

        # 在新线程中执行翻译
        self.translate_btn.configure(state='disabled', text="翻译中...")
        self.progress.start()
        self.is_translating = True

        thread = threading.Thread(target=self._full_translation_thread)
        thread.daemon = True
        thread.start()

    def _full_translation_thread(self):
        """全图翻译线程"""
        try:
            # 调用AI进行全图翻译
            results = self.call_full_image_translation(self.current_image_path)

            # 在主线程中更新UI
            self.root.after(0, self._translation_complete, results)

        except Exception as e:
            self.root.after(0, self._translation_error, str(e))

    def _translation_complete(self, results):
        """翻译完成"""
        self.progress.stop()
        self.translate_btn.configure(state='normal', text="开始全图翻译")
        self.is_translating = False

        if results:
            self.translation_results = results
            self.display_translation_results()
            self.status_var.set(f"翻译完成，共识别 {len(results)} 个文本块")
        else:
            messagebox.showinfo("信息", "未识别到任何文本内容")
            self.status_var.set("未识别到文本内容")

    def _translation_error(self, error_msg):
        """翻译错误"""
        self.progress.stop()
        self.translate_btn.configure(state='normal', text="开始全图翻译")
        self.is_translating = False
        messagebox.showerror("错误", f"翻译失败: {error_msg}")
        self.status_var.set("翻译失败")

    def call_full_image_translation(self, image_path):
        """调用AI进行全图翻译"""
        try:
            # 读取图片并编码为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 获取图片尺寸
            img = cv2.imread(image_path)
            height, width = img.shape[:2]

            # 获取当前配置
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
            elif provider == "custom":
                custom_headers = provider_config.get("headers", {})
                headers.update(custom_headers)

            # 构建全图翻译提示词
            prompt = """请分析这张图片中的所有文本内容，包括对话气泡、标题、旁白、音效文字等。

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
  },
  {
    "type": "旁白",
    "original_text": "原文内容",
    "translation": "中文翻译"
  }
]
```

注意：
- 每个独立的文本区域都要单独列出
- 即使是很短的文字也要包含
- 翻译要准确且符合中文表达习惯
- 保持原文的情感色彩"""

            # 构建请求数据
            if provider == "anthropic":
                # Anthropic API格式
                data = {
                    'model': provider_config.get("model_name", ""),
                    'max_tokens': 4000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': prompt
                                },
                                {
                                    'type': 'image',
                                    'source': {
                                        'type': 'base64',
                                        'media_type': 'image/jpeg',
                                        'data': image_base64
                                    }
                                }
                            ]
                        }
                    ]
                }
            else:
                # OpenAI兼容格式（OpenRouter, OpenAI, 自定义）
                data = {
                    'model': provider_config.get("model_name", ""),
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': prompt
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{image_base64}'
                                    }
                                }
                            ]
                        }
                    ]
                }

            # 发送请求
            base_url = provider_config.get("base_url", "")
            if provider == "anthropic":
                url = f"{base_url}/messages"
            else:
                url = f"{base_url}/chat/completions"

            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()

            # 解析响应
            if provider == "anthropic":
                content = result['content'][0]['text']
            else:
                content = result['choices'][0]['message']['content']

            # 解析JSON结果
            return self.parse_translation_response(content)

        except Exception as e:
            print(f"全图翻译调用失败: {e}")
            raise e

    def parse_translation_response(self, content):
        """解析翻译响应"""
        try:
            # 尝试提取JSON部分
            import re

            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有代码块，尝试直接解析
                json_str = content.strip()

            # 解析JSON
            results = json.loads(json_str)

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
                return validated_results
            else:
                # 如果不是列表格式，尝试转换
                if isinstance(results, dict):
                    return [results]

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始内容: {content}")

            # 如果JSON解析失败，尝试简单的文本解析
            return self.parse_text_response(content)

        except Exception as e:
            print(f"解析响应时出错: {e}")
            return []

    def parse_text_response(self, content):
        """解析纯文本响应"""
        try:
            # 简单的文本解析，将整个响应作为一个翻译结果
            lines = content.strip().split('\n')
            results = []

            current_item = {}
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('原文:') or line.startswith('Original:'):
                    current_item['original_text'] = line.split(':', 1)[1].strip()
                elif line.startswith('译文:') or line.startswith('Translation:'):
                    current_item['translation'] = line.split(':', 1)[1].strip()
                    if 'original_text' in current_item:
                        current_item['type'] = '文本'
                        results.append(current_item.copy())
                        current_item = {}
                elif '→' in line or '->' in line:
                    # 处理 "原文 → 译文" 格式
                    parts = line.split('→' if '→' in line else '->')
                    if len(parts) == 2:
                        results.append({
                            'type': '文本',
                            'original_text': parts[0].strip(),
                            'translation': parts[1].strip()
                        })

            # 如果没有解析到任何结果，将整个内容作为翻译
            if not results:
                results.append({
                    'type': '翻译结果',
                    'original_text': '图片内容',
                    'translation': content.strip()
                })

            return results

        except Exception as e:
            print(f"文本解析失败: {e}")
            return [{
                'type': '错误',
                'original_text': '解析失败',
                'translation': content[:500] + '...' if len(content) > 500 else content
            }]
    
    def display_translation_results(self):
        """显示翻译结果"""
        self.translation_text.delete(1.0, tk.END)

        if not self.translation_results:
            self.translation_text.insert(tk.END, "暂无翻译结果\n")
            self.result_count_var.set("(0 个文本块)")
            return

        self.result_count_var.set(f"({len(self.translation_results)} 个文本块)")

        for i, result in enumerate(self.translation_results, 1):
            # 文本块标题
            header = f"【文本块 {i}】"
            if result.get('type'):
                header += f" - {result['type']}"
            header += "\n"

            self.translation_text.insert(tk.END, header, "header")

            # 原文
            if result.get('original_text'):
                self.translation_text.insert(tk.END, "原文: ", "header")
                self.translation_text.insert(tk.END, f"{result['original_text']}\n", "original")

            # 翻译
            if result.get('translation'):
                self.translation_text.insert(tk.END, "译文: ", "header")
                self.translation_text.insert(tk.END, f"{result['translation']}\n", "translation")

            # 分隔线
            if i < len(self.translation_results):
                self.translation_text.insert(tk.END, "─" * 50 + "\n\n", "separator")

    def clear_results(self):
        """清空翻译结果"""
        self.translation_results = []
        self.translation_text.delete(1.0, tk.END)
        self.result_count_var.set("(0 个文本块)")
        self.status_var.set("已清空翻译结果")

    def save_translation_results(self):
        """保存翻译结果"""
        if not self.translation_results:
            messagebox.showwarning("警告", "没有翻译结果可保存")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存翻译结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            try:
                if file_path.endswith('.json'):
                    # 保存为JSON格式
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.translation_results, f, ensure_ascii=False, indent=2)
                else:
                    # 保存为文本格式
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for i, result in enumerate(self.translation_results, 1):
                            f.write(f"【文本块 {i}】")
                            if result.get('type'):
                                f.write(f" - {result['type']}")
                            f.write("\n")

                            if result.get('original_text'):
                                f.write(f"原文: {result['original_text']}\n")
                            if result.get('translation'):
                                f.write(f"译文: {result['translation']}\n")
                            f.write("\n" + "─" * 50 + "\n\n")

                messagebox.showinfo("成功", f"翻译结果已保存到: {file_path}")
                self.status_var.set(f"翻译结果已保存")

            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

    def open_settings(self):
        """打开设置窗口"""
        SettingsWindow(self.root, callback=self.on_settings_changed)

    def update_status_with_config(self):
        """更新状态栏显示当前配置"""
        provider = config_manager.config.get("api_provider", "openrouter")
        model = config_manager.get_current_model()
        self.status_var.set(f"当前配置: {provider} - {model}")

    def on_settings_changed(self):
        """设置改变后的回调"""
        global config_manager

        # 重新加载配置
        config_manager = config.ConfigManager()

        # 更新状态栏显示当前配置
        self.update_status_with_config()

    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.load_image(file_path)
    
    def load_image(self, image_path):
        """加载图片"""
        try:
            self.current_image_path = image_path
            self.current_image = cv2.imread(image_path)
            
            if self.current_image is None:
                messagebox.showerror("错误", "无法读取图片文件")
                return
            
            # 显示图片
            self.display_image()
            
            # 清空翻译结果
            self.translation_results = []
            self.display_translation_results()
            
            self.status_var.set(f"已加载: {os.path.basename(image_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {e}")
    
    def display_image(self):
        """在画布上显示图片"""
        if self.current_image is None:
            return

        # 转换为RGB格式
        image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

        # 转换为PIL图片
        pil_image = Image.fromarray(image_rgb)

        # 计算合适的显示尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:  # 确保画布已初始化
            img_width, img_height = pil_image.size

            # 计算缩放比例
            scale_w = canvas_width / img_width
            scale_h = canvas_height / img_height
            scale = min(scale_w, scale_h, 1.0)  # 不放大，只缩小

            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 转换为Tkinter可显示的格式
        self.photo = ImageTk.PhotoImage(pil_image)

        # 更新画布
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    # 旧的AI检测方法已移除，现在使用全图翻译功能

    def call_ai_detection(self, image_path):
        """调用AI进行文本检测"""
        try:
            # 读取图片并编码为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 获取图片尺寸
            img = cv2.imread(image_path)
            height, width = img.shape[:2]

            # 获取当前配置
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
            elif provider == "custom":
                custom_headers = provider_config.get("headers", {})
                headers.update(custom_headers)

            # 构建提示词
            prompt = config.PROMPT_TEMPLATE.format(width=width, height=height)

            # 构建请求数据
            if provider == "anthropic":
                # Anthropic API格式
                data = {
                    'model': provider_config.get("model_name", ""),
                    'max_tokens': 4000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': prompt
                                },
                                {
                                    'type': 'image',
                                    'source': {
                                        'type': 'base64',
                                        'media_type': 'image/jpeg',
                                        'data': image_base64
                                    }
                                }
                            ]
                        }
                    ]
                }
            else:
                # OpenAI兼容格式（OpenRouter, OpenAI, 自定义）
                data = {
                    'model': provider_config.get("model_name", ""),
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': prompt
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{image_base64}'
                                    }
                                }
                            ]
                        }
                    ]
                }

            # 发送请求
            base_url = provider_config.get("base_url", "")
            if provider == "anthropic":
                url = f"{base_url}/messages"
            else:
                url = f"{base_url}/chat/completions"

            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")

            result = response.json()

            # 根据不同API提取内容
            if provider == "anthropic":
                content = result['content'][0]['text']
            else:
                content = result['choices'][0]['message']['content']

            # 解析JSON结果
            try:
                # 尝试直接解析
                detections = json.loads(content)
            except json.JSONDecodeError:
                # 如果失败，尝试提取JSON部分
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    detections = json.loads(json_match.group())
                else:
                    raise Exception("无法解析AI返回的JSON格式")

            return detections

        except Exception as e:
            raise Exception(f"AI检测失败: {e}")

    def start_drawing(self):
        """开始绘制模式"""
        if self.current_image is None:
            messagebox.showwarning("警告", "请先加载图片")
            return

        self.drawing_mode = True
        self.status_var.set("绘制模式：点击并拖拽来创建检测框")

    def on_canvas_click(self, event):
        """画布点击事件"""
        if self.drawing_mode:
            self.start_point = (event.x, event.y)
        else:
            # 检查是否点击了某个检测框
            self.check_detection_click(event.x, event.y)

    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.drawing_mode and self.start_point:
            # 绘制临时矩形
            self.canvas.delete("temp_rect")
            self.canvas.create_rectangle(
                self.start_point[0], self.start_point[1],
                event.x, event.y,
                outline="red", width=2, tags="temp_rect"
            )

    def on_canvas_release(self, event):
        """画布释放事件"""
        if self.drawing_mode and self.start_point:
            # 创建新的检测区域
            x1, y1 = self.start_point
            x2, y2 = event.x, event.y

            # 确保坐标正确
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            # 添加新检测
            new_detection = {
                "box_2d": [x1, y1, x2, y2],
                "text_content": "手动添加的区域",
                "type": "dialogue"
            }

            self.detections.append(new_detection)
            self.update_detection_list()
            self.display_image()

            # 退出绘制模式
            self.drawing_mode = False
            self.start_point = None
            self.canvas.delete("temp_rect")
            self.status_var.set(f"已添加检测区域，共 {len(self.detections)} 个")

    def check_detection_click(self, x, y):
        """检查是否点击了检测框"""
        for i, detection in enumerate(self.detections):
            box_2d = detection.get('box_2d', [])
            if len(box_2d) == 4:
                x1, y1, x2, y2 = box_2d
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.selected_detection = i
                    self.detection_listbox.selection_clear(0, tk.END)
                    self.detection_listbox.selection_set(i)
                    self.load_detection_text(i)
                    self.display_image()
                    break

    def on_detection_select(self, event):
        """检测结果列表选择事件"""
        selection = self.detection_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_detection = index
            self.load_detection_text(index)
            self.display_image()

    def load_detection_text(self, index):
        """加载检测文本到编辑区域"""
        if 0 <= index < len(self.detections):
            detection = self.detections[index]

            # 清空文本框
            self.original_text.delete(1.0, tk.END)
            self.translated_text.delete(1.0, tk.END)

            # 加载原文
            original = detection.get('text_content', '')
            self.original_text.insert(1.0, original)

            # 加载译文（如果有）
            translated = detection.get('translated_text', '')
            self.translated_text.insert(1.0, translated)

    def delete_selected(self):
        """删除选中的检测区域"""
        if self.selected_detection is not None:
            if messagebox.askyesno("确认", "确定要删除选中的检测区域吗？"):
                del self.detections[self.selected_detection]
                self.selected_detection = None
                self.update_detection_list()
                self.display_image()
                self.clear_text_fields()
                self.status_var.set(f"已删除，剩余 {len(self.detections)} 个区域")

    def clear_all(self):
        """清除所有检测区域"""
        if self.detections and messagebox.askyesno("确认", "确定要清除所有检测区域吗？"):
            self.detections = []
            self.selected_detection = None
            self.update_detection_list()
            self.display_image()
            self.clear_text_fields()
            self.status_var.set("已清除所有检测区域")

    def clear_text_fields(self):
        """清空文本编辑区域"""
        self.original_text.delete(1.0, tk.END)
        self.translated_text.delete(1.0, tk.END)

    def update_detection_list(self):
        """更新检测结果列表"""
        self.detection_listbox.delete(0, tk.END)

        for i, detection in enumerate(self.detections):
            box_2d = detection.get('box_2d', [])
            text_content = detection.get('text_content', '')

            if len(box_2d) == 4:
                x1, y1, x2, y2 = box_2d
                width = x2 - x1
                height = y2 - y1

                # 显示简要信息
                display_text = f"#{i+1} ({width}x{height}) {text_content[:20]}..."
                self.detection_listbox.insert(tk.END, display_text)

    def ai_translate(self):
        """AI翻译当前选中的文本"""
        if self.selected_detection is None:
            messagebox.showwarning("警告", "请先选择一个检测区域")
            return

        original_text = self.original_text.get(1.0, tk.END).strip()
        if not original_text:
            messagebox.showwarning("警告", "原文为空")
            return

        # 在新线程中执行翻译
        thread = threading.Thread(target=self._ai_translate_thread, args=(original_text,))
        thread.daemon = True
        thread.start()

        self.status_var.set("正在翻译...")

    def _ai_translate_thread(self, text):
        """AI翻译线程"""
        try:
            translated = self.call_ai_translation(text)
            self.root.after(0, self._ai_translate_complete, translated)
        except Exception as e:
            self.root.after(0, self._ai_translate_error, str(e))

    def _ai_translate_complete(self, translated_text):
        """翻译完成"""
        self.translated_text.delete(1.0, tk.END)
        self.translated_text.insert(1.0, translated_text)
        self.status_var.set("翻译完成")

    def _ai_translate_error(self, error_msg):
        """翻译错误"""
        messagebox.showerror("错误", f"翻译失败: {error_msg}")
        self.status_var.set("翻译失败")

    def call_ai_translation(self, text):
        """调用AI进行翻译"""
        try:
            # 获取当前配置
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
            elif provider == "custom":
                custom_headers = provider_config.get("headers", {})
                headers.update(custom_headers)

            # 获取翻译设置（如果有的话）
            target_lang = getattr(self, 'target_lang_var', None)
            style = getattr(self, 'style_var', None)

            target_language = target_lang.get() if target_lang else "中文"
            translation_style = style.get() if style else "自然"

            # 构建翻译提示词
            prompt = f"""请将以下英文漫画对话翻译成{target_language}，要求：
1. 保持对话的语气和风格
2. 符合{target_language}表达习惯
3. 翻译风格：{translation_style}
4. 简洁明了，适合漫画对话框
5. 只返回翻译结果，不要其他说明

英文原文：{text}"""

            # 构建请求数据
            if provider == "anthropic":
                # Anthropic API格式
                data = {
                    'model': provider_config.get("model_name", ""),
                    'max_tokens': 1000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                }
            else:
                # OpenAI兼容格式
                data = {
                    'model': provider_config.get("model_name", ""),
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                }

            # 发送请求
            base_url = provider_config.get("base_url", "")
            if provider == "anthropic":
                url = f"{base_url}/messages"
            else:
                url = f"{base_url}/chat/completions"

            response = requests.post(url, headers=headers, json=data, timeout=30)

            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")

            result = response.json()

            # 根据不同API提取内容
            if provider == "anthropic":
                content = result['content'][0]['text']
            else:
                content = result['choices'][0]['message']['content']

            return content.strip()

        except Exception as e:
            raise Exception(f"翻译失败: {e}")

    def apply_translation(self):
        """应用翻译到当前检测区域"""
        if self.selected_detection is None:
            messagebox.showwarning("警告", "请先选择一个检测区域")
            return

        translated_text = self.translated_text.get(1.0, tk.END).strip()
        if not translated_text:
            messagebox.showwarning("警告", "译文为空")
            return

        # 更新检测数据
        self.detections[self.selected_detection]['translated_text'] = translated_text

        # 更新原文（如果有修改）
        original_text = self.original_text.get(1.0, tk.END).strip()
        self.detections[self.selected_detection]['text_content'] = original_text

        self.status_var.set("翻译已应用")
        messagebox.showinfo("成功", "翻译已应用到检测区域")

    def save_results(self):
        """保存结果"""
        if not self.detections:
            messagebox.showwarning("警告", "没有检测结果可保存")
            return

        if self.current_image_path is None:
            messagebox.showwarning("警告", "没有加载图片")
            return

        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if save_path:
            try:
                # 准备保存数据
                img = cv2.imread(self.current_image_path)
                height, width = img.shape[:2]

                save_data = {
                    'image_path': self.current_image_path,
                    'image_size': [width, height],
                    'detection_count': len(self.detections),
                    'detections': self.detections,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'app_version': '1.0'
                }

                # 保存JSON文件
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)

                # 保存带标注的图片
                image_save_path = save_path.replace('.json', '_annotated.jpg')
                self.save_annotated_image(image_save_path)

                messagebox.showinfo("成功", f"结果已保存到:\n{save_path}\n{image_save_path}")
                self.status_var.set("结果已保存")

            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")

    def save_annotated_image(self, save_path):
        """保存带标注的图片"""
        if self.current_image is None:
            return

        # 复制图片
        result_image = self.current_image.copy()

        # 绘制检测框和翻译
        for i, detection in enumerate(self.detections):
            box_2d = detection.get('box_2d', [])
            translated_text = detection.get('translated_text', '')

            if len(box_2d) == 4:
                x1, y1, x2, y2 = map(int, box_2d)

                # 绘制边框
                cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 绘制序号
                cv2.putText(result_image, f"#{i+1}", (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # 如果有翻译，在框内显示（简单版本）
                if translated_text:
                    # 这里可以添加更复杂的中文文本渲染
                    pass

        # 保存图片
        cv2.imwrite(save_path, result_image)


def main():
    """主函数"""
    global config_manager

    # 检查API密钥
    current_api_key = config_manager.get_current_api_key()
    if not current_api_key or current_api_key.startswith("<"):
        result = messagebox.askyesno(
            "API密钥未配置",
            "检测到API密钥未配置或使用默认值。\n\n是否现在打开设置进行配置？\n\n点击'否'将继续运行，但AI功能将无法使用。"
        )
        if result:
            # 创建临时窗口用于设置
            temp_root = tk.Tk()
            temp_root.withdraw()  # 隐藏主窗口

            def on_settings_done():
                temp_root.quit()

            SettingsWindow(temp_root, callback=on_settings_done)
            temp_root.mainloop()
            temp_root.destroy()

            # 重新加载配置
            config_manager = config.ConfigManager()

    # 创建主窗口
    root = tk.Tk()
    app = ComicTranslatorApp(root)

    # 运行应用
    root.mainloop()


if __name__ == "__main__":
    main()
