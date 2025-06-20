# -*- coding: utf-8 -*-
"""
修复NumPy兼容性问题的打包脚本
解决PyInstaller与新版NumPy的兼容性问题
"""

import os
import sys
import subprocess
import shutil

def print_header():
    """打印标题"""
    print("🔧 NumPy兼容性修复工具")
    print("=" * 50)
    print("解决PyInstaller与NumPy 2.x版本的兼容性问题")
    print()

def check_environment():
    """检查环境"""
    print("📋 检查当前环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查NumPy版本
    try:
        import numpy
        print(f"NumPy版本: {numpy.__version__}")
        
        # 检查是否是问题版本
        if numpy.__version__.startswith('2.'):
            print("⚠️ 检测到NumPy 2.x版本，可能存在兼容性问题")
            return False
        else:
            print("✅ NumPy版本兼容")
            return True
    except ImportError:
        print("❌ NumPy未安装")
        return False

def fix_numpy_version():
    """修复NumPy版本"""
    print("\n🔧 修复NumPy版本...")
    
    try:
        # 卸载当前NumPy
        print("卸载当前NumPy版本...")
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'numpy', '-y'], 
                      check=True, capture_output=True)
        
        # 安装兼容版本
        print("安装兼容的NumPy版本 (1.24.3)...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy==1.24.3'], 
                      check=True, capture_output=True)
        
        print("✅ NumPy版本修复完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ NumPy版本修复失败: {e}")
        return False

def install_compatible_packages():
    """安装兼容的包版本"""
    print("\n📦 安装兼容的依赖包...")
    
    packages = [
        "opencv-python==4.8.1.78",
        "numpy==1.24.3", 
        "Pillow==10.0.1",
        "openai==1.3.0",
        "requests==2.31.0",
        "pyinstaller==6.2.0"
    ]
    
    for package in packages:
        try:
            print(f"安装 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"⚠️ {package} 安装失败，尝试继续...")

def clean_build_dirs():
    """清理构建目录"""
    print("\n🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 删除目录: {dir_name}")

def create_fixed_spec():
    """创建修复后的spec文件"""
    print("\n📝 创建修复后的配置文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['comic_full_translator.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('ai_client.py', '.'),
        ('image_processor.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'cv2',
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.lib.format',
        'numpy.random',
        'openai',
        'requests',
        'json',
        'base64',
        'threading',
        'datetime',
        're',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'setuptools',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='漫画翻译器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('comic_translator_fixed.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 修复后的配置文件已创建: comic_translator_fixed.spec")

def build_with_fixed_config():
    """使用修复后的配置进行打包"""
    print("\n🔨 使用修复后的配置进行打包...")
    
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'comic_translator_fixed.spec']
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功!")
            print("📁 可执行文件位置: dist/漫画翻译器.exe")
            return True
        else:
            print("❌ 打包失败!")
            print(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出现异常: {e}")
        return False

def main():
    """主函数"""
    print_header()
    
    # 检查当前目录
    if not os.path.exists('comic_full_translator.py'):
        print("❌ 错误: 请在包含comic_full_translator.py的目录中运行此脚本")
        return False
    
    # 检查环境
    if not check_environment():
        # 修复NumPy版本
        if not fix_numpy_version():
            print("❌ 无法修复NumPy版本，请手动处理")
            return False
    
    # 安装兼容的包
    install_compatible_packages()
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建修复后的配置
    create_fixed_spec()
    
    # 执行打包
    if build_with_fixed_config():
        print("\n🎉 修复和打包完成!")
        print("=" * 50)
        print("📁 可执行文件位置: dist/漫画翻译器.exe")
        print("💡 现在可以测试运行exe文件了")
        return True
    else:
        print("\n❌ 打包失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("按回车键退出...")
        sys.exit(1)
    else:
        input("按回车键退出...")
