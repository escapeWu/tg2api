## Requirements

### Requirement: Subscriber 基类
系统 SHALL 提供 `Subscriber` 抽象基类，包含 `send(message: TGMessage)` 异步方法作为消息处理接口。

#### Scenario: 自定义 subscriber 继承基类
- **WHEN** 用户创建新的 subscriber 类继承 `Subscriber`
- **THEN** 用户 MUST 实现 `async send(message: TGMessage)` 方法

#### Scenario: Subscriber 提供名称标识
- **WHEN** subscriber 实例化
- **THEN** 每个 subscriber 实例具有 `name` 属性用于日志标识

### Requirement: Publisher 消息广播
系统 SHALL 提供 `Publisher` 类，负责维护 subscriber 注册列表并广播消息。

#### Scenario: 注册 subscriber
- **WHEN** 调用 `publisher.register(subscriber)` 传入一个 Subscriber 实例
- **THEN** 该 subscriber 被添加到广播列表

#### Scenario: 广播消息到所有 subscriber
- **WHEN** 调用 `publisher.publish(message)` 传入 TGMessage
- **THEN** 所有已注册的 subscriber 的 `send` 方法被调用

#### Scenario: 单个 subscriber 异常不影响其他
- **WHEN** 某个 subscriber 的 `send` 方法抛出异常
- **THEN** 系统记录错误日志，继续向其他 subscriber 发送消息

### Requirement: Subscriber 自动发现加载
系统 SHALL 在启动时自动扫描 `subscribers/` 目录，加载所有继承 `Subscriber` 基类的类。

#### Scenario: 自动加载 subscriber 文件
- **WHEN** `subscribers/` 目录下存在 `my_forwarder.py`，其中定义了继承 `Subscriber` 的类
- **THEN** 系统自动发现、实例化并注册该 subscriber

#### Scenario: 忽略非 subscriber 文件
- **WHEN** `subscribers/` 目录下存在不包含 `Subscriber` 子类的 `.py` 文件
- **THEN** 系统跳过该文件，记录 DEBUG 日志

#### Scenario: subscribers 目录为空
- **WHEN** `subscribers/` 目录不包含任何有效 subscriber
- **THEN** 系统正常启动，记录 WARNING 日志提示无 subscriber 注册

### Requirement: Telegram 消息通过 pub/sub 分发
系统 SHALL 将 Telethon 收到的频道消息通过 Publisher 广播给所有 subscriber，替代原有的直接 httpx 转发。

#### Scenario: 新消息触发广播
- **WHEN** Telethon 监听到新的频道消息
- **THEN** 消息被封装为 TGMessage 并通过 Publisher.publish() 广播

### Requirement: 示例 Subscriber 实现
系统 SHALL 在 `subscribers/` 目录提供 `example_logger.py` 示例，展示如何编写自定义 subscriber。

#### Scenario: 示例 subscriber 记录消息
- **WHEN** 示例 subscriber 收到消息
- **THEN** 将消息内容记录到日志

### Requirement: Webhook 转发 Subscriber
系统 SHALL 提供一个内置的 `WebhookSubscriber`，实现向指定 URL 的 HTTP POST 转发功能，保持与原有 `/receive` 端点的兼容。

#### Scenario: 转发消息到 webhook URL
- **WHEN** WebhookSubscriber 收到消息
- **THEN** 通过 httpx 向配置的 webhook URL 发送 POST 请求

#### Scenario: webhook 转发失败
- **WHEN** 目标 URL 不可达或返回非 200 状态码
- **THEN** 记录错误日志，不影响其他 subscriber
