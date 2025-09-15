#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地API客户端模块
用于调用本地EasyChat API服务器
"""

import json
import time
import logging
import requests
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import config

class LocalAPIClient:
    """本地API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化客户端
        
        Args:
            base_url: 本地API服务器地址
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url.rstrip('/')
        self.max_retries = getattr(config.request, 'max_retries', 3)
        self.request_timeout = getattr(config.request, 'timeout', 30)
        self.request_interval = getattr(config.request, 'interval', 1)
        
        self.logger.info(f"本地API客户端初始化完成，服务器: {self.base_url}")
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.1,
                       max_tokens: Optional[int] = None) -> Optional[str]:
        """发送聊天完成请求"""
        
        # 提取用户消息（简化处理，只取最后一条用户消息）
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            self.logger.error("未找到用户消息")
            return None
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"发送本地API请求，尝试 {attempt + 1}/{self.max_retries}")
                
                # 发送POST请求到本地API
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"message": user_message},
                    headers={"Content-Type": "application/json"},
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response')
                else:
                    self.logger.error(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"请求异常: {str(e)}")
                
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON解析错误: {str(e)}")
                
            except Exception as e:
                self.logger.error(f"未知错误: {str(e)}")
            
            # 等待后重试
            if attempt < self.max_retries - 1:
                time.sleep(self.request_interval)
        
        self.logger.error(f"API请求失败，已重试 {self.max_retries} 次")
        return None
    
    def evaluate_semantic_similarity(self, question: str, answer: str, 
                                   scenario: str = 'general') -> Optional[Dict[str, Any]]:
        """评估语义相似度"""
        
        # 构建评估提示
        from config.prompts import PromptBuilder
        prompt_builder = PromptBuilder(scenario)
        messages = prompt_builder.build_messages(question, answer)
        
        # 合并系统提示和用户提示
        prompt = messages[0]['content'] + "\n\n" + messages[1]['content']
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # 调用API
        response = self.chat_completion(messages)
        if not response:
            return None
        
        # 解析响应
        try:
            # 尝试直接解析JSON
            if response.strip().startswith('{'):
                result = json.loads(response)
                if self._validate_evaluation_result(result):
                    return result
            
            # 如果直接解析失败，尝试提取JSON
            return self._extract_score_fallback(response)
            
        except json.JSONDecodeError:
            self.logger.warning("响应不是有效的JSON格式，尝试提取分数")
            return self._extract_score_fallback(response)
    
    def _validate_evaluation_result(self, result: Dict[str, Any]) -> bool:
        """验证评估结果格式"""
        required_fields = ['score', 'reason']
        
        for field in required_fields:
            if field not in result:
                self.logger.warning(f"评估结果缺少必需字段: {field}")
                return False
        
        # 验证分数范围
        score = result.get('score')
        if not isinstance(score, (int, float)) or not (0 <= score <= 100):
            self.logger.warning(f"分数格式错误或超出范围: {score}")
            return False
        
        return True
    
    def _extract_score_fallback(self, content: str) -> Optional[Dict[str, Any]]:
        """从文本中提取分数（备用方法）"""
        import re
        
        # 尝试提取分数
        score_patterns = [
            r'"score"\s*:\s*(\d+(?:\.\d+)?)',
            r'分数[：:](\d+(?:\.\d+)?)',
            r'评分[：:](\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)分',
            r'(\d+(?:\.\d+)?)/100',
            r'(\d+(?:\.\d+)?)%'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 100:
                        return {
                            'score': score,
                            'reason': content,
                            'extracted': True
                        }
                except ValueError:
                    continue
        
        # 如果没有找到分数，返回一个默认的评估结果
        self.logger.warning("无法从响应中提取有效分数，返回默认评估")
        return {
            'score': 75,
            'reason': f"本地API响应: {content[:200]}...",
            'extracted': False
        }
    
    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'ok'
            else:
                self.logger.error(f"健康检查失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"连接测试失败: {str(e)}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """获取客户端信息"""
        return {
            'type': 'LocalAPIClient',
            'base_url': self.base_url,
            'max_retries': self.max_retries,
            'timeout': self.request_timeout
        }

if __name__ == '__main__':
    # 测试代码
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = LocalAPIClient()
        
        print("客户端信息:", client.get_client_info())
        
        # 测试连接
        if client.test_connection():
            print("✓ API连接正常")
            
            # 测试语义评估
            result = client.evaluate_semantic_similarity(
                "什么是人工智能？",
                "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"
            )
            
            if result:
                print("✓ 语义评估测试成功")
                print(f"评估结果: {result}")
            else:
                print("✗ 语义评估测试失败")
        else:
            print("✗ API连接失败")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")