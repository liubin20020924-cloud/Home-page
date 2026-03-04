-- =====================================================
-- 云户科技网站数据库初始化脚本
-- 适用于 MariaDB/MySQL
-- 创建时间: 2026-02-08
-- 最后更新: 2026-03-02 (v1.0 首次正式发布)
-- 版本: v1.0 (正式版)
-- 说明：整合官网、知识库、工单三个系统的数据库
--       本脚本可直接用于全新安装
-- =====================================================

-- =====================================================
-- 1. 创建三个数据库
-- =====================================================

-- 创建官网系统数据库
CREATE DATABASE IF NOT EXISTS `clouddoors_db`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建知识库系统数据库
CREATE DATABASE IF NOT EXISTS `YHKB`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 创建工单系统数据库
CREATE DATABASE IF NOT EXISTS `casedb`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 显示所有数据库
SHOW DATABASES;


-- =====================================================
-- 2. 初始化知识库系统数据库 (YHKB)
-- =====================================================
USE `YHKB`;

-- 知识库信息表
CREATE TABLE IF NOT EXISTS `KB-info` (
    `KB_Number` INT AUTO_INCREMENT PRIMARY KEY COMMENT '知识库编号',
    `KB_Name` VARCHAR(500) NOT NULL COMMENT '知识库名称',
    `KB_link` VARCHAR(500) COMMENT '知识库链接',
    `KB_Description` TEXT COMMENT '知识库描述',
    `KB_Category` VARCHAR(50) COMMENT '知识库分类',
    `KB_Author` VARCHAR(100) COMMENT '作者',
    `KB_CreateTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `KB_UpdateTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_KB_Name (`KB_Name`),
    INDEX idx_KB_Number (`KB_Number`),
    INDEX idx_KB_Category (`KB_Category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库信息表';

-- 统一用户表（知识库和工单系统共用）
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希值（werkzeug加密）',
    `display_name` VARCHAR(100) COMMENT '显示名称',
    `email` VARCHAR(100) COMMENT '邮箱',
    `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称(客户角色必填)',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
    `role` VARCHAR(20) DEFAULT 'user' COMMENT '角色：admin-管理员, user-普通用户, customer-客户',
    `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态：active-活跃, inactive-未激活, locked-锁定',
    `last_login` TIMESTAMP NULL COMMENT '最后登录时间',
    `login_attempts` INT DEFAULT 0 COMMENT '登录尝试次数',
    `password_type` VARCHAR(10) DEFAULT 'werkzeug' COMMENT '密码类型：werkzeug',
    `force_password_change` TINYINT(1) DEFAULT 0 COMMENT '是否强制修改密码：0-否, 1-是',
    `system` VARCHAR(20) DEFAULT 'unified' COMMENT '所属系统：unified-统一',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `created_by` VARCHAR(50) COMMENT '创建人',
    INDEX idx_username (`username`),
    INDEX idx_status (`status`),
    INDEX idx_role (`role`),
    INDEX idx_system (`system`),
    INDEX idx_company_name (`company_name`),
    INDEX idx_force_password_change (`force_password_change`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='统一用户表';

-- 知识库登录日志表
CREATE TABLE IF NOT EXISTS `mgmt_login_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    `user_id` INT COMMENT '用户ID',
    `username` VARCHAR(50) COMMENT '用户名',
    `ip_address` VARCHAR(50) COMMENT 'IP地址',
    `user_agent` TEXT COMMENT '用户代理',
    `status` VARCHAR(20) COMMENT '状态：success-成功, failed-失败',
    `failure_reason` VARCHAR(255) COMMENT '失败原因',
    `login_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    INDEX idx_user_id (`user_id`),
    INDEX idx_username (`username`),
    INDEX idx_status (`status`),
    INDEX idx_login_time (`login_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库登录日志表';

-- 插入默认管理员用户
-- 注意：生产环境部署后请立即修改默认密码！
INSERT INTO `users` (username, password_hash, password_type, display_name, role, status, system, created_by)
VALUES (
    'admin',
    'scrypt:32768:8:1$ZeitszjeQhBOqUJF$dbfa5f57ec9ba38892585302b8ff94cb79a77f9e73644ae32afc12087b2c39d9f3bd254eaff335baca953c4378b8e8b210b5fb9904569fd07b84ca190743b773',
    'werkzeug',
    '系统管理员',
    'admin',
    'active',
    'unified',
    'system'
)
ON DUPLICATE KEY UPDATE
    password_hash = VALUES(password_hash),
    password_type = VALUES(password_type),
    status = 'active',
    display_name = VALUES(display_name),
    role = VALUES(role);


-- =====================================================
-- 3. 初始化工单系统数据库 (casedb)
-- =====================================================
USE `casedb`;

-- 工单表
CREATE TABLE IF NOT EXISTS `tickets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
    `ticket_id` VARCHAR(32) NOT NULL UNIQUE COMMENT '工单唯一标识ID',
    `customer_name` VARCHAR(100) NOT NULL COMMENT '客户公司名称',
    `customer_contact_name` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '客户联系人姓名(当前登录用户)',
    `customer_contact` VARCHAR(50) NOT NULL COMMENT '客户联系方式',
    `customer_email` VARCHAR(100) NOT NULL COMMENT '客户邮箱',
    `cc_emails` TEXT NULL COMMENT '抄送邮箱(多个邮箱用逗号分隔)',
    `submit_user` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '提交工单的用户名(来自统一用户表)',
    `product` VARCHAR(50) NOT NULL COMMENT '涉及产品',
    `issue_type` VARCHAR(20) NOT NULL COMMENT '问题类型',
    `priority` VARCHAR(10) NOT NULL COMMENT '工单优先级',
    `title` VARCHAR(200) NOT NULL COMMENT '问题标题',
    `content` TEXT NOT NULL COMMENT '问题详情',
    `resolution` TEXT NULL COMMENT '解决方案',
    `status` VARCHAR(10) DEFAULT 'pending' COMMENT '工单状态',
    `assignee` VARCHAR(100) NULL COMMENT '处理人',
    `create_time` DATETIME NOT NULL COMMENT '创建时间',
    `update_time` DATETIME NOT NULL COMMENT '更新时间',
    INDEX idx_ticket_id (`ticket_id`),
    INDEX idx_customer_name (`customer_name`),
    INDEX idx_customer_contact_name (`customer_contact_name`),
    INDEX idx_submit_user (`submit_user`),
    INDEX idx_status (`status`),
    INDEX idx_assignee (`assignee`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单系统主表';

-- 工单聊天消息表
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    `ticket_id` VARCHAR(32) NOT NULL COMMENT '工单ID',
    `sender` VARCHAR(20) NOT NULL COMMENT '发送者',
    `sender_name` VARCHAR(100) NOT NULL COMMENT '发送者名称',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `send_time` DATETIME NOT NULL COMMENT '发送时间',
    INDEX idx_ticket_id (`ticket_id`),
    INDEX idx_send_time (`send_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单聊天消息表';

-- 工单满意度评价表
CREATE TABLE IF NOT EXISTS `satisfaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    `ticket_id` VARCHAR(32) NOT NULL UNIQUE COMMENT '工单ID',
    `rating` TINYINT NOT NULL COMMENT '评分(1-5)',
    `comment` TEXT NULL COMMENT '评价文字',
    `create_time` DATETIME NOT NULL COMMENT '评价时间',
    INDEX idx_ticket_id (`ticket_id`),
    INDEX idx_create_time (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单满意度评价表';

-- 工单数据由用户通过前端界面创建


-- =====================================================
-- 4. 初始化官网系统数据库 (clouddoors_db)
-- =====================================================
USE `clouddoors_db`;

-- 留言表
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '留言ID',
    `name` VARCHAR(100) NOT NULL COMMENT '姓名',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `message` TEXT NOT NULL COMMENT '留言内容',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `status` VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending-待处理, processed-已处理',
    INDEX idx_created_at (`created_at`),
    INDEX idx_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='官网留言表';

-- 留言数据由用户通过前端界面提交


-- =====================================================
-- 5. 验证数据库初始化
-- =====================================================

-- 查看知识库数据库表
USE `YHKB`;
SELECT '=================================================' AS info;
SELECT '知识库系统数据库 (YHKB) 表结构' AS info;
SELECT '=================================================' AS info;
SHOW TABLES;

-- 查看用户数据
SELECT '用户数据' AS info;
SELECT id, username, display_name, role, status, password_type FROM `users`;

-- 查看工单数据库表
USE `casedb`;
SELECT '=================================================' AS info;
SELECT '工单系统数据库 (casedb) 表结构' AS info;
SELECT '=================================================' AS info;
SHOW TABLES;



-- 查看官网数据库表
USE `clouddoors_db`;
SELECT '=================================================' AS info;
SELECT '官网系统数据库 (clouddoors_db) 表结构' AS info;
SELECT '=================================================' AS info;
SHOW TABLES;



-- =====================================================
-- 6. 初始化完成提示
-- =====================================================

SELECT '=================================================' AS info;
SELECT '数据库初始化完成！' AS status;
SELECT '=================================================' AS info;
SELECT '' AS info;
SELECT '默认管理员账号：' AS info;
SELECT '  用户名：admin' AS info;
SELECT '  密码：YHKB@2024' AS info;
SELECT '' AS info;
SELECT '系统包含三个数据库：' AS info;
SELECT '  1. clouddoors_db - 官网系统' AS info;
SELECT '  2. YHKB - 知识库系统' AS info;
SELECT '  3. casedb - 工单系统' AS info;
SELECT '=================================================' AS info;
