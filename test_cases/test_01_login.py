import requests
from config import LOGIN_URL

def test_login():
    url = LOGIN_URL

    #先跑通，后分离数据
    payload = {
        "username": "kobe",
        "password": "123456"
    }
    print("向靶场发送登录请求...")
    response = requests.post(url, json=payload)

    # 打印靶机返回的完整情报
    print(f"🎯 靶机返回的状态码: {response.status_code}")
    print(f"🎯 靶机返回的 JSON: {response.json()}")

    #获取Token
    my_token = response.json()["token"]
    print(f"🔑 成功缴获 Token: {my_token}")

    #断言登录状态
    assert response.status_code == 200, f"登录失败，状态码: {response.status_code}"
    