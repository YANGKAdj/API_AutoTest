import pytest
import os

if __name__ == '__main__':
    print("🚀 正在启动全军自动化测试突击...")

    # 极其优雅！因为有了 pytest.ini，这里什么参数都不用传了！
    # Pytest 总司令会自动去读 .ini 文件里的规矩！
    pytest.main([
        "--cov=api",                  # 雷达目标：只扫 api 文件夹里的代码
        "--cov-report=html",          # 生成极其华丽的 html 覆盖率报告
        "--cov-report=term-missing"   # 极其硬核：在终端直接打印出哪一行代码没测到！
    ])

    print("📊 正在生成极其华丽的 Allure HTML 战报...")
    os.system("allure generate ./allure-results -o ./reports/allure-report --clean")
    print("✅ 战报生成完毕！请在 reports 目录下查看！")