#!/bin/bash
# 启动脚本 - 格雷厄姆价值投资分析系统

echo "========================================"
echo "格雷厄姆价值投资分析系统 启动中..."
echo "========================================"

# 检查Python依赖
echo "检查Python环境..."
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.9+"
    exit 1
fi

# 启动后端服务
echo "启动后端服务..."
cd "$(dirname "$0")"
python run.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端服务
echo "启动前端服务..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务已启动 (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "系统启动成功！"
echo "========================================"
echo "后端API: http://localhost:5000"
echo "前端界面: http://localhost:3000"
echo "========================================"
echo ""
echo "提示："
echo "- 查看后端日志: tail -f logs/backend.log"
echo "- 查看前端日志: tail -f logs/frontend.log"
echo "- 停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "PID已保存到 .backend.pid 和 .frontend.pid"
echo "可以使用 ./stop.sh 停止所有服务"
