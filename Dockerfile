# 第一阶段：构建依赖（只做依赖安装和打包）
FROM python:3.11.9 as builder

# 升级pip
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# 先复制依赖文件，利用缓存
COPY requirements.txt .

# 下载所有依赖的wheel包到/wheels目录
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 第二阶段：运行阶段（只复制必要文件）
FROM python:3.11.9

# 创建非root用户，提高安全性
RUN useradd -m appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制wheel包
COPY --from=builder /wheels /wheels

# 安装依赖（只从本地wheel包安装，不联网）
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* && rm -rf /wheels

# 复制项目代码
COPY . .

# 创建日志和向量库目录，并修改权限给appuser
RUN mkdir -p logs vector_db && chown -R appuser:appuser /app

# 切换到非root用户运行
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令，设置2个worker进程
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]