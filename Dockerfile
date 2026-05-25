# 第一阶段：构建阶段，只用来安装依赖
FROM python:3.10-slim AS builder

# 设置工作目录
WORKDIR /app

# 先复制requirements.txt，利用Docker缓存机制，只有依赖变化时才重新安装
COPY requirements.txt .

# 安装所有依赖，使用清华源加速
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第二阶段：运行阶段，最终的镜像
FROM python:3.10-slim

# 创建非root用户，提高安全性
RUN useradd -m appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已经安装好的依赖
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# 复制项目代码
COPY . .

# 创建日志和向量库目录
RUN mkdir -p logs vector_db

# 切换到非root用户运行
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令，设置2个worker进程，适合2核服务器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]