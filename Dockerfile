FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖（PyMySQL 需要）
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 先安装依赖（利用 Docker 层缓存，依赖不变就不重装）
COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 再复制项目代码
COPY . .

# 默认启动银行服务；测试容器由 docker-compose command 覆盖此命令
CMD ["uvicorn", "bank_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
