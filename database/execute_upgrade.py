"""
数据库升级脚本执行器
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
        with db_connection('kb') as conn:
            cursor = conn.cursor()

            # 添加 activated_at 字段
            logger.info("正在添加 activated_at 字段...")
            cursor.execute("""
                ALTER TABLE `users`
                ADD COLUMN IF NOT EXISTS `activated_at` TIMESTAMP NULL DEFAULT NULL
                COMMENT '账户激活时间' AFTER `updated_at`
            """)
            logger.info("activated_at 字段添加成功")

            # 创建索引
            logger.info("正在创建索引...")
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_activated_at ON `users`(`activated_at`)")
                logger.info("索引创建成功")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    logger.warning("索引已存在，跳过")
                else:
                    raise

            conn.commit()

            # 验证字段是否添加成功
            cursor.execute("DESCRIBE users")
            columns = [row['Field'] for row in cursor.fetchall()]
            if 'activated_at' in columns:
                logger.info("✓ 升级成功：activated_at 字段已添加到 users 表")
                print("\n" + "="*50)
                print("用户表激活时间字段升级完成！")
                print("="*50 + "\n")
            else:
                logger.error("✗ 升级失败：activated_at 字段未找到")
                return False

            return True

    except Exception as e:
        logger.error(f"数据库升级失败: {str(e)}", exc_info=True)
        return False

if __name__ == '__main__':
    success = execute_upgrade()
    sys.exit(0 if success else 1)
