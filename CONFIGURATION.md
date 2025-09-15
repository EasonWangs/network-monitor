# 网络监控工具配置说明

## 🔒 安全配置方式

为了保护您的 DingTalk webhook 地址不被意外泄露，我们提供了多种安全的配置方式：

### 方式1：配置文件（适合个人使用）
### 方式2：环境变量（推荐用于生产环境）
### 方式3：Docker 容器配置

## 快速开始

1. **下载可执行文件** 到任意目录
2. **首次运行** - 程序会自动创建安全的配置模板
3. **配置 DingTalk webhook**（选择安全方式）
4. **重新运行程序**

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

## 🔐 DingTalk 钉钉安全配置

### 1. 创建钉钉机器人

1. 打开钉钉群聊
2. 点击群设置 → 智能群助手 → 添加机器人
3. 选择"自定义"机器人
4. 设置机器人名称（如"网络监控"）
5. 安全设置选择"加签"或"关键词"
6. 复制 Webhook 地址

### 2. 安全配置 Webhook

#### 🔒 方式1：环境变量配置（推荐）

```bash
# Windows
set DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=你的token
set CLIENT_NAME=我的网络监控
NetworkMonitor-GUI-Windows.exe

# macOS/Linux
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=你的token"
export CLIENT_NAME="我的网络监控"
./NetworkMonitor-GUI-macOS
```

#### 📝 方式2：配置文件（仅本地使用）

编辑 `config.json`：

```json
{
  "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=你的token",
  "dingtalk_enabled": true,
  "client_name": "我的网络监控"
}
```

⚠️ **注意**：配置文件方式仅适合个人本地使用，不要将包含 webhook 地址的配置文件上传到公共代码仓库！

#### 🐳 方式3：Docker 容器

```bash
docker run -e DINGTALK_WEBHOOK="你的webhook地址" -e CLIENT_NAME="容器监控" network-monitor
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

## 🔐 安全最佳实践

### 1. 保护敏感信息
- ✅ **推荐**：使用环境变量存储 webhook 地址
- ✅ **推荐**：将 `config.json` 添加到 `.gitignore`
- ❌ **避免**：将包含 webhook 的配置文件提交到代码仓库
- ❌ **避免**：在日志中记录完整的 webhook 地址

### 2. DingTalk 机器人安全
- ✅ 设置关键词验证（如：网络、监控、报警）
- ✅ 定期轮换 access_token
- ✅ 限制机器人权限范围
- ❌ 不要在公共场所展示 webhook 地址

### 3. 生产环境建议
```bash
# 使用专用配置目录
mkdir /etc/network-monitor
export DINGTALK_WEBHOOK="your-webhook-here"
export CLIENT_NAME="Production-Server-01"

# 设置适当的文件权限
chmod 600 /etc/network-monitor/config.json
```

## 常见问题

### Q: 程序提示找不到配置文件？
A: 程序首次运行会自动创建 `config.json`，确保有写入权限。

### Q: DingTalk 通知不工作？
A:
1. 检查环境变量 `DINGTALK_WEBHOOK` 是否设置正确
2. 确认钉钉机器人安全设置（关键词/加签）
3. 运行测试命令验证配置
4. 检查网络连接和防火墙设置

### Q: 如何禁用 DingTalk 通知？
A: 设置 `"dingtalk_enabled": false` 或不设置环境变量

### Q: 如何修改监控目标？
A: 编辑 `config.json` 中的 `targets` 数组，添加IP地址或域名。

### Q: 环境变量配置后仍然不工作？
A:
1. 确认环境变量名称正确：`DINGTALK_WEBHOOK`
2. 重启程序以加载新的环境变量
3. 检查程序启动日志是否显示"使用环境变量中的 DingTalk webhook 配置"

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