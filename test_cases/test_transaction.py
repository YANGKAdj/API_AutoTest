import requests
import pymysql
def test_full_pay_flow(get_token):
    #准备工作
    #headers = {"Authorization": f"Bearer {get_token}"}
    headers = {"token": get_token}

    #创建一个订单
    print("\n[动作一] 🚀 正在创建一笔 100 元的新订单...")
    create_url = "http://127.0.0.1:5000/api/order/create"
    order_payload = {"product_name": "《大厂测开晋升指南》", "amount": 100.00}
    res_create = requests.post(create_url, headers=headers, json=order_payload)

    #获取订单号
    order_id = res_create.json()["order_id"]
    print(f"[情报] ✅ 拿到新鲜的订单号: {order_id}")

    #扣款
    print(f"\n[动作二] 💸 正在对订单 {order_id} 发起支付指令...")
    pay_url = "http://127.0.0.1:5000/api/order/pay"
    #

    #
    pay_payload = {"order_id": order_id}
    res_pay = requests.post(url=pay_url, json=pay_payload, headers=headers)
    print(res_pay.json())

    # 接口级断言：确保接口说是成功的
    assert res_pay.status_code == 200
    assert res_pay.json()["code"] == 200
    print("[情报] ✅ 接口返回支付成功！")

    #数据库查账

    #建立数据库连接
    conn = pymysql.connect(
        host='127.0.0.1', user='root', password='123456789Yj',  # ⚠️ 改成你的密码！
        database='mall_target', cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    # 1. 查订单表：看状态是不是变成了 1（已支付）
    cursor.execute(f"SELECT status FROM orders WHERE id = {order_id}")
    order_data = cursor.fetchone()
    print(f"[核查] 订单当前状态为: {order_data['status']}")
    assert order_data['status'] == 1  # 极其严格的断言！

    # 2. 查用户表：刚才扣了 100 块，看 kobe 的余额是不是 400.00 了！
    cursor.execute("SELECT balance FROM users WHERE username = 'kobe'")
    user_data = cursor.fetchone()
    print(f"[核查] kobe 当前余额为: {user_data['balance']}")
    # ⚠️ 之前数据库里初始是 500 块，扣掉 100，这里必须断言等于 400！
    assert user_data['balance'] == 400.00

    conn.close()
    print("\n🎉 报告长官！交易链路全线贯通！数据库核查完美通过！没有一分钱流失！")


#金额不足
def test_pay_insufficient_balance(get_token):
    headers = {"token": get_token}

    # 【动作一：强行制造一笔天价订单】
    print("\n[异常演习] 🚀 kobe 只有 400 块，却试图购买价值 15000 元的 MacBook Pro...")
    create_url = "http://127.0.0.1:5000/api/order/create"
    order_payload = {"product_name": "MacBook Pro", "amount": 15000.00}
    # 提交需求
    res_create = requests.post(create_url, headers=headers, json=order_payload)
    
    order_id = res_create.json()["order_id"]
    print(f"[情报] ✅ 拿到天价的订单号: {order_id}")

    # 去支付
    pay_url = "http://127.0.0.1:5000/api/order/pay"
    # 在支付接口需要的是订单号
    pay_payload = {"order_id": order_id}
    res_pay = requests.post(url=pay_url, json=pay_payload, headers=headers)
    
    
    # ⚠️ 接口级断言：这次绝对不能是 200 成功了！必须被靶机无情拦截！
    print(f"[情报] 靶机返回拦截信息: {res_pay.json()}")
    assert res_pay.status_code == 200  # HTTP 请求本身通了
    assert res_pay.json()["code"] == 400  # 业务防线生效！状态码 400
    assert "余额不足" in res_pay.json()["msg"] # 必须提示余额不足

    #数据库查账，防止账户扣成负数
    print("\n[异常演习] 🕵️‍♂️ 潜入数据库核实：钱没少吧？订单没变成已支付吧？")

    #建立数据库连接
    conn = pymysql.connect(
        host='127.0.0.1', user='root', password='123456789Yj', # ⚠️ 改密码！
        database='mall_target', cursorclass=pymysql.cursors.DictCursor #字典游标，返回的字典易于查找  
    )
    cursor = conn.cursor()
    #金额必须还是400
    cursor.execute("SELECT balance FROM users WHERE username = 'kobe'")
    user_data = cursor.fetchone()
    print(f"[核查] kobe 当前余额为: {user_data['balance']}")
    assert user_data['balance'] == 400.00

    #订单必须还是未支付，status = 0
    cursor.execute(f"SELECT status FROM orders WHERE id = {order_id}")
    order_data = cursor.fetchone()
    print(f"[核查] 订单防线坚固，状态依然为: {order_data['status']}")
    assert order_data['status'] == 0

    # ================= 新增：动作四 =================
    print("\n[打扫战场] 🧹 测试结束，正在销毁本次演习产生的垃圾订单...")
    # 执行无情的 DELETE 抹杀指令！
    cursor.execute(f"DELETE FROM orders WHERE id = {order_id}")
    conn.commit()  # ⚠️ 极其致命：增删改操作必须 commit 才能生效！
    print(f"[打扫战场] 🗑️ 订单 {order_id} 已被物理毁灭！数据库恢复如初！")
    # ===============================================


    cursor.close()
    conn.close()
    print("\n🎉 报告长官！异常拦截演习圆满成功！靶机防线固若金汤，未发生任何资损！")