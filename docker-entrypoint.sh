#!/bin/sh

# =============================================================================
# Shezhen AI Backend — Docker Entrypoint
# =============================================================================
# 启动流程：
#   1. 运行 Alembic 数据库迁移（处理表已存在的情况）
#   2. 启动 Uvicorn 应用服务
# =============================================================================

echo "========================================"
echo "  Shezhen AI Backend — 启动中"
echo "========================================"

# 运行数据库迁移
echo "[1/2] 正在执行数据库迁移..."

# 尝试执行迁移
MIGRATION_OUTPUT=$(uv run alembic upgrade head 2>&1)
MIGRATION_EXIT_CODE=$?

if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
    echo "[1/2] 数据库迁移完成 ✅"
else
    # 检查是否是表已存在的错误
    if echo "$MIGRATION_OUTPUT" | grep -q "already exists"; then
        echo "[1/2] 检测到数据库表已存在，标记 Alembic 版本..."
        uv run alembic stamp head
        echo "[1/2] 数据库初始化完成 ✅"
    else
        echo "[1/2] 数据库迁移失败 ❌"
        echo "$MIGRATION_OUTPUT"
        exit 1
    fi
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
