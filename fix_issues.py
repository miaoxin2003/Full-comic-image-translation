#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目问题修复脚本
自动检测和修复常见问题
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    required_packages = [
        'opencv-python', 'openai', 'Pillow', 'numpy', 
        'requests', 'tkinterdnd2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 安装缺失的包...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败")
            return False
    
    return True

def check_config_file():
    """检查配置文件"""
    print("\n⚙️ 检查配置文件...")
    
    config_file = "user_config.json"
    template_file = "user_config_template.json"
    
    if not os.path.exists(config_file):
        if os.path.exists(template_file):
            print(f"📋 从模板创建配置文件...")
            shutil.copy(template_file, config_file)
            print(f"✅ 已创建 {config_file}")
            print(f"⚠️  请编辑 {config_file} 设置你的API密钥")
        else:
            print(f"❌ 配置文件和模板都不存在")
            return False
    
    # 检查配置文件内容
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查是否包含占位符
        placeholders = [
            "YOUR_OPENROUTER_API_KEY_HERE",
            "YOUR_OPENAI_API_KEY_HERE", 
            "YOUR_ANTHROPIC_API_KEY_HERE",
            "YOUR_CUSTOM_API_KEY_HERE"
        ]
        
        config_str = json.dumps(config)
        has_placeholders = any(placeholder in config_str for placeholder in placeholders)
        
        if has_placeholders:
            print("⚠️  配置文件包含占位符，请设置真实的API密钥")
        else:
            print("✅ 配置文件格式正确")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ 配置文件JSON格式错误")
        return False
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def check_file_permissions():
    """检查文件权限"""
    print("\n🔐 检查文件权限...")
    
    config_file = "user_config.json"
    if os.path.exists(config_file):
        # 在Windows上跳过权限检查
        if os.name == 'nt':
            print("ℹ️  Windows系统，跳过权限检查")
        else:
            # Unix系统检查权限
            stat = os.stat(config_file)
            mode = stat.st_mode & 0o777
            if mode != 0o600:
                print(f"⚠️  配置文件权限不安全: {oct(mode)}")
                try:
                    os.chmod(config_file, 0o600)
                    print("✅ 已修复文件权限")
                except:
                    print("❌ 无法修改文件权限")
            else:
                print("✅ 文件权限安全")
    
    return True

def check_api_connectivity():
    """检查API连接性"""
    print("\n🌐 检查API连接性...")
    
    try:
        import requests
        
        # 测试网络连接
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ 网络连接正常")
        else:
            print("⚠️  网络连接可能有问题")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络连接失败: {e}")
        return False
    except ImportError:
        print("❌ requests包未安装")
        return False

def create_gitignore():
    """创建.gitignore文件"""
    print("\n📝 检查.gitignore文件...")
    
    gitignore_content = """# 配置文件
user_config.json
*.key
*.secret
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# 临时文件
*.tmp
*.log
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✅ 已创建.gitignore文件")
    else:
        print("✅ .gitignore文件已存在")
    
    return True

def main():
    """主函数"""
    print("🔧 漫画翻译器项目问题修复工具")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("配置文件", check_config_file),
        ("文件权限", check_file_permissions),
        ("网络连接", check_api_connectivity),
        ("Git配置", create_gitignore),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有检查都通过了！项目可以正常运行。")
    else:
        print("\n⚠️  发现问题，请根据上述提示进行修复。")
    
    print("\n💡 下一步:")
    print("1. 编辑 user_config.json 设置API密钥")
    print("2. 运行: python comic_full_translator.py")
    
    return all_passed

if __name__ == "__main__":
    main()
