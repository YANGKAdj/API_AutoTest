import os
import pymysql


class DB:
    def __init__(self):
        self.config = {
            'host':        os.environ.get('DB_HOST', '127.0.0.1'),
            'port':        int(os.environ.get('DB_PORT', 3306)),
            'user':        os.environ.get('DB_USER', 'root'),
            'password':    os.environ.get('DB_PASSWORD', '123456789Yj'),
            'database':    os.environ.get('DB_NAME', 'bank_core'),
            'charset':     'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def query_one(self, sql, args=None):
        """查询单条记录，支持参数化防止 SQL 注入"""
        conn = pymysql.connect(**self.config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchone()
        finally:
            conn.close()

    def query_all(self, sql, args=None):
        """查询多条记录"""
        conn = pymysql.connect(**self.config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchall()
        finally:
            conn.close()

    def execute(self, sql, args=None):
        """执行写操作（INSERT/UPDATE/DELETE），自动提交"""
        conn = pymysql.connect(**self.config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
            conn.commit()
        finally:
            conn.close()


db = DB()