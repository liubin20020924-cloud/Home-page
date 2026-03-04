#!/usr/bin/env python3
"""
获取企业微信邮箱SMTP服务器的IP地址
使用标准socket进行DNS解析，避免eventlet的兼容性问题
"""

import socket

def get_smtp_ip():
    """获取smtp.exmail.qq.com的IP地址"""

    smtp_domains = [
        'smtp.exmail.qq.com',
        'smtp.qq.com'
    ]

    print("="*60)
    print("企业微信邮箱SMTP服务器IP地址查询")
    print("="*60)

    for domain in smtp_domains:
        print(f"\n查询域名: {domain}")
        try:
            # 使用标准socket进行DNS解析
            result = socket.getaddrinfo(domain, 465)

            print(f"  解析成功！找到 {len(result)} 个结果：")

            # 去重显示IP
            unique_ips = set()
            for item in result:
                ip = item[4][0]
                if ip not in unique_ips:
                    unique_ips.add(ip)
                    print(f"    - {ip}")

            # 返回第一个IP
            if unique_ips:
                first_ip = list(unique_ips)[0]
                print(f"\n  推荐使用的IP: {first_ip}")
                return first_ip

        except socket.gaierror as e:
            print(f"  解析失败: {e}")
            continue

    print("\n所有域名解析失败！")
    return None

if __name__ == '__main__':
    ip = get_smtp_ip()

    if ip:
        print("\n" + "="*60)
        print("配置方法：")
        print("="*60)
        print(f"\n在 .env 文件中添加或修改以下配置：")
        print(f"MAIL_SERVER={ip}")
        print(f"MAIL_PORT=465")
        print("\n这样就可以直接使用IP地址连接，避免DNS解析问题。")
    else:
        print("\n" + "="*60)
        print("错误提示：")
        print("="*60)
        print("无法解析SMTP服务器IP地址。")
        print("请检查：")
        print("1. 网络连接是否正常")
        print("2. DNS服务器配置是否正确")
        print("3. 防火墙是否允许DNS查询（UDP 53端口）")
