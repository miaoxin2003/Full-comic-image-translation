#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速打包脚本 - 简化版
直接使用PyInstaller命令打包
"""

import os
import sys
import subprocess
import shutil

def main():
    """主函数"""
    print("🚀 快速打包漫画翻译器")
    print("=" * 40)
    
    # 检查主文件是否存在
    if not os.path.exists('comic_full_translator.py'):
        print("❌ 错误: 找不到 comic_full_translator.py")
        return False
    
    # 清理之前的构建
    print("🧹 清理之前的构建...")
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🗑️ 删除 build 目录")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🗑️ 删除 dist 目录")
    
    # 删除旧的spec文件
    for spec_file in ['comic_translator.spec', '漫画翻译器.spec']:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"🗑️ 删除 {spec_file}")
    
    # 构建PyInstaller命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # 无控制台窗口
        '--name=漫画翻译器',             # 指定输出文件名
        '--add-data=config.py;.',       # 添加配置文件
        '--add-data=ai_client.py;.',    # 添加AI客户端
        '--add-data=image_processor.py;.', # 添加图像处理器
        '--hidden-import=tkinter',      # 隐式导入
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=openai',
        '--hidden-import=requests',
        '--hidden-import=json',
        '--hidden-import=base64',
        '--hidden-import=threading',
        '--hidden-import=datetime',
        '--hidden-import=re',
        '--clean',                      # 清理缓存
        '--noconfirm',                  # 不询问确认
        'comic_full_translator.py'      # 主文件
    ]
    
    print("🔨 开始打包...")
    print(f"执行命令: PyInstaller ...")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功!")
            
            # 复制文档文件到dist目录
            print("📁 复制文档文件...")
            dist_dir = 'dist'
            docs_to_copy = [
                'README.md',
                '全图翻译使用指南.md',
                '快速配置指南.md',
                '安全配置指南.md',
                'user_config_template.json',
                'requirements.txt'
            ]
            
            for doc in docs_to_copy:
                if os.path.exists(doc):
                    shutil.copy2(doc, dist_dir)
                    print(f"📄 复制: {doc}")
            
            print("\n🎉 打包完成!")
            print("=" * 40)
            print(f"📁 可执行文件: dist/漫画翻译器.exe")
            print("📚 文档文件已复制到 dist 目录")
            
            # 显示文件大小
            exe_path = os.path.join(dist_dir, '漫画翻译器.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📊 文件大小: {size_mb:.1f} MB")
            
            print("\n💡 使用提示:")
            print("1. 首次运行前请配置API密钥")
            print("2. 参考文档了解详细使用方法")
            print("3. 确保网络连接正常")
            
            return True
            
        else:
            print("❌ 打包失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 打包过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 如果遇到问题，请尝试:")
        print("1. 确保所有依赖已安装: pip install -r requirements.txt")
        print("2. 使用管理员权限运行")
        print("3. 检查防病毒软件是否阻止")
        sys.exit(1)
    else:
        print("\n🎊 打包成功完成!")
        input("按回车键退出...")
