#!/bin/bash
# 停止脚本 - 格雷厄姆价值投资分析系统

echo "停止格雷厄姆价值投资分析系统..."

# 读取PID
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "后端服务已停止 (PID: $BACKEND_PID)"
    rm .backend.pid
else
    echo "未找到后端PID文件"
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "前端服务已停止 (PID: $FRONTEND_PID)"
    rm .frontend.pid
else
    echo "未找到前端PID文件"
fi

# 额外清理可能残留的进程
pkill -f "python run.py" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "所有服务已停止"
