import requests
import pytest
from utils.yaml_util import read_yaml
from utils.db_util import db


#装饰器 DDT
@pytest.mark.parametrize("case_data",read_yaml("test_data.yaml")["pay_fail_data"]) #read_yaml返回字典
def test_pay_fail(get_token,case_data,order_cleaner):

    #传出所需数据
    product_name = case_data["product_name"]
    amount = case_data["amount"]
    expect_code = case_data["expect_code"]
    expect_msg = case_data["expect_msg"]

    headers = {"token": get_token}

    print(f"\n[DDT 异常演习] 🚀 kobe 试图购买: {product_name}，价值 {amount} 元...")

    # ================= 极其优雅的改进：拍快照！ =================
    # 在搞事情之前，先查一下 kobe 现在口袋里到底有多少钱？（绝不写死 400！）
    before_user_data = db.query_one("SELECT balance FROM users WHERE username = 'kobe'")
    initial_balance = before_user_data["balance"]
    print(f"[情报] 📷 战前快照：kobe 初始余额为 {initial_balance} 元")
    # =========================================================

    ###########流程##########
    #1. 创建订单
    create_url = "http://127.0.0.1:5000/api/order/create"
    order_payload = {"product_name": product_name, "amount": amount}
    res_create = requests.post(create_url, headers=headers, json=order_payload)

    # 获取订单号
    order_id = res_create.json()["order_id"]
    print(f"[情报] ✅ 拿到新鲜的订单号: {order_id}")
    order_cleaner.append(order_id)
    #2. 支付订单
    print(f"\n[动作二] 💸 正在对订单 {order_id} 发起支付指令...")
    pay_url = "http://127.0.0.1:5000/api/order/pay"

    pay_payload = {"order_id": order_id}
    res_pay = requests.post(url=pay_url, json=pay_payload, headers=headers)
    print(res_pay.json())

    # 接口级断言：确保接口说是成功的
    assert res_pay.status_code == 200, f"支付失败"
    assert res_pay.json()["code"] == expect_code  # 断言 400
    assert expect_msg in res_pay.json()["msg"]  # 断言包含 "余额不足"
    print("[情报] ✅ 接口返回支付失败！")

    # 数据库查账
    # # 1. 查订单表：看状态是不是还是0（已支付）
    order_data = db.query_one(f"SELECT * FROM orders WHERE id = {order_id}")

    print(f"[核查] 订单当前状态为: {order_data['status']}")
    assert order_data['status'] == 0, f"警告！！！订单支付失败但是显示成功"  # 极其严格的断言！

    #检查用户余额，应该不变
    user_data = db.query_one(f"SELECT * FROM users WHERE username = 'kobe'")
    ##这里断言不应该是固定数字，不同用户余额不同
    assert user_data["balance"] == initial_balance, f"余额变动异常"
    print("余额不变功能正常")

    #有order_cleaner代替
    # #销毁订单,但是用户余额没有变回去？？
    # db.execute(f"DELETE FROM orders WHERE id = {order_id}")
    # print(f"[打扫战场] 🗑️ 垃圾订单 {order_id} 已物理毁灭！")