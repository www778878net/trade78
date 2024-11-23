# 基于最新的镜像
FROM crpi-3zr415nakxg4qr8l.cn-hangzhou.personal.cr.aliyuncs.com/7788soft/trade78:latest

# 设置工作目录
WORKDIR /app

# 复制项目的所有文件到工作目录
COPY src /app/src

# 设置环境变量
ENV APP_ENV=production


# 暴露应用程序端口（如果需要）
# EXPOSE 8000

# 运行应用程序
CMD ["poetry", "run", "python", "src/main.py"]