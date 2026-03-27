import os
import redis

# 全局 Redis 连接池
_redis_pool = None

def get_redis_client():
    global _redis_pool
    if _redis_pool is None:
        host = os.environ.get("REDIS_HOST", "127.0.0.1")
        port = int(os.environ.get("REDIS_PORT", 6379))
        _redis_pool = redis.ConnectionPool(host=host, port=port, db=0, decode_responses=True)
    return redis.Redis(connection_pool=_redis_pool)

import json

def publish_notification(user_id: int, title: str, content: str):
    """异步投递消息：将通知发往 Redis List 作为 MQ，削峰填谷，加快主流程返回"""
    client = get_redis_client()
    msg = {
        "user_id": user_id,
        "title": title,
        "content": content
    }
    client.lpush("queue:notifications", json.dumps(msg))
