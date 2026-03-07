"""
邮件发送服务
支持发送邮件到企业微信邮箱
"""
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import logging
import time
from config import (
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT,
    MAIL_DEFAULT_SENDER, CONTACT_EMAIL
)
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务类"""

    def __init__(self):
        self.smtp_server = MAIL_SERVER
        self.smtp_port = MAIL_PORT
        self.smtp_username = MAIL_USERNAME
        self.smtp_password = MAIL_PASSWORD
        # 企业微信邮箱配置：
        # - 发送服务器：smtp.exmail.qq.com (SSL, 465)
        # - 使用 SMTP_SSL 而不是 SMTP + starttls()
        self.email_sender = MAIL_DEFAULT_SENDER or CONTACT_EMAIL

        # 检查配置
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("邮件配置不完整，部分功能可能无法使用")
            logger.warning(f"MAIL_SERVER: {self.smtp_server}")
            logger.warning(f"MAIL_USERNAME: {self.smtp_username}")
            logger.warning(f"MAIL_PASSWORD: {'已配置' if self.smtp_password else '未配置'}")
            logger.warning(f"MAIL_DEFAULT_SENDER: {self.email_sender}")

        # 如果使用域名而不是IP，给出提示
        if not self._is_valid_ip(self.smtp_server):
            logger.info(f"提示: 邮件服务器使用域名 {self.smtp_server}")
            logger.info(f"如果遇到DNS解析问题，可以使用IP地址：")
            logger.info(f"  运行: python3 scripts/get_smtp_ip.py 获取IP地址")
            logger.info(f"  然后在 .env 中设置: MAIL_SERVER=<IP地址>")

    def _is_valid_ip(self, address):
        """检查是否是有效的IP地址"""
        try:
            socket.inet_pton(socket.AF_INET, address)
            return True
        except socket.error:
            return False
    
    def _create_message(
        self, 
        to_email: str,
        subject: str,
        content: str,
        is_html: bool = False,
        cc_emails: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None
    ) -> MIMEMultipart:
        """创建邮件消息"""
        msg = MIMEMultipart('mixed')
        
        # 创建邮件正文
        if is_html:
            msg_text = MIMEText(content, 'html', 'utf-8')
        else:
            msg_text = MIMEText(content, 'plain', 'utf-8')
        msg_text.set_charset('utf-8')
        msg.attach(msg_text)
        
        # 添加抄送
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        
        # 添加附件
        if attachments:
            for attachment in attachments:
                part = MIMEApplication(
                    attachment['content'],
                    attachment['filename'],
                    _subtype='octet-stream'
                )
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=attachment['filename']
                )
                msg.attach(part)
        
        # 设置邮件头
        msg['From'] = formataddr(('云户科技', self.email_sender))
        msg['To'] = formataddr(('客户', to_email))
        msg['Subject'] = subject
        msg['X-Mailer'] = 'Cloud-Doors Mailer'
        
        return msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        is_html: bool = False,
        cc_emails: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None
    ) -> tuple[bool, str]:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            is_html: 是否HTML格式
            cc_emails: 抄送邮箱列表
            attachments: 附件列表，每个附件为 {'filename': 文件名, 'content': 文件内容}

        Returns:
            (success: bool, message: str)
        """
        try:
            # 检查邮件配置
            if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
                error_msg = "邮件配置不完整，请检查 MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD"
                logger.error(error_msg)
                return False, error_msg

            # 创建邮件消息
            msg = self._create_message(
                to_email=to_email,
                subject=subject,
                content=content,
                is_html=is_html,
                cc_emails=cc_emails,
                attachments=attachments
            )

            # 连接SMTP服务器并发送
            # 企业微信邮箱配置：
            # - 发送服务器：smtp.exmail.qq.com (SSL, 端口 465)
            # - 使用 SMTP_SSL 连接
            # 增加超时时间和重试机制
            max_retries = 2
            timeout = 60  # 增加超时时间到60秒

            for attempt in range(max_retries):
                try:
                    # 如果使用IP地址，需要设置local_hostname
                    local_hostname = None
                    if self._is_valid_ip(self.smtp_server):
                        # 使用IP地址时，设置local_hostname为域名
                        local_hostname = 'smtp.exmail.qq.com'

                    if self.smtp_port == 465:
                        with smtplib.SMTP_SSL(
                            self.smtp_server,
                            self.smtp_port,
                            timeout=timeout,
                            local_hostname=local_hostname
                        ) as server:
                            logger.info(f"使用 SMTP_SSL 连接到 {self.smtp_server}:{self.smtp_port}")
                            server.set_debuglevel(0)  # 关闭调试信息
                            server.login(self.smtp_username, self.smtp_password)
                            server.send_message(msg)
                            server.quit()
                    else:
                        with smtplib.SMTP(
                            self.smtp_server,
                            self.smtp_port,
                            timeout=timeout,
                            local_hostname=local_hostname
                        ) as server:
                            logger.info(f"使用 SMTP 连接到 {self.smtp_server}:{self.smtp_port}")
                            server.set_debuglevel(0)  # 关闭调试信息
                            server.starttls()
                            server.login(self.smtp_username, self.smtp_password)
                            server.send_message(msg)
                            server.quit()

                    logger.info(f"邮件发送成功: {to_email} - {subject}")
                    return True, "邮件发送成功"

                except (socket.gaierror, socket.timeout) as e:
                    error_msg = f"邮件发送失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                    logger.warning(error_msg)

                    if attempt < max_retries - 1:
                        # 等待2秒后重试
                        time.sleep(2)
                        continue
                    else:
                        # 最后一次尝试失败
                        raise

        except socket.gaierror as e:
            error_msg = f"DNS解析失败: {self.smtp_server} - {str(e)}"
            logger.error(error_msg)
            logger.error("解决方案:")
            logger.error("  1. 运行 python3 scripts/get_smtp_ip.py 获取IP地址")
            logger.error("  2. 在 .env 中设置: MAIL_SERVER=<IP地址>")
            return False, error_msg

        except socket.timeout as e:
            error_msg = f"连接超时: 无法连接到邮件服务器 {self.smtp_server}:{self.smtp_port} - {str(e)}"
            logger.error(error_msg)
            logger.error("请检查：1) 网络连接 2) 防火墙设置 3) 邮件服务器端口是否开放")
            return False, error_msg

        except ConnectionRefusedError as e:
            error_msg = f"连接被拒绝: 邮件服务器 {self.smtp_server}:{self.smtp_port} 拒绝连接 - {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP认证失败: 请检查邮箱用户名和密码/授权码 - {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"收件人被拒绝: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP服务器断开连接: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"邮件发送失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def send_contact_notification(
        self,
        name: str,
        email: str,
        phone: str,
        message: str
    ) -> tuple[bool, str]:
        """
        发送联系我们通知（首页留言）
        
        Args:
            name: 留言人姓名
            email: 留言人邮箱
            phone: 留言人电话
            message: 留言内容
        
        Returns:
            (success: bool, message: str)
        """
        if not self.email_sender:
            return False, "邮件发送未配置"
        
        subject = f"【云户科技】收到来自 {name} 的新留言"
        
        # 创建HTML邮件内容
        content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, "Microsoft YaHei", sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                    padding: 40px 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4DA2 0%, #2563eb 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 700;
                }}
                .content {{
                    padding: 30px;
                }}
                .info-item {{
                    margin-bottom: 20px;
                    padding: 20px;
                    background: #f9fafb;
                    border-radius: 8px;
                    border-left: 4px solid #0A4DA2;
                }}
                .info-item label {{
                    display: block;
                    font-weight: 600;
                    color: #6b7280;
                    margin-bottom: 8px;
                    font-size: 14px;
                }}
                .info-item span {{
                    font-size: 16px;
                    color: #1a202c;
                }}
                .message-box {{
                    background: #f0fdf4;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #bbf7d0;
                }}
                .message-box h3 {{
                    margin-top: 0;
                    color: #166534;
                    font-size: 18px;
                    margin-bottom: 12px;
                }}
                .message-content {{
                    color: #374151;
                    white-space: pre-wrap;
                    line-height: 1.8;
                    font-size: 15px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #6b7280;
                    font-size: 14px;
                    border-top: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 新留言通知</h1>
                </div>
                <div class="content">
                    <div class="info-item">
                        <label>留言人：</label>
                        <span>{name}</span>
                    </div>
                    <div class="info-item">
                        <label>联系邮箱：</label>
                        <span>{email}</span>
                    </div>
                    <div class="info-item">
                        <label>联系电话：</label>
                        <span>{phone}</span>
                    </div>
                    <div class="message-box">
                        <h3>留言内容：</h3>
                        <div class="message-content">{message}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>感谢您的留言，我们会尽快与您联系！</p>
                    <p style="margin-top: 10px;">
                        —<br>
                        云户科技 | 专业IT服务商<br>
                        <a href="https://www.cloud-doors.com" style="color: #0A4DA2; text-decoration: none;">www.cloud-doors.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.email_sender,
            subject=subject,
            content=content,
            is_html=True
        )
    
    def send_ticket_created_notification(
        self,
        ticket_id: str,
        title: str,
        customer_name: str,
        contact_name: str,
        priority: str,
        issue_type: str,
        content: str,
        attachments: Optional[List[dict]] = None
    ) -> tuple[bool, str]:
        """
        发送工单创建通知
        
        Args:
            ticket_id: 工单编号
            title: 工单标题
            customer_name: 客户公司名称
            contact_name: 联系人姓名
            priority: 优先级
            issue_type: 工单类型
            content: 工单详情内容
            attachments: 附件列表
        
        Returns:
            (success: bool, message: str)
        """
        if not self.email_sender:
            return False, "邮件发送未配置"
        
        # 优先级映射
        priority_map = {
            'urgent': '🔴 紧急',
            'high': '🟠 高',
            'medium': '🟡 中',
            'low': '🟢 低'
        }
        priority_label = priority_map.get(priority, priority)
        
        # 工单类型映射
        type_map = {
            'technical': '技术支持',
            'service': '产品咨询',
            'complaint': '售后投诉',
            'other': '其他问题'
        }
        type_label = type_map.get(issue_type, issue_type)
        
        subject = f"【云户科技】工单创建成功 - {ticket_id}"
        
        # 创建HTML邮件内容
        content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, "Microsoft YaHei", sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                    padding: 40px 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 700px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #2d8a4e 0%, #48bb78 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }}
                .ticket-id {{
                    background: rgba(255, 255, 255, 0.2);
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-size: 18px;
                    font-family: 'Courier New', monospace;
                    display: inline-block;
                }}
                .content {{
                    padding: 40px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .info-item {{
                    display: flex;
                    flex-direction: column;
                }}
                .info-item label {{
                    font-weight: 600;
                    color: #6b7280;
                    margin-bottom: 8px;
                    font-size: 14px;
                }}
                .info-item span {{
                    font-size: 16px;
                    color: #1a202c;
                }}
                .priority-box {{
                    background: #fee2e2;
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: 600;
                    font-size: 18px;
                    color: #c53030;
                }}
                .title-box {{
                    background: #f0fdf4;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #2d8a4e;
                    margin-bottom: 30px;
                }}
                .title-box h2 {{
                    margin: 0 0 15px 0;
                    font-size: 20px;
                    color: #166534;
                }}
                .content-box {{
                    background: #f9fafb;
                    padding: 25px;
                    border-radius: 8px;
                    line-height: 1.8;
                    white-space: pre-wrap;
                    color: #374151;
                    font-size: 15px;
                }}
                .attachments {{
                    margin-top: 30px;
                    padding-top: 30px;
                    border-top: 2px dashed #e5e7eb;
                }}
                .attachments h3 {{
                    color: #1a202c;
                    font-size: 16px;
                    margin-bottom: 15px;
                }}
                .attachments .attachment-list {{
                    display: grid;
                    gap: 10px;
                }}
                .attachments .attachment-item {{
                    background: white;
                    padding: 12px;
                    border-radius: 6px;
                    border: 1px solid #e5e7eb;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    color: #6b7280;
                    font-size: 14px;
                    border-top: 1px solid #e5e7eb;
                    background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                .footer a {{
                    color: #2d8a4e;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 工单创建成功</h1>
                    <p class="ticket-id">{ticket_id}</p>
                </div>
                <div class="content">
                    <div class="priority-box">
                        {priority_label}
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-item">
                            <label>客户公司</label>
                            <span>{customer_name}</span>
                        </div>
                        <div class="info-item">
                            <label>联系人</label>
                            <span>{contact_name}</span>
                        </div>
                        <div class="info-item">
                            <label>工单类型</label>
                            <span>{type_label}</span>
                        </div>
                        <div class="info-item">
                            <label>优先级</label>
                            <span>{priority_label}</span>
                        </div>
                    </div>
                    
                    <div class="title-box">
                        <h2>{title}</h2>
                    </div>
                    
                    <div class="content-box">
                        <strong>问题描述：</strong><br><br>
                        {content}
                    </div>
                    
                    {self._render_attachments(attachments) if attachments else ''}
                </div>
                
                <div class="footer">
                    <p>感谢您的信任，我们会尽快为您处理！</p>
                    <p>工单编号：<strong>{ticket_id}</strong></p>
                    <p>请记录工单编号，方便后续查询和跟进。</p>
                    <p style="margin-top: 20px;">
                        —<br>
                        云户科技工单系统<br>
                        <a href="https://www.cloud-doors.com/case/">查看工单</a> | 
                        <a href="https://www.cloud-doors.com/">官方网站</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.email_sender,
            subject=subject,
            content=content,
            is_html=True
        )
    
    def _render_attachments(self, attachments: List[dict]) -> str:
        """渲染附件列表HTML"""
        if not attachments:
            return ""

        items_html = []
        for attachment in attachments:
            items_html.append(f"""
                <div class="attachment-item">
                    <i class="fas fa-paperclip"></i>
                    <span>{attachment.get('filename', '附件')}</span>
                    <span style="color: #6b7280; font-size: 14px;">
                        ({attachment.get('size', '未知大小')})
                    </span>
                </div>
            """)

        return f"""
            <div class="attachments">
                <h3>📎 附件 ({len(attachments)} 个)</h3>
                <div class="attachment-list">
                    {"".join(items_html)}
                </div>
            </div>
        """

    def send_message_reply_notification(
        self,
        to_email: str,
        name: str,
        original_message: str,
        reply_content: str,
        replied_by: str
    ) -> tuple[bool, str]:
        """
        发送留言回复通知邮件

        Args:
            to_email: 收件人邮箱（客户的邮箱）
            name: 客户姓名
            original_message: 原始留言内容
            reply_content: 回复内容
            replied_by: 回复人

        Returns:
            (success: bool, message: str)
        """
        if not to_email:
            return False, "客户邮箱不能为空"

        subject = f"【云户科技】您的留言已收到回复"

        # 创建HTML邮件内容
        content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, "Microsoft YaHei", sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                    padding: 40px 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 700px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4DA2 0%, #2563eb 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 26px;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }}
                .content {{
                    padding: 40px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #1a202c;
                    margin-bottom: 30px;
                }}
                .message-box {{
                    background: #f9fafb;
                    padding: 25px;
                    border-radius: 8px;
                    border-left: 4px solid #9ca3af;
                    margin-bottom: 30px;
                }}
                .message-box h3 {{
                    margin: 0 0 15px 0;
                    color: #4b5563;
                    font-size: 16px;
                }}
                .message-content {{
                    color: #374151;
                    white-space: pre-wrap;
                    line-height: 1.8;
                    font-size: 15px;
                }}
                .reply-box {{
                    background: #f0fdf4;
                    padding: 30px;
                    border-radius: 8px;
                    border-left: 4px solid #10b981;
                    margin-bottom: 30px;
                }}
                .reply-box h3 {{
                    margin: 0 0 20px 0;
                    color: #047857;
                    font-size: 18px;
                }}
                .reply-content {{
                    color: #1a202c;
                    white-space: pre-wrap;
                    line-height: 1.8;
                    font-size: 16px;
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                }}
                .replied-by {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 15px;
                    text-align: right;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    color: #6b7280;
                    font-size: 14px;
                    border-top: 1px solid #e5e7eb;
                    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                .footer a {{
                    color: #0A4DA2;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📨 留言回复通知</h1>
                </div>
                <div class="content">
                    <p class="greeting">尊敬的 <strong>{name}</strong>，您好！</p>

                    <div class="message-box">
                        <h3>📋 您的原始留言：</h3>
                        <div class="message-content">{original_message}</div>
                    </div>

                    <div class="reply-box">
                        <h3>✨ 我们的回复：</h3>
                        <div class="reply-content">{reply_content}</div>
                        <div class="replied-by">回复人：{replied_by}</div>
                    </div>

                    <p style="color: #6b7280; font-size: 14px; line-height: 1.8;">
                        如有其他问题，欢迎随时联系我们。感谢您的信任与支持！
                    </p>
                </div>

                <div class="footer">
                    <p>—<br>
                    云户科技 | 专业IT服务商<br>
                    官网：<a href="https://www.cloud-doors.com">www.cloud-doors.com</a><br>
                    联系我们：support@cloud-doors.com</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            is_html=True
        )

    def send_account_activation_notification(
        self,
        to_email: str,
        name: str,
        username: str,
        password: str,
        company_name: str
    ) -> tuple[bool, str]:
        """
        发送账户激活通知邮件

        Args:
            to_email: 收件人邮箱（客户的邮箱）
            name: 客户姓名
            username: 用户名
            password: 临时密码
            company_name: 公司名称

        Returns:
            (success: bool, message: str)
        """
        if not to_email:
            return False, "客户邮箱不能为空"

        subject = "【云户科技】您的账户已开通"

        # 创建HTML邮件内容
        content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, "Microsoft YaHei", sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                    padding: 40px 20px;
                    margin: 0;
                }}
                .container {{
                    max-width: 700px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 26px;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                }}
                .content {{
                    padding: 40px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #1a202c;
                    margin-bottom: 30px;
                }}
                .company-name {{
                    font-size: 16px;
                    color: #6b7280;
                    margin-bottom: 20px;
                }}
                .account-box {{
                    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    padding: 30px;
                    border-radius: 10px;
                    border: 2px solid #10b981;
                    margin-bottom: 30px;
                }}
                .account-box h3 {{
                    margin: 0 0 20px 0;
                    color: #047857;
                    font-size: 20px;
                    text-align: center;
                }}
                .account-info {{
                    display: grid;
                    gap: 15px;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                    border-left: 4px solid #10b981;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #4b5563;
                    font-size: 15px;
                }}
                .info-value {{
                    font-weight: 700;
                    color: #1a202c;
                    font-size: 16px;
                    font-family: 'Courier New', monospace;
                }}
                .info-value.password {{
                    color: #dc2626;
                    font-size: 18px;
                }}
                .warning-box {{
                    background: #fef3c7;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #f59e0b;
                    margin-bottom: 20px;
                }}
                .warning-box h4 {{
                    margin: 0 0 10px 0;
                    color: #92400e;
                    font-size: 16px;
                }}
                .warning-box ul {{
                    margin: 0;
                    padding-left: 20px;
                    color: #78350f;
                    font-size: 14px;
                    line-height: 1.8;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    color: #6b7280;
                    font-size: 14px;
                    border-top: 1px solid #e5e7eb;
                    background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                .footer a {{
                    color: #10b981;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 账户开通成功</h1>
                </div>
                <div class="content">
                    <p class="greeting">尊敬的 <strong>{name}</strong>，您好！</p>
                    <p class="company-name"><strong>公司名称：</strong>{company_name}</p>

                    <div class="account-box">
                        <h3>🔐 您的账户信息</h3>
                        <div class="account-info">
                            <div class="info-row">
                                <span class="info-label">用户名：</span>
                                <span class="info-value">{username}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">临时密码：</span>
                                <span class="info-value password">{password}</span>
                            </div>
                        </div>
                    </div>

                    <div class="warning-box">
                        <h4>⚠️ 重要提示</h4>
                        <ul>
                            <li>请妥善保管您的用户名和密码</li>
                            <li><strong>首次登录后请立即修改密码</strong></li>
                            <li>如果忘记密码，请联系管理员重置</li>
                            <li>请勿将账户信息透露给他人</li>
                        </ul>
                    </div>

                    <p style="color: #6b7280; font-size: 14px; line-height: 1.8;">
                        如有任何问题，请随时联系我们。感谢您的信任！
                    </p>
                </div>

                <div class="footer">
                    <p>—<br>
                    云户科技 | 专业IT服务商<br>
                    官网：<a href="https://www.cloud-doors.com">www.cloud-doors.com</a><br>
                    联系我们：support@cloud-doors.com</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            is_html=True
        )


# 创建全局邮件服务实例
email_service = EmailService()
