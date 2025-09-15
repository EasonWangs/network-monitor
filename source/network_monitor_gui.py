#!/usr/bin/env python3
"""
网络监测工具 GUI版本
使用PySide6创建图形界面，实时显示网络状态
"""

import sys
import json
import threading
import time
import logging
import requests
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox,
    QLineEdit, QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTabWidget, QScrollArea, QFrame
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from PySide6.QtGui import QFont, QColor, QPalette

# 导入原网络监测模块
from network_monitor import NetworkMonitor


class MonitorThread(QThread):
    """网络监测线程"""
    status_update = Signal(str, float)  # 目标，延迟
    status_unreachable = Signal(str)    # 目标不可达
    log_message = Signal(str, str)      # 级别，消息
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = False
        self.monitor = None
        
    def run(self):
        """运行监测线程"""
        self.running = True
        self.monitor = NetworkMonitor()
        self.monitor.config.update(self.config)
        
        self.log_message.emit("INFO", f"开始网络监测... 目标: {', '.join(self.config['targets'])}")
        self.log_message.emit("INFO", f"延迟阈值: {self.config['latency_threshold']}ms")
        self.log_message.emit("INFO", f"检测间隔: {self.config['check_interval']}秒")
        
        while self.running:
            try:
                # 检查所有目标
                results = self.monitor.check_network_latency()
                
                for target, latency in results.items():
                    if latency is None:
                        self.status_unreachable.emit(target)
                        self.log_message.emit("ERROR", f"网络不可达: {target}")
                    elif latency > self.config['latency_threshold']:
                        self.status_update.emit(target, latency)
                        self.log_message.emit("WARNING", 
                            f"高延迟警告: {target} - {latency:.2f}ms (阈值: {self.config['latency_threshold']}ms)")
                    else:
                        self.status_update.emit(target, latency)
                        self.log_message.emit("INFO", f"{target}: {latency:.2f}ms (正常)")
                
                # 等待下次检测
                for i in range(self.config['check_interval']):
                    if not self.running:
                        break
                    self.msleep(1000)
                    
            except Exception as e:
                self.log_message.emit("ERROR", f"监测过程出错: {e}")
                break
                
        self.log_message.emit("INFO", "网络监测已停止")
    
    def stop(self):
        """停止监测"""
        self.running = False


