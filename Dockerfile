# 使用官方Python基础镜像
FROM crpi-3zr415nakxg4qr8l.cn-hangzhou.personal.cr.aliyuncs.com/7788soft/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装Poetry
RUN pip install   poetry

# 打印Poetry和Python版本
RUN poetry --version && python --version

# 复制依赖文件
COPY pyproject.toml poetry.lock  /app/

# 删除开发依赖项
#RUN poetry remove aicode78


# 设置虚拟环境路径
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

# 安装项目依赖，只安装生产环境的包，并删除Poetry缓存
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-root \
    && rm -rf $POETRY_CACHE_DIR

# 复制项目的所有文件到工作目录.
COPY src /app/src
RUN poetry install --without dev
# 打印当前目录内容
RUN ls -l /app && ls -l /app/src 

# 设置环境变量
ENV APP_ENV=development
# ENV logstash_host=192.168.31.181
# ENV logstash_port=30003

# 暴露应用程序端口（如果需要）
# EXPOSE 8000

# 运行应用程序
CMD ["poetry", "run", "python", "src/main.py"]