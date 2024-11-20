#!/bin/sh

# 设置Poetry路径
export PATH="$HOME/.local/bin:$PATH"

# 确保Poetry已安装
if ! command -v poetry &> /dev/null
then
    echo "Poetry could not be found, please install it."
    exit 1
fi

# 递增版本号
poetry run poetry version patch

# 获取新版本号
new_version=$(poetry run poetry version -s)

# 检查版本号是否为空
if [ -z "$new_version" ]; then
    echo "Failed to get new version number."
    exit 1
fi

# 私有镜像仓库地址
REPO_URL="crpi-3zr415nakxg4qr8l.cn-hangzhou.personal.cr.aliyuncs.com/7788soft"

# 镜像名称
IMAGE_NAME="trade78"

# 构建Docker镜像
docker build -f Dockerfile -t $REPO_URL/$IMAGE_NAME:$new_version .

# 推送Docker镜像到指定的镜像仓库
docker push $REPO_URL/$IMAGE_NAME:$new_version

# 更新latest标签
docker tag $REPO_URL/$IMAGE_NAME:$new_version $REPO_URL/$IMAGE_NAME:latest
docker push $REPO_URL/$IMAGE_NAME:latest

echo "Docker镜像已推送到仓库，版本号: $new_version"