-- =====================================================
-- 工单系统 v2.8 升级脚本
-- 添加满意度评价功能
-- 创建时间: 2026-02-26
-- =====================================================

USE `casedb`;

-- 检查并删除可能存在的旧表（如果创建失败）
DROP TABLE IF EXISTS `satisfaction`;

-- 创建满意度评价表（不使用外键，避免字符集问题）
CREATE TABLE `satisfaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    `ticket_id` VARCHAR(32) NOT NULL UNIQUE COMMENT '工单ID',
    `rating` TINYINT NOT NULL COMMENT '评分(1-5)',
    `comment` TEXT NULL COMMENT '评价文字',
    `create_time` DATETIME NOT NULL COMMENT '评价时间',
    INDEX idx_ticket_id (`ticket_id`),
    INDEX idx_create_time (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单满意度评价表';

-- 验证表创建
SELECT 'satisfaction 表创建完成' AS status;
SHOW TABLES;
DESCRIBE satisfaction;
