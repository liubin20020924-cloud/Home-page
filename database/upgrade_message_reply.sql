-- =====================================================
-- 留言回复功能数据库升级脚本
-- 创建时间: 2026-03-07
-- 说明: 为 messages 表添加回复相关字段
-- =====================================================

USE `clouddoors_db`;

-- 添加回复相关字段
-- reply_content: 回复内容（TEXT类型，支持长文本）
-- reply_time: 回复时间（TIMESTAMP类型）
-- replied_by: 回复人（VARCHAR类型，存储管理员用户名）
-- replied_at: 回复时使用的管理员显示名（VARCHAR类型，方便显示）
-- reply_status: 回复状态（draft-草稿, sent-已发送, failed-发送失败）

ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `reply_content` TEXT COMMENT '回复内容' AFTER `status`,
ADD COLUMN IF NOT EXISTS `reply_time` TIMESTAMP NULL COMMENT '回复时间' AFTER `reply_content`,
ADD COLUMN IF NOT EXISTS `replied_by` VARCHAR(50) COMMENT '回复人用户名' AFTER `reply_time`,
ADD COLUMN IF NOT EXISTS `replied_name` VARCHAR(100) COMMENT '回复人显示名' AFTER `replied_by`,
ADD COLUMN IF NOT EXISTS `reply_status` VARCHAR(20) DEFAULT 'draft' COMMENT '回复状态：draft-草稿, sent-已发送, failed-发送失败' AFTER `replied_name`;

-- 添加索引优化查询
CREATE INDEX IF NOT EXISTS idx_messages_reply_status ON `messages`(`reply_status`);
CREATE INDEX IF NOT EXISTS idx_messages_reply_time ON `messages`(`reply_time`);

-- 查看升级后的表结构
SELECT '=================================================' AS info;
SELECT '留言回复功能数据库升级完成！' AS status;
SELECT '=================================================' AS info;
SHOW COLUMNS FROM `messages`;
