## Why

当前项目是一个单文件 `main.py`，将 Telegram 频道监听、消息转发、FastAPI 接收全部耦合在一起。缺乏容器化部署能力、结构化日志、以及可扩展的消息分发机制。需要将项目模块化，支持 Docker 部署，并引入 pub/sub 架构让用户可以通过添加 `.py` 文件来自定义消息转发目标。

## What Changes

- 新增 `docker/` 目录，包含 `Dockerfile` 和 `docker-compose.yml`，使用 8101 端口对外服务
- 新增结构化日志模块，统一项目日志输出格式，支持文件和控制台输出
- 新增 pub/sub 消息转发模块：
  - 提供 `Subscriber` 基类，默认具备 `send` 方法
  - 自动扫描并加载用户在指定目录下新增的 `.py` 文件作为 subscriber
  - Telegram 消息到达后通过 publisher 广播给所有已注册的 subscriber
- **BREAKING**: 重构 `main.py`，将单文件拆分为模块化结构

## Capabilities

### New Capabilities
- `docker-deployment`: Docker 容器化部署能力，包括 Dockerfile、docker-compose 配置、环境变量管理
- `logging`: 结构化日志模块，统一日志格式、级别控制、文件输出
- `pubsub-forwarding`: Pub/Sub 消息转发架构，包括 Subscriber 基类、自动发现加载、消息广播机制

### Modified Capabilities
_(无已有 spec 需要修改)_

## Impact

- **代码结构**: `main.py` 拆分为多模块包结构 (`app/`)
- **依赖**: 无新增外部依赖，使用 Python 标准库 `importlib` + `logging`
- **部署**: 新增 Docker 部署方式，需要 Docker 和 docker-compose 环境
- **API**: `/receive` 端点保持不变，但内部从直接处理改为 pub/sub 分发
- **用户扩展点**: 用户在 `subscribers/` 目录下添加 `.py` 文件即可注册新的消息转发目标
