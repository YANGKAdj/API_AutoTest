import requests
from utils.logger import log

class OrderAPI:
    def __init__(self,token):
        self.base_url = "http://127.0.0.1:5000"
        self.headers = {"token": token}

    def create_order(self,product_name, amount):
        url = self.base_url + "/api/order/create"
        payload = {"product_name": product_name, "amount": amount}
        log.info(f"👉 发起[创建订单]请求: 产品={product_name}, 金额={amount}")
        res = requests.post(url,json=payload, headers=self.headers)
        log.info(f"👈 [创建订单]响应: {res.json()}")
        return res

    def pay_order(self,order_id):
        url = self.base_url + "/api/order/pay"
        payload = {"order_id": order_id}
        log.info(f"👉 发起[支付订单]请求: 订单号={order_id}")
        res = requests.post(url, json=payload, headers=self.headers)
        log.info(f"👈 [支付订单]响应: {res.json()}")
        return res