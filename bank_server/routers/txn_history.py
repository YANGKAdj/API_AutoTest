"""
交易流水查询模块
GET /api/transactions/history        — 查询流水（支持分页、类型过滤、日期过滤）
GET /api/transactions/{txn_id}       — 查询单条流水详情
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from bank_server.database import get_conn

router = APIRouter(prefix="/api/transactions", tags=["交易流水"])


def _get_user(token: str, conn):
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE token = %s", (token,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 不存在"})
    return user


@router.get("/history")
def get_transaction_history(
    authorization: str = Header(None),
    account_no: Optional[str] = Query(None, description="按账号过滤"),
    txn_type: Optional[str] = Query(None, description="交易类型: deposit/withdraw/transfer/cross_transfer"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
):
    """
    查询当前用户的交易流水（支持多维度过滤与分页）
    - 按账号、交易类型、日期范围过滤
    - 默认按时间倒序返回
    """
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()

        # 获取用户所有账号
        cur.execute("SELECT account_no FROM bank_accounts WHERE user_id = %s", (user["id"],))
        user_accounts = {row["account_no"] for row in cur.fetchall()}
        if not user_accounts:
            return {"code": 200, "data": [], "total": 0, "page": page, "page_size": page_size}

        # 如果指定了账号，校验归属
        if account_no and account_no not in user_accounts:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权查询此账号流水"})

        target_accounts = [account_no] if account_no else list(user_accounts)
        placeholders = ",".join(["%s"] * len(target_accounts))
        conditions = [f"(from_account IN ({placeholders}) OR to_account IN ({placeholders}))"]
        params = target_accounts + target_accounts

        if txn_type:
            conditions.append("txn_type = %s")
            params.append(txn_type)
        if start_date:
            conditions.append("DATE(created_at) >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("DATE(created_at) <= %s")
            params.append(end_date)

        where = " AND ".join(conditions)
        offset = (page - 1) * page_size

        # 计总数
        cur.execute(f"SELECT COUNT(*) as total FROM transactions WHERE {where}", params)
        total = cur.fetchone()["total"]

        # 分页查询
        cur.execute(
            f"SELECT txn_id, txn_type, from_account, to_account, amount, fee, status, remark, created_at "
            f"FROM transactions WHERE {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params + [page_size, offset],
        )
        records = cur.fetchall()
        return {
            "code": 200,
            "data": records,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    finally:
        conn.close()


@router.get("/{txn_id}")
def get_transaction_detail(txn_id: str, authorization: str = Header(None)):
    """查询单条交易流水详情"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()

        cur.execute("SELECT account_no FROM bank_accounts WHERE user_id = %s", (user["id"],))
        user_accounts = {row["account_no"] for row in cur.fetchall()}

        cur.execute("SELECT * FROM transactions WHERE txn_id = %s", (txn_id,))
        txn = cur.fetchone()
        if not txn:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "流水记录不存在"})

        if txn["from_account"] not in user_accounts and txn["to_account"] not in user_accounts:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权查询此流水"})

        return {"code": 200, "data": txn}
    finally:
        conn.close()
