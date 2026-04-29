# Shezhen AI 后端 — 服务器部署指南

## 前置要求

| 组件 | 最低版本 | 说明 |
|------|---------|------|
| Docker | 24.0+ | 容器运行时 |
| Docker Compose | 2.20+ | 编排工具（V2 插件） |
| 服务器 OS | - | Ubuntu 22.04+ / CentOS 8+ / Debian 12+ |
| 内存 | 2GB | 后端 512MB + MySQL 512MB + 系统开销 |
| 磁盘 | 20GB | 镜像 + 日志 + 数据增长预留 |

---

## 快速部署（推荐）

### 1. 克隆代码到服务器

```bash
git clone <你的仓库地址> /opt/shezhen-backend
cd /opt/shezhen-backend
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env  # 修改 JWT_SECRET_KEY、AI_API_KEY 等敏感配置
```

### 3. 构建并启动

```bash
# 首次启动（后台运行）
docker compose up -d --build

# 查看启动日志（注意：启动时会先执行 Alembic 迁移，再启动应用）
docker compose logs -f backend

# 确认服务健康
curl -s http://localhost:8000/health
```

### 4. 数据库迁移（自动处理）

**容器启动时会自动执行 `alembic upgrade head`**，无需手动干预。

- 首次启动：自动创建 `user` 和 `diagnosis` 表
- 后续更新：如果代码中新增了模型/字段，重新部署时会自动应用迁移

如需手动查看迁移状态：

```bash
docker compose exec backend uv run alembic current
docker compose exec backend uv run alembic history
```

---

## 常用运维命令

| 操作 | 命令 |
|------|------|
| 查看日志 | `docker compose logs -f backend` |
| 重启服务 | `docker compose restart backend` |
| 停止服务 | `docker compose down` |
| 查看资源 | `docker stats` |
| 进入容器 | `docker compose exec backend bash` |
| 清理旧镜像 | `docker image prune -f` |

---

## 安全建议

1. **JWT 密钥**：生产环境务必修改 `JWT_SECRET_KEY`，建议生成随机字符串：
   ```bash
   openssl rand -hex 32
   ```

2. **数据库密码**：修改 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_PASSWORD`

3. **防火墙**：仅开放必要端口（80/443 给 Nginx，8000 仅限内网或本机）

4. **HTTPS**：建议在前端使用 Nginx / Traefik 做反向代理和 SSL 终止

---

## 表结构一致性说明

Docker 容器与本地环境的表结构通过 **Alembic 迁移脚本** 保证一致：

| 对比项 | 本地开发 | Docker 生产 |
|--------|---------|------------|
| 建表方式 | `init_db()` → SQLAlchemy `create_all()` | `docker-entrypoint.sh` → `alembic upgrade head` |
| 表结构来源 | `app/models/user.py` + `app/models/diagnosis.py` | `migrations/versions/000000000001_initial_migration.py` |
| 结果 | 两张表（user、diagnosis） | **完全相同的两张表** |

**迁移脚本已对齐的字段清单**：

- `user` 表：`id` (PK)、`username` (唯一索引)、`password`、`salt`、`created_at`、`updated_at`
- `diagnosis` 表：`id` (PK)、`user_id` (FK+索引)、`tongue_analysis`、`syndromes`、`constitution`、`health_score` (默认 `{}`)、`advice` (默认 `''`)、`tongue_surface_image` (LONGBLOB)、`tongue_bottom_image` (LONGBLOB)、`created_at` (索引)

所有字段类型、约束、默认值、索引均与 SQLAlchemy 模型一致，字符集统一为 `utf8mb4`。

---

## 故障排查

| 现象 | 可能原因 | 排查方法 |
|------|---------|---------|
| 容器启动后立刻退出 | 数据库连接失败 | `docker compose logs backend` |
| 健康检查失败 | 应用启动慢或崩溃 | `docker compose ps` 查看状态 |
| 中文乱码 | 文件编码问题 | 确认 `doc/changshi.txt` 为 UTF-8 |
| 图片上传失败 | 内存不足 | 调高 `deploy.resources.limits.memory` |
| 迁移报错 "table already exists" | 本地 `create_all()` 与 Alembic 冲突 | 清空 MySQL 数据卷后重新启动 |
