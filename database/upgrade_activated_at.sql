-- =====================================================
-- 用户表添加激活时间字段升级脚本
-- 创建时间: 2026-03-07
-- 说明: 为 users 表添加 activated_at 字段，记录账户激活时间
-- =====================================================

USE `YHKB`;

-- 添加激活时间字段
ALTER TABLE `users`
ADD COLUMN IF NOT EXISTS `activated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '账户激活时间' AFTER `updated_at`;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_activated_at ON `YHKB`.`users`(`activated_at`);

-- 查看升级结果
SELECT '=================================================' AS info;
SELECT '用户表激活时间字段升级完成！' AS status;
SELECT '=================================================' AS info;
