"""
FastAPI 银行核心业务系统 - 主入口
启动命令：uvicorn bank_server.main:app --reload --port 8000
Swagger 文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from bank_server.routers import auth, account, transaction, upload, report

app = FastAPI(
    title="银行核心业务 API",
    description=(
        "模拟银行核心业务接口，提供用户注册/登录、账户管理、"
        "存取款、行内转账、跨行转账等功能。\n\n"
        "**测试账户**（已在 `sql/init.sql` 初始化）：\n"
        "- 用户名: `zhang_san` / 密码: `Test@1234` / 账户号: `6222020000000001`（余额 50000）\n"
        "- 用户名: `li_si`     / 密码: `Test@1234` / 账户号: `6222020000000003`（余额 10000）"
    ),
    version="1.0.0",
)

# 注册路由模块
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(transaction.router)
app.include_router(upload.router)    # KYC 文件上传
app.include_router(report.router)    # 异步报表生成


@app.get("/", tags=["健康检查"])
def health_check():
    return {"status": "ok", "service": "BankCore API Server", "docs": "/docs"}
