@echo off
REM 文件重复检测工具启动脚本
REM 设置代码页为UTF-8
chcp 65001 >nul

echo 文件重复检测工具启动中...
echo =============================

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python环境，请先安装Python 3.6或更高版本
    echo 请访问 https://www.python.org/downloads/ 下载并安装Python
    pause
    exit /b 1
)

echo Python环境检查通过

REM 检查主程序文件是否存在
if not exist "file_duplicate_detector.py" (
    echo 错误: 未找到主程序文件 file_duplicate_detector.py
    echo 请确保此批处理文件与主程序文件在同一目录下
    pause
    exit /b 1
)

echo 正在启动文件重复检测工具...

REM 运行程序
python file_duplicate_detector.py
if %errorlevel% neq 0 (
    echo 程序运行出错，请检查错误信息
    pause
    exit /b 1
)

echo 程序已退出
pause