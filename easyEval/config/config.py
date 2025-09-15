#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
easyEval 配置文件
用于管理评估系统的各项配置参数
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
EASYCHAT_ROOT = PROJECT_ROOT.parent / "easychat"

# 文件路径配置
CONFIG = {
    # 基础路径
    "project_root": PROJECT_ROOT,
    "easychat_root": EASYCHAT_ROOT,
    "results_dir": PROJECT_ROOT / "results",
    "logs_dir": PROJECT_ROOT / "logs",
    "tests_dir": PROJECT_ROOT / "tests",
    
    # EasyChat 相关路径
    "easychat_main": EASYCHAT_ROOT / "main.py",
    "easychat_env": EASYCHAT_ROOT / ".env",
    
    # 测试配置
    "test_cases_file": PROJECT_ROOT / "tests" / "test_cases.json",
    "test_timeout": 30,  # 单个测试超时时间（秒）
    
    # 评估配置
    "evaluation": {
        "max_retries": 3,  # 失败重试次数
        "retry_delay": 1,  # 重试间隔（秒）
        "success_threshold": 0.8,  # 成功率阈值
        "response_timeout": 15,  # 响应超时时间（秒）
    },
    
    # 日志配置
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": PROJECT_ROOT / "logs" / "eval.log",
        "max_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
    },
    
    # 报告配置
    "report": {
        "template_dir": PROJECT_ROOT / "templates",
        "output_format": "json",  # json, html, txt
        "include_details": True,
        "timestamp_format": "%Y-%m-%d %H:%M:%S",
    }
}

# 环境变量覆盖
def load_env_overrides():
    """从环境变量加载配置覆盖"""
    env_mappings = {
        "EVAL_TIMEOUT": ("evaluation", "response_timeout"),
        "EVAL_RETRIES": ("evaluation", "max_retries"),
        "LOG_LEVEL": ("logging", "level"),
    }
    
    for env_key, (section, key) in env_mappings.items():
        if env_key in os.environ:
            value = os.environ[env_key]
            # 尝试转换数值类型
            if value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
            
            CONFIG[section][key] = value

# 初始化配置
load_env_overrides()

# 确保目录存在
for path_key in ["results_dir", "logs_dir", "tests_dir"]:
    CONFIG[path_key].mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print("easyEval 配置信息:")
    for key, value in CONFIG.items():
        print(f"{key}: {value}")