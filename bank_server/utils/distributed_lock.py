import time
from contextlib import contextmanager
from fastapi import HTTPException
from bank_server.redis_client import get_redis_client

class DistributedLockError(HTTPException):
    def __init__(self, msg="系统繁忙，请稍后再试"):
        super().__init__(status_code=409, detail={"code": 409, "msg": msg})

@contextmanager
def acquire_lock(lock_key: str, timeout: int = 5, retry_interval: float = 0.1, max_wait: float = 3.0):
    """
    基于 Redis SETNX (Set if Not eXists) 的分布式自旋锁
    
    lock_key: 锁的唯一标识 (例如: "lock:account:6222020")
    timeout: 锁的自动过期时间（防死锁），单位秒
    retry_interval: 获取不到锁时的自旋等待时间
    max_wait: 最大等待时间
    """
    redis_client = get_redis_client()
    lock_id = "LOCKED"
    
    end_time = time.time() + max_wait
    acquired = False
    
    while time.time() < end_time:
        # nx=True 保证只有当前 Key 不存在时才能设置成功（即抢夺到锁）
        if redis_client.set(lock_key, lock_id, ex=timeout, nx=True):
            acquired = True
            break
        # 未抢到锁，短暂休眠后重试（自旋）
        time.sleep(retry_interval)
        
    if not acquired:
        # 如果等待 max_wait 秒依然没有抢到，强行熔断，防止阻塞线程
        raise DistributedLockError(msg="当前账户交易排队中，请稍后重试")
        
    try:
        # 将锁交还给 with 业务块
        yield
    finally:
        # 业务执行完毕（无论成功还是报错），必须释放锁
        redis_client.delete(lock_key)

@contextmanager
def acquire_double_lock(account1: str, account2: str):
    """
    用于行内转账的双账号锁。
    为防止互相转账造成的「死锁」(A锁了A等B，B锁了B等A)，必须进行排序后依次加锁。
    """
    # 按账号字符串排序，保证全局加锁顺序一致
    sorted_accounts = sorted([account1, account2])
    
    lock_key1 = f"lock:account:{sorted_accounts[0]}"
    lock_key2 = f"lock:account:{sorted_accounts[1]}"
    
    with acquire_lock(lock_key1):
        with acquire_lock(lock_key2):
            yield
