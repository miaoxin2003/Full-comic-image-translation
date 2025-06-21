# -*- coding: utf-8 -*-
"""
漫画全图翻译器 v2.0
专门用于全图翻译功能，不再进行区域检测，直接翻译整张图片的所有文本内容
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

# 导入设置窗口
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
        self.target_lang_var = tk.StringVar(value=config_manager.get_target_language())
        lang_combo = ttk.Combobox(translate_frame, textvariable=self.target_lang_var,
                                 values=["中文", "日文", "韩文", "法文", "德文", "西班牙文"],
                                 state="readonly", width=20)
        lang_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # 翻译风格
        ttk.Label(translate_frame, text="翻译风格:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.style_var = tk.StringVar(value=config_manager.get_translation_style())
        style_combo = ttk.Combobox(translate_frame, textvariable=self.style_var,
                                  values=["自然", "直译", "意译", "口语化", "正式"],
                                  state="readonly", width=20)
        style_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 提示词设置
        prompt_frame = ttk.LabelFrame(frame, text="自定义提示词", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, height=8, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.BOTH, expand=True)

        # 从配置中加载自定义提示词
        saved_prompt = config_manager.get_custom_prompt()
        self.prompt_text.insert(1.0, saved_prompt)
    
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

                # 优先显示自定义模型
                if current_model and current_model not in models:
                    # 如果当前模型不在预设列表中，显示为自定义模型
                    self.custom_model_var.set(current_model)
                    self.model_var.set("")
                elif current_model in models:
                    # 如果在预设列表中，显示为预设模型
                    self.model_var.set(current_model)
                    self.custom_model_var.set("")
                elif models:
                    # 如果没有当前模型但有预设模型，选择第一个
                    self.model_var.set(models[0])
                    self.custom_model_var.set("")
                else:
                    # 都没有，清空
                    self.model_var.set("")
                    self.custom_model_var.set("")

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
                print(f"💾 保存模型: {selected_model}")  # 调试信息
            else:
                print("⚠️ 没有选择模型")

            # 更新配置
            config_manager.update_provider_config(provider, provider_updates)

            # 保存高级设置
            advanced_settings = {}

            # 保存目标语言
            if hasattr(self, 'target_lang_var'):
                advanced_settings["target_language"] = self.target_lang_var.get()
                print(f"💾 保存目标语言: {self.target_lang_var.get()}")

            # 保存翻译风格
            if hasattr(self, 'style_var'):
                advanced_settings["translation_style"] = self.style_var.get()
                print(f"💾 保存翻译风格: {self.style_var.get()}")

            # 保存自定义提示词
            if hasattr(self, 'prompt_text'):
                custom_prompt = self.prompt_text.get(1.0, tk.END).strip()
                advanced_settings["custom_prompt"] = custom_prompt
                print(f"💾 保存自定义提示词: {len(custom_prompt)} 字符")

            # 更新高级设置到配置
            if advanced_settings:
                config_manager.update_advanced_settings(advanced_settings)

            # 验证保存结果
            saved_config = config_manager.get_current_provider_config()
            saved_model = saved_config.get("model_name", "")
            print(f"✅ 验证保存结果 - 模型: {saved_model}")

            messagebox.showinfo("保存成功", f"设置已保存！\n当前模型: {saved_model}")

            if self.callback:
                self.callback()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("保存失败", f"保存设置时发生错误: {e}")
    
    def cancel(self):
        """取消设置"""
        self.window.destroy()


class ComicFullTranslatorApp:
    """漫画全图翻译器主应用 - 多图片阅读器版"""

    def __init__(self, root):
        self.root = root
        self.root.title("漫画全图翻译器 v2.1 - 多图片阅读器")
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

        # 性能优化相关
        self.image_cache = {}  # 图片缓存 {scale: PIL_Image}
        self.last_canvas_size = (0, 0)  # 上次画布大小
        self.auto_fit_enabled = True  # 是否启用自适应缩放
        self.is_dragging = False  # 是否正在拖拽

        # 节流机制相关
        self.zoom_timer = None  # 缩放节流定时器
        self.last_zoom_time = 0  # 上次缩放时间
        self.zoom_accumulator = 0  # 缩放累积值
        self.target_scale = 1.0  # 目标缩放比例
        self.target_offset_x = 0  # 目标X偏移
        self.target_offset_y = 0  # 目标Y偏移

        # 创建UI
        self.create_ui()

        # 绑定拖拽事件
        self.setup_drag_drop()

        # 显示当前配置
        self.update_status_with_config()
    
    def create_ui(self):
        """创建用户界面 - 阅读器风格"""

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部控制面板
        top_panel = ttk.Frame(main_frame, height=80)
        top_panel.pack(fill=tk.X, pady=(0, 10))
        top_panel.pack_propagate(False)

        # 中间内容区域 - 使用可调节的PanedWindow
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建水平分割的PanedWindow
        self.main_paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧 - 图片列表区域
        left_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(left_panel, weight=1)

        # 中间和右侧的PanedWindow
        right_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(right_paned, weight=4)

        # 中间 - 图片显示区域
        center_panel = ttk.Frame(right_paned)
        right_paned.add(center_panel, weight=3)

        # 右侧 - 翻译结果区域
        right_panel = ttk.Frame(right_paned)
        right_paned.add(right_panel, weight=2)

        self.create_top_panel(top_panel)
        self.create_image_list_panel(left_panel)
        self.create_image_display_panel(center_panel)
        self.create_translation_panel(right_panel)

    def create_top_panel(self, parent):
        """创建顶部控制面板"""

        # 文件操作区域
        file_frame = ttk.LabelFrame(parent, text="文件操作", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 添加拖拽提示
        drag_tip = ttk.Label(file_frame, text="💡 可拖拽图片到窗口", foreground="blue", font=("Arial", 8))
        drag_tip.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(file_frame, text="选择多张图片", command=self.select_multiple_images, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="添加图片", command=self.add_images, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="清空列表", command=self.clear_image_list, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="设置", command=self.open_settings, width=8).pack(side=tk.LEFT, padx=2)

        # 导航区域
        nav_frame = ttk.LabelFrame(parent, text="导航", padding=10)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.prev_btn = ttk.Button(nav_frame, text="◀ 上一张", command=self.prev_image, width=10)
        self.prev_btn.pack(side=tk.LEFT, padx=2)

        self.image_info_var = tk.StringVar()
        self.image_info_var.set("0 / 0")
        ttk.Label(nav_frame, textvariable=self.image_info_var).pack(side=tk.LEFT, padx=10)

        self.next_btn = ttk.Button(nav_frame, text="下一张 ▶", command=self.next_image, width=10)
        self.next_btn.pack(side=tk.LEFT, padx=2)

        # 图片控制区域
        view_frame = ttk.LabelFrame(parent, text="视图控制", padding=10)
        view_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(view_frame, text="适应窗口", command=self.fit_to_window, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="原始大小", command=self.actual_size, width=10).pack(side=tk.LEFT, padx=2)

        # AI翻译区域
        ai_frame = ttk.LabelFrame(parent, text="AI翻译", padding=10)
        ai_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.translate_btn = ttk.Button(ai_frame, text="翻译当前图片", command=self.start_full_translation, width=12)
        self.translate_btn.pack(side=tk.LEFT, padx=2)

        self.batch_translate_btn = ttk.Button(ai_frame, text="批量翻译", command=self.start_batch_translation, width=10)
        self.batch_translate_btn.pack(side=tk.LEFT, padx=2)

        self.progress = ttk.Progressbar(ai_frame, mode='indeterminate', length=150)
        self.progress.pack(side=tk.LEFT, padx=2)

        # 导出区域
        export_frame = ttk.LabelFrame(parent, text="导出结果", padding=10)
        export_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(export_frame, text="保存当前", command=self.save_current_translation, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="保存全部", command=self.save_all_translations, width=10).pack(side=tk.LEFT, padx=2)

        # 状态显示
        status_frame = ttk.LabelFrame(parent, text="状态", padding=10)
        status_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar()
        self.status_var.set("请选择图片文件或拖拽图片到窗口")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(expand=True)

    def create_image_list_panel(self, parent):
        """创建图片列表面板"""

        # 图片列表标题
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(title_frame, text="图片列表", font=("Arial", 12, "bold")).pack(side=tk.LEFT)

        # 图片计数
        self.image_count_var = tk.StringVar()
        self.image_count_var.set("(0 张)")
        ttk.Label(title_frame, textvariable=self.image_count_var, foreground="gray").pack(side=tk.LEFT, padx=(10, 0))

        # 图片列表
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建列表框和滚动条
        self.image_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.configure(yscrollcommand=scrollbar.set)

        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        # 右键菜单
        self.create_context_menu()

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="翻译此图片", command=self.translate_selected_image)
        self.context_menu.add_command(label="从列表移除", command=self.remove_selected_image)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="在文件管理器中显示", command=self.show_in_explorer)

        # 绑定右键菜单
        self.image_listbox.bind("<Button-3>", self.show_context_menu)

    def create_image_display_panel(self, parent):
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

        # 绑定鼠标事件
        self.setup_image_events()

        # 绑定画布大小变化事件
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def setup_image_events(self):
        """设置图片交互事件"""
        # 鼠标滚轮缩放
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux

        # 鼠标拖拽
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # 双击重置
        self.canvas.bind("<Double-Button-1>", self.reset_image_view)

        # 键盘快捷键
        self.canvas.bind("<Key>", self.on_key_press)
        self.canvas.focus_set()  # 使画布能接收键盘事件

    def on_mouse_wheel(self, event):
        """鼠标滚轮缩放（节流优化版）"""
        if self.current_image is None:
            return

        # 禁用自适应缩放
        self.auto_fit_enabled = False

        import time
        current_time = time.time() * 1000  # 转换为毫秒

        # 获取鼠标位置
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)

        # 计算缩放方向
        if event.delta > 0 or event.num == 4:  # 向上滚动，放大
            zoom_delta = 0.1
        else:  # 向下滚动，缩小
            zoom_delta = -0.1

        # 累积缩放变化
        self.zoom_accumulator += zoom_delta

        # 计算目标缩放比例
        self.target_scale = self.image_scale * (1 + self.zoom_accumulator)

        # 限制缩放范围
        if self.target_scale < 0.1:
            self.target_scale = 0.1
            self.zoom_accumulator = (0.1 / self.image_scale) - 1
        elif self.target_scale > 10.0:
            self.target_scale = 10.0
            self.zoom_accumulator = (10.0 / self.image_scale) - 1

        # 计算目标偏移（基于当前显示状态）
        if abs(self.zoom_accumulator) > 0.01:
            scale_change = self.target_scale / self.image_scale
            self.target_offset_x = mouse_x - (mouse_x - self.image_offset_x) * scale_change
            self.target_offset_y = mouse_y - (mouse_y - self.image_offset_y) * scale_change

        # 立即更新状态栏显示目标缩放比例
        self.update_zoom_status_immediate()

        # 使用节流机制更新图片
        self.schedule_throttled_zoom_update()

    def update_zoom_status_immediate(self):
        """立即更新缩放状态显示"""
        current_status = self.status_var.get()
        if " | 缩放:" in current_status:
            current_status = current_status.split(" | 缩放:")[0]

        zoom_percent = int(self.target_scale * 100)
        self.status_var.set(f"{current_status} | 缩放: {zoom_percent}%")

    def schedule_throttled_zoom_update(self):
        """安排节流的缩放更新"""
        # 取消之前的定时器
        if self.zoom_timer:
            self.root.after_cancel(self.zoom_timer)

        # 设置新的定时器，16ms约等于60FPS
        self.zoom_timer = self.root.after(16, self.execute_throttled_zoom_update)

    def execute_throttled_zoom_update(self):
        """执行节流的缩放更新"""
        if abs(self.zoom_accumulator) < 0.01:
            return

        # 应用累积的缩放变化
        self.image_scale = self.target_scale
        self.image_offset_x = self.target_offset_x
        self.image_offset_y = self.target_offset_y

        # 重置累积器
        self.zoom_accumulator = 0
        self.zoom_timer = None

        # 更新图片显示
        self.update_image_display_smooth()

    def update_image_display_smooth(self):
        """平滑更新图片显示"""
        if self.original_pil_image is None:
            return

        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # 使用智能缓存获取图片
        display_image = self.get_cached_image_smart(self.image_scale)

        # 转换为Tkinter可显示的格式
        self.photo = ImageTk.PhotoImage(display_image)

        # 清空画布并显示图片
        self.canvas.delete("all")

        # 创建图片对象
        self.canvas.create_image(self.image_offset_x, self.image_offset_y,
                                anchor=tk.NW, image=self.photo, tags="image")

        # 更新滚动区域
        self.update_scroll_region_smooth()

    def get_cached_image_smart(self, scale):
        """智能缓存图片获取"""
        # 使用适中的缓存精度
        cache_key = round(scale, 2)

        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        # 创建新的缩放图片
        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)

        if scale != 1.0:
            # 根据缩放比例选择重采样方法
            if scale > 1.5:  # 大幅放大时使用快速算法
                resample = Image.Resampling.BILINEAR
            elif scale < 0.5:  # 大幅缩小时使用快速算法
                resample = Image.Resampling.BILINEAR
            else:  # 中等缩放时使用高质量算法
                resample = Image.Resampling.LANCZOS

            scaled_image = self.original_pil_image.resize(
                (scaled_width, scaled_height), resample
            )
        else:
            scaled_image = self.original_pil_image

        # 智能缓存管理
        if len(self.image_cache) > 8:
            # 移除最远离当前缩放比例的缓存
            keys_to_remove = sorted(self.image_cache.keys(),
                                  key=lambda x: abs(x - scale), reverse=True)[:3]
            for key in keys_to_remove:
                del self.image_cache[key]

        self.image_cache[cache_key] = scaled_image
        return scaled_image

    def update_scroll_region_smooth(self):
        """平滑更新滚动区域"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)

        x, y = self.image_offset_x, self.image_offset_y
        left = min(0, x)
        top = min(0, y)
        right = max(canvas_width, x + scaled_width)
        bottom = max(canvas_height, y + scaled_height)

        self.canvas.configure(scrollregion=(left, top, right, bottom))

    def update_image_display_fast(self):
        """快速更新图片显示（专为缩放优化）"""
        if self.original_pil_image is None:
            return

        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # 使用优化的缓存获取
        display_image = self.get_cached_image_fast(self.image_scale)

        # 转换为Tkinter可显示的格式
        self.photo = ImageTk.PhotoImage(display_image)

        # 清空画布并显示图片
        self.canvas.delete("all")

        # 创建图片对象
        self.canvas.create_image(self.image_offset_x, self.image_offset_y,
                                anchor=tk.NW, image=self.photo, tags="image")

        # 快速更新滚动区域
        self.update_scroll_region_fast()

        # 更新状态栏
        self.update_zoom_status_fast()

    def get_cached_image_fast(self, scale):
        """快速获取缓存图片（专为缩放优化）"""
        # 使用更粗粒度的缓存键以提高命中率
        cache_key = round(scale, 1)

        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        # 如果缓存未命中，创建新图片
        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)

        if scale != 1.0:
            # 对于缩放操作，优先使用速度而不是质量
            if abs(scale - 1.0) < 0.3:  # 接近原始大小时使用高质量
                resample = Image.Resampling.LANCZOS
            else:  # 大幅缩放时使用快速算法
                resample = Image.Resampling.BILINEAR

            scaled_image = self.original_pil_image.resize(
                (scaled_width, scaled_height), resample
            )
        else:
            scaled_image = self.original_pil_image

        # 限制缓存大小
        if len(self.image_cache) > 6:
            # 移除最旧的缓存项
            oldest_key = next(iter(self.image_cache))
            del self.image_cache[oldest_key]

        self.image_cache[cache_key] = scaled_image
        return scaled_image

    def update_scroll_region_fast(self):
        """快速更新滚动区域"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)

        x, y = self.image_offset_x, self.image_offset_y
        left = min(0, x)
        top = min(0, y)
        right = max(canvas_width, x + scaled_width)
        bottom = max(canvas_height, y + scaled_height)

        self.canvas.configure(scrollregion=(left, top, right, bottom))

    def update_zoom_status_fast(self):
        """快速更新缩放状态"""
        current_status = self.status_var.get()
        if " | 缩放:" in current_status:
            current_status = current_status.split(" | 缩放:")[0]

        zoom_percent = int(self.image_scale * 100)
        self.status_var.set(f"{current_status} | 缩放: {zoom_percent}%")



    def on_canvas_click(self, event):
        """画布点击事件"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = True
        self.canvas.configure(cursor="fleur")  # 改变鼠标样式为移动
        # 禁用自适应缩放
        self.auto_fit_enabled = False

    def on_canvas_drag(self, event):
        """画布拖拽事件（优化版）"""
        if self.current_image is None or not self.is_dragging:
            return

        # 计算拖拽距离
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        # 更新图片偏移
        self.image_offset_x += dx
        self.image_offset_y += dy

        # 更新拖拽起始点
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # 使用更高效的移动方式
        self.canvas.move("image", dx, dy)

        # 更新滚动区域（不重新绘制图片）
        self.update_scroll_region()

    def on_canvas_release(self, event):
        """画布释放事件"""
        self.is_dragging = False
        self.canvas.configure(cursor="")  # 恢复默认鼠标样式

    def update_scroll_region(self):
        """更新滚动区域（不重新绘制图片）"""
        if self.original_pil_image is None:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 计算缩放后的图片尺寸
        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)

        # 计算图片边界
        x = self.image_offset_x
        y = self.image_offset_y
        left = min(0, x)
        top = min(0, y)
        right = max(canvas_width, x + scaled_width)
        bottom = max(canvas_height, y + scaled_height)

        self.canvas.configure(scrollregion=(left, top, right, bottom))

    def reset_image_view(self, event=None):
        """重置图片视图（双击或快捷键）"""
        if self.current_image is None:
            return

        # 取消任何待处理的缩放
        if self.zoom_timer:
            self.root.after_cancel(self.zoom_timer)
            self.zoom_timer = None

        # 重置节流相关状态
        self.zoom_accumulator = 0
        self.target_scale = 1.0
        self.target_offset_x = 0
        self.target_offset_y = 0

        # 清空缓存并重新启用自适应缩放
        self.image_cache.clear()
        self.auto_fit_enabled = True
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.update_image_display()

    def fit_to_window(self):
        """适应窗口大小"""
        if self.current_image is None:
            return

        # 清空缓存并重新启用自适应缩放
        self.image_cache.clear()
        self.auto_fit_enabled = True
        self.update_image_display()

    def actual_size(self):
        """显示原始大小"""
        if self.current_image is None:
            return

        # 禁用自适应缩放，设置为原始大小
        self.auto_fit_enabled = False
        self.image_scale = 1.0

        # 居中显示
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.original_pil_image.size

        self.image_offset_x = max(0, (canvas_width - img_width) // 2)
        self.image_offset_y = max(0, (canvas_height - img_height) // 2)

        self.update_image_display()

    def on_canvas_configure(self, event):
        """画布大小变化事件"""
        # 只处理画布本身的配置变化，不处理其他控件
        if event.widget != self.canvas:
            return

        # 如果没有图片，直接返回
        if self.original_pil_image is None:
            return

        # 获取新的画布大小
        new_canvas_size = (event.width, event.height)

        # 如果大小没有实际变化，直接返回
        if new_canvas_size == self.last_canvas_size:
            return

        # 如果启用了自适应缩放，重新计算适应大小
        if self.auto_fit_enabled:
            # 延迟执行，避免频繁触发
            self.root.after(100, self._delayed_canvas_resize)
        else:
            # 只更新滚动区域
            self.update_scroll_region()

        self.last_canvas_size = new_canvas_size

    def _delayed_canvas_resize(self):
        """延迟处理画布大小变化"""
        if self.original_pil_image is None:
            return

        # 重新计算适应大小
        fit_scale = self.calculate_fit_scale()

        # 如果缩放比例变化较大，才重新适应
        if abs(fit_scale - self.image_scale) > 0.05:
            self.image_scale = fit_scale

            # 重新居中
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.original_pil_image.size
            scaled_width = int(img_width * self.image_scale)
            scaled_height = int(img_height * self.image_scale)

            self.image_offset_x = max(0, (canvas_width - scaled_width) // 2)
            self.image_offset_y = max(0, (canvas_height - scaled_height) // 2)

            self.update_image_display()

    def on_key_press(self, event):
        """键盘事件处理"""
        if event.keysym == "r" or event.keysym == "R":
            self.reset_image_view()
        elif event.keysym == "plus" or event.keysym == "equal":
            # 放大
            self.image_scale *= 1.2
            if self.image_scale > 10.0:
                self.image_scale = 10.0
            self.update_image_display()
        elif event.keysym == "minus":
            # 缩小
            self.image_scale *= 0.8
            if self.image_scale < 0.1:
                self.image_scale = 0.1
            self.update_image_display()

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

    def select_multiple_images(self):
        """选择多张图片文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择多张图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            self.add_images_to_list(file_paths)

    def add_images(self):
        """添加更多图片"""
        file_paths = filedialog.askopenfilenames(
            title="添加图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            self.add_images_to_list(file_paths)

    def add_images_to_list(self, file_paths):
        """添加图片到列表"""
        added_count = 0
        for file_path in file_paths:
            if file_path not in self.image_list:
                self.image_list.append(file_path)
                added_count += 1

        if added_count > 0:
            self.update_image_list_display()
            if len(self.image_list) == added_count:  # 第一次添加图片
                self.current_image_index = 0
                self.load_current_image()
            self.status_var.set(f"已添加 {added_count} 张图片，共 {len(self.image_list)} 张")
        else:
            self.status_var.set("没有新图片添加（可能已存在）")

    def clear_image_list(self):
        """清空图片列表"""
        if self.image_list:
            result = messagebox.askyesno("确认清空", "确定要清空所有图片吗？")
            if result:
                self.image_list = []
                self.current_image_index = 0
                self.current_image = None
                self.all_translation_results = {}
                self.update_image_list_display()
                self.display_image()
                self.display_translation_results()
                self.status_var.set("图片列表已清空")

    def update_image_list_display(self):
        """更新图片列表显示"""
        self.image_listbox.delete(0, tk.END)

        for i, image_path in enumerate(self.image_list):
            filename = os.path.basename(image_path)
            # 显示翻译状态
            status = ""
            if image_path in self.all_translation_results:
                result_count = len(self.all_translation_results[image_path])
                status = f" ✓({result_count})"

            display_text = f"{i+1:2d}. {filename}{status}"
            self.image_listbox.insert(tk.END, display_text)

        # 更新计数
        self.image_count_var.set(f"({len(self.image_list)} 张)")

        # 更新导航信息
        if self.image_list:
            self.image_info_var.set(f"{self.current_image_index + 1} / {len(self.image_list)}")
            # 选中当前图片
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(self.current_image_index)
            self.image_listbox.see(self.current_image_index)
        else:
            self.image_info_var.set("0 / 0")

        # 更新按钮状态
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """更新导航按钮状态"""
        if len(self.image_list) <= 1:
            self.prev_btn.configure(state='disabled')
            self.next_btn.configure(state='disabled')
        else:
            self.prev_btn.configure(state='normal' if self.current_image_index > 0 else 'disabled')
            self.next_btn.configure(state='normal' if self.current_image_index < len(self.image_list) - 1 else 'disabled')

    def on_image_select(self, event):
        """图片列表选择事件"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if index != self.current_image_index:
                self.current_image_index = index
                self.load_current_image()
                self.update_image_list_display()

    def prev_image(self):
        """上一张图片"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_current_image()
            self.update_image_list_display()

    def next_image(self):
        """下一张图片"""
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.load_current_image()
            self.update_image_list_display()

    def load_current_image(self):
        """加载当前图片"""
        if self.image_list and 0 <= self.current_image_index < len(self.image_list):
            image_path = self.image_list[self.current_image_index]
            self.load_image(image_path)

    def setup_drag_drop(self):
        """设置拖拽功能"""
        try:
            # 尝试导入tkinterdnd2
            from tkinterdnd2 import DND_FILES, TkinterDnD

            # 检查是否已经是TkinterDnD窗口
            if not hasattr(self.root, 'drop_target_register'):
                print("ℹ️  当前窗口不支持拖拽，需要重新创建窗口")
                print("💡 替代方案：使用 '选择多张图片' 按钮批量添加图片")
                return

            print("✅ 拖拽功能已启用")
            print("💡 提示：可以直接拖拽图片文件到窗口中")

            # 为现有的root添加拖拽支持
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)

        except ImportError:
            print("ℹ️  拖拽功能不可用（tkinterdnd2 未安装）")
            print("💡 替代方案：使用 '选择多张图片' 按钮批量添加图片")
            print("📦 安装拖拽支持：pip install tkinterdnd2")

            # 添加提示到状态栏
            current_status = self.status_var.get()
            if "拖拽" not in current_status:
                self.status_var.set(current_status + " | 提示：可使用'选择多张图片'按钮")
        except Exception as e:
            print(f"ℹ️  拖拽功能设置失败: {e}")
            print("💡 替代方案：使用 '选择多张图片' 按钮批量添加图片")

    def on_drop(self, event):
        """拖拽文件处理"""
        files = event.data.split()
        image_files = []

        for file_path in files:
            # 移除可能的大括号
            file_path = file_path.strip('{}')

            # 检查是否为图片文件
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')):
                image_files.append(file_path)

        if image_files:
            self.add_images_to_list(image_files)
        else:
            messagebox.showwarning("警告", "没有找到支持的图片文件")

    def load_image(self, image_path):
        """加载图片"""
        try:
            self.current_image = cv2.imread(image_path)

            if self.current_image is None:
                messagebox.showerror("错误", "无法读取图片文件")
                return

            # 转换为RGB格式并保存为PIL图片
            image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            self.original_pil_image = Image.fromarray(image_rgb)

            # 清空图片缓存
            self.image_cache.clear()

            # 重置视图参数并启用自适应缩放
            self.auto_fit_enabled = True
            self.image_scale = 1.0
            self.image_offset_x = 0
            self.image_offset_y = 0

            # 显示图片（会自动适应画布大小）
            self.display_image()

            # 显示对应的翻译结果
            self.display_current_translation_results()

            filename = os.path.basename(image_path)
            self.status_var.set(f"已加载: {filename}")

        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {e}")

    def get_current_image_path(self):
        """获取当前图片路径"""
        if self.image_list and 0 <= self.current_image_index < len(self.image_list):
            return self.image_list[self.current_image_index]
        return None

    def display_current_translation_results(self):
        """显示当前图片的翻译结果"""
        current_path = self.get_current_image_path()
        if current_path and current_path in self.all_translation_results:
            results = self.all_translation_results[current_path]
            self.display_translation_results(results)
        else:
            self.display_translation_results([])

    def display_image(self):
        """在画布上显示图片（兼容旧接口）"""
        self.update_image_display()

    def calculate_fit_scale(self):
        """计算适应画布的缩放比例"""
        if self.original_pil_image is None:
            return 1.0

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return 1.0

        img_width, img_height = self.original_pil_image.size

        # 计算适应宽度和高度的缩放比例
        scale_x = (canvas_width - 20) / img_width  # 留20像素边距
        scale_y = (canvas_height - 20) / img_height

        # 选择较小的缩放比例以确保图片完全显示
        fit_scale = min(scale_x, scale_y, 1.0)  # 不超过原始大小

        return max(fit_scale, 0.1)  # 最小缩放比例为0.1

    def get_cached_image(self, scale):
        """获取缓存的图片或创建新的缩放图片（高性能版）"""
        # 使用更粗粒度的缓存键，减少缓存数量
        cache_key = round(scale, 1)  # 精度降低到0.1

        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        # 智能缓存管理：保留常用的缩放比例
        if len(self.image_cache) > 8:  # 增加缓存数量
            # 保留1.0（原始大小）和当前最接近的几个
            keys_to_keep = sorted(self.image_cache.keys(), key=lambda x: abs(x - scale))[:6]
            if 1.0 not in keys_to_keep and 1.0 in self.image_cache:
                keys_to_keep.append(1.0)  # 总是保留原始大小

            # 清理其他缓存
            keys_to_remove = [k for k in self.image_cache.keys() if k not in keys_to_keep]
            for k in keys_to_remove:
                del self.image_cache[k]

        # 创建新的缩放图片
        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)

        # 优化重采样策略
        if scale != 1.0:
            # 根据缩放比例和图片大小选择重采样方法
            if scale > 2.0 or (scaled_width * scaled_height) > 4000000:  # 大图或大幅放大
                # 使用更快的重采样方法
                resample = Image.Resampling.BILINEAR
            else:
                # 使用高质量重采样
                resample = Image.Resampling.LANCZOS

            scaled_image = self.original_pil_image.resize(
                (scaled_width, scaled_height), resample
            )
        else:
            scaled_image = self.original_pil_image

        # 缓存图片
        self.image_cache[cache_key] = scaled_image
        return scaled_image

    def update_image_display(self):
        """更新图片显示（支持缩放和拖拽）"""
        if self.original_pil_image is None:
            return

        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # 画布还未初始化，延迟显示
            self.root.after(100, self.update_image_display)
            return

        # 检查是否需要自适应缩放
        current_canvas_size = (canvas_width, canvas_height)
        if self.auto_fit_enabled:
            # 计算适应画布的缩放比例
            fit_scale = self.calculate_fit_scale()
            self.image_scale = fit_scale

            # 居中显示图片
            img_width, img_height = self.original_pil_image.size
            scaled_width = int(img_width * self.image_scale)
            scaled_height = int(img_height * self.image_scale)

            self.image_offset_x = max(0, (canvas_width - scaled_width) // 2)
            self.image_offset_y = max(0, (canvas_height - scaled_height) // 2)

            # 禁用自适应缩放，避免重复触发
            self.auto_fit_enabled = False

        # 记录当前画布大小
        self.last_canvas_size = current_canvas_size

        # 获取缓存的图片或创建新的
        display_image = self.get_cached_image(self.image_scale)

        # 转换为Tkinter可显示的格式
        self.photo = ImageTk.PhotoImage(display_image)

        # 清空画布并显示图片
        self.canvas.delete("all")

        # 计算图片在画布上的位置
        x = self.image_offset_x
        y = self.image_offset_y

        # 创建图片对象
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo, tags="image")

        # 计算缩放后的图片尺寸
        img_width, img_height = self.original_pil_image.size
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)

        # 设置滚动区域
        left = min(0, x)
        top = min(0, y)
        right = max(canvas_width, x + scaled_width)
        bottom = max(canvas_height, y + scaled_height)

        self.canvas.configure(scrollregion=(left, top, right, bottom))

        # 更新状态栏显示缩放信息
        self.update_zoom_status_fast()

    def start_full_translation(self):
        """开始当前图片的全图翻译"""
        current_path = self.get_current_image_path()
        if not current_path:
            messagebox.showwarning("警告", "请先选择图片文件")
            return

        if self.is_translating:
            messagebox.showinfo("提示", "翻译正在进行中，请稍候...")
            return

        # 在新线程中执行翻译
        self.translate_btn.configure(state='disabled', text="翻译中...")
        self.progress.start()
        self.is_translating = True

        thread = threading.Thread(target=self._full_translation_thread, args=(current_path,))
        thread.daemon = True
        thread.start()

    def start_batch_translation(self):
        """开始批量翻译"""
        if not self.image_list:
            messagebox.showwarning("警告", "请先添加图片文件")
            return

        if self.is_translating or self.is_batch_translating:
            messagebox.showinfo("提示", "翻译正在进行中，请稍候...")
            return

        # 确认批量翻译
        untranslated_count = sum(1 for path in self.image_list if path not in self.all_translation_results)
        if untranslated_count == 0:
            messagebox.showinfo("提示", "所有图片都已翻译完成")
            return

        result = messagebox.askyesno("确认批量翻译",
                                   f"将翻译 {untranslated_count} 张未翻译的图片，这可能需要较长时间。\n\n是否继续？")
        if not result:
            return

        # 开始批量翻译
        self.batch_translate_btn.configure(state='disabled', text="批量翻译中...")
        self.translate_btn.configure(state='disabled')
        self.progress.start()
        self.is_batch_translating = True

        thread = threading.Thread(target=self._batch_translation_thread)
        thread.daemon = True
        thread.start()

    def _full_translation_thread(self, image_path):
        """全图翻译线程"""
        try:
            # 调用AI进行全图翻译
            results = self.call_full_image_translation(image_path)

            # 在主线程中更新UI
            self.root.after(0, self._translation_complete, image_path, results)

        except Exception as e:
            self.root.after(0, self._translation_error, str(e))

    def _batch_translation_thread(self):
        """批量翻译线程"""
        try:
            total_images = len(self.image_list)
            translated_count = 0

            for i, image_path in enumerate(self.image_list):
                # 跳过已翻译的图片
                if image_path in self.all_translation_results:
                    continue

                # 更新状态
                self.root.after(0, self._update_batch_status, i + 1, total_images, os.path.basename(image_path))

                # 翻译图片
                results = self.call_full_image_translation(image_path)

                # 保存结果
                if results:
                    self.all_translation_results[image_path] = results
                    translated_count += 1

                # 更新UI
                self.root.after(0, self._update_image_list_after_translation)

            # 批量翻译完成
            self.root.after(0, self._batch_translation_complete, translated_count)

        except Exception as e:
            self.root.after(0, self._batch_translation_error, str(e))

    def _translation_complete(self, image_path, results):
        """翻译完成"""
        self.progress.stop()
        self.translate_btn.configure(state='normal', text="翻译当前图片")
        self.is_translating = False

        if results:
            # 保存翻译结果
            self.all_translation_results[image_path] = results

            # 如果是当前图片，显示结果
            current_path = self.get_current_image_path()
            if current_path == image_path:
                self.display_translation_results(results)

            # 更新图片列表显示
            self.update_image_list_display()

            filename = os.path.basename(image_path)
            self.status_var.set(f"{filename} 翻译完成，共识别 {len(results)} 个文本块")
        else:
            messagebox.showinfo("信息", "未识别到任何文本内容")
            self.status_var.set("未识别到文本内容")

    def _update_batch_status(self, current, total, filename):
        """更新批量翻译状态"""
        self.status_var.set(f"批量翻译中 ({current}/{total}): {filename}")

    def _update_image_list_after_translation(self):
        """翻译后更新图片列表"""
        self.update_image_list_display()

    def _batch_translation_complete(self, translated_count):
        """批量翻译完成"""
        self.progress.stop()
        self.batch_translate_btn.configure(state='normal', text="批量翻译")
        self.translate_btn.configure(state='normal')
        self.is_batch_translating = False

        # 更新当前图片的翻译结果显示
        self.display_current_translation_results()

        messagebox.showinfo("批量翻译完成", f"成功翻译了 {translated_count} 张图片")
        self.status_var.set(f"批量翻译完成，共翻译 {translated_count} 张图片")

    def _batch_translation_error(self, error_msg):
        """批量翻译错误"""
        self.progress.stop()
        self.batch_translate_btn.configure(state='normal', text="批量翻译")
        self.translate_btn.configure(state='normal')
        self.is_batch_translating = False
        messagebox.showerror("错误", f"批量翻译失败: {error_msg}")
        self.status_var.set("批量翻译失败")

    def _translation_error(self, error_msg):
        """翻译错误"""
        self.progress.stop()
        self.translate_btn.configure(state='normal', text="开始全图翻译")
        self.is_translating = False
        messagebox.showerror("错误", f"翻译失败: {error_msg}")
        self.status_var.set("翻译失败")

    def display_translation_results(self, results=None):
        """显示翻译结果"""
        self.translation_text.delete(1.0, tk.END)

        if results is None:
            results = []

        if not results:
            self.translation_text.insert(tk.END, "暂无翻译结果\n")
            self.result_count_var.set("(0 个文本块)")
            return

        self.result_count_var.set(f"({len(results)} 个文本块)")

        for i, result in enumerate(results, 1):
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
            if i < len(results):
                self.translation_text.insert(tk.END, "─" * 50 + "\n\n", "separator")

    def clear_results(self):
        """清空当前图片的翻译结果"""
        current_path = self.get_current_image_path()
        if current_path and current_path in self.all_translation_results:
            result = messagebox.askyesno("确认清空", "确定要清空当前图片的翻译结果吗？")
            if result:
                del self.all_translation_results[current_path]
                self.display_translation_results([])
                self.update_image_list_display()
                self.status_var.set("已清空当前图片的翻译结果")
        else:
            self.display_translation_results([])
            self.status_var.set("当前图片无翻译结果")

    def save_current_translation(self):
        """保存当前图片的翻译结果"""
        current_path = self.get_current_image_path()
        if not current_path or current_path not in self.all_translation_results:
            messagebox.showwarning("警告", "当前图片没有翻译结果可保存")
            return

        results = self.all_translation_results[current_path]
        filename = os.path.splitext(os.path.basename(current_path))[0]

        file_path = filedialog.asksaveasfilename(
            title="保存当前图片翻译结果",
            initialname=f"{filename}_翻译结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self._save_results_to_file(file_path, {current_path: results})

    def save_all_translations(self):
        """保存所有翻译结果"""
        if not self.all_translation_results:
            messagebox.showwarning("警告", "没有翻译结果可保存")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存所有翻译结果",
            initialname="漫画翻译结果_全部",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self._save_results_to_file(file_path, self.all_translation_results)

    def _save_results_to_file(self, file_path, results_dict):
        """保存翻译结果到文件"""
        try:
            if file_path.endswith('.json'):
                # 保存为JSON格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results_dict, f, ensure_ascii=False, indent=2)
            else:
                # 保存为文本格式
                with open(file_path, 'w', encoding='utf-8') as f:
                    for image_path, results in results_dict.items():
                        filename = os.path.basename(image_path)
                        f.write(f"{'='*60}\n")
                        f.write(f"图片: {filename}\n")
                        f.write(f"{'='*60}\n\n")

                        for i, result in enumerate(results, 1):
                            f.write(f"【文本块 {i}】")
                            if result.get('type'):
                                f.write(f" - {result['type']}")
                            f.write("\n")

                            if result.get('original_text'):
                                f.write(f"原文: {result['original_text']}\n")
                            if result.get('translation'):
                                f.write(f"译文: {result['translation']}\n")
                            f.write("\n" + "─" * 50 + "\n\n")

                        f.write("\n\n")

            count = sum(len(results) for results in results_dict.values())
            messagebox.showinfo("成功", f"翻译结果已保存到: {file_path}\n共 {len(results_dict)} 张图片，{count} 个文本块")
            self.status_var.set(f"翻译结果已保存")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def show_context_menu(self, event):
        """显示右键菜单"""
        selection = self.image_listbox.curselection()
        if selection:
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def translate_selected_image(self):
        """翻译选中的图片"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if index != self.current_image_index:
                self.current_image_index = index
                self.load_current_image()
                self.update_image_list_display()
            self.start_full_translation()

    def remove_selected_image(self):
        """从列表移除选中的图片"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            image_path = self.image_list[index]
            filename = os.path.basename(image_path)

            result = messagebox.askyesno("确认移除", f"确定要从列表中移除 {filename} 吗？")
            if result:
                # 移除图片和翻译结果
                self.image_list.pop(index)
                if image_path in self.all_translation_results:
                    del self.all_translation_results[image_path]

                # 调整当前索引
                if index <= self.current_image_index:
                    self.current_image_index = max(0, self.current_image_index - 1)

                # 更新显示
                self.update_image_list_display()
                if self.image_list:
                    self.load_current_image()
                else:
                    self.current_image = None
                    self.display_image()
                    self.display_translation_results([])

    def show_in_explorer(self):
        """在文件管理器中显示"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            image_path = self.image_list[index]
            try:
                import subprocess
                subprocess.run(['explorer', '/select,', image_path.replace('/', '\\')], check=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件管理器: {e}")

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

    def call_full_image_translation(self, image_path):
        """调用AI进行全图翻译"""
        try:
            # 读取图片并编码为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

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

            # 获取高级设置
            target_language = config_manager.get_target_language()
            translation_style = config_manager.get_translation_style()
            custom_prompt = config_manager.get_custom_prompt()

            # 构建全图翻译提示词
            # 如果用户自定义了提示词，使用自定义的；否则使用动态生成的
            if custom_prompt and custom_prompt.strip():
                # 替换提示词中的占位符
                prompt = custom_prompt.replace("{target_language}", target_language)
                prompt = prompt.replace("{translation_style}", translation_style)
            else:
                # 使用默认提示词模板，但根据设置动态调整
                prompt = f"""请分析这张图片中的所有文本内容，包括对话气泡、标题、旁白、音效文字等。

要求：
1. 识别图片中的每一个文本块
2. 对每个文本块进行分类（如：对话、旁白、标题、音效等）
3. 将所有文本翻译成{target_language}
4. 翻译风格：{translation_style}
5. 保持原文的语气和风格

请按以下JSON格式返回结果：
```json
[
  {{
    "type": "对话气泡",
    "original_text": "原文内容",
    "translation": "{target_language}翻译"
  }},
  {{
    "type": "旁白",
    "original_text": "原文内容",
    "translation": "{target_language}翻译"
  }}
]
```

注意：
- 每个独立的文本区域都要单独列出
- 即使是很短的文字也要包含
- 翻译要准确且符合{target_language}表达习惯
- 保持原文的情感色彩
- 翻译风格要体现{translation_style}的特点"""

            print(f"🎯 使用翻译设置 - 目标语言: {target_language}, 风格: {translation_style}")
            print(f"📝 提示词长度: {len(prompt)} 字符")

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

            print(f"🔗 发送请求到: {url}")
            print(f"📝 使用模型: {provider_config.get('model_name', 'Unknown')}")

            response = requests.post(url, headers=headers, json=data, timeout=60)

            print(f"📊 响应状态码: {response.status_code}")

            # 检查HTTP状态
            if response.status_code != 200:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"📄 响应内容: {response.text}")
                raise Exception(f"API调用失败，状态码: {response.status_code}, 响应: {response.text}")

            result = response.json()
            print(f"📋 API响应结构: {list(result.keys())}")

            # 调试：打印完整响应（仅在开发时）
            if 'error' in result:
                print(f"❌ API返回错误: {result['error']}")
                raise Exception(f"API错误: {result['error']}")

            # 解析响应
            content = None
            if provider == "anthropic":
                if 'content' in result and len(result['content']) > 0:
                    content = result['content'][0]['text']
                else:
                    print(f"❌ Anthropic响应格式错误: {result}")
                    raise Exception("Anthropic API响应中缺少content字段")
            else:
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                else:
                    print(f"❌ OpenAI兼容API响应格式错误: {result}")
                    # 检查是否有错误信息
                    if 'error' in result:
                        raise Exception(f"API错误: {result['error']}")
                    else:
                        raise Exception(f"API响应中缺少choices字段。响应结构: {list(result.keys())}")

            if not content:
                raise Exception("API返回的内容为空")

            print(f"✅ 成功获取AI响应，内容长度: {len(content)}")

            # 解析JSON结果
            return self.parse_translation_response(content)

        except requests.exceptions.RequestException as e:
            print(f"🌐 网络请求失败: {e}")
            raise Exception(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"📄 JSON解析失败: {e}")
            print(f"📄 原始响应: {response.text if 'response' in locals() else 'No response'}")
            raise Exception(f"API响应不是有效的JSON格式: {e}")
        except KeyError as e:
            print(f"🔑 响应字段缺失: {e}")
            print(f"📋 可用字段: {list(result.keys()) if 'result' in locals() else 'No result'}")
            raise Exception(f"API响应中缺少必要字段: {e}")
        except Exception as e:
            print(f"❌ 全图翻译调用失败: {e}")
            raise e

    def parse_translation_response(self, content):
        """解析翻译响应"""
        try:
            # 尝试提取JSON部分

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

    # 创建主窗口（尝试支持拖拽）
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        print("✅ 创建了支持拖拽的窗口")
    except ImportError:
        root = tk.Tk()
        print("ℹ️  创建了标准窗口（不支持拖拽）")

    app = ComicFullTranslatorApp(root)

    # 运行应用
    root.mainloop()


if __name__ == "__main__":
    main()
