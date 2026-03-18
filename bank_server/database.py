import os
import pymysql
from pymysql.cursors import DictCursor


def get_db_config():
    return {
        'host':        os.environ.get('DB_HOST', '127.0.0.1'),
        'port':        int(os.environ.get('DB_PORT', 3306)),
        'user':        os.environ.get('DB_USER', 'root'),
        'password':    os.environ.get('DB_PASSWORD', '123456789Yj'),
        'database':    os.environ.get('DB_NAME', 'bank_core'),
        'charset':     'utf8mb4',
        'cursorclass': DictCursor,
    }


def get_conn():
    """获取数据库连接（调用方负责关闭）"""
    return pymysql.connect(**get_db_config())


def query_one(sql: str, args=None):
    """查询单条记录"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchone()
    finally:
        conn.close()


def query_all(sql: str, args=None):
    """查询多条记录"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        conn.close()


def execute(sql: str, args=None):
    """执行写操作（INSERT / UPDATE / DELETE），返回 lastrowid"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            conn.commit()
            return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_transaction(statements: list):
    """
    执行多条 SQL 的原子事务。
    statements: [(sql, args), (sql, args), ...]
    所有语句全部成功则提交，任意一条失败则全部回滚。
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            for sql, args in statements:
                cur.execute(sql, args)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
