# 图片发送功能使用说明

## API 端点

`POST /send`

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `target` | string | 是 | 目标聊天（用户名或群组名） |
| `text` | string | 是 | 消息文本内容 |
| `image_url` | string | 否 | 图片 URL（支持 http/https） |
| `image_path` | string | 否 | 本地图片路径 |

**注意**：
- 如果同时提供 `image_url` 和 `image_path`，优先使用 `image_url`
- Telethon 会自动下载 URL 图片并发送
- 支持的图片格式：jpg, png, gif, webp 等

## 使用示例

### 1. 发送纯文本消息

```bash
curl -X POST http://localhost:8101/send \
  -H "Content-Type: application/json" \
  -d '{
    "target": "your_target_or_chat_id",
    "text": "这是一条测试消息"
  }'
```

### 2. 发送带图片 URL 的消息

```bash
curl -X POST http://localhost:8101/send \
  -H "Content-Type: application/json" \
  -d '{
    "target": "your_target_or_chat_id",
    "text": "查看这张图片",
    "image_url": "https://example.com/image.jpg"
  }'
```

### 3. 发送本地图片

```bash
curl -X POST http://localhost:8101/send \
  -H "Content-Type: application/json" \
  -d '{
    "target": "your_target_or_chat_id",
    "text": "本地图片测试",
    "image_path": "/path/to/local/image.png"
  }'
```

### 4. Python 调用示例

```python
import requests

# 发送带图片的消息
response = requests.post(
    "http://localhost:8101/send",
    json={
        "target": "your_target_or_chat_id",
        "text": "Python 发送的图片消息",
        "image_url": "https://picsum.photos/400/300"
    }
)

print(response.json())
# 输出: {"message_id": 12345, "target": "your_target_or_chat_id"}
```

## 响应格式

成功响应：
```json
{
  "message_id": 12345,
  "target": "your_target_or_chat_id"
}
```

错误响应：
```json
{
  "detail": "Chat not found: 'invalid_target'"
}
```

## 测试脚本

项目提供了两个测试脚本：

1. **send_test.py** - 原有的纯文本发送测试
2. **send_image_test.py** - 新增的图片发送测试（包含 3 个测试用例）

运行测试：
```bash
python send_image_test.py
```

## 技术实现

- 使用 Telethon 的 `send_message(entity, text, file=...)` 方法
- `file` 参数支持：
  - URL 字符串（自动下载）
  - 本地文件路径
  - 文件对象
  - bytes 数据
- 图片会自动压缩并上传到 Telegram 服务器
