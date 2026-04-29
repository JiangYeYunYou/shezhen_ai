#!/bin/sh
set -e

# =============================================================================
# Shezhen AI Backend — Docker Entrypoint
# =============================================================================
# 启动流程：
#   1. 运行 Alembic 数据库迁移（确保表结构与代码模型一致）
#   2. 启动 Uvicorn 应用服务
# =============================================================================

echo "========================================"
echo "  Shezhen AI Backend — 启动中"
echo "========================================"

# 运行数据库迁移（若表已存在则跳过，若不存在则创建）
echo "[1/2] 正在执行数据库迁移..."
uv run alembic upgrade head
if [ $? -eq 0 ]; then
    echo "[1/2] 数据库迁移完成 ✅"
else
    echo "[1/2] 数据库迁移失败 ❌"
    exit 1
fi

# 启动应用
echo "[2/2] 正在启动应用服务..."
echo "========================================"

# 使用 exec 使 uvicorn 接管 PID 1，确保信号正确处理
exec uv run --no-sync uvicorn app.main:app \
    --host "${UVICORN_HOST:-0.0.0.0}" \
    --port "${UVICORN_PORT:-8000}" \
    --workers "${UVICORN_WORKERS:-4}" \
    --proxy-headers \
    --forwarded-allow-ips "*"
