# JWT Token 升级说明

## 升级概述

本次升级将项目从简单的字符串token升级为标准的JWT(JSON Web Token)加密认证。

## 主要变更

### 1. 新增依赖
- `PyJWT==2.8.0` - JWT token生成和验证库

### 2. 新增工具模块
创建了 `bank_server/utils/jwt_handler.py`,提供以下功能:
- `create_access_token()` - 生成JWT token
- `verify_token()` - 验证并解析JWT token
- `extract_user_id()` - 从token中提取用户ID
- `refresh_token()` - 刷新token

### 3. 更新的路由文件
以下路由文件已更新为使用JWT验证:
- `bank_server/routers/auth.py` - 登录时生成JWT token
- `bank_server/routers/account.py` - 账户管理
- `bank_server/routers/transaction.py` - 交易操作
- `bank_server/routers/fixed_deposit.py` - 定期存款
- `bank_server/routers/profile.py` - 个人资料
- `bank_server/routers/loan.py` - 贷款管理
- `bank_server/routers/notification.py` - 系统通知

## JWT配置

### 默认配置
```python
SECRET_KEY = "bank_api_secret_key_2026_please_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2  # 2小时过期
ISSUER = "bank_api_server"
```

### 环境变量配置(推荐生产环境使用)
```bash
export JWT_SECRET_KEY="your_secure_secret_key_here"
```

## Token格式变化

### 旧格式(已废弃)
```
BANK_TOKEN_{user_id}_{random_number}
例如: BANK_TOKEN_123_456789
```

### 新格式(JWT)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInVzZXJuYW1lIjoidGVzdCIsImV4cCI6MTcxMTQ4MDAwMCwiaWF0IjoxNzExNDcyODAwLCJpc3MiOiJiYW5rX2FwaV9zZXJ2ZXIifQ.abc123...
```

## JWT Payload结构

```json
{
  "user_id": 123,
  "username": "test_user",
  "exp": 1711480000,  // 过期时间戳
  "iat": 1711472800,  // 签发时间戳
  "iss": "bank_api_server"  // 签发者
}
```

## 使用示例

### 登录获取Token
```python
# 请求
POST /api/auth/login
{
  "username": "test_user",
  "password": "password123"
}

# 响应
{
  "code": 200,
  "msg": "登录成功",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 123,
  "expires_in": 7200
}
```

### 使用Token访问API
```python
# 请求
GET /api/account/list
Headers: {
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Token过期处理
```python
# 响应(401)
{
  "code": 401,
  "msg": "Token 已过期,请重新登录"
}
```

## 安全优势

1. **加密签名** - 使用HS256算法签名,防止token被篡改
2. **过期机制** - 内置exp字段,自动验证token是否过期
3. **签发者验证** - 验证token是否由本系统签发
4. **无状态验证** - 不依赖数据库存储token,减少查询开销
5. **标准化** - 遵循JWT标准(RFC 7519),便于跨系统集成

## 迁移注意事项

1. **测试用例更新** - 需要确保测试用例使用新的JWT token
2. **前端适配** - 前端需要处理token过期的重新登录逻辑
3. **密钥管理** - 生产环境务必使用环境变量配置密钥
4. **旧Token清理** - 数据库中的token字段已不再使用,可考虑清理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 下一步建议

1. 配置生产环境密钥
2. 更新API文档
3. 完善测试用例
4. 考虑实现token刷新机制
5. 可选:实现token黑名单机制(用于用户登出)
