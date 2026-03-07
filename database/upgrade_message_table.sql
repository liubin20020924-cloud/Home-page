-- =====================================================
-- 在线留言功能数据库升级脚本
-- 创建时间: 2026-03-07
-- 说明: 为官网联系表单添加留言持久化存储
--       添加 phone 字段以支持电话联系功能
-- =====================================================

USE `clouddoors_db`;

-- 添加 phone 字段（如果不存在）
ALTER TABLE `messages`
ADD COLUMN IF NOT EXISTS `phone` VARCHAR(20) COMMENT '联系电话' AFTER `email`;

-- 查看当前表结构
SHOW COLUMNS FROM `messages`;

-- 备份现有数据（如果有）
-- CREATE TABLE IF NOT EXISTS `messages_backup` AS SELECT * FROM `messages`;

-- 添加索引优化查询性能
-- 如果状态索引不存在，则添加
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_status (`status`);
ALTER TABLE `messages` ADD INDEX IF NOT EXISTS idx_created_at (`created_at`);

-- 插入测试数据（可选，用于测试）
-- INSERT INTO `messages` (name, email, company_name, phone, message, status)
-- VALUES
--     ('测试用户', 'test@example.com', '测试公司', '13800138000', '这是一条测试留言', 'pending');

-- =====================================================
-- 升级完成
-- =====================================================
SELECT '在线留言功能数据库升级完成！' AS status;
SELECT '请重启应用后测试功能' AS info;
