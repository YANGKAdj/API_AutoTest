"""
系统通知模块
GET /api/notifications/          — 查询通知列表（支持过滤未读）
PUT /api/notifications/{id}/read — 标记单条为已读
PUT /api/notifications/read-all  — 全部标记已读
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from bank_server.database import get_conn

router = APIRouter(prefix="/api/notifications", tags=["系统通知"])


def _get_user(token: str, conn):
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE token = %s", (token,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 不存在"})
    return user


@router.get("/")
def list_notifications(
    authorization: str = Header(None),
    unread_only: bool = Query(False, description="是否只查未读"),
):
    """查询通知列表"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        sql = "SELECT * FROM notifications WHERE user_id = %s"
        params = [user["id"]]
        if unread_only:
            sql += " AND is_read = 0"
        sql += " ORDER BY created_at DESC"
        cur.execute(sql, params)
        notifications = cur.fetchall()

        cur.execute("SELECT COUNT(*) as cnt FROM notifications WHERE user_id = %s AND is_read = 0", (user["id"],))
        unread_count = cur.fetchone()["cnt"]

        return {"code": 200, "data": notifications, "unread_count": unread_count}
    finally:
        conn.close()


@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, authorization: str = Header(None)):
    """标记单条通知为已读"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("SELECT id, user_id FROM notifications WHERE id = %s", (notification_id,))
        notif = cur.fetchone()
        if not notif:
            raise HTTPException(status_code=404, detail={"code": 404, "msg": "通知不存在"})
        if notif["user_id"] != user["id"]:
            raise HTTPException(status_code=403, detail={"code": 403, "msg": "无权操作此通知"})
        cur.execute("UPDATE notifications SET is_read = 1 WHERE id = %s", (notification_id,))
        conn.commit()
        return {"code": 200, "msg": "已标记为已读"}
    finally:
        conn.close()


@router.put("/read-all")
def mark_all_as_read(authorization: str = Header(None)):
    """全部标记为已读"""
    conn = get_conn()
    try:
        user = _get_user(authorization, conn)
        cur = conn.cursor()
        cur.execute("UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0", (user["id"],))
        affected = cur.rowcount
        conn.commit()
        return {"code": 200, "msg": f"已将 {affected} 条通知标记为已读"}
    finally:
        conn.close()
