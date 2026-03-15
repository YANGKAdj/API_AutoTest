FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖（给 PyMySQL / MySQL 客户端等用）
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖并安装
COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制项目代码
COPY . .

# 默认只进入 shell，由 Jenkins 或 docker-compose 决定执行命令
CMD ["bash"]

