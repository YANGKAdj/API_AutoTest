# 🚀 企业级 API 自动化测试框架 (API_AutoTest)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pytest](https://img.shields.io/badge/Pytest-8.0+-green.svg)
![Allure](https://img.shields.io/badge/Allure_Report-passed-success.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
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
├── api/                    # [POM分层] API 对象封装层 (如 order_api.py)
├── test_cases/             # [测试用例] 核心测试脚本库 (涵盖业务流与异常边界测试)
├── data/                   # [测试数据] YAML 数据驱动文件 (test_data.yaml)
├── utils/                  # [公共工具] 核心工具类封装 (db_util, yaml_util, logger)
├── conftest.py             # [全局夹具] Pytest 全局配置 (处理登录状态维持与数据回收)
├── pytest.ini              # [框架配置] Pytest 全局运行参数配置文件
├── run.py                  # [执行入口] 测试任务调度与 Allure 报告生成总入口
├── requirements.txt        # [环境依赖] 项目核心依赖包版本控制清单
├── logs/                   # [运行日志] 自动化执行日志按天归档目录
└── reports/                # [测试报告] Allure 静态 HTML 报告输出目录
```
## 🧠 框架核心架构思想 (Core Architecture)

1. **API Object Model (POM 降维维护)**：将接口定义与测试用例剥离，实现解耦。
2. **数据与安全双驱动 (DDT & Security)**：利用 YAML 统一管理测试数据，不仅测业务逻辑，还可通过配置恶意 Payload（如 `1=1`、`<script>`）对接口进行自动化安全扫描。
3. **快照物理断言 (Snapshot Assert)**：拒绝硬编码，动作前后对数据库拍快照对比，精准拦截 P0 级业务资损漏洞。
4. **覆盖率可视监控 (Code Coverage)**：集成 `pytest-cov`，确保核心接口代码的分支覆盖率达到 90% 以上。

## ⚙️ 本地极速部署与运行 (Quick Start)

### 1. 安装依赖 (Install Dependencies)

确保本地已安装 Python 3.8+ 环境。在项目根目录下打开终端，执行以下命令极速安装框架所需的所有第三方库：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 2. 启动本地被测靶机 (Start Mock Server)

本框架自带基于 Flask 开发的本地测试靶机，完美模拟电商核心业务链路。在运行自动化测试前，请先新开一个终端启动靶机服务：

```bash
python flask/mock_server.py
```
注意：靶机服务默认运行在 http://127.0.0.1:5000，请保持该终端窗口开启
### 3.一键运行 run.py
靶机就绪后，在项目根目录运行统一启动脚本。框架将自动利用 Pytest 收集并执行 test_cases 目录下的所有用例，并同步生成覆盖率统计：
```bash
python run.py
```
### 4.查看Allure报告
测试执行完毕后，控制台会输出代码分支覆盖率（Coverage）。要查看详细的 Allure 动态测试报告，请在终端执行：

```Bash
allure serve ./allure-results
```

## 🐳 Jenkins + Docker + CentOS7 部署步骤

下面是将本项目部署到 **CentOS7 -> Docker -> Jenkins** 的完整步骤示例。

### 1. 服务器上安装 Docker

```bash
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 使用 Docker 运行 Jenkins

```bash
sudo mkdir -p /data/jenkins_home
sudo chown -R 1000:1000 /data/jenkins_home

docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v /data/jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

浏览器访问 `http://<服务器IP>:8080`，按向导完成 Jenkins 初始化。

### 3. 项目内 Docker 化说明

- `Dockerfile`：定义测试运行环境（Python + 依赖）。
- `docker-compose.yml`：同时拉起 `mall-mysql`（MySQL 测试库）和 `api-tests`（mock_server + pytest）。
- `utils/db_util.py` 与 `flask/mock_server.py` 中的 `host` 已配置为 `mall-mysql`，与 `docker-compose.yml` 中服务名一致。

在服务器上（或本地）手动验证时，可以在项目根目录执行：

```bash
docker-compose up --build
```

会自动：
- 启动 MySQL：`mall-mysql`
- 启动 Flask 靶机：`python flask/mock_server.py`
- 执行所有 Pytest 用例：`pytest -q`

### 4. Jenkins Pipeline 配置

本项目根目录内提供了一个示例 `Jenkinsfile`，典型的 Jenkins 流水线包含：

1. 从 Git 仓库拉取 `API_AutoTest` 源码；
2. 使用项目根目录的 `Dockerfile` 构建镜像 `api-autotest:latest`；
3. 执行 `docker-compose up --abort-on-container-exit --build` 运行测试；
4. 测试完成后执行 `docker-compose down` 清理环境。

在 Jenkins 中新建流水线任务时：

- 源码管理选择 Git，填入本项目仓库地址；
- Pipeline 定义选择「从 SCM 中的 `Jenkinsfile`」；
- 保存后点击「立即构建」即可触发一整套 Docker 化的接口测试流程。

