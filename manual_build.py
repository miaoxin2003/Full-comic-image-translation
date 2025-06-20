# -*- coding: utf-8 -*-
"""
手动打包脚本 - 简化版
适用于无法自动运行的环境
"""

import os
import sys

def print_instructions():
    """打印详细的手动打包指令"""
    print("🚀 漫画翻译器手动打包指令")
    print("=" * 60)
    print()
    
    print("📋 步骤1: 检查Python环境")
    print("请在命令行中运行以下命令检查Python版本：")
    print("  python --version")
    print("  (需要Python 3.8或更高版本)")
    print()
    
    print("📦 步骤2: 安装依赖包")
    print("请依次运行以下命令安装必要的依赖：")
    print("  pip install opencv-python>=4.8.0")
    print("  pip install openai>=1.0.0") 
    print("  pip install Pillow>=9.0.0")
    print("  pip install numpy>=1.21.0")
    print("  pip install requests>=2.25.0")
    print("  pip install pyinstaller>=5.0.0")
    print()
    print("或者一次性安装：")
    print("  pip install -r requirements.txt")
    print()
    
    print("🔨 步骤3: 执行打包")
    print("选择以下任一方式进行打包：")
    print()
    
    print("方式A - 使用配置文件（推荐）：")
    print("  pyinstaller --clean --noconfirm comic_translator.spec")
    print()
    
    print("方式B - 简单命令：")
    print("  pyinstaller --onefile --windowed --name=\"漫画翻译器\" comic_full_translator.py")
    print()
    
    print("方式C - 完整命令：")
    cmd = ('pyinstaller --onefile --windowed --name="漫画翻译器" '
           '--add-data="config.py;." --add-data="ai_client.py;." '
           '--add-data="image_processor.py;." '
           '--hidden-import=tkinter --hidden-import=PIL '
           '--hidden-import=cv2 --hidden-import=numpy '
           '--hidden-import=openai --hidden-import=requests '
           'comic_full_translator.py')
    print(f"  {cmd}")
    print()
    
    print("✅ 步骤4: 验证结果")
    print("打包完成后，检查以下内容：")
    print("  - dist目录是否存在")
    print("  - dist/漫画翻译器.exe文件是否存在")
    print("  - 文件大小是否合理（50-200MB）")
    print("  - 双击exe文件是否能正常启动")
    print()
    
    print("🎯 常用打包选项说明：")
    print("  --onefile        : 打包成单个exe文件")
    print("  --windowed       : 不显示控制台窗口")
    print("  --name           : 指定exe文件名")
    print("  --add-data       : 添加数据文件")
    print("  --hidden-import  : 添加隐藏导入的模块")
    print("  --clean          : 清理之前的构建文件")
    print("  --noconfirm      : 不询问确认，直接覆盖")
    print()
    
    print("🐛 常见问题解决：")
    print("1. 如果提示缺少模块，使用 --hidden-import=模块名 添加")
    print("2. 如果文件过大，可以使用 --exclude-module=模块名 排除不需要的模块")
    print("3. 如果启动慢，可以使用 --onedir 替代 --onefile")
    print("4. 如果出现编码问题，确保所有文件都是UTF-8编码")
    print()
    
    print("📁 项目文件检查：")
    files_to_check = [
        'comic_full_translator.py',
        'config.py', 
        'ai_client.py',
        'image_processor.py',
        'requirements.txt',
        'comic_translator.spec'
    ]
    
    print("请确保以下文件存在于当前目录：")
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (缺失)")
    print()
    
    print("🎉 完成后的文件结构：")
    print("  dist/")
    print("  ├── 漫画翻译器.exe    # 主程序")
    print("  └── (其他临时文件)")
    print()
    print("build/                   # 构建临时文件（可删除）")
    print("漫画翻译器.spec          # PyInstaller配置文件")
    print()
    
    print("💡 使用提示：")
    print("- 首次运行exe需要配置API密钥")
    print("- 确保网络连接正常以访问AI服务")
    print("- 可以将exe文件复制到任何位置使用")
    print("- 建议同时提供使用说明文档")
    print()
    
    print("🔗 相关文档：")
    print("- 打包指南.md     : 详细打包说明")
    print("- 使用说明.md     : 软件使用指南") 
    print("- 项目总结.md     : 功能概述")
    print()
    
    print("=" * 60)
    print("如需帮助，请参考打包指南.md文件获取更多信息")

def create_batch_file():
    """创建Windows批处理文件"""
    batch_content = '''@echo off
chcp 65001 >nul
echo 🚀 漫画翻译器打包工具
echo ================================

echo.
echo 📋 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📦 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败，尝试单独安装...
    pip install opencv-python openai Pillow numpy requests pyinstaller
)

echo.
echo 🔨 开始打包...
echo 使用配置文件打包...
pyinstaller --clean --noconfirm comic_translator.spec
if errorlevel 1 (
    echo ❌ 配置文件打包失败，尝试简单命令...
    pyinstaller --onefile --windowed --name="漫画翻译器" comic_full_translator.py
)

echo.
if exist "dist\\漫画翻译器.exe" (
    echo ✅ 打包成功！
    echo 📁 可执行文件位置: dist\\漫画翻译器.exe
    echo.
    echo 💡 提示：
    echo - 首次运行需要配置API密钥
    echo - 详细说明请查看使用文档
) else (
    echo ❌ 打包失败，请检查错误信息
    echo 请参考打包指南.md获取帮助
)

echo.
pause'''
    
    with open('quick_build.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✅ 已创建 quick_build.bat 批处理文件")
    print("💡 双击运行该文件可自动完成打包过程")

def main():
    """主函数"""
    print_instructions()
    print()
    
    # 询问是否创建批处理文件
    try:
        response = input("是否创建自动打包的批处理文件？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是', '']:
            create_batch_file()
    except KeyboardInterrupt:
        print("\n操作已取消")
    except:
        pass

if __name__ == "__main__":
    main()
