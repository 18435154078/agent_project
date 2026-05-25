# 第一阶段：构建依赖（用阿里云镜像源）
# FROM python:3.11.9 AS builder
FROM registry.aliyuncs.com/library/python:3.11.9 AS builder
# 或者用阿里云镜像：FROM registry.aliyuncs.com/library/python:3.11.9 AS builder

# 升级pip，用清华源
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 下载依赖wheel包
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第二阶段：运行阶段（同样换基础镜像）
FROM python:3.11.9
# 或者用阿里云镜像：FROM registry.aliyuncs.com/library/python:3.11.9

# 创建非root用户
RUN useradd -m appuser

WORKDIR /app

# 复制wheel包
COPY --from=builder /wheels /wheels

# 安装依赖
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# 复制代码
COPY . .

# 创建目录并授权
RUN mkdir -p logs vector_db && chown -R appuser:appuser /app

# 切换用户
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]