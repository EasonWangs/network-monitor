# Network Monitor

A cross-platform network monitoring tool with both GUI and command-line interfaces. Monitor network latency, detect connection issues, and receive notifications via DingTalk.

## Features

- 🔍 **Real-time Network Monitoring**: Monitor multiple network targets simultaneously
- 📊 **GUI Interface**: User-friendly graphical interface with real-time charts
- 💻 **Command Line Interface**: Lightweight CLI version for server environments
- 🔔 **DingTalk Notifications**: Automatic alerts when network issues are detected
- 🎯 **Configurable Thresholds**: Set custom latency thresholds and check intervals
- 📱 **Cross-platform**: Supports Windows, macOS, and Linux

## Quick Start

### Download Pre-built Binaries

Download the latest release from the [Releases](https://github.com/EasonWangs/network-monitor/releases) page:

- **Windows**: `NetworkMonitor-GUI-Windows.exe` or `NetworkMonitor-CLI-Windows.exe`
- **macOS**: `NetworkMonitor-GUI-macOS` or `NetworkMonitor-CLI-macOS`
- **Linux**: `NetworkMonitor-GUI-Linux` or `NetworkMonitor-CLI-Linux`

### Run from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/EasonWangs/network-monitor.git
   cd network-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # GUI version
   python source/network_monitor_gui.py

   # Command line version
   python source/network_monitor.py
   ```

## Configuration

### Quick Setup for Downloaded Executables

1. **Download** the executable for your platform
2. **Run** the executable once - it will create a default `config.json` file
3. **Edit** `config.json` to configure DingTalk webhook (optional)
4. **Run** again to start monitoring

### Configuration File

The program automatically creates `config.json` on first run:

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
  "client_name": "Network Monitor Client",
  "log_file": "network_monitor.log"
}
```

📖 **Detailed configuration guide**: See [CONFIGURATION.md](CONFIGURATION.md)

### Configuration Options

- `targets`: List of IP addresses or hostnames to monitor
- `latency_threshold`: Latency threshold in milliseconds (alerts triggered above this)
- `check_interval`: Time between checks in seconds
- `timeout`: Ping timeout in seconds
- `dingtalk_webhook`: DingTalk robot webhook URL for notifications
- `dingtalk_enabled`: Enable/disable DingTalk notifications
- `notification_interval`: Minimum time between notifications in seconds
- `client_name`: Display name for this monitoring client
- `log_file`: Log file path

## Usage

### GUI Version

The GUI version provides:
- Real-time latency charts
- Visual network status indicators
- Easy configuration management
- System tray integration

### Command Line Version

The CLI version is perfect for:
- Server environments
- Background monitoring
- Automated deployments
- Resource-constrained systems

### DingTalk Integration

1. Create a DingTalk robot in your group
2. Copy the webhook URL
3. Update `dingtalk_webhook` in `config.json`
4. Test notifications: `python source/test_dingtalk.py`

## Building from Source

### Local Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build GUI version
pyinstaller --onefile --windowed source/network_monitor_gui.py --name NetworkMonitor-GUI

# Build CLI version
pyinstaller --onefile source/network_monitor.py --name NetworkMonitor-CLI
```

### Automated Builds

This project uses GitHub Actions for automated building and releasing:

- **Continuous Integration**: Runs tests on every push and PR
- **Multi-platform Builds**: Automatically builds for Windows, macOS, and Linux
- **Automatic Releases**: Creates releases when tags are pushed

To create a new release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Development

### Project Structure

```
network-monitor/
├── source/                    # Source code
│   ├── network_monitor.py     # CLI version
│   ├── network_monitor_gui.py # GUI version
│   └── test_dingtalk.py      # DingTalk test utility
├── .github/workflows/         # GitHub Actions CI/CD
│   └── build-and-release.yml  # Automated building and releases
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── package.json              # Project metadata and scripts
├── icon.ico                  # Application icon
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Requirements

- Python 3.8+
- PySide6 (for GUI)
- requests (for DingTalk notifications)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/EasonWangs/network-monitor/issues)
- **Documentation**: All documentation is in this README file
- **DingTalk Setup**: See `source/test_dingtalk.py` for testing webhook configuration

## Changelog

### v1.0.0
- Initial release
- GUI and CLI versions
- DingTalk integration
- Cross-platform support
- Automated building and releases