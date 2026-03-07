-- =====================================================
-- 留言系统添加咨询类型和注册来源字段升级脚本
-- 创建时间: 2026-03-07
-- 说明: 为 messages 表添加 inquiry_type 字段，为 users 表添加 registration_source 字段
-- =====================================================

USE `clouddoors_db`;

-- messages 表添加咨询类型字段
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `inquiry_type` VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型：account-开通账户, technical-技术咨询, other-其他' AFTER `reply_status`;

-- 切换到用户数据库
USE `YHKB`;

-- users 表添加注册来源字段
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `registration_source` VARCHAR(50) COMMENT '注册来源：contact_form-联系表单, manual-手动创建, other-其他' AFTER `created_by`,
ADD COLUMN IF NOT EXISTS `contact_message_id` INT COMMENT '关联的留言ID' AFTER `registration_source`;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_messages_inquiry_type ON `clouddoors_db`.`messages`(`inquiry_type`);
CREATE INDEX IF NOT EXISTS idx_users_registration_source ON `YHKB`.`users`(`registration_source`);

-- 查看升级结果
SELECT '=================================================' AS info;
SELECT '留言系统咨询类型和注册来源升级完成！' AS status;
SELECT '=================================================' AS info;
