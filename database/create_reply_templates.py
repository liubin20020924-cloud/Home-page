"""
回复模板表创建脚本执行器
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database_context import db_connection
from common.logger import logger


def execute_upgrade():
    """执行数据库升级"""
    try:
        import pymysql
        with db_connection('home') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 创建回复模板表
            logger.info("正在创建 reply_templates 表...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `reply_templates` (
                    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '模板ID',
                    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
                    `category` VARCHAR(50) DEFAULT 'general' COMMENT '模板分类',
                    `content` TEXT NOT NULL COMMENT '模板内容',
                    `description` VARCHAR(500) DEFAULT NULL COMMENT '模板描述',
                    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用',
                    `is_system` TINYINT(1) DEFAULT 0 COMMENT '是否系统模板',
                    `sort_order` INT(11) DEFAULT 0 COMMENT '排序顺序',
                    `use_count` INT(11) DEFAULT 0 COMMENT '使用次数',
                    `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
                    `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '最后修改人',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    PRIMARY KEY (`id`),
                    KEY `idx_category` (`category`),
                    KEY `idx_active` (`is_active`),
                    KEY `idx_sort` (`sort_order`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='留言回复模板表'
            """)
            logger.info("reply_templates 表创建成功")

            # 插入系统预设模板
            logger.info("正在插入系统预设模板...")
            system_templates = [
                ('通用回复-收到留言', 'general',
                 '尊敬的{name}：\n\n您好！感谢您的留言。\n\n我们已收到您的留言，稍后会有专人与您联系处理。如有紧急事宜，请直接拨打我们的客服电话：400-XXX-XXXX\n\n祝您生活愉快！\n\n此致\n敬礼\n\n云户科技客服团队',
                 '通用回复模板，表示已收到留言', 1, 1, 'system'),
                ('技术支持-收到咨询', 'technical',
                 '尊敬的{name}：\n\n您好！感谢您联系云户科技技术支持。\n\n我们已收到您的技术咨询内容：\n"{message}"\n\n我们的技术工程师正在尽快处理您的咨询，预计在1-2个工作日内给您详细回复。如有紧急技术问题，请拨打技术支持热线：400-XXX-XXXX\n\n感谢您的信任与支持！\n\n云户科技技术支持团队',
                 '技术支持类回复模板', 1, 2, 'system'),
                ('账户相关-账户已激活', 'account',
                 '尊敬的{name}：\n\n您好！很高兴通知您，您的账户已成功激活。\n\n账户信息：\n- 用户名：{username}\n- 登录地址：https://您的域名.com/login\n\n请使用管理员通过邮件发送给您的初始密码登录系统，首次登录后请及时修改密码。\n\n如有任何问题，请联系我们的客服团队。\n\n祝您使用愉快！\n\n云户科技客服团队',
                 '账户激活成功回复模板', 1, 3, 'system'),
                ('通用回复-问题已解决', 'general',
                 '尊敬的{name}：\n\n您好！\n\n您之前咨询的问题已得到解决。感谢您的耐心等待，如有其他疑问，欢迎随时联系我们。\n\n祝您一切顺利！\n\n云户科技客服团队',
                 '问题解决后的通用回复', 1, 4, 'system'),
                ('通用回复-转交处理', 'general',
                 '尊敬的{name}：\n\n您好！\n\n您的留言已收到，我们已将您的问题转交给相关部门处理。相关部门会尽快与您联系。\n\n如有其他需要，请随时联系我们。\n\n云户科技客服团队',
                 '转交相关部门处理的回复', 1, 5, 'system'),
            ]

            for template in system_templates:
                cursor.execute("""
                    INSERT INTO `reply_templates` (`name`, `category`, `content`, `description`, `is_system`, `sort_order`, `created_by`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, template)

            logger.info(f"系统预设模板插入成功（共 {len(system_templates)} 个）")

            conn.commit()

            # 验证表是否创建成功
            cursor.execute("DESCRIBE reply_templates")
            columns = [row['Field'] for row in cursor.fetchall()]
            if 'id' in columns and 'content' in columns:
                logger.info("✓ 升级成功：reply_templates 表已创建")

                # 查询模板数量
                cursor.execute("SELECT COUNT(*) as count FROM reply_templates")
                count = cursor.fetchone()['count']
                print("\n" + "="*50)
                print("回复模板表创建完成！")
                print(f"系统预设模板数量：{count}")
                print("="*50 + "\n")
            else:
                logger.error("✗ 升级失败：reply_templates 表验证失败")
                return False

            return True

    except Exception as e:
        logger.error(f"数据库升级失败: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    success = execute_upgrade()
    sys.exit(0 if success else 1)
