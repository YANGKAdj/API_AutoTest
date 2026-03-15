# 创建订单（演示用例，复用 OrderAPI，避免硬编码 URL）
from api.order_api import OrderAPI


def test_create_order(get_token):
    order_api = OrderAPI(get_token)

    res = order_api.create_order("《架构师的自我修养》", 99.00)

    # 终极断言：确认下单成功，并且靶机返回了订单号！
    assert res.status_code == 200
    assert res.json()["code"] == 200
    assert "order_id" in res.json()