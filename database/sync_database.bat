@echo off
REM =====================================================
REM 智能数据库同步脚本 (Windows)
REM =====================================================

echo.
echo ====================================================
echo    云户科技 - 智能数据库同步工具 (Windows)
echo ====================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 检查 PyMySQL 是否安装
python -c "import pymysql" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] PyMySQL 未安装，正在安装...
    pip install pymysql
    if %errorlevel% neq 0 (
        echo [错误] PyMySQL 安装失败
        pause
        exit /b 1
    )
)

REM 获取参数
set HOST=%1
set PORT=%2
set USER=%3
set PASSWORD=%4

REM 如果没有提供参数，使用默认值或提示输入
if "%HOST%"=="" set HOST=localhost
if "%PORT%"=="" set PORT=3306
if "%USER%"=="" set USER=root
if "%PASSWORD%"=="" (
    set /p PASSWORD="请输入MySQL密码（留空表示无密码）: "
)

REM 执行同步
echo.
echo [开始] 执行数据库同步...
echo.
python "%~dp0sync_database.py" %HOST% %PORT% %USER% %PASSWORD%

if %errorlevel% equ 0 (
    echo.
    echo [成功] 数据库同步完成
) else (
    echo.
    echo [失败] 数据库同步失败
)

echo.
pause
