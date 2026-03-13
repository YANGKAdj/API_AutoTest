#创建订单
import requests

def test_create_order(get_token):
    url = "http://192.168.152.1:5000/api/order/create"

    # 绝密操作：带着 Token 才能进后院！把 Token 塞进请求头 (Headers) 里！
    headers = {
        "token": get_token
    }

    # 买一本 99 块钱的书
    payload = {
        "product_name": "《架构师的自我修养》",
        "amount": 99.00
    }

    print("\n🚀 正在携 Token 突击下单接口...")
    res = requests.post(url=url, json=payload, headers=headers)

    print(f"🎯 靶机返回状态码: {res.status_code}")
    print(f"🎯 靶机返回的 JSON: {res.json()}")

    # 终极断言：确认下单成功，并且靶机返回了订单号！
    assert res.status_code == 200
    assert res.json()["code"] == 200
    assert "order_id" in res.json()