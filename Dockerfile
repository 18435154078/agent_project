# 第一阶段：构建依赖（使用阿里云镜像，不会超时）
FROM registry.aliyuncs.com/library/python:3.11.9 AS builder

# 升级pip，使用清华源加速
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 下载所有依赖的wheel包
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第二阶段：运行阶段（同样使用阿里云镜像）
FROM registry.aliyuncs.com/library/python:3.11.9

# 创建非root用户，提高安全性
RUN useradd -m appuser

WORKDIR /app

# 从构建阶段复制wheel包
COPY --from=builder /wheels /wheels

# 安装依赖，仅从本地wheel包安装
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# 复制项目代码
COPY . .

# 创建日志和向量库目录，并授权给appuser
RUN mkdir -p logs vector_db && chown -R appuser:appuser /app

# 切换到appuser用户运行
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]