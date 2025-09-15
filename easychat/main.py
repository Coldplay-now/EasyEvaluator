#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyChat 2.0 - 基于 DeepSeek API 的流式问答程序

支持两种运行模式：
1. CLI模式（默认）：命令行交互式聊天
2. API模式：HTTP API服务器，供其他系统调用

使用方法：
- CLI模式：python main.py
- API模式：python main.py --api
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify


def setup_logging():
    """
    设置简单的日志配置
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_config():
    """
    加载配置文件
    """
    # 加载 .env 文件
    load_dotenv()
    
    # 获取 API 配置
    api_key = os.getenv('DEEPSEEK_API_KEY')
    base_url = os.getenv('API_BASE_URL', 'https://api.deepseek.com/v1')
    
    if not api_key:
        print("错误: 未找到 DEEPSEEK_API_KEY，请检查 .env 文件")
        sys.exit(1)
    
    return api_key, base_url


def load_system_prompt():
    """
    加载系统提示词
    """
    try:
        with open('systemprompt.md', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("警告: 未找到 systemprompt.md 文件，使用默认系统提示词")
        return "你是一个有用的AI助手，请友好地回答用户的问题。"


def create_client(api_key, base_url):
    """
    创建 OpenAI 客户端
    """
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )


def get_chat_response(client, message, system_prompt):
    """
    获取单次聊天响应（非流式，用于API模式）
    """
    logger = logging.getLogger(__name__)
    logger.info(f"收到聊天请求，消息长度: {len(message)}")
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            max_tokens=2000,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        logger.info(f"API调用成功，响应长度: {len(result)}")
        return result
    
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")
        raise Exception(f"API 调用失败: {str(e)}")


def stream_chat(client, messages):
    """
    流式对话（用于CLI模式）
    """
    try:
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
            max_tokens=2000,
            temperature=0.7
        )
        
        response_content = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                response_content += content
        
        print()  # 换行
        return response_content
    
    except Exception as e:
        print(f"\n错误: API 调用失败 - {str(e)}")
        return None


def create_flask_app():
    """
    创建Flask应用
    """
    app = Flask(__name__)
    
    # 加载配置
    api_key, base_url = load_config()
    system_prompt = load_system_prompt()
    client = create_client(api_key, base_url)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查端点"""
        return jsonify({"status": "ok"})
    
    @app.route('/chat', methods=['POST'])
    def chat():
        """聊天端点"""
        logger = logging.getLogger(__name__)
        logger.info(f"收到POST /chat请求，来源IP: {request.remote_addr}")
        
        try:
            # 获取请求数据
            data = request.get_json()
            if not data or 'message' not in data:
                logger.warning("请求缺少message参数")
                return jsonify({"error": "缺少message参数"}), 400
            
            message = data['message'].strip()
            if not message:
                logger.warning("请求message为空")
                return jsonify({"error": "message不能为空"}), 400
            
            # 获取AI响应
            response = get_chat_response(client, message, system_prompt)
            logger.info("聊天请求处理成功")
            return jsonify({"response": response})
            
        except Exception as e:
            logger.error(f"聊天请求处理失败: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    return app


def run_cli_mode():
    """
    运行CLI模式
    """
    print("=" * 50)
    print("🤖 EasyChat - DeepSeek AI 助手")
    print("=" * 50)
    print("输入 'quit' 退出程序")
    print("-" * 50)
    
    # 加载配置
    try:
        api_key, base_url = load_config()
        system_prompt = load_system_prompt()
        client = create_client(api_key, base_url)
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)
    
    # 初始化对话历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    print("\n✅ 初始化完成，开始对话...\n")
    
    # 主对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("👤 你: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break
            
            # 检查空输入
            if not user_input:
                print("请输入有效的问题...")
                continue
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 获取 AI 回复
            print("🤖 AI: ", end='', flush=True)
            response = stream_chat(client, messages)
            
            if response:
                # 添加 AI 回复到对话历史
                messages.append({"role": "assistant", "content": response})
            else:
                # 如果 API 调用失败，移除用户消息
                messages.pop()
            
            print()  # 空行分隔
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("请重试...\n")


def main():
    """
    主程序入口
    """
    # 初始化日志系统
    logger = setup_logging()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='EasyChat 2.0 - AI聊天程序')
    parser.add_argument('--api', action='store_true', help='启动API服务器模式')
    args = parser.parse_args()
    
    if args.api:
        # API模式
        logger.info("启动API服务器模式")
        print("🚀 启动API服务器模式...")
        print("📡 服务器地址: http://localhost:8000")
        print("📋 API端点:")
        print("  - GET  /health - 健康检查")
        print("  - POST /chat   - 聊天接口")
        print("-" * 50)
        
        app = create_flask_app()
        logger.info("Flask应用启动，监听端口8000")
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        # CLI模式
        logger.info("启动CLI模式")
        run_cli_mode()


if __name__ == "__main__":
    main()