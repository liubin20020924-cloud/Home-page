@echo off
REM =====================================================
REM 云户科技网站数据库初始化脚本 (Windows)
REM 用于全新部署系统时初始化数据库
REM 版本: v2.0
REM 创建时间: 2026-02-27
REM =====================================================

echo ====================================================
echo 云户科技网站数据库初始化脚本 (v2.0)
echo ====================================================
echo.

REM 检查参数
if "%~1"=="" (
    echo 用法: init_database.bat [MySQL用户名]
    echo 示例: init_database.bat root
    echo.
    echo 注意: 首次运行会提示输入MySQL密码
    pause
    exit /b 1
)

set MYSQL_USER=%~1
set MYSQL_HOST=localhost
set MYSQL_PORT=3306

echo 配置信息:
echo   MySQL用户: %MYSQL_USER%
echo   MySQL主机: %MYSQL_HOST%
echo   MySQL端口: %MYSQL_PORT%
echo.

REM 检查SQL文件是否存在
if not exist "init_database.sql" (
    echo 错误: 找不到 init_database.sql 文件
    pause
    exit /b 1
)

echo 正在执行数据库初始化...
echo 请输入MySQL密码:
echo.

REM 执行初始化脚本
mysql -h %MYSQL_HOST% -P %MYSQL_PORT% -u %MYSQL_USER% -p < init_database.sql

if %errorlevel% equ 0 (
    echo.
    echo ====================================================
    echo 数据库初始化成功!
    echo ====================================================
    echo.
    echo 默认管理员账号:
    echo   用户名: admin
    echo   密码: YHKB@2024
    echo.
    echo 重要: 生产环境部署后请立即修改默认密码！
    echo ====================================================
) else (
    echo.
    echo ====================================================
    echo 数据库初始化失败!
    echo 请检查:
    echo 1. MySQL服务是否启动
    echo 2. 用户名和密码是否正确
    echo 3. 用户是否有创建数据库的权限
    echo ====================================================
)

echo.
pause
