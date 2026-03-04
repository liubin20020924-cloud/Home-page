@echo off
REM 图片快速优化脚本（Windows版本）
REM 无需修改代码，直接运行即可优化所有图片

echo ======================================
echo    图片优化脚本
echo ======================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3
    pause
    exit /b 1
)

REM 检查 Pillow 是否安装
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 Pillow...
    pip install Pillow
)

REM 备份原图
echo 1. 备份原始图片...
if not exist "static\home\images\backup" mkdir "static\home\images\backup"
if not exist "static\case\images\backup" mkdir "static\case\images\backup"
if not exist "static\kb\images\backup" mkdir "static\kb\images\backup"

for %%f in (static\home\images\*.jpg) do copy "%%f" "static\home\images\backup\" >nul
for %%f in (static\case\images\*.jpg) do copy "%%f" "static\case\images\backup\" >nul 2>nul
for %%f in (static\kb\images\*.jpg) do copy "%%f" "static\kb\images\backup\" >nul 2>nul

echo    - 原图已备份到 backup 目录
echo.

REM 优化首页图片
echo 2. 优化首页图片...
python scripts\optimize_images.py static\home\images -o static\home\images\optimized -q 80 -w 1400
echo.

REM 应用优化后的首页图片
echo 3. 应用优化后的首页图片...
for %%f in (static\home\images\optimized\*_opt.jpg) do copy "%%f" "static\home\images\" >nul
echo    - 首页图片已更新
echo.

REM 优化工单系统图片
if exist "static\case\images" (
    echo 4. 优化工单系统图片...
    python scripts\optimize_images.py static\case\images -o static\case\images\optimized -q 80 -w 800
    for %%f in (static\case\images\optimized\*_opt.jpg) do copy "%%f" "static\case\images\" >nul
    echo    - 工单系统图片已更新
    echo.
)

REM 优化知识库图片
if exist "static\kb\images" (
    echo 5. 优化知识库图片...
    python scripts\optimize_images.py static\kb\images -o static\kb\images\optimized -q 80 -w 800
    for %%f in (static\kb\images\optimized\*_opt.jpg) do copy "%%f" "static\kb\images\" >nul
    echo    - 知识库图片已更新
    echo.
)

REM 清理临时文件
echo 6. 清理优化后的临时文件...
if exist "static\home\images\optimized" rmdir /s /q "static\home\images\optimized"
if exist "static\case\images\optimized" rmdir /s /q "static\case\images\optimized"
if exist "static\kb\images\optimized" rmdir /s /q "static\kb\images\optimized"

echo ======================================
echo    优化完成！
echo ======================================
echo.
echo 原图片已备份到各目录的 backup 文件夹
echo.
echo 如需恢复原图，执行：
echo   copy static\home\images\backup\*.jpg static\home\images\
echo.
echo 查看优化效果：
echo   打开浏览器 F12 -^> Network -^> 刷新页面
echo.
pause
