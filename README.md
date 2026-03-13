# 🚀 企业级 API 自动化测试框架 (API_AutoTest)

本项目是一个基于 `Python + Pytest + Requests + Allure` 打造的现代化、高可用接口自动化测试框架。

## 🛠️ 核心技术栈 (Tech Stack)
* **测试调度框架**：`Pytest` (利用 `yield` 夹具实现极度安全的后置数据清理)
* **接口请求引擎**：`Requests`
* **数据驱动模块**：`PyYAML` (彻底实现代码与测试数据的解耦)
* **数据库操作库**：`PyMySQL` (深入底层数据库进行快照级别的物理断言)
* **测试报告引擎**：`Allure-Pytest`

## 📂 项目目录结构 (Project Structure)
```text
API_AutoTest/
├── api/                    # 📄 [POM分层] API 对象封装层 (如 order_api.py)
├── test_cases/             # 🧪 [测试用例] 核心测试脚本库 (涵盖业务流与异常边界测试)
├── data/                   # 📦 [测试数据] YAML 数据驱动文件 (test_data.yaml)
├── utils/                  # 🔧 [公共工具] 核心工具类封装 (db_util, yaml_util, logger)
├── conftest.py             # 🛡️ [全局夹具] Pytest 全局配置 (处理登录状态维持与数据回收)
├── pytest.ini              # 📜 [框架配置] Pytest 全局运行参数配置文件
├── run.py                  # 🚀 [执行入口] 测试任务调度与 Allure 报告生成总入口
├── requirements.txt        # 📃 [环境依赖] 项目核心依赖包版本控制清单
├── logs/                   # 📝 [运行日志] 自动化执行日志按天归档目录
└── reports/                # 📊 [测试报告] Allure 静态 HTML 报告输出目录
```
## 🧠 框架核心架构思想 (Core Architecture)

1. **API Object Model (POM 降维维护)**：将接口定义与测试用例剥离，实现解耦。
2. **数据与安全双驱动 (DDT & Security)**：利用 YAML 统一管理测试数据，不仅测业务逻辑，还可通过配置恶意 Payload（如 `1=1`、`<script>`）对接口进行自动化安全扫描。
3. **快照物理断言 (Snapshot Assert)**：拒绝硬编码，动作前后对数据库拍快照对比，精准拦截 P0 级业务资损漏洞。
4. **覆盖率可视监控 (Code Coverage)**：集成 `pytest-cov`，确保核心接口代码的分支覆盖率达到 90% 以上。

## ⚙️ 本地极速部署与运行 (Quick Start)

### 1. 启动底层数据库 (Docker 方式)

确保本地已安装 Docker，拉取并启动独立的测试数据库容器：

```bash
docker run -d --name test_db -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=api_test
```