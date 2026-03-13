import pymysql

class DB:
    def __init__(self):
        self.config = {
            'host': '192.168.152.1',
            'user': 'root',
            'password': '123456789Yj',
            'database': 'mall_target',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def query_one(self, sql):
        conn = pymysql.connect(**self.config)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def execute(self, sql):
        """
        💥 专属爆破技能 (INSERT/UPDATE/DELETE)：负责修改数据，并全自动提交！
        """
        conn = pymysql.connect(**self.config)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()  # 自动提交，再也不怕忘写了！
        conn.close()

db =DB()