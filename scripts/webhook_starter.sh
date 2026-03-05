#!/bin/bash

# Webhook Receiver 启动脚本
cd /opt/Home-page

# 使用虚拟环境运行
exec /opt/Home-page/venv/bin/python /opt/Home-page/scripts/webhook_receiver_github.py > /var/log/integrate-code/webhook.log 2>&1
