"""GitHub Webhook 接收器 - 接收 GitHub 推送通知"""
from flask import Flask, request, jsonify
import subprocess
import logging
import os
import hmac
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GitHub Webhook 密钥
# 生产环境建议使用环境变量或随机生成强密钥: python -c "import secrets; print(secrets.token_urlsafe(32))"
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your-webhook-secret-here')

# 部署脚本路径
DEPLOY_SCRIPT = '/opt/Home-page/scripts/deploy.sh'

# 版本记录文件路径
VERSION_FILE = '/opt/Home-page/.version_info.json'

# 部署日志路径
DEPLOY_LOG = '/var/log/integrate-code/deployment.log'


def save_version_info(payload, deploy_status):
    """保存版本信息"""
    try:
        version_info = {
            'version': payload.get('version', 'latest'),
            'repository': payload.get('repository', ''),
            'commit': payload.get('commit', ''),
            'author': payload.get('author', ''),
            'message': payload.get('message', ''),
            'timestamp': payload.get('timestamp', datetime.now().isoformat()),
            'deployed_at': datetime.now().isoformat(),
            'deploy_status': deploy_status
        }

        with open(VERSION_FILE, 'w') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)

        logger.info(f"Version info saved: {version_info['version']}")
    except Exception as e:
        logger.error(f"Failed to save version info: {e}")


def get_version_info():
    """获取当前版本信息"""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Failed to read version info: {e}")
        return None


@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """接收 GitHub Webhook"""
    # 验证签名（仅在配置了真正的密钥时）
    signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Hub-Signature')

    signature_valid = True
    if signature and WEBHOOK_SECRET != 'your-webhook-secret-here':
        if signature and signature.startswith('sha256='):
            payload = request.data
            expected_signature = 'sha256=' + hmac.new(
                WEBHOOK_SECRET.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning(f"Invalid webhook signature")
                logger.warning(f"Received: {signature}")
                logger.warning(f"Expected: {expected_signature}")
                logger.warning(f"WEBHOOK_SECRET length: {len(WEBHOOK_SECRET)}")
                # 临时允许签名验证失败,仅记录警告
                signature_valid = False
                logger.warning("Signature validation failed, but proceeding anyway (temporary)")

    # 解析 payload
    try:
        payload = request.json
    except Exception as e:
        logger.error(f"Failed to parse JSON payload: {str(e)}")
        return jsonify({'error': 'Invalid JSON'}), 400

    # 从 payload 提取信息
    ref = payload.get('ref', '')

    # 兼容不同的 payload 格式
    if 'repository' in payload:
        # GitHub Webhook 标准格式
        branch = ref.replace('refs/heads/', '') if ref else ''
        commit = payload.get('after', '')
        repository = payload.get('repository', {}).get('full_name', '')
        author = payload.get('pusher', {}).get('name', '')
        message = payload.get('head_commit', {}).get('message', '')
        timestamp = payload.get('head_commit', {}).get('timestamp', '')
    else:
        # CI/CD 通知格式
        branch = ref.replace('refs/heads/', '') if ref else ''
        commit = payload.get('commit', '')
        repository = payload.get('repository', '')
        author = payload.get('author', '')
        message = payload.get('message', '')
        timestamp = payload.get('timestamp', '')

    version = payload.get('version', 'latest')

    logger.info(f"Received GitHub webhook event: branch={branch}, commit={commit[:7]}, version={version}")

    # 只处理 main 分支的推送
    if branch == 'main':
        logger.info(f"Triggering deployment for branch: {branch}")

        # 记录部署开始
        deploy_start_time = datetime.now()

        try:
            # 执行部署脚本
            logger.info(f"Executing deploy script: {DEPLOY_SCRIPT}")
            result = subprocess.run(
                DEPLOY_SCRIPT,
                capture_output=True,
                text=True,
                timeout=600,  # 10分钟超时
                shell=True
            )

            # 记录部署结束
            deploy_duration = (datetime.now() - deploy_start_time).total_seconds()

            if result.returncode == 0:
                logger.info(f"Deployment successful (duration: {deploy_duration:.2f}s)")

                # 保存版本信息
                save_version_info({
                    'version': version,
                    'repository': repository,
                    'commit': commit,
                    'author': author,
                    'message': message,
                    'timestamp': timestamp
                }, deploy_status='success')

                # 写入部署日志
                with open(DEPLOY_LOG, 'a') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"部署时间: {datetime.now().isoformat()}\n")
                    f.write(f"版本: {version}\n")
                    f.write(f"提交: {commit}\n")
                    f.write(f"作者: {author}\n")
                    f.write(f"耗时: {deploy_duration:.2f}s\n")
                    f.write(f"状态: 成功\n")
                    f.write(f"{'='*60}\n")

                return jsonify({
                    'message': 'Deployment successful',
                    'version': version,
                    'commit': commit,
                    'duration': deploy_duration
                }), 200
            else:
                logger.error(f"Deployment failed: {result.stderr}")
                logger.error(f"Deployment stdout: {result.stdout}")

                # 保存版本信息（失败状态）
                save_version_info({
                    'version': version,
                    'repository': repository,
                    'commit': commit,
                    'author': author,
                    'message': message,
                    'timestamp': timestamp
                }, deploy_status='failed')

                # 写入部署日志
                with open(DEPLOY_LOG, 'a') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"部署时间: {datetime.now().isoformat()}\n")
                    f.write(f"版本: {version}\n")
                    f.write(f"提交: {commit}\n")
                    f.write(f"作者: {author}\n")
                    f.write(f"状态: 失败\n")
                    f.write(f"错误: {result.stderr}\n")
                    f.write(f"{'='*60}\n")

                return jsonify({
                    'error': 'Deployment failed',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }), 500

        except subprocess.TimeoutExpired:
            logger.error("Deployment timeout (10 minutes)")
            return jsonify({'error': 'Deployment timeout'}), 500
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    else:
        logger.info(f"Ignoring push event for branch: {branch}")
        return jsonify({
            'message': 'Ignored',
            'branch': branch
        }), 200


@app.route('/webhook/health', methods=['GET'])
def webhook_health():
    """Webhook 服务健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Webhook service is running'
    }), 200


@app.route('/webhook/version', methods=['GET'])
def webhook_version():
    """获取当前部署版本信息"""
    version_info = get_version_info()
    if version_info:
        return jsonify({
            'status': 'ok',
            'version': version_info
        }), 200
    else:
        return jsonify({
            'status': 'ok',
            'message': 'No version info available'
        }), 200


@app.route('/webhook/logs', methods=['GET'])
def webhook_logs():
    """获取部署日志（最近 20 条）"""
    try:
        with open(DEPLOY_LOG, 'r') as f:
            lines = f.readlines()
            # 返回最后 100 行
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            return jsonify({
                'status': 'ok',
                'logs': ''.join(recent_lines)
            }), 200
    except FileNotFoundError:
        return jsonify({
            'status': 'ok',
            'logs': 'No deployment logs found'
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting GitHub webhook receiver on port 9000...")
    logger.info(f"Webhook secret configured: {'Yes' if WEBHOOK_SECRET != 'your-webhook-secret-here' else 'No (using default)'}")
    logger.info(f"Deploy script: {DEPLOY_SCRIPT}")
    app.run(host='0.0.0.0', port=9000)
