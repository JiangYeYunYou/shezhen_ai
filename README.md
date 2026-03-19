# Shezhen Backend

舌诊后端服务

## 技术栈

- Python 3.13.3
- FastAPI
- SQLAlchemy (异步)
- MySQL (aiomysql)
- JWT认证

## 快速开始

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置MySQL连接信息

# 运行服务
uv run uvicorn app.main:app --reload
```

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
