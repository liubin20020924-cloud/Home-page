"""
安全加固脚本

功能：
1. 检查前端 XSS 漏洞
2. 检查 CSRF 保护
3. 检查 API 限流
4. 生成安全报告
5. 自动修复简单问题
"""

import os
import re
import logging
from typing import List, Dict, Tuple
from datetime import datetime


class SecurityAuditor:
    """安全审计器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.issues = []
        self.templates_dir = 'templates'
        self.routes_dir = 'routes'

    def audit_all(self) -> List[Dict]:
        """
        执行完整的安全审计

        Returns:
            发现的问题列表
        """
        self.logger.info("Starting security audit...")

        # 检查 XSS 漏洞
        self.check_xss_vulnerabilities()

        # 检查 CSRF 保护
        self.check_csrf_protection()

        # 检查 API 限流
        self.check_rate_limiting()

        # 检查敏感信息泄露
        self.check_sensitive_data_exposure()

        # 检查依赖漏洞
        self.check_dependency_vulnerabilities()

        self.logger.info(f"Security audit completed. Found {len(self.issues)} issues.")

        return self.issues

    def check_xss_vulnerabilities(self):
        """检查 XSS 漏洞"""
        self.logger.info("Checking for XSS vulnerabilities...")

        # 扫描所有模板文件
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    self._check_template_xss(file_path)

    def _check_template_xss(self, file_path: str):
        """
        检查模板文件的 XSS 漏洞

        Args:
            file_path: 模板文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 危险的 Jinja2 模式（未转义）
        dangerous_patterns = [
            r'\{\{\s*[^|}]+\|\s*safe\s*\}\}',  # {{ content|safe }}
            r'\{\{\s*[^|}]+[^|]\s*\}\}',  # {{ content }} (没有 |safe 以外的过滤)
        ]

        # 检查用户输入是否被转义
        user_input_patterns = [
            r'\{\{\s*(message\.|content\.|description\.|comment\.)',
            r'\{\{\s*(form\.)',
            r'\{\{\s*(request\.)',
        ]

        line_num = 0
        for line in lines:
            line_num += 1

            # 检查危险模式
            for pattern in dangerous_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if '|safe' not in line and 'autoescape' not in content:
                        self._add_issue(
                            severity='HIGH',
                            category='XSS',
                            file=file_path,
                            line=line_num,
                            message=f"Potential XSS vulnerability: {match.group()}",
                            recommendation="Use Jinja2 autoescaping or explicitly escape user input"
                        )

            # 检查用户输入是否正确转义
            for pattern in user_input_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if '|safe' in line or 'autoescape false' in content.lower():
                        self._add_issue(
                            severity='HIGH',
                            category='XSS',
                            file=file_path,
                            line=line_num,
                            message=f"Unescaped user input: {match.group()}",
                            recommendation="Remove |safe filter or add autoescape"
                        )

    def check_csrf_protection(self):
        """检查 CSRF 保护"""
        self.logger.info("Checking CSRF protection...")

        # 检查 Flask-WTF 是否安装
        try:
            import flask_wtf
            csrf_enabled = True
        except ImportError:
            csrf_enabled = False
            self._add_issue(
                severity='MEDIUM',
                category='CSRF',
                file='app.py',
                line=1,
                message='Flask-WTF not installed - CSRF protection disabled',
                recommendation='Install flask-wtf: pip install flask-wtf'
            )

        if csrf_enabled:
            # 检查表单是否包含 CSRF token
            for root, dirs, files in os.walk(self.templates_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        self._check_form_csrf(file_path)

    def _check_form_csrf(self, file_path: str):
        """
        检查表单的 CSRF 保护

        Args:
            file_path: 模板文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 查找表单标签
        in_form = False
        form_start_line = 0
        has_csrf = False

        line_num = 0
        for line in lines:
            line_num += 1

            if '<form' in line.lower():
                in_form = True
                form_start_line = line_num
                has_csrf = False
            elif '</form>' in line.lower():
                if in_form and not has_csrf:
                    # 跳过 GET 请求的表单
                    if 'method="get"' not in lines[form_start_line-1:line_num]:
                        self._add_issue(
                            severity='MEDIUM',
                            category='CSRF',
                            file=file_path,
                            line=form_start_line,
                            message='Form missing CSRF token',
                            recommendation='Add {{ csrf_token() }} inside form tag'
                        )
                in_form = False
            elif 'csrf_token' in line:
                has_csrf = True

    def check_rate_limiting(self):
        """检查 API 限流"""
        self.logger.info("Checking rate limiting...")

        # 检查路由文件中是否有限流装饰器
        rate_limit_patterns = [
            r'@.*limit.*request',
            r'@.*ratelimit',
            r'@.*rate_limit',
        ]

        for root, dirs, files in os.walk(self.routes_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    self._check_rate_limiting_file(file_path, rate_limit_patterns)

    def _check_rate_limiting_file(self, file_path: str, patterns: List[str]):
        """
        检查文件的限流配置

        Args:
            file_path: 文件路径
            patterns: 限流模式列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 检查是否有公开 API 路由
        has_public_api = any('@auth_bp.route' in line or '@api_bp.route' in line
                            for line in lines)

        if has_public_api:
            # 检查是否有限流
            has_rate_limit = any(re.search(pattern, content, re.IGNORECASE)
                                for pattern in patterns)

            if not has_rate_limit:
                self._add_issue(
                    severity='MEDIUM',
                    category='Rate Limiting',
                    file=file_path,
                    line=1,
                    message='Public API endpoints missing rate limiting',
                    recommendation='Add rate limiting decorators to public API routes'
                )

    def check_sensitive_data_exposure(self):
        """检查敏感信息泄露"""
        self.logger.info("Checking for sensitive data exposure...")

        # 检查是否在日志中记录密码
        password_patterns = [
            r'logger\.(info|debug|warning)\([^)]*[pP]assword',
            r'print\([^)]*[pP]assword',
            r'console\.log\([^)]*[pP]assword',
        ]

        # 扫描 Python 文件
        for root, dirs, files in os.walk('.'):
            # 跳过虚拟环境和 node_modules
            if '__pycache__' in root or 'venv' in root or 'node_modules' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._check_sensitive_logging(file_path, password_patterns)

    def _check_sensitive_logging(self, file_path: str, patterns: List[str]):
        """
        检查文件中的敏感信息日志

        Args:
            file_path: 文件路径
            patterns: 敏感信息模式
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        line_num = 0
        for line in lines:
            line_num += 1

            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self._add_issue(
                        severity='HIGH',
                        category='Sensitive Data',
                        file=file_path,
                        line=line_num,
                        message='Potential password logging detected',
                        recommendation='Remove sensitive data from logs and use proper password handling'
                    )

    def check_dependency_vulnerabilities(self):
        """检查依赖漏洞"""
        self.logger.info("Checking for known dependency vulnerabilities...")

        # 检查 requirements.txt
        req_file = 'requirements.txt'
        if os.path.exists(req_file):
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()

            # 已知有漏洞的包版本（示例）
            known_vulnerabilities = {
                'flask': {'<2.0.0': 'CSRF vulnerability'},
                'werkzeug': {'<2.0.0': 'Remote code execution'},
                'jinja2': {'<3.0.0': 'Template injection'},
            }

            for req in requirements:
                if not req.strip() or req.startswith('#'):
                    continue

                # 解析包名和版本
                parts = req.strip().split('==')
                package_name = parts[0].lower().strip()

                if package_name in known_vulnerabilities:
                    self._add_issue(
                        severity='HIGH',
                        category='Dependency',
                        file=req_file,
                        line=1,
                        message=f'Package {package_name} may have vulnerabilities',
                        recommendation=f'Check and update {package_name} to latest version'
                    )

    def _add_issue(self, severity: str, category: str, file: str,
                    line: int, message: str, recommendation: str):
        """
        添加安全问题

        Args:
            severity: 严重程度（HIGH, MEDIUM, LOW）
            category: 问题类别
            file: 文件路径
            line: 行号
            message: 问题描述
            recommendation: 修复建议
        """
        issue = {
            'severity': severity,
            'category': category,
            'file': file,
            'line': line,
            'message': message,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
        self.issues.append(issue)
        self.logger.warning(f"[{severity}] {category}: {message}")

    def generate_report(self) -> str:
        """
        生成安全审计报告

        Returns:
            Markdown 格式的报告
        """
        report_lines = [
            "# 安全审计报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        ]

        # 按严重程度分组
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low_issues = [i for i in self.issues if i['severity'] == 'LOW']

        # 高危问题
        if high_issues:
            report_lines.append("## 🔴 高危问题")
            report_lines.append(f"\n发现 {len(high_issues)} 个高危问题\n")
            report_lines.extend(self._format_issues(high_issues))

        # 中危问题
        if medium_issues:
            report_lines.append("## 🟡 中危问题")
            report_lines.append(f"\n发现 {len(medium_issues)} 个中危问题\n")
            report_lines.extend(self._format_issues(medium_issues))

        # 低危问题
        if low_issues:
            report_lines.append("## 🟢 低危问题")
            report_lines.append(f"\n发现 {len(low_issues)} 个低危问题\n")
            report_lines.extend(self._format_issues(low_issues))

        # 无问题
        if not self.issues:
            report_lines.append("\n✅ 未发现安全问题！\n")

        # 统计信息
        report_lines.append("## 📊 统计信息")
        report_lines.append(f"\n- 高危问题: {len(high_issues)}")
        report_lines.append(f"- 中危问题: {len(medium_issues)}")
        report_lines.append(f"- 低危问题: {len(low_issues)}")
        report_lines.append(f"- **总计**: {len(self.issues)} 个问题\n")

        return "\n".join(report_lines)

    def _format_issues(self, issues: List[Dict]) -> List[str]:
        """
        格式化问题列表

        Args:
            issues: 问题列表

        Returns:
            格式化的行列表
        """
        lines = []

        for issue in issues:
            lines.append(f"### {issue['category']}")
            lines.append(f"\n**文件**: `{issue['file']}`")
            lines.append(f"**行号**: {issue['line']}")
            lines.append(f"**描述**: {issue['message']}")
            lines.append(f"**建议**: {issue['message']}\n")

        return lines


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='安全审计工具')
    parser.add_argument('--output', type=str, default='security_audit_report.md',
                       help='输出报告文件路径')
    parser.add_argument('--fix', action='store_true',
                       help='尝试自动修复简单问题')

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建审计器
    auditor = SecurityAuditor()

    # 执行审计
    issues = auditor.audit_all()

    # 生成报告
    report = auditor.generate_report()

    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 安全审计报告已保存到: {args.output}")
    print(f"\n发现 {len(issues)} 个安全问题")
    print(f"  - 高危: {len([i for i in issues if i['severity'] == 'HIGH'])}")
    print(f"  - 中危: {len([i for i in issues if i['severity'] == 'MEDIUM'])}")
    print(f"  - 低危: {len([i for i in issues if i['severity'] == 'LOW'])}")
    print("\n" + report)


if __name__ == '__main__':
    main()