class NetworkMonitorGUI(QMainWindow):
    """网络监测GUI主窗口"""
    
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.config = self.load_config()
        self.setup_logging()
        self.init_ui()
        
    def load_config(self):
        """加载配置，支持环境变量覆盖敏感信息"""
        config_file = "config.json"
        default_config = {
            "targets": ["8.8.8.8", "1.1.1.1", "114.114.114.114"],
            "latency_threshold": 100.0,
            "check_interval": 10,
            "timeout": 5,
            "dingtalk_webhook": "",
            "dingtalk_enabled": False,
            "notification_interval": 300,
            "client_name": "默认客户端"
        }

        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError):
                pass
        else:
            # 创建安全的默认配置文件（不包含敏感信息）
            safe_config = default_config.copy()
            safe_config["dingtalk_webhook"] = "YOUR_DINGTALK_WEBHOOK_URL_HERE"
            safe_config["client_name"] = "Network Monitor Client"

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2, ensure_ascii=False)

        # 支持环境变量覆盖敏感配置
        env_webhook = os.getenv('DINGTALK_WEBHOOK')
        if env_webhook:
            default_config["dingtalk_webhook"] = env_webhook
            default_config["dingtalk_enabled"] = True

        env_client_name = os.getenv('CLIENT_NAME')
        if env_client_name:
            default_config["client_name"] = env_client_name

        return default_config
    
    def setup_logging(self):
        """设置日志记录"""
        # 创建GUI专用的日志文件
        log_file = self.config.get('log_file', 'network_monitor.log')
        gui_log_file = log_file.replace('.log', '_gui.log')
        
        # 设置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(gui_log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.gui_log_file = gui_log_file
    
    def save_config(self):
        """保存配置"""
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError:
            QMessageBox.warning(self, "警告", "配置文件保存失败")
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("网络监测工具 v2.0")
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中央部件和标签页
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 监测页面
        monitor_tab = self.create_monitor_tab()
        tab_widget.addTab(monitor_tab, "网络监测")
        
        # 配置页面
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "配置设置")
        
        # 日志页面
        log_tab = self.create_log_tab()
        tab_widget.addTab(log_tab, "日志查看")
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_monitor_tab(self):
        """创建监测标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_group = QGroupBox("监测控制")
        control_layout = QHBoxLayout(control_group)
        
        self.start_btn = QPushButton("开始监测")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        self.start_btn.clicked.connect(self.start_monitoring)
        
        self.stop_btn = QPushButton("停止监测")
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_group)
        
        # 状态显示表格
        status_group = QGroupBox("实时状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_table = QTableWidget(0, 4)
        self.status_table.setHorizontalHeaderLabels(["目标", "状态", "延迟(ms)", "最后检测时间"])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        status_layout.addWidget(self.status_table)
        layout.addWidget(status_group)
        
        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QGridLayout(stats_group)
        
        self.total_checks_label = QLabel("总检测次数: 0")
        self.high_latency_count_label = QLabel("高延迟次数: 0")
        self.unreachable_count_label = QLabel("不可达次数: 0")
        self.avg_latency_label = QLabel("平均延迟: 0.00ms")
        
        stats_layout.addWidget(self.total_checks_label, 0, 0)
        stats_layout.addWidget(self.high_latency_count_label, 0, 1)
        stats_layout.addWidget(self.unreachable_count_label, 1, 0)
        stats_layout.addWidget(self.avg_latency_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # 初始化统计变量
        self.total_checks = 0
        self.high_latency_count = 0
        self.unreachable_count = 0
        self.latency_sum = 0.0
        self.latency_count = 0
        
        return widget
    
    def create_config_tab(self):
        """创建配置标签页"""
        widget = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # 目标设置
        targets_group = QGroupBox("监测目标")
        targets_layout = QVBoxLayout(targets_group)
        
        self.targets_edit = QTextEdit()
        self.targets_edit.setPlainText('\n'.join(self.config['targets']))
        self.targets_edit.setMaximumHeight(100)
        targets_layout.addWidget(QLabel("请输入监测目标(每行一个IP或域名):"))
        targets_layout.addWidget(self.targets_edit)
        
        layout.addWidget(targets_group)
        
        # 阈值设置
        threshold_group = QGroupBox("阈值设置")
        threshold_layout = QGridLayout(threshold_group)
        
        threshold_layout.addWidget(QLabel("延迟阈值 (ms):"), 0, 0)
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 10000.0)
        self.threshold_spin.setDecimals(1)
        self.threshold_spin.setValue(self.config['latency_threshold'])
        threshold_layout.addWidget(self.threshold_spin, 0, 1)
        
        threshold_layout.addWidget(QLabel("检测间隔 (秒):"), 1, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 300)
        self.interval_spin.setValue(self.config['check_interval'])
        threshold_layout.addWidget(self.interval_spin, 1, 1)
        
        threshold_layout.addWidget(QLabel("超时时间 (秒):"), 2, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(self.config['timeout'])
        threshold_layout.addWidget(self.timeout_spin, 2, 1)
        
        layout.addWidget(threshold_group)
        
        # 客户端设置
        client_group = QGroupBox("客户端设置")
        client_layout = QGridLayout(client_group)
        
        client_layout.addWidget(QLabel("客户端名称:"), 0, 0)
        self.client_name_edit = QLineEdit()
        self.client_name_edit.setText(self.config.get('client_name', '默认客户端'))
        self.client_name_edit.setPlaceholderText("用于标识不同的监测实例")
        client_layout.addWidget(self.client_name_edit, 0, 1)
        
        layout.addWidget(client_group)
        
        # 钉钉通知设置
        dingtalk_group = QGroupBox("钉钉通知设置")
        dingtalk_layout = QGridLayout(dingtalk_group)
        
        # 启用钉钉通知
        dingtalk_layout.addWidget(QLabel("启用钉钉通知:"), 0, 0)
        self.dingtalk_enabled_checkbox = QPushButton("关闭")
        self.dingtalk_enabled_checkbox.setCheckable(True)
        self.dingtalk_enabled_checkbox.setChecked(self.config.get('dingtalk_enabled', False))
        self.dingtalk_enabled_checkbox.clicked.connect(self.toggle_dingtalk_enabled)
        self.update_dingtalk_button_text()
        dingtalk_layout.addWidget(self.dingtalk_enabled_checkbox, 0, 1)
        
        # Webhook地址
        dingtalk_layout.addWidget(QLabel("Webhook地址:"), 1, 0)
        self.dingtalk_webhook_edit = QLineEdit()
        self.dingtalk_webhook_edit.setText(self.config.get('dingtalk_webhook', ''))
        self.dingtalk_webhook_edit.setPlaceholderText("https://oapi.dingtalk.com/robot/send?access_token=...")
        dingtalk_layout.addWidget(self.dingtalk_webhook_edit, 1, 1)
        
        # 通知间隔
        dingtalk_layout.addWidget(QLabel("通知间隔 (秒):"), 2, 0)
        self.notification_interval_spin = QSpinBox()
        self.notification_interval_spin.setRange(60, 3600)
        self.notification_interval_spin.setValue(self.config.get('notification_interval', 300))
        self.notification_interval_spin.setSuffix(" 秒")
        dingtalk_layout.addWidget(self.notification_interval_spin, 2, 1)
        
        # 测试通知按钮
        test_notification_btn = QPushButton("测试钉钉通知")
        test_notification_btn.clicked.connect(self.test_dingtalk_notification)
        dingtalk_layout.addWidget(test_notification_btn, 3, 0, 1, 2)
        
        layout.addWidget(dingtalk_group)
        
        # 保存按钮
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_configuration)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        widget.setWidget(content)
        return widget
    
    def create_log_tab(self):
        """创建日志标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志显示
        log_group = QGroupBox("实时日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier", 10))
        log_layout.addWidget(self.log_display)
        
        # 日志控制
        log_control_layout = QHBoxLayout()
        clear_log_btn = QPushButton("清空显示")
        clear_log_btn.clicked.connect(self.clear_logs)
        
        self.auto_scroll_btn = QPushButton("自动滚动: 开")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        
        load_log_btn = QPushButton("加载历史日志")
        load_log_btn.clicked.connect(self.load_log_history)
        
        save_log_btn = QPushButton("导出日志")
        save_log_btn.clicked.connect(self.export_logs)
        
        log_control_layout.addWidget(clear_log_btn)
        log_control_layout.addWidget(self.auto_scroll_btn)
        log_control_layout.addWidget(load_log_btn)
        log_control_layout.addWidget(save_log_btn)
        log_control_layout.addStretch()
        
        log_layout.addLayout(log_control_layout)
        
        # 日志文件信息
        log_info_label = QLabel(f"日志文件: {getattr(self, 'gui_log_file', 'network_monitor_gui.log')}")
        log_info_label.setStyleSheet("color: gray; font-size: 10px;")
        log_layout.addWidget(log_info_label)
        
        layout.addWidget(log_group)
        
        # 加载启动时的历史日志
        self.load_log_history()
        
        return widget
    
    def save_configuration(self):
        """保存配置"""
        try:
            # 获取目标列表
            targets_text = self.targets_edit.toPlainText().strip()
            targets = [line.strip() for line in targets_text.split('\n') if line.strip()]
            
            if not targets:
                QMessageBox.warning(self, "警告", "至少需要一个监测目标")
                return
            
            # 更新配置
            self.config['targets'] = targets
            self.config['latency_threshold'] = self.threshold_spin.value()
            self.config['check_interval'] = self.interval_spin.value()
            self.config['timeout'] = self.timeout_spin.value()
            self.config['client_name'] = self.client_name_edit.text().strip() or "默认客户端"
            self.config['dingtalk_enabled'] = self.dingtalk_enabled_checkbox.isChecked()
            self.config['dingtalk_webhook'] = self.dingtalk_webhook_edit.text().strip()
            self.config['notification_interval'] = self.notification_interval_spin.value()
            
            # 保存到文件
            self.save_config()
            
            QMessageBox.information(self, "成功", "配置已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")
    
    def toggle_dingtalk_enabled(self):
        """切换钉钉通知开关"""
        self.update_dingtalk_button_text()
    
    def update_dingtalk_button_text(self):
        """更新钉钉开关按钮文本"""
        if self.dingtalk_enabled_checkbox.isChecked():
            self.dingtalk_enabled_checkbox.setText("开启")
            self.dingtalk_enabled_checkbox.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        else:
            self.dingtalk_enabled_checkbox.setText("关闭")
            self.dingtalk_enabled_checkbox.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
    
    def test_dingtalk_notification(self):
        """测试钉钉通知"""
        webhook_url = self.dingtalk_webhook_edit.text().strip()
        
        if not webhook_url:
            QMessageBox.warning(self, "警告", "请先配置钉钉Webhook地址")
            return
        
        try:
            client_name = self.client_name_edit.text().strip() or "默认客户端"
            # 发送测试消息
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"🧪 网络监测工具测试消息\n\n"
                              f"客户端: {client_name}\n"
                              f"这是一条来自网络监测工具的测试通知。\n"
                              f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                              f"状态: 测试正常"
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
                    QMessageBox.information(self, "成功", "钉钉测试通知发送成功！")
                    self.add_log_message("INFO", "钉钉测试通知发送成功")
                else:
                    QMessageBox.warning(self, "失败", f"钉钉通知发送失败: {result.get('errmsg', '未知错误')}")
                    self.add_log_message("ERROR", f"钉钉通知发送失败: {result.get('errmsg', '未知错误')}")
            else:
                QMessageBox.warning(self, "失败", f"钉钉通知发送失败: HTTP {response.status_code}")
                self.add_log_message("ERROR", f"钉钉通知发送失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "网络错误", f"发送钉钉通知时网络错误:\n{e}")
            self.add_log_message("ERROR", f"发送钉钉通知时网络错误: {e}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发送钉钉通知时发生错误:\n{e}")
            self.add_log_message("ERROR", f"发送钉钉通知时发生错误: {e}")
    
    def start_monitoring(self):
        """开始监测"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            return
            
        # 重置统计
        self.total_checks = 0
        self.high_latency_count = 0
        self.unreachable_count = 0
        self.latency_sum = 0.0
        self.latency_count = 0
        self.update_stats()
        
        # 清空状态表格
        self.status_table.setRowCount(0)
        
        # 初始化状态表格
        for target in self.config['targets']:
            row = self.status_table.rowCount()
            self.status_table.insertRow(row)
            self.status_table.setItem(row, 0, QTableWidgetItem(target))
            self.status_table.setItem(row, 1, QTableWidgetItem("等待中..."))
            self.status_table.setItem(row, 2, QTableWidgetItem("-"))
            self.status_table.setItem(row, 3, QTableWidgetItem("-"))
        
        # 启动监测线程
        self.monitor_thread = MonitorThread(self.config)
        self.monitor_thread.status_update.connect(self.update_status)
        self.monitor_thread.status_unreachable.connect(self.update_unreachable)
        self.monitor_thread.log_message.connect(self.add_log_message)
        self.monitor_thread.start()
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.statusBar().showMessage("监测中...")
        
    def stop_monitoring(self):
        """停止监测"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        # 更新UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("监测已停止")
        
    def update_status(self, target: str, latency: float):
        """更新目标状态"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 查找目标行
        for row in range(self.status_table.rowCount()):
            if self.status_table.item(row, 0).text() == target:
                # 更新状态
                if latency > self.config['latency_threshold']:
                    status = "高延迟"
                    self.status_table.item(row, 1).setBackground(QColor(255, 200, 200))
                    self.high_latency_count += 1
                else:
                    status = "正常"
                    self.status_table.item(row, 1).setBackground(QColor(200, 255, 200))
                
                self.status_table.setItem(row, 1, QTableWidgetItem(status))
                self.status_table.setItem(row, 2, QTableWidgetItem(f"{latency:.2f}"))
                self.status_table.setItem(row, 3, QTableWidgetItem(current_time))
                break
        
        # 更新统计
        self.total_checks += 1
        self.latency_sum += latency
        self.latency_count += 1
        self.update_stats()
        
    def update_unreachable(self, target: str):
        """更新不可达状态"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # 查找目标行
        for row in range(self.status_table.rowCount()):
            if self.status_table.item(row, 0).text() == target:
                self.status_table.setItem(row, 1, QTableWidgetItem("不可达"))
                self.status_table.item(row, 1).setBackground(QColor(255, 150, 150))
                self.status_table.setItem(row, 2, QTableWidgetItem("-"))
                self.status_table.setItem(row, 3, QTableWidgetItem(current_time))
                break
        
        # 更新统计
        self.total_checks += 1
        self.unreachable_count += 1
        self.update_stats()
        
    def update_stats(self):
        """更新统计信息"""
        self.total_checks_label.setText(f"总检测次数: {self.total_checks}")
        self.high_latency_count_label.setText(f"高延迟次数: {self.high_latency_count}")
        self.unreachable_count_label.setText(f"不可达次数: {self.unreachable_count}")
        
        if self.latency_count > 0:
            avg_latency = self.latency_sum / self.latency_count
            self.avg_latency_label.setText(f"平均延迟: {avg_latency:.2f}ms")
        
    def add_log_message(self, level: str, message: str):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # 写入日志文件
        if hasattr(self, 'logger'):
            if level == "INFO":
                self.logger.info(message)
            elif level == "WARNING":
                self.logger.warning(message)
            elif level == "ERROR":
                self.logger.error(message)
            elif level == "CRITICAL":
                self.logger.critical(message)
            else:
                self.logger.info(message)
        
        # 根据级别设置颜色
        if level == "ERROR" or level == "CRITICAL":
            color = "red"
        elif level == "WARNING":
            color = "orange"
        elif level == "INFO":
            color = "blue"
        else:
            color = "black"
            
        self.log_display.append(f'<span style="color: {color};">{log_entry}</span>')
        
        # 自动滚动到底部
        if self.auto_scroll_btn.isChecked():
            cursor = self.log_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
    
    def clear_logs(self):
        """清空显示的日志（不删除日志文件）"""
        self.log_display.clear()
        self.add_log_message("INFO", "日志显示已清空")
        
    def load_log_history(self):
        """加载历史日志"""
        try:
            if hasattr(self, 'gui_log_file') and Path(self.gui_log_file).exists():
                with open(self.gui_log_file, 'r', encoding='utf-8') as f:
                    # 读取最后100行日志
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        if line:
                            # 解析日志级别
                            if " - INFO - " in line:
                                level = "INFO"
                                color = "blue"
                            elif " - WARNING - " in line:
                                level = "WARNING" 
                                color = "orange"
                            elif " - ERROR - " in line:
                                level = "ERROR"
                                color = "red"
                            elif " - CRITICAL - " in line:
                                level = "CRITICAL"
                                color = "red"
                            else:
                                level = "INFO"
                                color = "black"
                            
                            self.log_display.append(f'<span style="color: {color};">{line}</span>')
                
                # 滚动到底部
                if self.auto_scroll_btn.isChecked():
                    cursor = self.log_display.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    self.log_display.setTextCursor(cursor)
                    
        except Exception as e:
            print(f"加载历史日志失败: {e}")
    
    def export_logs(self):
        """导出日志到指定文件"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"network_monitor_export_{timestamp}.txt"
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "导出日志",
                default_filename,
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                # 获取当前显示的所有日志
                log_content = self.log_display.toPlainText()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                QMessageBox.information(self, "成功", f"日志已导出到: {filename}")
                self.add_log_message("INFO", f"日志已导出到: {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出日志失败: {e}")
            self.add_log_message("ERROR", f"导出日志失败: {e}")
        
    def toggle_auto_scroll(self):
        """切换自动滚动"""
        if self.auto_scroll_btn.isChecked():
            self.auto_scroll_btn.setText("自动滚动: 开")
        else:
            self.auto_scroll_btn.setText("自动滚动: 关")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            reply = QMessageBox.question(
                self, "确认退出",
                "网络监测正在运行，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_monitoring()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = NetworkMonitorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()