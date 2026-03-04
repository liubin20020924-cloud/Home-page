@echo off
chcp 65001 >nul
echo ========================================
echo 云户科技网站 - 启动脚本
echo ========================================
echo.

echo 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

echo [成功] Python 已安装
echo.

echo 检查依赖包...
python -c "import flask, pymysql, flask_socketio" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
)

echo [成功] 依赖包已就绪
echo.

echo 启动应用...
echo ========================================
echo 官网首页: http://localhost:5000/
echo 知识库系统: http://localhost:5000/kb
echo 工单系统: http://localhost:5000/case
echo 用户管理: http://localhost:5000/user-mgmt/
echo ========================================
echo.

python app.py

pause
