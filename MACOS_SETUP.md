# macOS 安装和运行指南

## 🍎 macOS 专用说明

网络监控工具为 macOS 提供了标准的 .dmg 安装包，符合 Mac 用户的使用习惯。

## 📦 下载文件

从 [Releases](https://github.com/EasonWangs/network-monitor/releases) 页面下载：

- **`NetworkMonitor-macOS.dmg`** - macOS 磁盘镜像安装包（推荐）
- **`NetworkMonitor.app`** - macOS 应用包（可单独下载）
- **`NetworkMonitor-GUI-macOS`** - GUI 可执行文件
- **`NetworkMonitor-CLI-macOS`** - 命令行可执行文件

## 🚀 安装和运行

### 方式1：使用 .dmg 安装包（推荐）

1. **下载** `NetworkMonitor-macOS.dmg`
2. **双击** 打开 .dmg 文件
3. **拖拽** `NetworkMonitor.app` 到 `Applications` 文件夹
4. **从启动台或应用程序文件夹** 启动 Network Monitor

**优势**：
- ✅ 标准 macOS 安装体验
- ✅ 自动包含 CLI 版本
- ✅ 包含安装说明
- ✅ 符合 macOS 分发规范

### 方式2：直接使用 .app 应用包

1. **下载** `NetworkMonitor.app`
2. **拖拽** 到应用程序文件夹（可选）
3. **双击** 运行

如果遇到安全提示：
- 点击 **"取消"**
- 打开 **系统偏好设置** → **安全性与隐私**
- 点击 **"仍要打开"**

### 方式3：使用终端运行

如果从 .dmg 安装，CLI 版本已包含在内：

```bash
# 如果通过 .dmg 安装，CLI 版本位于应用包内
/Applications/NetworkMonitor.app/Contents/Resources/NetworkMonitor-CLI-macOS

# 或者下载独立的可执行文件
chmod +x NetworkMonitor-GUI-macOS  # 通常不需要，文件已有权限
chmod +x NetworkMonitor-CLI-macOS

# 运行 GUI 版本
./NetworkMonitor-GUI-macOS

# 运行命令行版本
./NetworkMonitor-CLI-macOS
```

### 方式4：绕过 Gatekeeper（高级用户）

```bash
# 对于 .dmg 文件
xattr -d com.apple.quarantine NetworkMonitor-macOS.dmg

# 对于单独的可执行文件
xattr -d com.apple.quarantine NetworkMonitor-GUI-macOS
xattr -d com.apple.quarantine NetworkMonitor-CLI-macOS

# 然后正常运行
./NetworkMonitor-GUI-macOS
```

## ⚠️ 常见问题解决

### 问题1："NetworkMonitor-GUI-macOS" 已损坏，无法打开

**原因**：macOS Gatekeeper 阻止未签名的应用

**解决方案**：
```bash
# 方法1：临时绕过 Gatekeeper
sudo spctl --master-disable

# 运行程序后重新启用
sudo spctl --master-enable

# 方法2：为单个文件移除隔离
xattr -d com.apple.quarantine NetworkMonitor-GUI-macOS
```

### 问题2：双击没有反应

**原因**：文件没有执行权限或被系统拦截

**解决方案**：
1. 使用终端给文件权限：`chmod +x NetworkMonitor-GUI-macOS`
2. 在终端中运行：`./NetworkMonitor-GUI-macOS`
3. 或使用提供的 `.app` 应用包

### 问题3：程序运行后立即退出

**可能原因**：
- Python 依赖问题
- 配置文件权限问题

**调试方法**：
```bash
# 在终端中运行以查看错误信息
./NetworkMonitor-GUI-macOS
```

### 问题4：网络权限问题

**症状**：ping 操作失败

**解决方案**：
1. 运行时可能需要输入管理员密码
2. 或在 **系统偏好设置** → **安全性与隐私** → **隐私** → **完全磁盘访问** 中添加程序

## 🔧 环境变量配置

在 macOS 上设置环境变量：

### Terminal/Bash:
```bash
export DINGTALK_WEBHOOK="your-webhook-url"
export CLIENT_NAME="My Mac Monitor"
./NetworkMonitor-GUI-macOS
```

### 永久设置（添加到 ~/.zshrc 或 ~/.bash_profile）:
```bash
echo 'export DINGTALK_WEBHOOK="your-webhook-url"' >> ~/.zshrc
echo 'export CLIENT_NAME="My Mac Monitor"' >> ~/.zshrc
source ~/.zshrc
```

## 📱 使用 .app 应用包的优势

- ✅ 可以双击运行
- ✅ 出现在启动台中
- ✅ 可以拖拽到 Dock
- ✅ 更好的 macOS 集成
- ✅ 自动管理配置文件路径

## 🛠️ 开发者选项

如果你是开发者，想要构建自己的版本：

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 构建 macOS 应用包
pyinstaller --onefile --windowed source/network_monitor_gui.py --name NetworkMonitor

# 创建 .app 包结构
mkdir -p dist/NetworkMonitor.app/Contents/MacOS
cp dist/NetworkMonitor dist/NetworkMonitor.app/Contents/MacOS/
```

## 📞 技术支持

如果遇到其他问题：
1. 查看程序运行日志：`network_monitor.log`
2. 在终端中运行程序查看错误信息
3. 提交 Issue：[GitHub Issues](https://github.com/EasonWangs/network-monitor/issues)

---

## 🔄 自动启动（可选）

如果要在系统启动时自动运行：

1. 打开 **系统偏好设置** → **用户与群组**
2. 选择当前用户 → **登录项**
3. 点击 **+** 添加 `NetworkMonitor.app`

或使用 `launchd`（高级用户）：

```bash
# 创建启动配置
cat > ~/Library/LaunchAgents/com.easonwangs.networkmonitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.easonwangs.networkmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/NetworkMonitor-CLI-macOS</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# 加载配置
launchctl load ~/Library/LaunchAgents/com.easonwangs.networkmonitor.plist
```