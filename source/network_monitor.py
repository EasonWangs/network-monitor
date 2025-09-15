#!/usr/bin/env python3
"""
Network Monitor - 网络状态监测工具
监测网络延迟，当延迟过高时记录日志
"""

import subprocess
import time
import logging
import argparse
import json
import platform
import requests
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class NetworkMonitor:
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.last_notification_time = {}  # 记录上次通知时间，避免频繁发送
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件，支持环境变量覆盖敏感信息"""
        default_config = {
            "targets": ["8.8.8.8", "1.1.1.1", "114.114.114.114"],
            "latency_threshold": 100,  # 毫秒
            "check_interval": 10,      # 秒
            "log_file": "network_monitor.log",
            "timeout": 5,              # ping超时时间(秒)
            "dingtalk_webhook": "",    # 钉钉Webhook地址
            "dingtalk_enabled": False, # 是否启用钉钉通知
            "notification_interval": 300,  # 通知间隔(秒)，避免频繁发送
            "client_name": "默认客户端",  # 客户端名称，用于标识不同的监测实例
        }

        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"配置文件读取错误: {e}, 使用默认配置")
        else:
            # 创建安全的默认配置文件（不包含敏感信息）
            safe_config = default_config.copy()
            safe_config["dingtalk_webhook"] = "YOUR_DINGTALK_WEBHOOK_URL_HERE"
            safe_config["client_name"] = "Network Monitor Client"

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2, ensure_ascii=False)
            print(f"已创建默认配置文件: {config_file}")
            print("请编辑配置文件设置 DingTalk webhook 地址")

        # 支持环境变量覆盖敏感配置
        env_webhook = os.getenv('DINGTALK_WEBHOOK')
        if env_webhook:
            default_config["dingtalk_webhook"] = env_webhook
            default_config["dingtalk_enabled"] = True
            print("使用环境变量中的 DingTalk webhook 配置")

        env_client_name = os.getenv('CLIENT_NAME')
        if env_client_name:
            default_config["client_name"] = env_client_name

        return default_config
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ping_host(self, host: str) -> Optional[float]:
        """ping指定主机，返回延迟时间（毫秒）"""
        try:
            # 根据操作系统选择ping命令
            system = platform.system().lower()
            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", str(self.config['timeout'] * 1000), host]
            else:  # Linux, macOS
                cmd = ["ping", "-c", "1", "-W", str(self.config['timeout']), host]
            
            # 执行ping命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config['timeout'] + 2)
            
            if result.returncode == 0:
                # 解析ping输出获取延迟时间
                output = result.stdout
                if system == "windows":
                    # Windows: time=XXXms 或 时间=XXXms
                    import re
                    match = re.search(r'(?:time|时间)[=<](\d+(?:\.\d+)?)ms', output)
                    if match:
                        return float(match.group(1))
                else:  # Linux, macOS
                    # Linux/macOS: time=XXX ms 或 time=XXX.XXX ms
                    import re
                    match = re.search(r'time=(\d+(?:\.\d+)?)\s*ms', output)
                    if match:
                        return float(match.group(1))
            
            return None
        except subprocess.TimeoutExpired:
            self.logger.debug(f"Ping {host} 超时")
            return None
        except Exception as e:
            self.logger.error(f"Ping {host} 失败: {e}")
            return None
    
    def check_network_latency(self) -> Dict[str, Optional[float]]:
        """检查所有目标主机的延迟"""
        results = {}
        for target in self.config['targets']:
            latency = self.ping_host(target)
            results[target] = latency
        return results
    
    def log_high_latency(self, target: str, latency: float):
        """记录高延迟事件"""
        message = f"高延迟警告: {target} - {latency:.2f}ms (阈值: {self.config['latency_threshold']}ms)"
        self.logger.warning(message)
        
        # 发送钉钉通知
        if self.should_send_notification(target, "high_latency"):
            client_name = self.config.get('client_name', '未知客户端')
            self.send_dingtalk_notification(
                f"⚠️ 网络监测报警\n\n"
                f"客户端: {client_name}\n"
                f"目标: {target}\n"
                f"状态: 高延迟警告\n"
                f"当前延迟: {latency:.2f}ms\n"
                f"阈值: {self.config['latency_threshold']}ms\n"
                f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
    
    def log_unreachable(self, target: str):
        """记录不可达事件"""
        message = f"网络不可达: {target} - 无法ping通"
        self.logger.error(message)
        
        # 网络不可达时不发送钉钉通知，因为此时可能无法连接外网
        # 只记录日志即可
    
    def should_send_notification(self, target: str, alert_type: str) -> bool:
        """判断是否应该发送通知（避免频繁发送）"""
        if not self.config.get('dingtalk_enabled', False):
            return False
        
        key = f"{target}_{alert_type}"
        now = time.time()
        last_time = self.last_notification_time.get(key, 0)
        
        # 检查是否超过通知间隔
        if now - last_time >= self.config.get('notification_interval', 300):
            self.last_notification_time[key] = now
            return True
        return False
    
    def send_dingtalk_notification(self, message: str):
        """发送钉钉通知"""
        webhook_url = self.config.get('dingtalk_webhook', '')
        if not webhook_url:
            self.logger.warning("钉钉Webhook地址未配置，跳过通知")
            return
        
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(webhook_url, 
                                   data=json.dumps(payload), 
                                   headers=headers, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    self.logger.info("钉钉通知发送成功")
                else:
                    self.logger.error(f"钉钉通知发送失败: {result.get('errmsg', '未知错误')}")
            else:
                self.logger.error(f"钉钉通知发送失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"发送钉钉通知时网络错误: {e}")
        except Exception as e:
            self.logger.error(f"发送钉钉通知时发生错误: {e}")
    
    def run_monitor(self):
        """运行网络监测"""
        self.logger.info("开始网络监测...")
        self.logger.info(f"监测目标: {', '.join(self.config['targets'])}")
        self.logger.info(f"延迟阈值: {self.config['latency_threshold']}ms")
        self.logger.info(f"检测间隔: {self.config['check_interval']}秒")
        
        try:
            while True:
                results = self.check_network_latency()
                
                # 检查延迟和连通性
                high_latency_count = 0
                unreachable_count = 0
                
                for target, latency in results.items():
                    if latency is None:
                        self.log_unreachable(target)
                        unreachable_count += 1
                    elif latency > self.config['latency_threshold']:
                        self.log_high_latency(target, latency)
                        high_latency_count += 1
                    else:
                        # 正常延迟时也记录一下
                        self.logger.info(f"{target}: {latency:.2f}ms (正常，低于阈值{self.config['latency_threshold']}ms)")
                
                # 如果所有目标都有问题，额外记录
                if high_latency_count + unreachable_count == len(self.config['targets']):
                    self.logger.critical("网络状态异常：所有监测目标都存在问题")
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("监测停止")
        except Exception as e:
            self.logger.error(f"监测过程出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='网络状态监测工具')
    parser.add_argument('-c', '--config', default='config.json', 
                       help='配置文件路径 (默认: config.json)')
    parser.add_argument('-t', '--threshold', type=float,
                       help='延迟阈值(毫秒)，覆盖配置文件设置')
    parser.add_argument('-i', '--interval', type=int,
                       help='检测间隔(秒)，覆盖配置文件设置')
    parser.add_argument('--targets', nargs='+',
                       help='监测目标，覆盖配置文件设置')
    
    args = parser.parse_args()
    
    # 创建监测器
    monitor = NetworkMonitor(args.config)
    
    # 命令行参数覆盖配置文件
    if args.threshold:
        monitor.config['latency_threshold'] = args.threshold
    if args.interval:
        monitor.config['check_interval'] = args.interval
    if args.targets:
        monitor.config['targets'] = args.targets
    
    # 运行监测
    monitor.run_monitor()

if __name__ == "__main__":
    main()