"""
账户管理路由：开户 / 查询账户详情 / 查询余额 / 注销账户
"""
import random
from fastapi import APIRouter, Header, HTTPException
from bank_server.models import CreateAccountRequest
from bank_server import database as db
from bank_server.utils.jwt_handler import extract_user_id

router = APIRouter(prefix="/api/account", tags=["账户管理模块"])


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


def _gen_account_no() -> str:
    """生成唯一 16 位账号"""
    while True:
        no = "6222" + "".join([str(random.randint(0, 9)) for _ in range(12)])
        if not db.query_one("SELECT id FROM bank_accounts WHERE account_no = %s", (no,)):
            return no


# ---------- 查询账户列表 ----------
@router.get("/list", summary="查询本人所有账户")
def list_accounts(token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    accounts = db.query_all("SELECT * FROM bank_accounts WHERE user_id = %s ORDER BY created_at DESC", (user["id"],))
    return {
        "code": 200,
        "data": [
            {
                "account_no": a["account_no"],
                "account_type": a["account_type"],
                "balance": float(a["balance"]),
                "status": a["status"],
                "created_at": str(a["created_at"])
            }
            for a in accounts
        ]
    }


# ---------- 开立账户 ----------
@router.post("/create", summary="开立银行账户")
def create_account(body: CreateAccountRequest, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    if body.account_type not in ("savings", "current"):
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "账户类型无效，仅支持 savings / current"})

    account_no = _gen_account_no()
    db.execute(
        "INSERT INTO bank_accounts (account_no, user_id, account_type) VALUES (%s, %s, %s)",
        (account_no, user["id"], body.account_type)
    )
    return {"code": 200, "msg": "开户成功", "account_no": account_no}


# ---------- 查询账户详情 ----------
@router.get("/{account_no}", summary="查询账户详情")
def get_account(account_no: str, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    account = db.query_one("SELECT * FROM bank_accounts WHERE account_no = %s", (account_no,))

    if not account:
        raise HTTPException(status_code=404, detail={"code": 404, "msg": "账户不存在"})
    # 越权防护：只能查自己的账户
    if account["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权访问他人账户"})

    return {
        "code": 200,
        "data": {
            "account_no":   account["account_no"],
            "account_type": account["account_type"],
            "balance":      float(account["balance"]),
            "status":       account["status"],
            "created_at":   str(account["created_at"])
        }
    }


# ---------- 查询余额 ----------
@router.get("/balance/{account_no}", summary="查询账户余额")
def get_balance(account_no: str, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    account = db.query_one("SELECT * FROM bank_accounts WHERE account_no = %s", (account_no,))

    if not account:
        raise HTTPException(status_code=404, detail={"code": 404, "msg": "账户不存在"})
    if account["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权访问他人账户"})

    return {"code": 200, "data": {"balance": float(account["balance"]), "currency": "CNY"}}


# ---------- 注销账户 ----------
@router.post("/close/{account_no}", summary="注销账户（余额须为 0）")
def close_account(account_no: str, token: str = Header(..., alias="token")):
    user = _get_user_from_token(token)
    account = db.query_one("SELECT * FROM bank_accounts WHERE account_no = %s", (account_no,))

    if not account:
        raise HTTPException(status_code=404, detail={"code": 404, "msg": "账户不存在"})
    if account["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权操作他人账户"})
    if float(account["balance"]) != 0.00:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "账户余额不为 0，无法注销"})

    db.execute("UPDATE bank_accounts SET status = 'closed' WHERE account_no = %s", (account_no,))
    return {"code": 200, "msg": "账户已成功注销"}
