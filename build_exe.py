# -*- coding: utf-8 -*-
"""
漫画翻译器打包脚本
使用PyInstaller将Python应用打包为exe文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    print("🔍 检查依赖...")
    
    # 包名映射：pip包名 -> 导入名
    package_mapping = {
        'pyinstaller': 'PyInstaller',
        'opencv-python': 'cv2',
        'openai': 'openai',
        'Pillow': 'PIL',
        'numpy': 'numpy',
        'requests': 'requests',
        'tkinterdnd2': 'tkinterdnd2'
    }

    missing_packages = []

    for pip_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name} - 已安装")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"❌ {pip_name} - 未安装")
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖已安装")
    return True

def clean_build_dirs():
    """清理之前的构建目录"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 删除目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"🗑️ 删除文件: {spec_file}")

def create_pyinstaller_spec():
    """创建PyInstaller配置文件"""
    print("📝 创建PyInstaller配置...")
    
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
    excludes=[],
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
    
    with open('comic_translator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 配置文件已创建: comic_translator.spec")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    try:
        # 使用PyInstaller构建
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'comic_translator.spec'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功!")
            print(f"输出: {result.stdout}")
        else:
            print("❌ 构建失败!")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现异常: {e}")
        return False
    
    return True

def copy_resources():
    """复制必要的资源文件到dist目录"""
    print("📁 复制资源文件...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    # 要复制的文件
    resource_files = [
        'requirements.txt',
        'README.md',
        '全图翻译使用指南.md',
        '快速配置指南.md',
        '安全配置指南.md',
        'user_config_template.json'
    ]
    
    for file_name in resource_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_dir)
            print(f"📄 复制文件: {file_name}")
    
    print("✅ 资源文件复制完成")
    return True

def main():
    """主函数"""
    print("🚀 漫画翻译器打包工具")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('comic_full_translator.py'):
        print("❌ 错误: 请在包含comic_full_translator.py的目录中运行此脚本")
        return False
    
    # 步骤1: 检查依赖
    if not check_dependencies():
        return False
    
    # 步骤2: 清理构建目录
    clean_build_dirs()
    
    # 步骤3: 创建配置文件
    create_pyinstaller_spec()
    
    # 步骤4: 构建可执行文件
    if not build_executable():
        return False
    
    # 步骤5: 复制资源文件
    if not copy_resources():
        return False
    
    print("\n🎉 打包完成!")
    print("=" * 50)
    print("📁 可执行文件位置: dist/漫画翻译器.exe")
    print("📚 使用说明文档也已复制到dist目录")
    print("\n💡 使用提示:")
    print("1. 首次运行前请确保网络连接正常")
    print("2. 在config.py中配置正确的API密钥")
    print("3. 参考使用说明文档了解详细操作步骤")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
