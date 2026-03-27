"""
JWT Token 处理工具
提供 token 的生成、验证、解析等功能
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

# JWT 配置
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "bank_api_secret_key_2026_please_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2  # 2小时过期
ISSUER = "bank_api_server"


def create_access_token(
    user_id: int,
    username: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    生成 JWT access token
    
    Args:
        user_id: 用户ID
        username: 用户名
        expires_delta: 自定义过期时间间隔
    
    Returns:
        编码后的JWT token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": ISSUER
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证并解析 JWT token
    
    Args:
        token: JWT token字符串
    
    Returns:
        解析后的payload字典
    
    Raises:
        HTTPException: token无效、过期或格式错误时抛出401异常
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": "Token 已过期,请重新登录"}
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": "Token 签发者无效"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": f"Token 无效: {str(e)}"}
        )


def extract_user_id(token: str) -> int:
    """
    从 token 中提取用户ID
    
    Args:
        token: JWT token字符串
    
    Returns:
        用户ID
    
    Raises:
        HTTPException: token无效时抛出401异常
    """
    payload = verify_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": "Token 中缺少用户信息"}
        )
    return int(user_id)


def refresh_token(token: str) -> str:
    """
    刷新 token (延长过期时间)
    
    Args:
        token: 原有的JWT token
    
    Returns:
        新的JWT token
    
    Raises:
        HTTPException: token无效时抛出401异常
    """
    payload = verify_token(token)
    user_id = payload.get("user_id")
    username = payload.get("username")
    
    if not user_id or not username:
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": "Token 中缺少必要信息"}
        )
    
    return create_access_token(user_id, username)
