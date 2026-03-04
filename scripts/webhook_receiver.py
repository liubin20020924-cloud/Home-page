"""Webhook 接收器 - 接收 Gitee 推送通知"""
from flask import Flask, request, jsonify
import subprocess
import logging
import os

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Gitee Webhook 密钥 - 请修改为你的密钥
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'change-me-in-production')

# 部署脚本路径
DEPLOY_SCRIPT = '/opt/integrate-code/scripts/deploy.sh'


@app.route('/webhook/gitee', methods=['POST'])
def gitee_webhook():
    """接收 Gitee Webhook"""
    # 验证签名
    signature = request.headers.get('X-Gitee-Token')
    if signature != WEBHOOK_SECRET:
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401

    # 解析 payload
    try:
        payload = request.json
    except Exception as e:
        logger.error(f"Failed to parse JSON payload: {str(e)}")
        return jsonify({'error': 'Invalid JSON'}), 400

    ref = payload.get('ref', '')
    branch = ref.replace('refs/heads/', '') if ref else ''

    logger.info(f"Received webhook event: branch={branch}")

    # 只处理 main 分支的推送
    if branch == 'main':
        logger.info(f"Triggering deployment for branch: {branch}")

        try:
            # 执行部署脚本
            result = subprocess.run(
                [DEPLOY_SCRIPT],
                capture_output=True,
                text=True,
                timeout=300,
                shell=True
            )

            if result.returncode == 0:
                logger.info("Deployment successful")
                return jsonify({'message': 'Deployment started'}), 200
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                return jsonify({'error': 'Deployment failed'}), 500

        except subprocess.TimeoutExpired:
            logger.error("Deployment timeout")
            return jsonify({'error': 'Deployment timeout'}), 500
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        logger.info(f"Ignoring push event for branch: {branch}")
        return jsonify({'message': 'Ignored'}), 200


@app.route('/webhook/health', methods=['GET'])
def webhook_health():
    """Webhook 服务健康检查"""
    return jsonify({'status': 'ok', 'message': 'Webhook service is running'}), 200


if __name__ == '__main__':
    logger.info("Starting webhook receiver on port 9000...")
    app.run(host='0.0.0.0', port=9000)
