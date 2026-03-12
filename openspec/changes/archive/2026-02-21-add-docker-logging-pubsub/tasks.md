## 1. 项目结构与配置

- [x] 1.1 创建 `app/` 包目录结构（`__init__.py`, `config.py`, `models.py`, `api.py`, `telegram.py`, `logging_config.py`）
- [x] 1.2 创建 `app/pubsub/` 子包（`__init__.py`, `publisher.py`, `subscriber.py`, `loader.py`）
- [x] 1.3 创建 `subscribers/` 目录（`__init__.py`）
- [x] 1.4 使用 pydantic-settings 实现 `app/config.py`，从环境变量/.env 读取 TG_API_ID、TG_API_HASH、CHANNELS_TO_WATCH、WEBHOOK_URL、LOG_LEVEL
- [x] 1.5 创建 `.env.example` 模板文件，列出所有配置项及说明
- [x] 1.6 更新 `pyproject.toml` 添加 `pydantic-settings` 依赖

## 2. 日志模块

- [x] 2.1 实现 `app/logging_config.py`：配置 RotatingFileHandler（10MB/5备份）+ StreamHandler，统一格式 `%(asctime)s | %(name)s | %(levelname)s | %(message)s`
- [x] 2.2 提供 `get_logger(name)` 函数，支持通过 LOG_LEVEL 环境变量控制级别
- [x] 2.3 创建 `logs/` 目录，添加 `logs/.gitkeep`

## 3. Pub/Sub 转发模块

- [x] 3.1 实现 `app/pubsub/subscriber.py`：Subscriber 抽象基类，包含 `name` 属性和 `async send(message)` 抽象方法
- [x] 3.2 实现 `app/pubsub/publisher.py`：Publisher 类，支持 register/publish，单个 subscriber 异常不影响其他
- [x] 3.3 实现 `app/pubsub/loader.py`：扫描 `subscribers/` 目录，使用 importlib 动态加载 Subscriber 子类并注册
- [x] 3.4 创建 `subscribers/example_logger.py`：示例 subscriber，将消息记录到日志
- [x] 3.5 创建 `subscribers/webhook_forwarder.py`：WebhookSubscriber，通过 httpx POST 转发到配置的 WEBHOOK_URL

## 4. 核心模块重构

- [x] 4.1 将 TGMessage 模型移至 `app/models.py`
- [x] 4.2 实现 `app/telegram.py`：Telethon 客户端逻辑，消息到达后调用 publisher.publish()
- [x] 4.3 实现 `app/api.py`：FastAPI 路由，保留 `/receive` 端点
- [x] 4.4 重写 `main.py` 入口：初始化配置、日志、pub/sub loader、启动 FastAPI + Telethon

## 5. Docker 部署

- [x] 5.1 创建 `docker/Dockerfile`：基于 python:3.11-slim，安装依赖，暴露 8101 端口
- [x] 5.2 创建 `docker-compose.yml`：配置服务、端口映射 8101、volume 挂载（subscribers/、logs/、session 文件）、env_file
- [x] 5.3 更新 `.gitignore`：添加 .env、logs/*.log、*.session 等规则
