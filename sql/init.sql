-- ==================================================
-- 银行核心业务系统 数据库初始化脚本 v2.0
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
    token       VARCHAR(100) NULL COMMENT '当前登录Token',
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
    txn_type        VARCHAR(20)    NOT NULL COMMENT '交易类型: deposit/withdraw/transfer/cross_transfer/loan_repay',
    from_account    VARCHAR(20)    NULL COMMENT '付款账号',
    to_account      VARCHAR(20)    NULL COMMENT '收款账号',
    amount          DECIMAL(15, 2) NOT NULL COMMENT '交易金额',
    fee             DECIMAL(15, 2) NOT NULL DEFAULT 0.00 COMMENT '手续费',
    status          VARCHAR(20)    NOT NULL DEFAULT 'success' COMMENT '交易状态: success/failed',
    remark          VARCHAR(255)   NULL COMMENT '交易备注',
    created_at      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
) COMMENT='交易流水表';

-- --------------------------------------------------
-- 表4：用户扩展资料表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profile (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL UNIQUE COMMENT '关联用户ID',
    real_name   VARCHAR(50)  NULL COMMENT '真实姓名',
    email       VARCHAR(100) NULL COMMENT '邮箱地址',
    avatar_url  VARCHAR(255) NULL DEFAULT '/static/default_avatar.png' COMMENT '头像地址',
    id_card     VARCHAR(18)  NULL COMMENT '身份证号（KYC）',
    kyc_status  VARCHAR(20)  NOT NULL DEFAULT 'unverified' COMMENT 'KYC状态: unverified/pending/verified',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='用户扩展资料表';

-- --------------------------------------------------
-- 表5：贷款表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS loans (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    loan_id         VARCHAR(30)    NOT NULL UNIQUE COMMENT '贷款编号',
    user_id         INT            NOT NULL COMMENT '借款人用户ID',
    account_no      VARCHAR(20)    NOT NULL COMMENT '放款账号',
    amount          DECIMAL(15, 2) NOT NULL COMMENT '贷款金额（元）',
    term_months     INT            NOT NULL COMMENT '贷款期限（月）',
    annual_rate     DECIMAL(5, 4)  NOT NULL DEFAULT 0.0480 COMMENT '年利率',
    monthly_payment DECIMAL(15, 2) NOT NULL COMMENT '每月还款额',
    remaining       DECIMAL(15, 2) NOT NULL COMMENT '剩余应还本金',
    status          VARCHAR(20)    NOT NULL DEFAULT 'active' COMMENT '状态: active/settled/overdue',
    purpose         VARCHAR(100)   NULL COMMENT '贷款用途',
    created_at      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='贷款表';

-- --------------------------------------------------
-- 表6：贷款还款记录表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS loan_repayments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    loan_id     VARCHAR(30)    NOT NULL COMMENT '关联贷款编号',
    amount      DECIMAL(15, 2) NOT NULL COMMENT '本次还款金额',
    principal   DECIMAL(15, 2) NOT NULL COMMENT '其中本金部分',
    interest    DECIMAL(15, 2) NOT NULL COMMENT '其中利息部分',
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
) COMMENT='贷款还款明细表';

-- --------------------------------------------------
-- 表7：定期存款表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS fixed_deposits (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    fd_id       VARCHAR(30)    NOT NULL UNIQUE COMMENT '定期存款编号',
    user_id     INT            NOT NULL COMMENT '关联用户ID',
    account_no  VARCHAR(20)    NOT NULL COMMENT '关联活期账号',
    amount      DECIMAL(15, 2) NOT NULL COMMENT '存入本金（元）',
    term_months INT            NOT NULL COMMENT '存款期限（月）: 1/3/6/12',
    annual_rate DECIMAL(5, 4)  NOT NULL COMMENT '年利率',
    interest    DECIMAL(15, 2) NOT NULL COMMENT '预计利息',
    status      VARCHAR(20)    NOT NULL DEFAULT 'active' COMMENT '状态: active/matured/broken',
    maturity_at DATETIME       NOT NULL COMMENT '到期日期',
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='定期存款表';

-- --------------------------------------------------
-- 表8：系统通知表
-- --------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL COMMENT '接收用户ID',
    title       VARCHAR(100) NOT NULL COMMENT '通知标题',
    content     VARCHAR(500) NOT NULL COMMENT '通知内容',
    type        VARCHAR(20)  NOT NULL DEFAULT 'transaction' COMMENT '类型: transaction/system/marketing',
    is_read     TINYINT      NOT NULL DEFAULT 0 COMMENT '是否已读: 0=未读, 1=已读',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='系统通知表';

-- --------------------------------------------------
-- 初始化测试数据
-- --------------------------------------------------

INSERT INTO users (username, password, phone) VALUES
('zhang_san', 'Test@1234', '13800138001'),
('li_si',     'Test@1234', '13800138002'),
('wang_wu',   'Test@1234', '13800138003');

INSERT INTO bank_accounts (account_no, user_id, account_type, balance) VALUES
('6222020000000001', 1, 'savings', 50000.00),
('6222020000000002', 1, 'current', 5000.00),
('6222020000000003', 2, 'savings', 10000.00),
('6222020000000004', 3, 'savings', 0.00);

INSERT INTO user_profile (user_id, real_name, email, kyc_status) VALUES
(1, '张三', 'zhangsan@test.com', 'verified'),
(2, '李四', 'lisi@test.com',     'unverified'),
(3, '王五', 'wangwu@test.com',   'unverified');

INSERT INTO notifications (user_id, title, content, type) VALUES
(1, '欢迎使用星辰银行', '尊敬的张三，欢迎加入星辰银行！', 'system'),
(1, '账户安全提醒', '您的储蓄账户 6222020000000001 已成功开通，初始余额 50,000 元。', 'transaction'),
(2, '欢迎使用星辰银行', '尊敬的李四，欢迎加入星辰银行！', 'system');
