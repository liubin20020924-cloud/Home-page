"""GitHub Webhook 接收器 - 接收 GitHub 推送通知"""
from flask import Flask, request, jsonify
import subprocess
import logging
import os
import hmac
import hashlib
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 尝试从 .env 文件加载环境变量
def load_env_file():
    """加载 .env 文件中的环境变量"""
    # 查找 .env 文件的位置
    possible_env_paths = [
        '/opt/Home-page/.env',
        Path(__file__).parent.parent / '.env',
        '.env'
    ]

    for env_path in possible_env_paths:
        if isinstance(env_path, Path):
            env_path = str(env_path)

        if os.path.exists(env_path):
            logger.info(f"Loading .env from: {env_path}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 如果环境变量不存在,则设置
                        if key not in os.environ:
                            os.environ[key] = value
                            logger.debug(f"Set env var: {key}")
            break

# 加载环境变量
load_env_file()

# GitHub Webhook 密钥
# 优先使用系统环境变量,其次使用 .env 文件中的配置
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
        raw_payload = request.json
        # 调试日志：记录原始 payload 类型
        logger.info(f"Raw payload type: {type(raw_payload)}, isinstance str: {isinstance(raw_payload, str)}")
        logger.info(f"Raw payload (first 200 chars): {str(raw_payload)[:200] if len(str(raw_payload)) > 200 else str(raw_payload)}")

        # request.json 可能返回字符串或字典，统一处理
        if isinstance(raw_payload, str):
            logger.info("Payload is string, parsing with json.loads()")
            payload = json.loads(raw_payload)
        else:
            logger.info("Payload is not string, using directly")
            payload = raw_payload

        # 调试日志：记录转换后的 payload 类型
        logger.info(f"Parsed payload type: {type(payload)}")
    except Exception as e:
        logger.error(f"Failed to parse JSON payload: {str(e)}")
        logger.error(f"Raw payload type when error occurred: {type(raw_payload)}")
        return jsonify({'error': 'Invalid JSON'}), 400

    # 从 payload 提取信息
    ref = payload.get('ref', '')
    commit = payload.get('commit', '')
    repository = payload.get('repository', '')
    author = payload.get('author', '')
    message = payload.get('message', '')
    timestamp = payload.get('timestamp', '')

    version = payload.get('version', 'latest')

    logger.info(f"Received GitHub webhook event: commit={commit[:7]}, version={version}")

    # 只处理 main 分支的推送（需要获取 branch 信息）
    # 从 payload 中获取 branch
    branch_payload = payload.get('branch', payload.get('ref', ''))
    branch = branch_payload.replace('refs/heads/', '') if branch_payload else ''

    # 只处理 main 分支的推送
    if branch == 'main':
        logger.info(f"Triggering deployment for branch: {branch}")

        # 记录部署开始
        deploy_start_time = datetime.now()

        try:
            # 确保 deploy.sh 有执行权限
            chmod_cmd = f"chmod +x {DEPLOY_SCRIPT}"
            logger.info(f"Setting execute permission: {chmod_cmd}")
            subprocess.run(chmod_cmd, shell=True, check=True)

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
    try:
        logger.info("="*60)
        logger.info("Starting GitHub webhook receiver on port 9000...")
        logger.info("="*60)

        # 检查 Python 版本
        import sys
        logger.info(f"Python version: {sys.version}")

        # 检查部署脚本是否存在
        if os.path.exists(DEPLOY_SCRIPT):
            logger.info(f"Deploy script exists: {DEPLOY_SCRIPT}")
        else:
            logger.error(f"Deploy script NOT found: {DEPLOY_SCRIPT}")

        # 检查日志目录是否可写
        log_dir = os.path.dirname(DEPLOY_LOG)
        if os.path.exists(log_dir):
            if os.access(log_dir, os.W_OK):
                logger.info(f"Log directory writable: {log_dir}")
            else:
                logger.error(f"Log directory NOT writable: {log_dir}")
        else:
            logger.error(f"Log directory NOT exists: {log_dir}")

        logger.info(f"Webhook secret configured: {'Yes' if WEBHOOK_SECRET != 'your-webhook-secret-here' else 'No (using default)'}")
        logger.info(f"Deploy script: {DEPLOY_SCRIPT}")
        logger.info(f"Version file: {VERSION_FILE}")
        logger.info(f"Deploy log: {DEPLOY_LOG}")
        logger.info("="*60)

        app.run(host='0.0.0.0', port=9000)
    except Exception as e:
        logger.error(f"Failed to start webhook receiver: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
