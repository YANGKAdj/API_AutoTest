"""
FastAPI 银行核心业务系统 - 主入口
启动命令：uvicorn bank_server.main:app --reload --port 8000
Swagger 文档：http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from bank_server.routers import (
    auth, account, transaction, upload, report,
    loan, fixed_deposit, txn_history, profile, notification,
)

app = FastAPI(
    title="星辰银行 核心业务 API",
    description=(
        "全功能银行核心系统，覆盖鉴权、账户管理、存取款、转账、"
        "贷款、定期存款、交易流水、个人资料、系统通知等完整业务链路。\n\n"
        "**测试账户**（已在 `sql/init.sql` 初始化）：\n"
        "- 用户名: `zhang_san` / 密码: `Test@1234` / 账户号: `6222020000000001`（余额 50000）\n"
        "- 用户名: `li_si`     / 密码: `Test@1234` / 账户号: `6222020000000003`（余额 10000）"
    ),
    version="2.0.0",
)

# 跨域支持（供前端 HTML 页面调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（前端页面）
try:
    app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception:
    pass  # 前端目录不存在时忽略

# 注册路由模块
app.include_router(auth.router)
app.include_router(account.router)
app.include_router(transaction.router)
app.include_router(upload.router)
app.include_router(report.router)
app.include_router(loan.router)
app.include_router(fixed_deposit.router)
app.include_router(txn_history.router)
app.include_router(profile.router)
app.include_router(notification.router)


@app.get("/", tags=["健康检查"])
def health_check():
    return {
        "status": "ok",
        "service": "星辰银行 BankCore API Server v2.0",
        "docs": "/docs",
        "frontend": "/frontend/login.html",
    }
