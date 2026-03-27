"""
贷款模块 - 申请贷款、查看还款计划、还款
POST /api/loan/apply       — 申请贷款
GET  /api/loan/list        — 我的贷款列表
GET  /api/loan/{loan_id}   — 贷款详情与还款计划
POST /api/loan/{loan_id}/repay — 还款
"""
import uuid
import math
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from bank_server.database import get_conn
from bank_server.utils.jwt_handler import extract_user_id

router = APIRouter(prefix="/api/loan", tags=["贷款中心"])

ANNUAL_RATE = 0.0480  # 基准年利率 4.80%
MAX_LOAN = 500_000.0
MIN_LOAN = 1_000.0
VALID_TERMS = {3, 6, 12, 24, 36}  # 允许贷款期限（月）


class LoanApplyRequest(BaseModel):
    account_no: str = Field(..., example="6222020000000001", description="放款入账账号")
    amount: float = Field(..., gt=0, le=MAX_LOAN, example=50000.0, description="贷款金额（元），最高50万")
    term_months: int = Field(..., example=12, description="贷款期限（月）：3/6/12/24/36")
    purpose: str = Field(default="个人消费", example="装修", description="贷款用途")


class RepayRequest(BaseModel):
    account_no: str = Field(..., example="6222020000000001", description="还款账号")
    amount: float = Field(..., gt=0, example=5000.0, description="还款金额")


def _get_user(token: str, conn):
    """从 JWT Token 中解析用户"""
    # 使用 JWT 工具提取用户ID
    user_id = extract_user_id(token)
    
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "用户不存在"})
    return user


def _calc_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """等额还款（等额本息）月还款额计算"""
    r = annual_rate / 12
    return round(principal * r * (1 + r) ** term_months / ((1 + r) ** term_months - 1), 2)


@router.post("/apply")
def apply_loan(body: LoanApplyRequest, authorization: str = Header(None)):
    """申请贷款，系统自动审批并放款至指定账号"""
    if body.amount < MIN_LOAN:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": f"最低贷款金额为 {MIN_LOAN} 元"})
    if body.term_months not in VALID_TERMS:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": f"贷款期限仅支持 {sorted(VALID_TERMS)} 月"})

    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()

        # 校验放款账号
        cur.execute("SELECT id, user_id, balance, status FROM bank_accounts WHERE account_no = %s", (body.account_no,))
        acct = cur.fetchone()
        if not acct:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "账号不存在"})
        if acct["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权操作此账号"})
        if acct["status"] != "active":
            raise HTTPException(status_code=400, detail={"code": 400, "msg": "账号状态异常，无法放款"})

        monthly = _calc_monthly_payment(body.amount, ANNUAL_RATE, body.term_months)
        total_interest = round(monthly * body.term_months - body.amount, 2)
        loan_id = f"LOAN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

        # 插入贷款记录
        cur.execute(
            """INSERT INTO loans (loan_id, user_id, account_no, amount, term_months, annual_rate,
               monthly_payment, remaining, status, purpose)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s)""",
            (loan_id, user["id"], body.account_no, body.amount, body.term_months,
             ANNUAL_RATE, monthly, body.amount, body.purpose),
        )
        # 放款：账户余额增加
        cur.execute("UPDATE bank_accounts SET balance = balance + %s WHERE account_no = %s",
                    (body.amount, body.account_no))
        # 写通知
        cur.execute(
            "INSERT INTO notifications (user_id, title, content, type) VALUES (%s, %s, %s, 'transaction')",
            (user["id"],
             "贷款放款成功",
             f"您的贷款 {loan_id} 已成功放款 {body.amount:.2f} 元至账号 {body.account_no}，月还款额 {monthly:.2f} 元。"),
        )
        conn.commit()
        return {
            "code": 200,
            "msg": "贷款申请成功，已自动放款",
            "data": {
                "loan_id": loan_id,
                "amount": body.amount,
                "term_months": body.term_months,
                "annual_rate": f"{ANNUAL_RATE * 100:.2f}%",
                "monthly_payment": monthly,
                "total_interest": total_interest,
                "status": "active",
            },
        }
    finally:
        conn.close()


