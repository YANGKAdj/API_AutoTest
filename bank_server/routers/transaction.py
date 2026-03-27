"""
交易模块路由：存款 / 取款 / 行内转账 / 跨行转账 / 交易记录查询
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException, Query
from bank_server.models import DepositRequest, WithdrawRequest, TransferRequest, CrossBankTransferRequest
from bank_server import database as db
from bank_server.utils.jwt_handler import extract_user_id

router = APIRouter(prefix="/api/transaction", tags=["交易模块"])

CROSS_BANK_FEE_RATE = 0.001  # 跨行转账手续费 0.1%


def _get_user_from_token(token: str) -> dict:
    """从 JWT Token 中解析用户"""
    # 使用 JWT 工具提取用户ID
    user_id = extract_user_id(token)
    
    # 从数据库查询用户完整信息
    user = db.query_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "用户不存在"})
    
    # 检查用户状态
    if user["status"] == 0:
        raise HTTPException(status_code=423, detail={"code": 423, "msg": "账户已锁定,请联系客服"})
    
    return user


def _gen_txn_id() -> str:
    return "TXN" + datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex[:6]).upper()


def _get_own_account(account_no: str, user_id: int) -> dict:
    """获取账户并验证归属，账户不存在或不属于当前用户则抛出异常"""
    account = db.query_one("SELECT * FROM bank_accounts WHERE account_no = %s AND status = 'active'", (account_no,))
    if not account:
        raise HTTPException(status_code=404, detail={"code": 404, "msg": "账户不存在或已注销"})
    if account["user_id"] != user_id:
        raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权操作他人账户"})
    return account


# ---------- 存款 ----------
@router.post("/deposit", summary="存款")
def deposit(body: DepositRequest, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    account = _get_own_account(body.account_no, user["id"])

    txn_id = _gen_txn_id()
    db.execute_transaction([
        ("UPDATE bank_accounts SET balance = balance + %s WHERE account_no = %s",
         (body.amount, body.account_no)),
        ("INSERT INTO transactions (txn_id, txn_type, to_account, amount) VALUES (%s, 'deposit', %s, %s)",
         (txn_id, body.account_no, body.amount)),
    ])
    new_balance = float(account["balance"]) + body.amount
    return {"code": 200, "msg": "存款成功", "txn_id": txn_id, "balance_after": round(new_balance, 2)}



# ---------- 取款 ----------
@router.post("/withdraw", summary="取款")
def withdraw(body: WithdrawRequest, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    account = _get_own_account(body.account_no, user["id"])

    if float(account["balance"]) < body.amount:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "余额不足，取款失败"})

    txn_id = _gen_txn_id()
    db.execute_transaction([
        ("UPDATE bank_accounts SET balance = balance - %s WHERE account_no = %s",
         (body.amount, body.account_no)),
        ("INSERT INTO transactions (txn_id, txn_type, from_account, amount) VALUES (%s, 'withdraw', %s, %s)",
         (txn_id, body.account_no, body.amount)),
    ])
    new_balance = float(account["balance"]) - body.amount
    return {"code": 200, "msg": "取款成功", "txn_id": txn_id, "balance_after": round(new_balance, 2)}



# ---------- 行内转账 ----------
@router.post("/transfer", summary="行内转账")
def transfer(body: TransferRequest, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)

    if body.from_account == body.to_account:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "转入与转出账号不能相同"})

    from_acc = _get_own_account(body.from_account, user["id"])
    to_acc = db.query_one(
        "SELECT * FROM bank_accounts WHERE account_no = %s AND status = 'active'", (body.to_account,))
    if not to_acc:
        raise HTTPException(status_code=404, detail={"code": 404, "msg": "收款账户不存在或已注销"})

    if float(from_acc["balance"]) < body.amount:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "余额不足，无法完成转账"})

    txn_id = _gen_txn_id()
    db.execute_transaction([
        ("UPDATE bank_accounts SET balance = balance - %s WHERE account_no = %s",
         (body.amount, body.from_account)),
        ("UPDATE bank_accounts SET balance = balance + %s WHERE account_no = %s",
         (body.amount, body.to_account)),
        ("INSERT INTO transactions (txn_id, txn_type, from_account, to_account, amount, remark) "
         "VALUES (%s, 'transfer', %s, %s, %s, %s)",
         (txn_id, body.from_account, body.to_account, body.amount, body.remark)),
    ])
    return {"code": 200, "msg": "转账成功", "txn_id": txn_id, "fee": 0.00}



# ---------- 跨行转账 ----------
@router.post("/transfer/cross-bank", summary="跨行转账（收取手续费 0.1%）")
def cross_bank_transfer(body: CrossBankTransferRequest, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    
    if not body.to_account.isdigit() or len(body.to_account) < 8:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "外部账号格式非法"})
        
    from_acc = _get_own_account(body.from_account, user["id"])

    fee = round(body.amount * CROSS_BANK_FEE_RATE, 2)
    total = round(body.amount + fee, 2)

    if float(from_acc["balance"]) < total:
        raise HTTPException(status_code=400, detail={
            "code": 400,
            "msg": f"余额不足，转账金额 {body.amount} + 手续费 {fee} = {total}，当前余额 {float(from_acc['balance'])}"
        })

    txn_id = _gen_txn_id()
    db.execute_transaction([
        ("UPDATE bank_accounts SET balance = balance - %s WHERE account_no = %s",
         (total, body.from_account)),
        ("INSERT INTO transactions (txn_id, txn_type, from_account, to_account, amount, fee, remark) "
         "VALUES (%s, 'cross_transfer', %s, %s, %s, %s, %s)",
         (txn_id, body.from_account, body.to_account, body.amount, fee,
          f"跨行至{body.to_bank_code}")),
    ])
    return {"code": 200, "msg": "跨行转账成功", "txn_id": txn_id, "fee": fee, "total_deducted": total}



# ---------- 查询交易记录 ----------
@router.get("/history", summary="查询交易记录（支持分页）")
def get_history(
        account_no: str = Query(..., description="账户号"),
        page:       int = Query(default=1, ge=1),
        size:       int = Query(default=10, ge=1, le=100),
        token: str = Header(..., alias="token")
):
    user = _get_user_from_token(token)
    _get_own_account(account_no, user["id"])  # 鉴权

    offset = (page - 1) * size
    records = db.query_all(
        "SELECT * FROM transactions WHERE from_account = %s OR to_account = %s "
        "ORDER BY created_at DESC LIMIT %s OFFSET %s",
        (account_no, account_no, size, offset)
    )
    total_row = db.query_one(
        "SELECT COUNT(*) as cnt FROM transactions WHERE from_account = %s OR to_account = %s",
        (account_no, account_no)
    )
    # 序列化 Decimal 和 datetime
    for r in records:
        r["amount"] = float(r["amount"])
        r["fee"] = float(r["fee"])
        r["created_at"] = str(r["created_at"])

    return {"code": 200, "data": {"total": total_row["cnt"], "page": page, "size": size, "records": records}}
