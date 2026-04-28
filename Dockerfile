# syntax=docker/dockerfile:1

# =============================================================================
# 基础镜像选择
# =============================================================================
# 使用官方 Python 3.13 Slim 镜像（基于 Debian Bookworm）
# 优点：体积较小、安全补丁及时、Python 版本与项目要求一致（>=3.11）
FROM python:3.13-slim-bookworm AS builder

# =============================================================================
# 构建阶段：安装依赖
# =============================================================================
WORKDIR /app

# 安装 uv —— 项目使用的现代 Python 包管理器（固定版本保证可复现）
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

# 安装系统级编译依赖（ Pillow 等含 C 扩展的包构建时需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 先仅复制依赖锁定文件 → 利用 Docker 构建缓存，代码变更不触发重新安装依赖
COPY pyproject.toml uv.lock ./

# 使用 uv 同步依赖（--frozen 确保严格按 uv.lock 安装，--no-dev 排除开发包）
RUN uv sync --frozen --no-dev

# =============================================================================
# 生产阶段：精简运行镜像
# =============================================================================
FROM python:3.13-slim-bookworm AS production

WORKDIR /app

# 安装 uv（生产阶段仍需 uv 来运行应用）
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

# 安装运行时系统依赖 + curl（健康检查用）
# libjpeg62-turbo / libpng16-16：Pillow 运行时库
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# 环境变量配置
# =============================================================================
# PYTHONDONTWRITEBYTECODE: 禁止生成 .pyc 文件，减少容器体积
# PYTHONUNBUFFERED: 确保 Python 输出实时刷新到日志
# PYTHONPATH: 确保模块导入路径正确
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_NO_CACHE=1 \
    APP_ENV=production

# =============================================================================
# 安全：非 root 用户运行
# =============================================================================
RUN groupadd -r shezhen && useradd -r -g shezhen shezhen

# =============================================================================
# 复制应用代码与数据文件
# =============================================================================
# 从构建阶段复制已安装的虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用源代码及运行时必需的数据文件
COPY app/ ./app/
COPY doc/ ./doc/
COPY prompts/ ./prompts/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# 设置文件权限
RUN chown -R shezhen:shezhen /app

# 切换到非 root 用户
USER shezhen

# =============================================================================
# 端口暴露
# =============================================================================
EXPOSE 8000

# =============================================================================
# 健康检查机制
# =============================================================================
# interval:  每 30 秒检查一次
# timeout:   单次检查最多等待 5 秒
# start-period: 容器启动后前 15 秒为缓冲期（应用启动需要时间）
# retries:   连续失败 3 次后才判定为不健康
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# =============================================================================
# 启动命令
# =============================================================================
# 生产环境使用 4 个 Uvicorn worker 进程处理并发请求
# 如需在 K8s 中横向扩展，建议改为 --workers 1，通过副本数控制并发
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4", \
     "--proxy-headers", "--forwarded-allow-ips", "*"]
