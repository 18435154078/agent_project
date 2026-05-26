# 第一阶段：用你本地的 Python 构建依赖（不依赖任何外部镜像）
FROM python:3.13 AS builder

# 升级 pip，用清华源加速
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app
COPY requirements.txt .

# 下载所有依赖的 wheel 包（只下载，不安装）
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第二阶段：用超小的 alpine 镜像运行（几乎所有网络都能拉到）
FROM alpine:latest

# 安装 Python 和 pip（alpine 自带国内源，必成）
RUN apk add --no-cache python3 py3-pip

# 环境变量
ENV env=pro

# 创建非 root 用户，提升安全性
RUN adduser -D appuser

WORKDIR /app

# 从构建阶段复制 wheel 包
COPY --from=builder /wheels /wheels

# 本地安装依赖（完全不上网）
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# 复制项目代码
COPY . .

# 创建日志和向量库目录，并授权给 appuser
RUN mkdir -p logs vector_db && chown -R appuser:appuser /app

# 切换到 appuser 用户运行
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]