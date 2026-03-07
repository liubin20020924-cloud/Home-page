#!/usr/bin/env python3
"""
智能数据库同步脚本
自动检测数据库状态并补充缺失的内容
"""

import pymysql
import sys
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'charset': 'utf8mb4'
}

DATABASES = ['clouddoors_db', 'YHKB', 'casedb']


class DatabaseSync:
    """数据库同步工具"""

    def __init__(self, host='localhost', port=3306, user='root', password='', charset='utf8mb4'):
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'charset': charset
        }
        self.conn = None
        self.changes = []

    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(**self.config)
            print(f"✅ 成功连接到 MySQL 数据库")
            return True
        except Exception as e:
            print(f"❌ 连接数据库失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print("🔌 数据库连接已关闭")

    def database_exists(self, db_name):
        """检查数据库是否存在"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Exception as e:
            print(f"❌ 检查数据库 {db_name} 失败: {e}")
            return False

    def create_database(self, db_name):
        """创建数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                CREATE DATABASE IF NOT EXISTS `{db_name}`
                DEFAULT CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
            """)
            self.conn.commit()
            print(f"✅ 数据库 {db_name} 创建成功")
            self.changes.append(f"创建数据库: {db_name}")
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ 创建数据库 {db_name} 失败: {e}")
            return False

    def table_exists(self, db_name, table_name):
        """检查表是否存在"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = '{db_name}'
                AND table_name = '{table_name}'
            """)
            result = cursor.fetchone()
            cursor.close()
            return result[0] > 0
        except Exception as e:
            print(f"❌ 检查表 {db_name}.{table_name} 失败: {e}")
            return False

    def column_exists(self, db_name, table_name, column_name):
        """检查列是否存在"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = '{db_name}'
                AND table_name = '{table_name}'
                AND column_name = '{column_name}'
            """)
            result = cursor.fetchone()
            cursor.close()
            return result[0] > 0
        except Exception as e:
            print(f"❌ 检查列 {db_name}.{table_name}.{column_name} 失败: {e}")
            return False

    def index_exists(self, db_name, table_name, index_name):
        """检查索引是否存在"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*)
                FROM information_schema.statistics
                WHERE table_schema = '{db_name}'
                AND table_name = '{table_name}'
                AND index_name = '{index_name}'
            """)
            result = cursor.fetchone()
            cursor.close()
            return result[0] > 0
        except Exception as e:
            print(f"❌ 检查索引 {db_name}.{table_name}.{index_name} 失败: {e}")
            return False

    def add_column(self, db_name, table_name, column_name, column_definition):
        """添加列"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                ALTER TABLE `{db_name}`.`{table_name}`
                ADD COLUMN `{column_name}` {column_definition}
            """)
            self.conn.commit()
            print(f"  ✅ 添加列: {table_name}.{column_name}")
            self.changes.append(f"添加列: {db_name}.{table_name}.{column_name}")
            cursor.close()
            return True
        except Exception as e:
            if "Duplicate column name" in str(e):
                print(f"  ⏭️  列已存在: {table_name}.{column_name}")
                return True
            print(f"  ❌ 添加列失败: {table_name}.{column_name} - {e}")
            return False

    def add_index(self, db_name, table_name, index_name, index_definition):
        """添加索引"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                {index_definition}
            """)
            self.conn.commit()
            print(f"  ✅ 添加索引: {table_name}.{index_name}")
            self.changes.append(f"添加索引: {db_name}.{table_name}.{index_name}")
            cursor.close()
            return True
        except Exception as e:
            if "Duplicate key name" in str(e):
                print(f"  ⏭️  索引已存在: {table_name}.{index_name}")
                return True
            print(f"  ❌ 添加索引失败: {table_name}.{index_name} - {e}")
            return False

    def create_table(self, db_name, table_name, table_sql):
        """创建表"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"USE `{db_name}`")
            cursor.execute(table_sql)
            self.conn.commit()
            print(f"✅ 创建表: {db_name}.{table_name}")
            self.changes.append(f"创建表: {db_name}.{table_name}")
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ 创建表失败: {db_name}.{table_name} - {e}")
            return False

    def sync_clouddoors_db(self):
        """同步官网数据库"""
        print("\n" + "="*60)
        print("📦 同步 clouddoors_db (官网系统)")
        print("="*60)

        db_name = 'clouddoors_db'

        # 确保数据库存在
        if not self.database_exists(db_name):
            self.create_database(db_name)

        # 同步 messages 表
        if self.table_exists(db_name, 'messages'):
            print("  📋 检查 messages 表字段...")
            self.add_column(db_name, 'messages', 'phone',
                          "VARCHAR(20) COMMENT '联系电话' AFTER `email`")
            self.add_column(db_name, 'messages', 'company_name',
                          "VARCHAR(200) DEFAULT NULL COMMENT '公司名称' AFTER `phone`")
            self.add_column(db_name, 'messages', 'reply_content',
                          "TEXT COMMENT '回复内容' AFTER `status`")
            self.add_column(db_name, 'messages', 'reply_time',
                          "TIMESTAMP NULL COMMENT '回复时间' AFTER `reply_content`")
            self.add_column(db_name, 'messages', 'replied_by',
                          "VARCHAR(50) COMMENT '回复人用户名' AFTER `reply_time`")
            self.add_column(db_name, 'messages', 'replied_name',
                          "VARCHAR(100) COMMENT '回复人显示名' AFTER `replied_by`")
            self.add_column(db_name, 'messages', 'reply_status',
                          "VARCHAR(20) DEFAULT 'draft' COMMENT '回复状态' AFTER `replied_name`")
            self.add_column(db_name, 'messages', 'inquiry_type',
                          "VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型' AFTER `reply_status`")

            # 添加索引
            print("  📋 检查 messages 表索引...")
            self.add_index(db_name, 'messages', 'idx_status',
                         f"ALTER TABLE `{db_name}`.`messages` ADD INDEX `idx_status` (`status`)")
            self.add_index(db_name, 'messages', 'idx_messages_status_date',
                         f"CREATE INDEX `idx_messages_status_date` ON `{db_name}`.`messages`(`status`, `created_at`)")
            self.add_index(db_name, 'messages', 'idx_messages_email',
                         f"CREATE INDEX `idx_messages_email` ON `{db_name}`.`messages`(`email`)")
            self.add_index(db_name, 'messages', 'idx_messages_reply_status',
                         f"CREATE INDEX `idx_messages_reply_status` ON `{db_name}`.`messages`(`reply_status`)")
            self.add_index(db_name, 'messages', 'idx_messages_reply_time',
                         f"CREATE INDEX `idx_messages_reply_time` ON `{db_name}`.`messages`(`reply_time`)")
            self.add_index(db_name, 'messages', 'idx_messages_inquiry_type',
                         f"CREATE INDEX `idx_messages_inquiry_type` ON `{db_name}`.`messages`(`inquiry_type`)")

        else:
            print("  ⚠️  messages 表不存在，请先执行 init_database.sql")

        # 同步 reply_templates 表
        if not self.table_exists(db_name, 'reply_templates'):
            print("  📋 创建 reply_templates 表...")
            table_sql = """
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
                    KEY `idx_is_system` (`is_system`),
                    KEY `idx_sort` (`sort_order`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='留言回复模板表'
            """
            self.create_table(db_name, 'reply_templates', table_sql)
        else:
            print("  ✅ reply_templates 表已存在")

    def sync_yhkb_db(self):
        """同步知识库数据库"""
        print("\n" + "="*60)
        print("📦 同步 YHKB (知识库系统)")
        print("="*60)

        db_name = 'YHKB'

        # 确保数据库存在
        if not self.database_exists(db_name):
            self.create_database(db_name)

        # 同步 users 表
        if self.table_exists(db_name, 'users'):
            print("  📋 检查 users 表字段...")
            self.add_column(db_name, 'users', 'registration_source',
                          "VARCHAR(50) COMMENT '注册来源' AFTER `created_by`")
            self.add_column(db_name, 'users', 'contact_message_id',
                          "INT COMMENT '关联的留言ID' AFTER `registration_source`")
            self.add_column(db_name, 'users', 'activated_at',
                          "TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间' AFTER `updated_at`")

            # 添加索引
            print("  📋 检查 users 表索引...")
            self.add_index(db_name, 'users', 'idx_users_registration_source',
                         f"CREATE INDEX `idx_users_registration_source` ON `{db_name}`.`users`(`registration_source`)")
            self.add_index(db_name, 'users', 'idx_users_activated_at',
                         f"CREATE INDEX `idx_users_activated_at` ON `{db_name}`.`users`(`activated_at`)")
        else:
            print("  ⚠️  users 表不存在，请先执行 init_database.sql")

    def sync_casedb_db(self):
        """同步工单数据库"""
        print("\n" + "="*60)
        print("📦 同步 casedb (工单系统)")
        print("="*60)

        db_name = 'casedb'

        # 确保数据库存在
        if not self.database_exists(db_name):
            self.create_database(db_name)

        # 工单数据库目前无需额外同步
        print("  ✅ 工单数据库无需额外同步")

    def show_summary(self):
        """显示同步摘要"""
        print("\n" + "="*60)
        print("📊 同步摘要")
        print("="*60)
        if self.changes:
            print(f"共执行 {len(self.changes)} 项变更：")
            for i, change in enumerate(self.changes, 1):
                print(f"  {i}. {change}")
        else:
            print("✅ 所有内容已是最新，无需同步")

        print("\n" + "="*60)
        print("✅ 数据库同步完成")
        print("="*60)

    def sync_all(self):
        """同步所有数据库"""
        if not self.connect():
            return False

        try:
            print("="*60)
            print("🚀 开始数据库同步")
            print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)

            self.sync_clouddoors_db()
            self.sync_yhkb_db()
            self.sync_casedb_db()
            self.show_summary()

            return True
        except Exception as e:
            print(f"❌ 同步过程中出错: {e}")
            return False
        finally:
            self.close()


def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║          云户科技 - 智能数据库同步工具                  ║
    ║          Intelligent Database Sync Tool              ║
    ╚════════════════════════════════════════════════════════╝
    """)

    # 检查命令行参数
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 3306
    user = sys.argv[3] if len(sys.argv) > 3 else 'root'
    password = sys.argv[4] if len(sys.argv) > 4 else ''

    # 如果未提供密码，提示输入
    if password == '' and len(sys.argv) <= 4:
        import getpass
        password = getpass.getpass("请输入MySQL密码（留空表示无密码）: ")

    print(f"📌 配置信息:")
    print(f"   主机: {host}")
    print(f"   端口: {port}")
    print(f"   用户: {user}")
    print(f"   密码: {'******' if password else '(空)'}")
    print()

    # 执行同步
    sync = DatabaseSync(host=host, port=port, user=user, password=password)
    sync.sync_all()


if __name__ == '__main__':
    main()
