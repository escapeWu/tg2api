## Requirements

### Requirement: 结构化日志格式
系统 SHALL 使用统一的日志格式 `%(asctime)s | %(name)s | %(levelname)s | %(message)s` 输出所有日志。

#### Scenario: 日志输出包含模块名
- **WHEN** 任何模块产生日志
- **THEN** 日志输出包含时间戳、模块名、日志级别和消息内容

### Requirement: 控制台日志输出
系统 SHALL 将日志同时输出到控制台（stdout）。

#### Scenario: 启动时控制台显示日志
- **WHEN** 应用启动
- **THEN** 控制台实时显示结构化格式的日志

### Requirement: 文件日志输出
系统 SHALL 将日志写入 `logs/` 目录下的日志文件，支持文件轮转。

#### Scenario: 日志写入文件
- **WHEN** 应用运行产生日志
- **THEN** 日志同时写入 `logs/app.log` 文件

#### Scenario: 日志文件轮转
- **WHEN** 日志文件大小超过 10MB
- **THEN** 自动轮转，保留最近 5 个备份文件

### Requirement: 日志级别可配置
系统 SHALL 支持通过环境变量 `LOG_LEVEL` 配置日志级别。

#### Scenario: 设置 DEBUG 级别
- **WHEN** 环境变量 `LOG_LEVEL=DEBUG`
- **THEN** 应用输出 DEBUG 及以上级别的日志

#### Scenario: 默认 INFO 级别
- **WHEN** 未设置 `LOG_LEVEL` 环境变量
- **THEN** 应用默认使用 INFO 级别

### Requirement: 统一日志获取接口
系统 SHALL 提供 `get_logger(name)` 函数供各模块获取已配置的 logger 实例。

#### Scenario: 模块获取 logger
- **WHEN** 任何模块调用 `get_logger("module_name")`
- **THEN** 返回已配置好控制台和文件 handler 的 logger 实例
