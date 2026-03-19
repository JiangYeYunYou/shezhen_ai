# Shezhen AI Backend

深圳AI后端服务

## 技术栈

- Python 3.13.3
- FastAPI
- SQLAlchemy (异步)
- SQLite (aiosqlite)
- JWT认证

## 快速开始

```bash
# 安装依赖
uv sync

# 运行服务
uv run uvicorn app.main:app --reload
```

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
