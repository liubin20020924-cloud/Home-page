-- =====================================================
-- 数据库升级脚本 v1.0 → v2.0
-- 创建时间: 2026-03-07
-- 说明: 将现有数据库升级到最新版本
--       安全升级，不会影响现有数据
-- =====================================================
-- 使用场景:
-- - 已有运行中的数据库
-- - 需要添加新字段和表
-- - 不希望丢失现有数据
-- =====================================================

-- =====================================================
-- 第一部分：升级 messages 表（官网留言表）
-- =====================================================

USE `clouddoors_db`;

-- 添加 phone 字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `phone` VARCHAR(20) COMMENT '联系电话' AFTER `email`;

-- 添加 company_name 字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `company_name` VARCHAR(200) DEFAULT NULL COMMENT '公司名称' AFTER `phone`;

-- 添加回复相关字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `reply_content` TEXT COMMENT '回复内容' AFTER `status`,
ADD COLUMN IF NOT EXISTS `reply_time` TIMESTAMP NULL COMMENT '回复时间' AFTER `reply_content`,
ADD COLUMN IF NOT EXISTS `replied_by` VARCHAR(50) COMMENT '回复人用户名' AFTER `reply_time`,
ADD COLUMN IF NOT EXISTS `replied_name` VARCHAR(100) COMMENT '回复人显示名' AFTER `replied_by`,
ADD COLUMN IF NOT EXISTS `reply_status` VARCHAR(20) DEFAULT 'draft' COMMENT '回复状态：draft-草稿, sent-已发送, failed-发送失败' AFTER `replied_name`;

-- 添加咨询类型字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `inquiry_type` VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型：account-开通账户, technical-技术咨询, other-其他' AFTER `reply_status`;

-- 添加索引（如果不存在）
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_status (`status`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_created_at (`created_at`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_messages_status_date (`status`, `created_at`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_messages_email (`email`);
CREATE INDEX IF NOT EXISTS idx_messages_reply_status ON `messages`(`reply_status`);
CREATE INDEX IF NOT EXISTS idx_messages_reply_time ON `messages`(`reply_time`);
CREATE INDEX IF NOT EXISTS idx_messages_inquiry_type ON `messages`(`inquiry_type`);

SELECT '✅ messages 表升级完成' AS status;


-- =====================================================
-- 第二部分：升级 users 表（统一用户表）
-- =====================================================

USE `YHKB`;

-- 添加注册来源字段（如果不存在）
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `registration_source` VARCHAR(50) COMMENT '注册来源：contact_form-联系表单, manual-手动创建, other-其他' AFTER `created_by`;

-- 添加关联留言ID字段（如果不存在）
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `contact_message_id` INT COMMENT '关联的留言ID' AFTER `registration_source`;

-- 添加激活时间字段（如果不存在）
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `activated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间' AFTER `updated_at`;

-- 添加索引（如果不存在）
CREATE INDEX IF NOT EXISTS idx_users_registration_source ON `YHKB`.`users`(`registration_source`);
CREATE INDEX IF NOT EXISTS idx_users_activated_at ON `YHKB`.`users`(`activated_at`);

SELECT '✅ users 表升级完成' AS status;


-- =====================================================
-- 第三部分：创建 reply_templates 表（回复模板表）
-- =====================================================

USE `clouddoors_db`;

-- 创建回复模板表
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

-- 插入系统预设模板（使用 INSERT IGNORE 避免重复）
INSERT IGNORE INTO `reply_templates` (`name`, `category`, `content`, `description`, `is_system`, `sort_order`, `created_by`) VALUES
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

云户科技客服团队', '转交相关部门处理的回复', 1, 5, 'system');

SELECT '✅ reply_templates 表创建完成' AS status;


-- =====================================================
-- 第四部分：验证升级结果
-- =====================================================

-- 查看 messages 表结构
USE `clouddoors_db`;
SELECT '=================================================' AS info;
SELECT 'messages 表当前结构：' AS info;
SELECT '=================================================' AS info;
SHOW COLUMNS FROM `messages`;

-- 查看 reply_templates 表数据
SELECT '=================================================' AS info;
SELECT '系统预设回复模板：' AS info;
SELECT '=================================================' AS info;
SELECT id, name, category, is_system, is_active FROM `reply_templates` WHERE `is_system` = 1;

-- 查看 users 表相关字段
USE `YHKB`;
SELECT '=================================================' AS info;
SELECT 'users 表新增字段：' AS info;
SELECT '=================================================' AS info;
SELECT
    COLUMN_NAME AS '字段名',
    DATA_TYPE AS '数据类型',
    IS_NULLABLE AS '允许NULL',
    COLUMN_DEFAULT AS '默认值',
    COLUMN_COMMENT AS '注释'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'YHKB'
  AND TABLE_NAME = 'users'
  AND COLUMN_NAME IN ('registration_source', 'contact_message_id', 'activated_at');


-- =====================================================
-- 升级完成
-- =====================================================

SELECT '=================================================' AS info;
SELECT '=================================================' AS info;
SELECT '🎉 数据库升级到 v2.0 完成！' AS status;
SELECT '=================================================' AS info;
SELECT '升级内容汇总：' AS info;
SELECT '-------------------------------------------------' AS info;
SELECT '1. ✅ messages 表添加 phone 字段' AS item;
SELECT '2. ✅ messages 表添加 company_name 字段' AS item;
SELECT '3. ✅ messages 表添加回复相关字段（5个字段）' AS item;
SELECT '4. ✅ messages 表添加咨询类型字段' AS item;
SELECT '5. ✅ messages 表添加所有索引' AS item;
SELECT '6. ✅ users 表添加注册来源字段' AS item;
SELECT '7. ✅ users 表添加关联留言ID字段' AS item;
SELECT '8. ✅ users 表添加激活时间字段' AS item;
SELECT '9. ✅ users 表添加索引' AS item;
SELECT '10. ✅ 创建 reply_templates 表' AS item;
SELECT '11. ✅ 插入系统预设回复模板（5个）' AS item;
SELECT '=================================================' AS info;
SELECT '⚠️  注意：所有现有数据已保留' AS info;
SELECT '✅ 升级安全，可重复执行' AS info;
SELECT '请重启应用后测试功能' AS info;
SELECT '=================================================' AS info;
SELECT '=================================================' AS info;
