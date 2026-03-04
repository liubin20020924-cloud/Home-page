#!/usr/bin/env python3
"""
云户科技网站 - 部署配置检查脚本
用于验证自动部署配置是否正确
"""

import os
import sys

# 颜色输出
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def print_info(msg):
    print(f"[INFO] {msg}")


def print_warn(msg):
    print(f"[WARN] {msg}")


def print_error(msg):
    print(f"[ERROR] {msg}")


def print_step(msg):
    print(f"[STEP] {msg}")


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print_info(f"[OK] {description}: {filepath}")
        return True
    else:
        print_error(f"[X] {description} 不存在: {filepath}")
        return False


def check_file_content(filepath, content, description):
    """检查文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_content = f.read()

        if content in file_content:
            print_info(f"[OK] {description} 配置正确")
            return True
        else:
            print_warn(f"[!] {description} 需要更新")
            print(f"  期望包含: {content}")
            return False
    except FileNotFoundError:
        print_error(f"[X] 文件不存在: {filepath}")
        return False


def main():
    print("=" * 60)
    print("云户科技网站 - 部署配置检查")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # 检查核心文件
    print_step("检查核心文件...")
    all_checks_passed &= check_file_exists('.github/workflows/sync-to-gitee.yml', 'GitHub Action 配置')
    all_checks_passed &= check_file_exists('.github/workflows/ci-cd.yml', 'CI/CD 配置')
    all_checks_passed &= check_file_exists('CHANGELOG.md', '变更日志')
    all_checks_passed &= check_file_exists('scripts/deploy.sh', '部署脚本')
    all_checks_passed &= check_file_exists('scripts/rollback.sh', '回滚脚本')
    all_checks_passed &= check_file_exists('scripts/check_and_deploy.sh', '自动检测脚本')
    all_checks_passed &= check_file_exists('scripts/webhook_receiver.py', 'Webhook 接收器')
    all_checks_passed &= check_file_exists('scripts/deploy_service.sh', '部署服务安装')
    print()
    
    # 检查文档
    print_step("检查文档...")
    all_checks_passed &= check_file_exists('docs/VERSION_MANAGEMENT_GUIDE.md', '版本管理规范')
    all_checks_passed &= check_file_exists('docs/QUICK_START_VERSIONING.md', '版本管理快速指南')
    all_checks_passed &= check_file_exists('docs/AUTO_DEPLOY_SETUP.md', '自动部署配置')
    print()
    
    # 检查配置占位符
    print_step("检查配置占位符...")
    
    webhook_files = [
        ('scripts/webhook_receiver.py', "WEBHOOK_SECRET = 'your-webhook-secret-here'"),
        ('scripts/check_and_deploy.sh', 'WEBHOOK_SECRET="your-webhook-secret-here"'),
    ]
    
    for filepath, placeholder in webhook_files:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'your-webhook-secret-here' in content or 'change-me-in-production' in content:
                print_warn(f"[!] {filepath} 包含占位符，请修改为实际密钥")
            else:
                print_info(f"[OK] {filepath} 配置已更新")
    
    print()
    
    # 检查 GitHub Actions 配置
    print_step("检查 GitHub Actions 配置...")
    
    if os.path.exists('.github/workflows/sync-to-gitee.yml'):
        with open('.github/workflows/sync-to-gitee.yml', 'r', encoding='utf-8') as f:
            content = f.read()

        if '${{ secrets.SSH_PRIVATE_KEY }}' in content:
            print_info("[OK] SSH 私钥已配置(使用 GitHub Secrets)")
        else:
            print_warn("[!] SSH 私钥配置需要检查")

        if '${{ secrets.GITEE_REPO }}' in content:
            print_info("[OK] Gitee 仓库路径已配置(使用 GitHub Secrets)")
        else:
            print_warn("[!] Gitee 仓库路径配置需要检查")
    
    print()
    
    # 显示下一步操作
    print("=" * 60)
    if all_checks_passed:
        print("[OK] 所有核心文件已创建！")
    else:
        print("[!] 部分文件缺失，请检查上述错误")
    print()
    print("下一步操作：")
    print()
    print("1. GitHub 配置:")
    print("   - 生成 SSH 密钥对")
    print("   - 配置 Gitee SSH 公钥")
    print("   - 添加 GitHub Secrets:")
    print("     * SSH_PRIVATE_KEY")
    print("     * GITEE_REPO")
    print()
    print("2. Gitee 配置:")
    print("   - 配置 Webhook（可选）")
    print("   - URL: http://your-server-ip:9000/webhook/gitee")
    print()
    print("3. 云主机配置:")
    print("   - 修改 scripts/webhook_receiver.py 中的 WEBHOOK_SECRET")
    print("   - 修改 scripts/check_and_deploy.sh 中的 WEBHOOK_SECRET")
    print("   - 运行: bash scripts/deploy_service.sh")
    print()
    print("详细文档：")
    print("   - docs/VERSION_MANAGEMENT_GUIDE.md")
    print("   - docs/QUICK_START_VERSIONING.md")
    print("   - docs/AUTO_DEPLOY_SETUP.md")
    print("=" * 60)


if __name__ == '__main__':
    main()
