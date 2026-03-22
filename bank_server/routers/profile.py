"""
个人资料模块
GET  /api/profile/           — 查看个人资料
PUT  /api/profile/           — 修改个人资料（姓名/邮箱）
PUT  /api/profile/password   — 修改密码
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from bank_server.database import get_conn

router = APIRouter(prefix="/api/profile", tags=["个人中心"])


class ProfileUpdateRequest(BaseModel):
    real_name: Optional[str] = Field(None, max_length=50, example="张三", description="真实姓名")
    email: Optional[str] = Field(None, example="zhangsan@example.com", description="邮箱地址")


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., example="Test@1234", description="当前密码")
    new_password: str = Field(..., min_length=8, example="NewPass@5678", description="新密码（至少8位）")


def _get_user(token: str, conn):
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})
    cur = conn.cursor()
    cur.execute("SELECT id, username, phone FROM users WHERE token = %s", (token,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 不存在"})
    return user


@router.get("/")
def get_profile(authorization: str = Header(None)):
    """获取当前用户的个人资料"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_profile WHERE user_id = %s", (user["id"],))
        profile = cur.fetchone()
        return {
            "code": 200,
            "data": {
                "username": user["username"],
                "phone": user["phone"],
                "real_name": profile["real_name"] if profile else None,
                "email": profile["email"] if profile else None,
                "avatar_url": profile["avatar_url"] if profile else "/static/default_avatar.png",
                "kyc_status": profile["kyc_status"] if profile else "unverified",
            },
        }
    finally:
        conn.close()


@router.put("/")
def update_profile(body: ProfileUpdateRequest, authorization: str = Header(None)):
    """修改个人资料（姓名/邮箱）"""
    if not body.real_name and not body.email:
        raise HTTPException(status_code=400, detail={"code": 400, "msg": "至少提供一个需要修改的字段"})

    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()

        # 确保 profile 行存在
        cur.execute("SELECT id FROM user_profile WHERE user_id = %s", (user["id"],))
        if not cur.fetchone():
            cur.execute("INSERT INTO user_profile (user_id) VALUES (%s)", (user["id"],))

        updates, params = [], []
        if body.real_name:
            updates.append("real_name = %s")
            params.append(body.real_name)
        if body.email:
            updates.append("email = %s")
            params.append(body.email)
        params.append(user["id"])

        cur.execute(f"UPDATE user_profile SET {', '.join(updates)} WHERE user_id = %s", params)
        conn.commit()
        return {"code": 200, "msg": "资料更新成功"}
    finally:
        conn.close()


@router.put("/password")
def change_password(body: PasswordChangeRequest, authorization: str = Header(None)):
    """修改登录密码（需验证旧密码）"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE id = %s", (user["id"],))
        row = cur.fetchone()
        if row["password"] != body.old_password:
            raise HTTPException(status_code=401, detail={"code": 401, "msg": "原密码错误"})
        if body.new_password == body.old_password:
            raise HTTPException(status_code=400, detail={"code": 400, "msg": "新密码不能与原密码相同"})

        cur.execute("UPDATE users SET password = %s WHERE id = %s", (body.new_password, user["id"]))
        conn.commit()
        return {"code": 200, "msg": "密码修改成功，请重新登录"}
    finally:
        conn.close()
