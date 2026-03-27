"""
认证模块路由：用户注册 / 登录
"""
from fastapi import APIRouter, HTTPException
from bank_server.models import RegisterRequest, LoginRequest
from bank_server import database as db
from bank_server.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["认证模块"])


# ---------- 用户注册 ----------
@router.post("/register", summary="用户注册")
def register(body: RegisterRequest):
    # 检查用户名是否重复
    if db.query_one("SELECT id FROM users WHERE username = %s", (body.username,)):
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "用户名已存在"})
    # 检查手机号是否重复
    if db.query_one("SELECT id FROM users WHERE phone = %s", (body.phone,)):
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "手机号已注册"})

    user_id = db.execute(
        "INSERT INTO users (username, password, phone) VALUES (%s, %s, %s)",
        (body.username, body.password, body.phone)
    )
    return {"code": 200, "msg": "注册成功", "user_id": user_id}


# ---------- 用户登录 ----------
@router.post("/login", summary="用户登录")
def login(body: LoginRequest):
    user = db.query_one("SELECT * FROM users WHERE username = %s", (body.username,))

    # 用户不存在
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "用户名或密码错误"})

    # 账户已锁定
    if user["status"] == 0:
        raise HTTPException(status_code=423, detail={"code": 423, "msg": "账户已锁定，请联系客服"})

    # 密码错误：累计失败次数，达到 5 次锁定
    if user["password"] != body.password:
        fail_count = user["fail_count"] + 1
        if fail_count >= 5:
            db.execute("UPDATE users SET fail_count = %s, status = 0 WHERE id = %s",
                       (fail_count, user["id"]))
            raise HTTPException(status_code=423, detail={"code": 423, "msg": "密码错误次数过多，账户已锁定"})
        else:
            db.execute("UPDATE users SET fail_count = %s WHERE id = %s",
                       (fail_count, user["id"]))
            raise HTTPException(status_code=401, detail={
                "code": 401,
                "msg": f"密码错误，剩余尝试次数：{5 - fail_count}"
            })

    # 登录成功：重置失败次数，使用 JWT 生成 Token
    db.execute("UPDATE users SET fail_count = 0 WHERE id = %s", (user["id"],))
    
    # 生成 JWT token
    token = create_access_token(user["id"], user["username"])
    
    return {
        "code": 200,
        "msg": "登录成功",
        "token": token,
        "user_id": user["id"],
        "expires_in": 7200
    }
