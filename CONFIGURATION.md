# 网络监控工具配置说明

## 快速开始

1. **下载可执行文件** 到任意目录
2. **创建配置文件** `config.json`（可复制 `config.example.json`）
3. **配置 DingTalk webhook**（可选）
4. **运行程序**

## 配置文件说明

### 创建配置文件

在可执行文件同目录下创建 `config.json` 文件：

```json
{
  "targets": [
    "8.8.8.8",
    "1.1.1.1",
    "114.114.114.114"
  ],
  "latency_threshold": 100.0,
  "check_interval": 10,
  "timeout": 5,
  "dingtalk_webhook": "YOUR_DINGTALK_WEBHOOK_URL_HERE",
  "dingtalk_enabled": true,
  "notification_interval": 300,
  "client_name": "我的网络监控",
  "log_file": "network_monitor.log"
}
```

### 配置项说明

| 配置项 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `targets` | 监控目标IP或域名 | `["8.8.8.8"]` | `["8.8.8.8", "baidu.com"]` |
| `latency_threshold` | 延迟阈值(毫秒) | `100.0` | `150.0` |
| `check_interval` | 检查间隔(秒) | `10` | `30` |
| `timeout` | 超时时间(秒) | `5` | `3` |
| `dingtalk_webhook` | 钉钉机器人webhook地址 | `""` | 见下方说明 |
| `dingtalk_enabled` | 是否启用钉钉通知 | `true` | `false` |
| `notification_interval` | 通知间隔(秒) | `300` | `600` |
| `client_name` | 客户端名称 | `"网络监控"` | `"办公室电脑"` |
| `log_file` | 日志文件名 | `"network_monitor.log"` | `"my_log.log"` |

## DingTalk 钉钉配置

### 1. 创建钉钉机器人

1. 打开钉钉群聊
2. 点击群设置 → 智能群助手 → 添加机器人
3. 选择"自定义"机器人
4. 设置机器人名称（如"网络监控"）
5. 安全设置选择"加签"或"关键词"
6. 复制 Webhook 地址

### 2. 配置 Webhook

将获取的 Webhook 地址填入 `config.json`：

```json
{
  "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=你的token",
  "dingtalk_enabled": true
}
```

### 3. 测试通知

运行测试命令验证配置：
```bash
# Windows
NetworkMonitor-CLI-Windows.exe --test-dingtalk

# macOS/Linux
./NetworkMonitor-CLI-macOS --test-dingtalk
```

## 运行方式

### GUI 版本
- **Windows**: 双击 `NetworkMonitor-GUI-Windows.exe`
- **macOS**: 双击 `NetworkMonitor-GUI-macOS`
- **Linux**: `./NetworkMonitor-GUI-Linux`

### 命令行版本
- **Windows**: `NetworkMonitor-CLI-Windows.exe`
- **macOS**: `./NetworkMonitor-CLI-macOS`
- **Linux**: `./NetworkMonitor-CLI-Linux`

## 目录结构示例

```
网络监控/
├── NetworkMonitor-GUI-Windows.exe    # GUI版本
├── NetworkMonitor-CLI-Windows.exe    # 命令行版本
├── config.json                       # 配置文件
├── config.example.json              # 示例配置
├── CONFIGURATION.md                  # 本说明文件
└── network_monitor.log              # 运行日志
```

## 常见问题

### Q: 程序提示找不到配置文件？
A: 确保 `config.json` 与可执行文件在同一目录下。

### Q: DingTalk 通知不工作？
A:
1. 检查 webhook 地址是否正确
2. 确认钉钉机器人安全设置
3. 运行测试命令验证配置

### Q: 如何禁用 DingTalk 通知？
A: 设置 `"dingtalk_enabled": false`

### Q: 如何修改监控目标？
A: 编辑 `config.json` 中的 `targets` 数组，添加IP地址或域名。

## 高级配置

### 自定义日志位置
```json
{
  "log_file": "/var/log/network_monitor.log"
}
```

### 多目标监控
```json
{
  "targets": [
    "8.8.8.8",
    "1.1.1.1",
    "baidu.com",
    "github.com",
    "192.168.1.1"
  ]
}
```

### 敏感环境配置
```json
{
  "latency_threshold": 50.0,
  "check_interval": 5,
  "notification_interval": 60
}
```