#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
负责加载环境变量和管理系统配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class SystemConfig:
    """系统配置类"""
    
    def __init__(self, config_file=None):
        """初始化配置
        
        Args:
            config_file: 可选的配置文件路径（暂未使用）
        """
        # 重新加载环境变量（如果指定了配置文件）
        if config_file and os.path.exists(config_file):
            load_dotenv(config_file)
        
        # 初始化配置属性
        self._init_config()
    
    def _init_config(self):
        """初始化配置属性"""
        # DeepSeek API 配置
        self.deepseek = type('obj', (object,), {
            'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
            'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        })()
        
        # 请求配置
        self.request = type('obj', (object,), {
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
            'interval': float(os.getenv('REQUEST_INTERVAL', '1.0'))
        })()
        
        # EasyChat 配置
        self.easychat = type('obj', (object,), {
            'url': os.getenv('EASYCHAT_URL', 'http://localhost:8000'),
            'timeout': int(os.getenv('EASYCHAT_TIMEOUT', '10'))
        })()
        
        # 日志配置
        self.log = type('obj', (object,), {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file': project_root / os.getenv('LOG_FILE', 'logs/semantic_eval.log')
        })()
        
        # 项目路径
        self.paths = type('obj', (object,), {
            'project_root': project_root,
            'results_dir': project_root / 'results',
            'tests_dir': project_root / 'tests',
            'logs_dir': project_root / 'logs'
        })()
    
    def validate(self):
        """验证配置是否完整"""
        errors = []
        
        if not self.deepseek.api_key:
            errors.append("DEEPSEEK_API_KEY 未设置")
        
        if not self.deepseek.base_url:
            errors.append("DEEPSEEK_BASE_URL 未设置")
            
        # 创建必要的目录
        self.paths.results_dir.mkdir(exist_ok=True)
        self.paths.logs_dir.mkdir(exist_ok=True)
        
        return errors
    
    def get_summary(self):
        """获取配置摘要"""
        return {
            'deepseek_model': self.deepseek.model,
            'max_retries': self.request.max_retries,
            'request_timeout': self.request.timeout,
            'easychat_url': self.easychat.url,
            'log_level': self.log.level,
            'api_key_configured': bool(self.deepseek.api_key)
        }

# 全局配置实例
config = SystemConfig()

if __name__ == '__main__':
    # 测试配置
    errors = config.validate()
    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")
        print("配置摘要:", config.get_summary())