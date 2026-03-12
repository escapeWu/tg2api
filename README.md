# tg2fastapi

一个基于 **Telethon + FastAPI** 的 Telegram 消息处理服务：
- 监听指定频道消息
- 通过发布/订阅管道分发到多个处理器（Subscriber）
- 提供 HTTP API 主动发送消息（支持图片）

## 功能概览

- 监听频道：按 `CHANNELS_TO_WATCH` 接收 Telegram 新消息
- 插件化处理：自动加载 `subscribers/*.py` 中的 `Subscriber` 子类
- 内置 API：
  - `POST /send`：发送消息到一个或多个聊天
  - `POST /inject`：将测试消息注入处理管道
  - `POST /receive`：接收消息（当前为占位返回）
- 日志：控制台 + `logs/app.log` 滚动文件日志

## 目录结构

```text
tg2fastapi/
├── app/
│   ├── api.py
│   ├── config.py
│   ├── telegram.py
│   └── pubsub/
├── subscribers/
│   ├── saveToLocal.py
│   └── news_rater.py
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── main.py
```

## 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/)（用于依赖管理和运行）
- Telegram API 凭据（`TG_API_ID`、`TG_API_HASH`）

## 本地启动

1. 复制环境变量模板

```bash
cp .env.example .env
```

2. 编辑 `.env`，至少填写：
- `TG_API_ID`
- `TG_API_HASH`

3. 安装依赖并启动

```bash
uv sync
uv run python main.py
```

服务默认监听：`http://0.0.0.0:8101`

> 首次运行 Telethon 可能要求登录验证，登录后会在项目目录生成会话文件（默认 `tg_session.session`）。

## Docker 启动

`docker-compose.yml` 使用了外部网络 `aitrade-network`，首次需要创建：

```bash
docker network create aitrade-network
```

然后：

```bash
cp .env.example .env
# 编辑 .env（至少填写 TG_API_ID / TG_API_HASH）
docker compose up -d --build
```

## 配置项说明

主要配置位于 `.env`（参考 `.env.example`）：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `TG_API_ID` | Telegram API ID（必填） | - |
| `TG_API_HASH` | Telegram API Hash（必填） | - |
| `TG_SESSION_NAME` | Telethon 会话名 | `tg_session` |
| `TG_PROXY` | Telegram 代理，如 `socks5://127.0.0.1:1080` | 空 |
| `CHANNELS_TO_WATCH` | 监听频道列表（JSON 数组字符串） | `["theblockbeats","Odaily_News","WatcherGuru"]` |
| `WEBHOOK_URL` | 预留 webhook 配置 | `http://127.0.0.1:8101/receive` |
| `SENTIMENT_API_URL` | 预留情绪 API 地址 | 空 |
| `SENTIMENT_API_KEY` | 预留情绪 API Key | 空 |
| `NEWS_RATER_URL` | news-rater 接口地址 | `http://localhost:3099/api/agents/news-rater/run` |
| `HOST` | FastAPI 监听地址 | `0.0.0.0` |
| `PORT` | FastAPI 监听端口 | `8101` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## API 使用

### 1) 发送消息：`POST /send`

请求体（单目标）：

```json
{
  "target": "your_target_or_chat_id",
  "text": "hello from tg2fastapi"
}
```

请求体（多目标）：

```json
{
  "targets": ["target_a", "target_b"],
  "text": "broadcast message"
}
```

可选图片字段：
- `image_url`：图片 URL
- `image_path`：本地路径

若两者同时提供，优先使用 `image_url`。

示例：

```bash
curl -X POST http://localhost:8101/send \
  -H "Content-Type: application/json" \
  -d '{
    "target": "your_target_or_chat_id",
    "text": "查看图片",
    "image_url": "https://example.com/image.jpg"
  }'
```

### 2) 注入测试消息：`POST /inject`

将消息直接送入发布/订阅管道（便于联调 subscriber）：

```bash
curl -X POST http://localhost:8101/inject \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "test_channel",
    "message_id": 1001,
    "text": "test message",
    "date": "2026-03-12T12:00:00+00:00",
    "media": false
  }'
```

### 3) 接收消息：`POST /receive`

当前用于兼容/占位，接收 `TGMessage` 后返回：

```json
{"status":"success"}
```

## Subscriber 开发

在 `subscribers/` 下新增 `.py` 文件并继承基类：

```python
from app.models import TGMessage
from app.pubsub.subscriber import Subscriber


class MySubscriber(Subscriber):
    async def send(self, message: TGMessage) -> None:
        # 处理逻辑
        pass
```

应用启动后会自动扫描并注册。

## 现有 Subscriber

- `SaveToLocalSubscriber`：将消息追加写入 `data/messages.csv`
- `NewsRaterSubscriber`：按防抖窗口聚合消息并调用 `NEWS_RATER_URL`

## 安全建议

- 不要提交 `.env`、`*.session`、`data/`、日志文件
- 如果 token 曾在聊天记录或终端暴露，请立即在对应平台撤销并重新生成
