# 项目长期记忆

## 项目概况
- **项目名称**: 星辰银行 API 自动化测试系统
- **技术栈**: FastAPI + MySQL + Redis + JWT认证
- **前端**: 纯 HTML/JS,使用 Fetch API 调用后端

## 认证方式升级 (2026-03-26)
### JWT认证迁移
- **旧方式**: 使用 `BANK_TOKEN_` 前缀的固定 token,存储在数据库中
- **新方式**: 使用 JWT (PyJWT 2.8.0),token 包含 user_id、username、过期时间等信息
- **前端适配**: 同时发送 `token` 和 `authorization` 两个 header,兼容新旧模块

### 已迁移的模块
✅ auth.py - 登录注册(生成JWT)
✅ account.py - 账户管理
✅ transaction.py - 存取款转账
✅ txn_history.py - 交易流水查询
✅ loan.py - 贷款管理
✅ profile.py - 个人资料
✅ notification.py - 系统通知
✅ fixed_deposit.py - 定期存款
✅ report.py - 异步报表
✅ upload.py - 文件上传

### JWT配置
- **密钥**: 环境变量 `JWT_SECRET_KEY`,默认值在生产环境需修改
- **算法**: HS256
- **过期时间**: 2小时
- **签发者**: bank_api_server

## 常见问题

### 1. PyJWT 模块缺失
**症状**: `ModuleNotFoundError: No module named 'jwt'`
**解决**: `pip install PyJWT==2.8.0`

### 2. Windows 中文编码问题
**症状**: PowerShell 中 emoji 显示为乱码
**解决**: 
- 设置环境变量: `$env:PYTHONIOENCODING="utf-8"`
- 或在代码中避免使用 emoji

### 3. 认证失败 401 错误
**原因**: 某些模块还在使用旧的 `BANK_TOKEN_` 认证方式
**解决**: 检查对应路由文件,确保使用 `extract_user_id(token)` 验证 JWT

## 数据库配置
- **默认地址**: 127.0.0.1:3306
- **默认用户**: root
- **默认密码**: 123456789Yj
- **数据库名**: bank_core
- **配置文件**: `bank_server/database.py`

## 测试账户
- **张三**: 用户名 `zhang_san` / 密码 `Test@1234` / 账户号 `6222020000000001` (余额 50000)
- **李四**: 用户名 `li_si` / 密码 `Test@1234` / 账户号 `6222020000000003` (余额 10000)
