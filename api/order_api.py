import requests
from utils.logger import log
from config import CREATE_ORDER_URL, PAY_ORDER_URL, BASE_URL

class OrderAPI:
    def __init__(self,token):
        # 接口都跑在本地 Flask mock_server 的 BASE_URL
        self.base_url = BASE_URL
        self.headers = {"token": token}

    def create_order(self,product_name, amount):
        url = CREATE_ORDER_URL
        payload = {"product_name": product_name, "amount": amount}
        log.info(f"👉 发起[创建订单]请求: 产品={product_name}, 金额={amount}")
        res = requests.post(url,json=payload, headers=self.headers)
        log.info(f"👈 [创建订单]响应: {res.json()}")
        return res

    def pay_order(self,order_id):
        url = PAY_ORDER_URL
        payload = {"order_id": order_id}
        log.info(f"👉 发起[支付订单]请求: 订单号={order_id}")
        res = requests.post(url, json=payload, headers=self.headers)
        log.info(f"👈 [支付订单]响应: {res.json()}")
        return res