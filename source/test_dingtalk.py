#!/usr/bin/env python3
"""
测试钉钉通知功能
用于验证钉钉Webhook集成是否正常工作
"""

import json
import requests
from datetime import datetime

def test_dingtalk_webhook():
    """测试钉钉Webhook通知"""
    # 从配置文件读取钉钉Webhook地址
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        webhook_url = config.get('dingtalk_webhook', '')

        if not webhook_url or webhook_url == "YOUR_DINGTALK_WEBHOOK_URL_HERE":
            print("⚠️ 钉钉Webhook未配置，跳过测试")
            print("请在 config.json 中设置正确的 dingtalk_webhook 地址")
            return
    except FileNotFoundError:
        print("❌ 配置文件 config.json 不存在")
        return
    except json.JSONDecodeError:
        print("❌ 配置文件格式错误")
        return
    
    # 测试消息
    client_name = "测试客户端"
    test_message = (
        f"🧪 网络监测工具测试消息\n\n"
        f"客户端: {client_name}\n"
        f"这是一条来自网络监测工具的测试通知。\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"功能: 钉钉Webhook集成测试\n"
        f"状态: 测试正常"
    )
    
    # 高延迟测试消息
    high_latency_message = (
        f"⚠️ 网络监测报警\n\n"
        f"客户端: {client_name}\n"
        f"目标: 8.8.8.8\n"
        f"状态: 高延迟警告\n"
        f"当前延迟: 150.25ms\n"
        f"阈值: 100ms\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    messages = [
        ("基础测试", test_message),
        ("高延迟报警", high_latency_message),
    ]
    
    print("🚀 开始测试钉钉Webhook通知...")
    print(f"📡 Webhook地址: {webhook_url}")
    print()
    
    success_count = 0
    
    for test_name, message in messages:
        print(f"📤 发送 {test_name} 消息...")
        
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
                    print(f"✅ {test_name} 发送成功")
                    success_count += 1
                else:
                    print(f"❌ {test_name} 发送失败: {result.get('errmsg', '未知错误')}")
            else:
                print(f"❌ {test_name} 发送失败: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {test_name} 网络错误: {e}")
        except Exception as e:
            print(f"❌ {test_name} 发生错误: {e}")
        
        print()
    
    print(f"🎯 测试完成: {success_count}/{len(messages)} 条消息发送成功")
    
    if success_count == len(messages):
        print("🎉 所有测试通过！钉钉Webhook集成正常工作。")
    else:
        print("⚠️ 部分测试失败，请检查Webhook配置。")

if __name__ == "__main__":
    test_dingtalk_webhook()