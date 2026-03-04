#!/bin/bash

# 云户科技网站 - Linux启动脚本

echo "========================================"
echo "云户科技网站 - 启动脚本"
echo "========================================"
echo ""

# 检查 Python 环境
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3 未安装"
    exit 1
fi

echo "[成功] Python3 已安装: $(python3 --version)"
echo ""

# 检查依赖包
echo "检查依赖包..."
python3 -c "import flask, pymysql, flask_socketio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[提示] 正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖包安装失败"
        exit 1
    fi
fi

echo "[成功] 依赖包已就绪"
echo ""

# 启动应用
echo "启动应用..."
echo "========================================"
echo "官网首页: http://localhost:5000/"
echo "知识库系统: http://localhost:5000/kb"
echo "工单系统: http://localhost:5000/case"
echo "用户管理: http://localhost:5000/user-mgmt/"
echo "========================================"
echo ""

python3 app.py
