# 🏦 星辰银行核心业务 API 测试框架 (API_AutoTest)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pytest](https://img.shields.io/badge/Pytest-8.0+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal.svg)
![Allure](https://img.shields.io/badge/Allure_Report-passed-success.svg)

本项目是一个基于 `Python + Pytest + Requests + PyMySQL + Allure` 打造的金融级高可用接口自动化测试框架。专门针对银行核心交易链路（存款、取款、多形态转账）设计，实现了 9 大核心交易 API 的 100% 场景拦截与高并发阻断测试。

## 🌟 项目亮点与核心架构 (Core Features)

1. **AOM (API Object Model) 降维解耦**：借鉴传统 UI 的 PO 思想，落地 `配置层 -> API 对象封装层 -> 测试用例层` 的三层解耦架构，大幅提升核心脚本复用率。
2. **防资损的三维深度断言机制**：摒弃单一 HTTP 状态响应，自研“`网关响应校验` + `Accounts 账务落库比对` + `Transactions 流水追溯`”的三维立体断言机制，彻底杜绝接口“假阳性”通过。
3. **YAML 数据驱动与极值覆盖**：隔离业务与测试数据，针对并发透支、转账负数攻击等边界场景独立落地 **44 条高价值覆盖用例**。
4. **沙盒生态与脏数据动态治理**：深度运用 Pytest Fixture (Yield 机制) 构建“前置无缝造数 -> 消费测试 -> 环境回滚”的自动化生态闭环，确保测试环境零数据污染。
5. **CI/CD 独立隔离构建**：通过 Docker-Compose 编排 FastAPI 后端与 MySQL 数据库，实现代码提交自触发拉起单次执行的临时沙盒测试环境。

## 📂 项目目录结构 (Project Structure)
```text
API_AutoTest/
├── api/                    # [AOM分层] API 对象封装层 (如 account_api.py, transaction_api.py)
├── test_cases/             # [测试用例] 核心测试脚本库 (覆盖业务流、安全边界与并发竞争)
├── data/                   # [测试数据] YAML 数据驱动文件 (bank_test_data.yaml)
├── utils/                  # [公共工具] 核心工具类封装 (db_util, yaml_util)
├── bank_server/            # [被测后端] 基于 FastAPI 开发的银行本地核心服务靶机
├── conftest.py             # [全局夹具] Pytest 全局注入 (处理 Token生成、临时用户造数与回收)
├── pytest.ini              # [框架配置] Pytest 全局运行参数配置文件
├── run.py                  # [执行入口] 测试任务调度与 Allure 报告生成总入口
├── docker-compose.yml      # [容器编排] 一键拉起 DB + Backend + Tests 临时构建沙盒
└── requirements.txt        # [环境依赖] 框架依赖包控制清单
```

## ⚙️ 一键极速部署与运行 (Quick Start)

### 方案一：Docker-Compose 沙盒一键执行（推荐，极简测试版）
确保本地已安装 Docker，在项目根目录执行：
```bash
docker-compose up --build
```
*执行流程：自动拉起 MySQL(bank_core) 库初始化 -> 启动 FastAPI 银行服务 -> 健康检查通过后，运行全量 Pytest 自动化测试。*

### 方案二：本地手动开发与调试
1. **安装环境依赖**：
```bash
pip install -r requirements.txt
```
2. **启动本地测试靶机 (FastAPI)**：
```bash
uvicorn bank_server.main:app --host 127.0.0.1 --port 8000 --reload
```
3. **新开终端运行全量测试**：
```bash
pytest            # 直接运行全量用例
# 或者
python run.py     # 运行用例并自动生成 Allure 报表
```

## 📊 测试报告与全链路监控
测试执行完毕后，控制台会输出执行结果。可通过以下命令查看携带全量通信日志的 Allure 动态报表（需提前配置 Allure 环境变量）：
```bash
allure serve ./reports/allure-report
```

