-- =====================================================
-- 回复模板表创建脚本
-- 创建时间: 2026-03-07
-- 说明: 创建 reply_templates 表，用于管理留言回复模板
-- =====================================================

USE `clouddoors_db`;

-- 创建回复模板表
CREATE TABLE IF NOT EXISTS `reply_templates` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '模板ID',
    `name` VARCHAR(100) NOT NULL COMMENT '模板名称',
    `category` VARCHAR(50) DEFAULT 'general' COMMENT '模板分类：general-通用, account-账户相关, technical-技术支持, billing-计费相关, other-其他',
    `content` TEXT NOT NULL COMMENT '模板内容（支持变量：{name}, {email}, {phone}, {company_name}, {message}）',
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
    KEY `idx_sort` (`sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='留言回复模板表';

-- 插入系统预设模板
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

云户科技客服团队', '转交相关部门处理的回复', 1, 5, 'system');

-- 查看创建结果
SELECT '=================================================' AS info;
SELECT '回复模板表创建成功！' AS status;
SELECT '=================================================' AS info;
SELECT '系统预设模板数量：' AS info, COUNT(*) AS count FROM `reply_templates` WHERE `is_system` = 1;
