-- ==================================================
-- 银行核心业务系统 数据库初始化脚本
-- 数据库：bank_core
-- ==================================================

CREATE DATABASE IF NOT EXISTS bank_core DEFAULT CHARACTER SET utf8mb4;
USE bank_core;

-- --------------------------------------------------
-- 表1：用户表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE COMMENT '登录用户名',
    password    VARCHAR(255) NOT NULL COMMENT '密码（明文，测试环境简化）',
    phone       VARCHAR(20)  NOT NULL UNIQUE COMMENT '手机号',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '账户状态: 1=正常, 0=锁定',
    fail_count  INT          NOT NULL DEFAULT 0 COMMENT '连续登录失败次数',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='用户表';

-- --------------------------------------------------
-- 表2：银行账户表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS bank_accounts (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    account_no   VARCHAR(20)    NOT NULL UNIQUE COMMENT '银行账号（16位）',
    user_id      INT            NOT NULL COMMENT '关联用户ID',
    account_type VARCHAR(20)    NOT NULL DEFAULT 'savings' COMMENT '账户类型: savings=储蓄, current=活期',
    balance      DECIMAL(15, 2) NOT NULL DEFAULT 0.00 COMMENT '账户余额（元）',
    status       VARCHAR(20)    NOT NULL DEFAULT 'active' COMMENT '账户状态: active=正常, frozen=冻结, closed=注销',
    created_at   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='银行账户表';

-- --------------------------------------------------
-- 表3：交易流水表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS transactions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    txn_id          VARCHAR(30)    NOT NULL UNIQUE COMMENT '交易流水号（唯一）',
    txn_type        VARCHAR(20)    NOT NULL COMMENT '交易类型: deposit/withdraw/transfer/cross_transfer',
    from_account    VARCHAR(20)    NULL COMMENT '付款账号（取款/转账时有值）',
    to_account      VARCHAR(20)    NULL COMMENT '收款账号（存款/转账时有值）',
    amount          DECIMAL(15, 2) NOT NULL COMMENT '交易金额',
    fee             DECIMAL(15, 2) NOT NULL DEFAULT 0.00 COMMENT '手续费',
    status          VARCHAR(20)    NOT NULL DEFAULT 'success' COMMENT '交易状态: success/failed',
    remark          VARCHAR(255)   NULL COMMENT '交易备注',
    created_at      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT='交易流水表';

-- --------------------------------------------------
-- 初始化测试数据
-- --------------------------------------------------

-- 测试用户
INSERT INTO users (username, password, phone) VALUES
('zhang_san', 'Test@1234', '13800138001'),
('li_si',     'Test@1234', '13800138002'),
('wang_wu',   'Test@1234', '13800138003');

-- 测试账户（zhang_san 有两个账户，初始余额较充足）
INSERT INTO bank_accounts (account_no, user_id, account_type, balance) VALUES
('6222020000000001', 1, 'savings', 50000.00),   -- zhang_san 储蓄账户
('6222020000000002', 1, 'current', 5000.00),    -- zhang_san 活期账户
('6222020000000003', 2, 'savings', 10000.00),   -- li_si 储蓄账户
('6222020000000004', 3, 'savings', 0.00);       -- wang_wu （余额为0，用于注销测试）
