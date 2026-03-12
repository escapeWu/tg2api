## ADDED Requirements

### Requirement: Docker 镜像构建
系统 SHALL 提供 `docker/Dockerfile`，基于 Python 3.11 slim 镜像构建应用容器。

#### Scenario: 成功构建 Docker 镜像
- **WHEN** 用户在项目根目录执行 `docker build -f docker/Dockerfile -t tg2fastapi .`
- **THEN** 系统成功构建包含所有依赖的 Docker 镜像

### Requirement: docker-compose 编排
系统 SHALL 提供 `docker-compose.yml`，配置应用服务并映射 8101 端口。

#### Scenario: docker-compose 启动服务
- **WHEN** 用户执行 `docker-compose up -d`
- **THEN** 应用容器启动，主机 8101 端口可访问 FastAPI 服务

#### Scenario: 挂载用户自定义 subscriber
- **WHEN** docker-compose 启动时
- **THEN** `subscribers/` 目录通过 volume 挂载到容器内，用户可在宿主机编辑 subscriber 文件

#### Scenario: 日志持久化
- **WHEN** 应用运行产生日志
- **THEN** `logs/` 目录通过 volume 挂载到宿主机，容器重启不丢失日志

### Requirement: 环境变量配置
系统 SHALL 通过 `.env` 文件或环境变量管理敏感配置（API_ID、API_HASH、监听频道列表）。

#### Scenario: 从 .env 文件读取配置
- **WHEN** 项目根目录存在 `.env` 文件且包含 `TG_API_ID` 和 `TG_API_HASH`
- **THEN** 应用使用 `.env` 中的值启动，不再依赖硬编码配置

#### Scenario: 提供 .env.example 模板
- **WHEN** 用户首次克隆项目
- **THEN** 项目包含 `.env.example` 文件，列出所有必需和可选的环境变量及说明

### Requirement: Session 文件持久化
系统 SHALL 通过 Docker volume 持久化 Telegram session 文件。

#### Scenario: 容器重启保持登录
- **WHEN** 容器重启后
- **THEN** Telegram 客户端使用已有 session 文件自动连接，无需重新认证
