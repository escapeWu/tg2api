## Context

当前项目 `tg2fastapi` 是一个 Telegram 频道消息监听+转发工具，所有逻辑集中在单个 `main.py` 中（约 85 行）。使用 Telethon 监听频道消息，通过 httpx 转发到本地 FastAPI `/receive` 端点。项目缺乏：
- 容器化部署（每次需手动配置 Python 环境）
- 结构化日志（当前仅基础 `logging.basicConfig`）
- 可扩展的消息分发机制（当前硬编码转发到单一 webhook）

技术栈：Python 3.11+, FastAPI, Telethon, httpx, uvicorn

## Goals / Non-Goals

**Goals:**
- 将单文件拆分为模块化包结构，便于维护和扩展
- 提供 Docker + docker-compose 一键部署，端口 8101
- 实现结构化日志系统，支持控制台 + 文件输出
- 实现 pub/sub 消息转发架构，用户通过添加 `.py` 文件即可注册新的 subscriber
- 保持 `/receive` API 端点兼容

**Non-Goals:**
- 不引入消息队列中间件（Redis/RabbitMQ），使用进程内 pub/sub
- 不实现消息持久化或重试队列
- 不修改 Telethon 认证流程
- 不添加 Web UI 管理界面

## Decisions

### 1. 项目结构：采用 `app/` 包结构

将 `main.py` 拆分为：
```
app/
  __init__.py
  config.py          # 配置管理（环境变量）
  logging_config.py  # 日志配置
  models.py          # Pydantic 模型
  api.py             # FastAPI 路由
  telegram.py        # Telethon 客户端逻辑
  pubsub/
    __init__.py
    publisher.py     # Publisher 消息广播
    subscriber.py    # Subscriber 基类
    loader.py        # 自动发现加载 subscriber
subscribers/         # 用户自定义 subscriber 目录
  __init__.py
  example_logger.py  # 示例 subscriber
main.py              # 入口文件
```

**理由**: 包结构清晰分离关注点，`subscribers/` 作为用户扩展目录独立于核心代码。

### 2. Pub/Sub：进程内同步广播

- `Subscriber` 基类提供 `send(message: TGMessage)` 抽象方法
- `Publisher` 维护 subscriber 列表，消息到达时遍历调用各 subscriber 的 `send`
- 使用 `asyncio` 支持异步 subscriber

**理由**: 项目规模不需要外部消息队列，进程内实现简单可靠。

**替代方案**: 使用 Redis pub/sub — 过度复杂，引入额外依赖和运维负担。

### 3. Subscriber 自动发现：`importlib` 动态加载

- 启动时扫描 `subscribers/` 目录下所有 `.py` 文件
- 使用 `importlib.import_module` 动态加载
- 查找继承 `Subscriber` 基类的类并自动实例化注册
- 支持热加载（可选，通过 API 触发重新扫描）

**理由**: 用户只需要放一个 `.py` 文件，零配置即可扩展。

### 4. 日志：标准库 logging + 文件轮转

- 使用 `logging.handlers.RotatingFileHandler` 输出到 `logs/` 目录
- 同时保留控制台输出
- 日志格式：`%(asctime)s | %(name)s | %(levelname)s | %(message)s`
- 通过环境变量控制日志级别

**理由**: 无需额外依赖，标准库足够满足需求。

### 5. Docker：多阶段构建 + docker-compose

- `Dockerfile` 使用 Python 3.11 slim 镜像
- `docker-compose.yml` 映射 8101 端口，挂载 `subscribers/` 和 `logs/` 目录
- 通过 `.env` 文件管理 API_ID、API_HASH 等敏感配置
- 挂载 session 文件以持久化 Telegram 登录状态

**理由**: docker-compose 简化部署，volume 挂载让用户可以在容器外编辑 subscriber。

### 6. 配置管理：环境变量 + pydantic-settings

- 使用 `pydantic-settings` 的 `BaseSettings` 从环境变量/`.env` 文件读取配置
- 不再硬编码 API_ID、API_HASH 等敏感信息

**理由**: 生产部署标准实践，支持 Docker 环境变量注入。

## Risks / Trade-offs

- **[进程内 pub/sub 不支持跨进程]** → 当前规模足够，未来如需可替换为 Redis pub/sub，接口保持不变
- **[动态加载 subscriber 安全风险]** → `subscribers/` 目录应由管理员控制，不对外暴露
- **[Telegram session 文件持久化]** → Docker volume 挂载确保容器重启不丢失登录状态
- **[单文件拆分为 BREAKING change]** → 项目尚未正式发布，可接受