@router.get("/list")
def list_loans(authorization: str = Header(None)):
    """查询当前用户所有贷款记录"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT loan_id, amount, term_months, annual_rate, monthly_payment, remaining, status, purpose, created_at "
            "FROM loans WHERE user_id = %s ORDER BY created_at DESC",
            (user["id"],),
        )
        loans = cur.fetchall()
        return {"code": 200, "data": loans}
    finally:
        conn.close()


@router.get("/{loan_id}")
def get_loan_detail(loan_id: str, authorization: str = Header(None)):
    """查询贷款详情及还款历史"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT * FROM loans WHERE loan_id = %s AND user_id = %s", (loan_id, user["id"]))
        loan = cur.fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "贷款记录不存在"})
        cur.execute("SELECT * FROM loan_repayments WHERE loan_id = %s ORDER BY created_at DESC", (loan_id,))
        repayments = cur.fetchall()
        return {"code": 200, "data": {**loan, "repayments": repayments}}
    finally:
        conn.close()


@router.post("/{loan_id}/repay")
def repay_loan(loan_id: str, body: RepayRequest, authorization: str = Header(None)):
    """还款（支持部分还款，全额还清后状态自动变为 settled）"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT * FROM loans WHERE loan_id = %s AND user_id = %s", (loan_id, user["id"]))
        loan = cur.fetchone()
        if not loan:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "贷款记录不存在"})
        if loan["status"] == "settled":
            raise HTTPException(status_code=400, detail={"code": 400, "msg": "该贷款已还清"})

        # 校验还款账户余额
        cur.execute("SELECT balance, user_id FROM bank_accounts WHERE account_no = %s", (body.account_no,))
        acct = cur.fetchone()
        if not acct or acct["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权使用此账号还款"})
        if acct["balance"] < body.amount:
            raise HTTPException(status_code=400, detail={"code": 400, "msg": "账户余额不足"})
        if body.amount > float(loan["remaining"]):
            raise HTTPException(status_code=400, detail={"code": 400, "msg": f"还款金额超过剩余应还本金 {loan['remaining']:.2f} 元"})

        # 简化：利息按月利率 * 剩余本金
        monthly_rate = ANNUAL_RATE / 12
        interest = round(float(loan["remaining"]) * monthly_rate, 2)
        principal = round(body.amount - interest, 2)
        if principal < 0:
            principal = 0

        new_remaining = round(float(loan["remaining"]) - principal, 2)
        new_status = "settled" if new_remaining <= 0 else "active"

        cur.execute("UPDATE loans SET remaining = %s, status = %s WHERE loan_id = %s",
                    (max(new_remaining, 0), new_status, loan_id))
        cur.execute("UPDATE bank_accounts SET balance = balance - %s WHERE account_no = %s",
                    (body.amount, body.account_no))
        cur.execute(
            "INSERT INTO loan_repayments (loan_id, amount, principal, interest) VALUES (%s, %s, %s, %s)",
            (loan_id, body.amount, principal, interest),
        )
        cur.execute(
            "INSERT INTO notifications (user_id, title, content, type) VALUES (%s, %s, %s, 'transaction')",
            (user["id"], "还款成功",
             f"贷款 {loan_id} 还款 {body.amount:.2f} 元，剩余本金 {max(new_remaining, 0):.2f} 元。"),
        )
        conn.commit()
        return {
            "code": 200,
            "msg": "还款成功" if new_status == "active" else "恭喜！贷款已全额还清",
            "data": {
                "loan_id": loan_id,
                "repaid": body.amount,
                "principal": principal,
                "interest": interest,
                "remaining": max(new_remaining, 0),
                "status": new_status,
            },
        }
    finally:
        conn.close()
