"""
文件上传模块 - 模拟银行 KYC 身份证件上传接口
POST /api/account/{account_no}/kyc-upload
"""
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from bank_server.database import get_conn

router = APIRouter(prefix="/api/account", tags=["文件上传"])

# 允许的文件类型和大小限制
ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


def _verify_token(token: str) -> dict:
    """验证 Token 并返回用户信息"""
    if not token or not token.startswith("BANK_TOKEN_"):
        raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 无效"})
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE token = %s", (token,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail={"code": 401, "msg": "Token 不存在"})
        return user
    finally:
        conn.close()


@router.post("/{account_no}/kyc-upload")
async def kyc_upload(
    account_no: str,
    file: UploadFile = File(...),
    authorization: str = Header(None),
):
    """
    KYC 身份证件上传接口
    - 支持格式：JPG / PNG / PDF
    - 单文件大小限制：5MB
    - 需要有效 Token
    """
    # 鉴权
    _verify_token(authorization)

    # 校验文件类型
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail={"code": 400, "msg": f"不支持的文件类型: {file.content_type}，仅支持 JPG/PNG/PDF"},
        )

    # 读取内容并校验大小
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail={"code": 400, "msg": f"文件大小超过限制（最大 5MB），当前 {len(content) / 1024:.1f}KB"},
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail={"code": 400, "msg": "上传文件不能为空"},
        )

    return {
        "code": 200,
        "msg": "KYC 文件上传成功，等待人工审核",
        "data": {
            "account_no": account_no,
            "filename": file.filename,
            "size_kb": round(len(content) / 1024, 2),
            "content_type": file.content_type,
            "status": "pending_review",
        },
    }
