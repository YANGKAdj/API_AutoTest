"""
定期存款模块
POST /api/fixed-deposit/create        — 开立定期存款
GET  /api/fixed-deposit/list          — 我的定期列表
POST /api/fixed-deposit/{fd_id}/withdraw — 提前支取（利息打折）
"""
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from bank_server.database import get_conn

router = APIRouter(prefix="/api/fixed-deposit", tags=["定期存款"])

# 各期限年利率
RATES = {1: 0.0175, 3: 0.0195, 6: 0.0210, 12: 0.0250}
EARLY_WITHDRAW_RATE = 0.0035  # 提前支取按活期利率计算


class FDCreateRequest(BaseModel):
    account_no: str = Field(..., example="6222020000000002", description="关联活期账号（到期后打入）")
    amount: float = Field(..., gt=0, le=1_000_000, example=10000.0, description="存款金额（元）")
    term_months: int = Field(..., example=12, description="期限（月）：1/3/6/12")


def _get_user(token: str, conn):
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE token = %s", (token,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 不存在"})
    return user


@router.post("/create")
def create_fixed_deposit(body: FDCreateRequest, authorization: str = Header(None)):
    """开立定期存款，资金从关联活期账号划出"""
    if body.term_months not in RATES:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": f"期限仅支持 {sorted(RATES.keys())} 个月"})

    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()

        cur.execute("SELECT balance, user_id, status FROM bank_accounts WHERE account_no = %s", (body.account_no,))
        acct = cur.fetchone()
        if not acct:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "账号不存在"})
        if acct["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权操作此账号"})
        if float(acct["balance"]) < body.amount:
            raise HTTPException(status_code=400, detail={"code": 400, "msg": "账户余额不足"})

        rate = RATES[body.term_months]
        interest = round(body.amount * rate * body.term_months / 12, 2)
        maturity = datetime.now() + relativedelta(months=body.term_months)
        fd_id = f"FD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

        cur.execute(
            """INSERT INTO fixed_deposits (fd_id, user_id, account_no, amount, term_months,
               annual_rate, interest, status, maturity_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', %s)""",
            (fd_id, user["id"], body.account_no, body.amount, body.term_months,
             rate, interest, maturity),
        )
        cur.execute("UPDATE bank_accounts SET balance = balance - %s WHERE account_no = %s",
                    (body.amount, body.account_no))
        cur.execute(
            "INSERT INTO notifications (user_id, title, content, type) VALUES (%s, %s, %s, 'transaction')",
            (user["id"], "定期存款开户成功",
             f"您的定期存款 {fd_id} 已成功开立，存入 {body.amount:.2f} 元，{body.term_months} 个月后到期，预计利息 {interest:.2f} 元。"),
        )
        conn.commit()
        return {
            "code": 200,
            "msg": "定期存款开立成功",
            "data": {
                "fd_id": fd_id,
                "amount": body.amount,
                "term_months": body.term_months,
                "annual_rate": f"{rate * 100:.2f}%",
                "interest": interest,
                "maturity_at": maturity.strftime("%Y-%m-%d"),
                "status": "active",
            },
        }
    finally:
        conn.close()


@router.get("/list")
def list_fixed_deposits(authorization: str = Header(None)):
    """查询当前用户所有定期存款"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute(
            "SELECT fd_id, amount, term_months, annual_rate, interest, status, maturity_at, created_at "
            "FROM fixed_deposits WHERE user_id = %s ORDER BY created_at DESC",
            (user["id"],),
        )
        return {"code": 200, "data": cur.fetchall()}
    finally:
        conn.close()


@router.post("/{fd_id}/withdraw")
def withdraw_fixed_deposit(fd_id: str, authorization: str = Header(None)):
    """
    提前支取定期存款。
    利息按活期利率（0.35%/年）重新计算，不足7天不计息。
    """
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT * FROM fixed_deposits WHERE fd_id = %s AND user_id = %s", (fd_id, user["id"]))
        fd = cur.fetchone()
        if not fd:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "定期存款记录不存在"})
        if fd["status"] != "active":
            raise HTTPException(status_code=400, detail={"code": 400, "msg": f"该定期已{fd['status']}，无法再次支取"})

        days_held = (datetime.now() - fd["created_at"]).days
        actual_interest = round(float(fd["amount"]) * EARLY_WITHDRAW_RATE * days_held / 365, 2) if days_held >= 7 else 0
        total_return = round(float(fd["amount"]) + actual_interest, 2)
        lost_interest = round(float(fd["interest"]) - actual_interest, 2)

        cur.execute("UPDATE fixed_deposits SET status = 'broken' WHERE fd_id = %s", (fd_id,))
        cur.execute("UPDATE bank_accounts SET balance = balance + %s WHERE account_no = %s",
                    (total_return, fd["account_no"]))
        cur.execute(
            "INSERT INTO notifications (user_id, title, content, type) VALUES (%s, %s, %s, 'transaction')",
            (user["id"], "定期存款提前支取",
             f"定期存款 {fd_id} 已提前支取，返还本金 {fd['amount']:.2f} 元，实际利息 {actual_interest:.2f} 元（损失利息 {lost_interest:.2f} 元）。"),
        )
        conn.commit()
        return {
            "code": 200,
            "msg": "提前支取成功，利息已按活期利率重新计算",
            "data": {
                "fd_id": fd_id,
                "principal": float(fd["amount"]),
                "days_held": days_held,
                "actual_interest": actual_interest,
                "lost_interest": lost_interest,
                "total_return": total_return,
            },
        }
    finally:
        conn.close()
