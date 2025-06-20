@echo off
chcp 65001 >nul
echo 🚀 漫画翻译器自动打包工具
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
echo 📦 安装/更新依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo 🔨 开始打包...
python build_exe.py
if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成！
echo 📁 可执行文件位置: dist\漫画翻译器.exe
echo.
echo 💡 提示：
echo - 首次运行需要配置API密钥
echo - 详细说明请查看dist目录中的文档
echo.
pause
