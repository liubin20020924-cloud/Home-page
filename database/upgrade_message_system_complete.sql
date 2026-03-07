-- =====================================================
-- 留言系统完整升级脚本
-- 创建时间: 2026-03-07
-- 说明: 留言系统所有功能的完整升级脚本
--       包含：留言表基础升级、回复功能、咨询类型、账户激活
-- =====================================================
-- 执行顺序：
-- 1. messages 表基础升级（phone 字段）
-- 2. messages 表回复功能字段
-- 3. messages 表咨询类型字段
-- 4. users 表激活相关字段
-- 5. 创建索引
-- 6. 显示升级结果
-- =====================================================

-- =====================================================
-- 第一部分：messages 表基础升级（phone 字段）
-- =====================================================

USE `clouddoors_db`;

-- 添加 phone 字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `phone` VARCHAR(20) COMMENT '联系电话' AFTER `email`;

-- 添加索引优化查询性能
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_status (`status`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_created_at (`created_at`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_messages_status_date (`status`, `created_at`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_messages_email (`email`);

SELECT '=================================================' AS info;
SELECT '✅ messages 表基础升级完成（phone 字段）' AS status;
SELECT '=================================================' AS info;

-- =====================================================
-- 第二部分：messages 表回复功能字段
-- =====================================================

USE `clouddoors_db`;

-- 添加回复相关字段
-- reply_content: 回复内容（TEXT类型，支持长文本）
-- reply_time: 回复时间（TIMESTAMP类型）
-- replied_by: 回复人（VARCHAR类型，存储管理员用户名）
-- replied_name: 回复人显示名（VARCHAR类型，方便显示）
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

SELECT '=================================================' AS info;
SELECT '✅ messages 表回复功能字段升级完成' AS status;
SELECT '=================================================' AS info;

-- =====================================================
-- 第三部分：messages 表咨询类型字段
-- =====================================================

USE `clouddoors_db`;

-- messages 表添加咨询类型字段
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `inquiry_type` VARCHAR(50) DEFAULT 'other' COMMENT '咨询类型：account-开通账户, technical-技术咨询, other-其他' AFTER `reply_status`;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_messages_inquiry_type ON `messages`(`inquiry_type`);

SELECT '=================================================' AS info;
SELECT '✅ messages 表咨询类型字段升级完成' AS status;
SELECT '=================================================' AS info;

-- =====================================================
-- 第四部分：users 表激活相关字段
-- =====================================================

USE `YHKB`;

-- users 表添加注册来源、关联留言ID和激活时间字段
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `registration_source` VARCHAR(50) COMMENT '注册来源：contact_form-联系表单, manual-手动创建, other-其他' AFTER `created_by`,
ADD COLUMN IF NOT EXISTS `contact_message_id` INT COMMENT '关联的留言ID' AFTER `registration_source`,
ADD COLUMN IF NOT EXISTS `activated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间' AFTER `updated_at`;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_registration_source ON `YHKB`.`users`(`registration_source`);
CREATE INDEX IF NOT EXISTS idx_users_activated_at ON `YHKB`.`users`(`activated_at`);

SELECT '=================================================' AS info;
SELECT '✅ users 表激活相关字段升级完成' AS status;
SELECT '=================================================' AS info;

-- =====================================================
-- 第五部分：查看升级结果
-- =====================================================

-- 查看 messages 表结构
USE `clouddoors_db`;
SELECT '=================================================' AS info;
SELECT 'messages 表当前结构：' AS info;
SELECT '=================================================' AS info;
SHOW COLUMNS FROM `messages`;

-- 查看 users 表相关字段
USE `YHKB`;
SELECT '=================================================' AS info;
SELECT 'users 表相关字段：' AS info;
SELECT '=================================================' AS info;
SELECT
    COLUMN_NAME AS '字段名',
    DATA_TYPE AS '数据类型',
    COLUMN_TYPE AS '完整类型',
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
SELECT '🎉 留言系统完整升级完成！' AS status;
SELECT '=================================================' AS info;
SELECT '升级内容汇总：' AS info;
SELECT '-------------------------------------------------' AS info;
SELECT '1. ✅ messages 表添加 phone 字段' AS item;
SELECT '2. ✅ messages 表添加回复相关字段（5个字段）' AS item;
SELECT '3. ✅ messages 表添加咨询类型字段' AS item;
SELECT '4. ✅ users 表添加注册来源字段' AS item;
SELECT '5. ✅ users 表添加关联留言ID字段' AS item;
SELECT '6. ✅ users 表添加激活时间字段' AS item;
SELECT '7. ✅ 创建所有相关索引' AS item;
SELECT '=================================================' AS info;
SELECT '请重启应用后测试功能' AS info;
SELECT '=================================================' AS info;
SELECT '=================================================' AS info;
