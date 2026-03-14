import pytest
import os

if __name__ == '__main__':
    print("🚀 正在启动全军自动化测试突击...")

    # 极其优雅！因为有了 pytest.ini，这里什么参数都不用传了！
    # Pytest 总司令会自动去读 .ini 文件里的规矩！
    # 第一个参数强行指定测试用例所在的文件夹，绝不让它乱跑
    pytest.main([
        "./test_cases",
        "--cov=api",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])

    print("📊 正在生成极其华丽的 Allure HTML 战报...")
    os.system("allure generate ./allure-results -o ./reports/allure-report --clean")
    print("✅ 战报生成完毕！请在 reports 目录下查看！")