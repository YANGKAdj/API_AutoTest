"""
Locust 压力测试脚本 - 星辰银行核心接口
运行方式：locust -f locustfile.py --host=http://127.0.0.1:8000
然后浏览器打开 http://localhost:8089 配置并发数
"""
from locust import HttpUser, task, between


class BankUser(HttpUser):
    """模拟银行用户行为"""
    wait_time = between(0.5, 2)  # 每个用户请求间隔 0.5-2 秒
    token = None

    def on_start(self):
        """用户初始化：先注册再登录拿 Token"""
        import random, string
        suffix = ''.join(random.choices(string.digits, k=8))
        username = f"test_{suffix}"
        phone = f"138{suffix}"

        # 注册
        self.client.post("/api/auth/register", json={
            "username": username,
            "password": "test123456",
            "phone": phone
        })

        # 登录拿 Token
        res = self.client.post("/api/auth/login", json={
            "username": username,
            "password": "test123456"
        })
        if res.status_code == 200:
            self.token = res.json().get("data", {}).get("token")

    def _headers(self):
        return {"Authorization": self.token} if self.token else {}

    @task(3)
    def login(self):
        """高频任务：登录（权重 3）"""
        self.client.post("/api/auth/login", json={
            "username": "zhang_san",
            "password": "password123"
        }, name="POST /login")

    @task(2)
    def get_account_detail(self):
        """中频任务：查询账户（权重 2）"""
        self.client.get(
            "/api/account/6222020000000001",
            headers=self._headers(),
            name="GET /account/detail"
        )

    @task(1)
    def deposit(self):
        """低频任务：存款（权重 1）"""
        self.client.post(
            "/api/transaction/deposit",
            json={"account_no": "6222020000000001", "amount": 100},
            headers=self._headers(),
            name="POST /deposit"
        )
