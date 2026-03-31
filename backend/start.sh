#!/bin/bash

# IP Agent Backend 启动脚本

echo "🚀 启动 IP Agent 后端服务..."

# 检查 Python 版本
python3 --version

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 安装 Playwright 浏览器
echo "🌐 安装 Playwright 浏览器..."
playwright install chromium

# 启动服务
echo "🔥 启动后端服务..."
echo "📍 API 文档：http://localhost:8002/docs"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
