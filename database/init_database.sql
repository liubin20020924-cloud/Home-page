-- =====================================================
-- 云户科技网站数据库初始化脚本
-- 适用于 MariaDB/MySQL
-- 创建时间: 2026-02-08
-- 最后更新: 2026-03-07 (v2.0 整合所有补丁)
-- 版本: v2.0 (正式版)
-- 说明：整合官网、知识库、工单三个系统的数据库
--       本脚本可直接用于全新安装，包含所有功能和字段
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
    `registration_source` VARCHAR(50) COMMENT '注册来源：contact_form-联系表单, manual-手动创建, other-其他',
    `contact_message_id` INT COMMENT '关联的留言ID',
    `activated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间',
    INDEX idx_username (`username`),
    INDEX idx_status (`status`),
    INDEX idx_role (`role`),
    INDEX idx_system (`system`),
    INDEX idx_company_name (`company_name`),
    INDEX idx_force_password_change (`force_password_change`),
    INDEX idx_users_registration_source (`registration_source`),
    INDEX idx_users_activated_at (`activated_at`)
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

-- 留言表（完整版本，包含所有字段）
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '留言ID',
    `name` VARCHAR(100) NOT NULL COMMENT '姓名',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称',
    `message` TEXT NOT NULL COMMENT '留言内容',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `status` VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending-未处理, processed-已处理, completed-已完成',
    `reply_content` TEXT COMMENT '回复内容',
    `reply_time` TIMESTAMP NULL COMMENT '回复时间',
    `replied_by` VARCHAR(50) COMMENT '回复人用户名',
    `replied_name` VARCHAR(100) COMMENT '回复人显示名',
    `reply_status` VARCHAR(20) DEFAULT 'draft' COMMENT '回复状态：draft-草稿, sent-已发送, failed-发送失败',
    `inquiry_type` VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型：account-开通账户, technical-技术咨询, other-其他',
    INDEX idx_created_at (`created_at`),
    INDEX idx_status (`status`),
    INDEX idx_messages_status_date (`status`, `created_at`),
    INDEX idx_messages_email (`email`),
    INDEX idx_messages_reply_status (`reply_status`),
    INDEX idx_messages_reply_time (`reply_time`),
    INDEX idx_messages_inquiry_type (`inquiry_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='官网留言表';

-- 回复模板表
CREATE TABLE IF NOT EXISTS `reply_templates` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '模板ID',
    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `category` VARCHAR(50) DEFAULT 'general' COMMENT '模板分类：general-通用, account-账户相关, technical-技术支持, billing-计费相关, other-其他',
    `content` TEXT NOT NULL COMMENT '模板内容（支持变量：{name}, {email}, {phone}, {company_name}, {message}, {username}）',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '模板描述',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用：0-禁用，1-启用',
    `is_system` TINYINT(1) DEFAULT 0 COMMENT '是否系统模板：0-自定义，1-系统预设',
    `sort_order` INT(11) DEFAULT 0 COMMENT '排序顺序（数字越小越靠前）',
    `use_count` INT(11) DEFAULT 0 COMMENT '使用次数',
    `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
    `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '最后修改人',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_category` (`category`),
    KEY `idx_active` (`is_active`),
    KEY `idx_is_active` (`is_active`),
    KEY `idx_is_system` (`is_system`),
    KEY `idx_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='留言回复模板表';

-- 插入系统预设回复模板
INSERT INTO `reply_templates` (`name`, `category`, `content`, `description`, `is_system`, `sort_order`, `created_by`) VALUES
('通用回复-收到留言', 'general', '尊敬的{name}：

您好！感谢您的留言。

我们已收到您的留言，稍后会有专人与您联系处理。如有紧急事宜，请直接拨打我们的客服电话：400-XXX-XXXX

祝您生活愉快！

此致
敬礼

云户科技客服团队', '通用回复模板，表示已收到留言', 1, 1, 'system'),
('技术支持-收到咨询', 'technical', '尊敬的{name}：

您好！感谢您联系云户科技技术支持。

我们已收到您的技术咨询内容：
"{message}"

我们的技术工程师正在尽快处理您的咨询，预计在1-2个工作日内给您详细回复。如有紧急技术问题，请拨打技术支持热线：400-XXX-XXXX

感谢您的信任与支持！

云户科技技术支持团队', '技术支持类回复模板', 1, 2, 'system'),
('账户相关-账户已激活', 'account', '尊敬的{name}：

您好！很高兴通知您，您的账户已成功激活。

账户信息：
- 用户名：{username}
- 登录地址：https://您的域名.com/login

请使用管理员通过邮件发送给您的初始密码登录系统，首次登录后请及时修改密码。

如有任何问题，请联系我们的客服团队。

祝您使用愉快！

云户科技客服团队', '账户激活成功回复模板', 1, 3, 'system'),
('通用回复-问题已解决', 'general', '尊敬的{name}：

您好！

您之前咨询的问题已得到解决。感谢您的耐心等待，如有其他疑问，欢迎随时联系我们。

祝您一切顺利！

云户科技客服团队', '问题解决后的通用回复', 1, 4, 'system'),
('通用回复-转交处理', 'general', '尊敬的{name}：

您好！

您的留言已收到，我们已将您的问题转交给相关部门处理。相关部门会尽快与您联系。

如有其他需要，请随时联系我们。

云户科技客服团队', '转交相关部门处理的回复', 1, 5, 'system')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    category = VALUES(category),
    content = VALUES(content),
    description = VALUES(description);

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

-- 查看留言表结构
SELECT '官网留言表 (messages) 结构' AS info;
SHOW COLUMNS FROM `messages`;

-- 查看回复模板数量
SELECT '系统预设回复模板数量：' AS info, COUNT(*) AS count FROM `reply_templates` WHERE `is_system` = 1;


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
SELECT '' AS info;
SELECT '数据库表结构汇总：' AS info;
SELECT '-------------------------------------------------' AS info;
SELECT 'clouddoors_db (官网系统)：' AS info;
SELECT '  - messages (留言表) - 包含完整的回复和咨询类型字段' AS info;
SELECT '  - reply_templates (回复模板表) - 包含系统预设模板' AS info;
SELECT '' AS info;
SELECT 'YHKB (知识库系统)：' AS info;
SELECT '  - KB-info (知识库信息表)' AS info;
SELECT '  - users (统一用户表) - 包含注册来源和激活时间字段' AS info;
SELECT '  - mgmt_login_logs (登录日志表)' AS info;
SELECT '' AS info;
SELECT 'casedb (工单系统)：' AS info;
SELECT '  - tickets (工单表)' AS info;
SELECT '  - messages (工单消息表)' AS info;
SELECT '  - satisfaction (满意度评价表)' AS info;
SELECT '=================================================' AS info;
SELECT '' AS info;
SELECT '✅ 所有字段和表已完整初始化' AS info;
SELECT '✅ 索引已创建完成' AS info;
SELECT '✅ 系统预设数据已插入' AS info;
SELECT '=================================================' AS info;
