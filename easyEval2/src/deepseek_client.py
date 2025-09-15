#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API客户端模块
负责封装API调用逻辑和处理认证
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from config.config import config

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.logger = logging.getLogger(__name__)
        
        # 验证API密钥
        if not config.deepseek.api_key:
            raise ValueError("DeepSeek API密钥未配置，请检查.env文件")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=config.deepseek.api_key,
            base_url=config.deepseek.base_url
        )
        
        self.model = config.deepseek.model
        self.max_retries = config.request.max_retries
        self.request_timeout = config.request.timeout
        self.request_interval = config.request.interval
        
        self.logger.info(f"DeepSeek客户端初始化完成，模型: {self.model}")
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.1,
                       max_tokens: Optional[int] = None) -> Optional[str]:
        """发送聊天完成请求"""
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"发送API请求，尝试 {attempt + 1}/{self.max_retries}")
                
                # 构建请求参数
                request_params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": self.request_timeout
                }
                
                if max_tokens:
                    request_params["max_tokens"] = max_tokens
                
                # 发送请求
                response = self.client.chat.completions.create(**request_params)
                
                # 提取回复内容
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    self.logger.debug(f"API请求成功，返回内容长度: {len(content) if content else 0}")
                    
                    # 请求间隔
                    if self.request_interval > 0:
                        time.sleep(self.request_interval)
                    
                    return content
                else:
                    self.logger.warning("API返回空响应")
                    return None
                    
            except Exception as e:
                self.logger.error(f"API请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # 指数退避
                    wait_time = (2 ** attempt) * self.request_interval
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.logger.error("所有重试均失败")
                    return None
        
        return None
    
    def evaluate_semantic_similarity(self, question: str, answer: str, 
                                   scenario: str = 'general') -> Optional[Dict[str, Any]]:
        """评估语义相似度"""
        
        from config.prompts import PromptBuilder
        
        try:
            # 构建提示词
            prompt_builder = PromptBuilder(scenario)
            messages = prompt_builder.build_messages(question, answer)
            
            self.logger.info(f"开始评估语义相似度，场景: {scenario}")
            self.logger.debug(f"问题: {question[:100]}...")
            self.logger.debug(f"回答: {answer[:100]}...")
            
            # 发送API请求
            response_content = self.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            if not response_content:
                self.logger.error("API请求失败，无法获取评估结果")
                return None
            
            # 解析JSON响应
            try:
                result = json.loads(response_content)
                
                # 验证响应格式
                if not self._validate_evaluation_result(result):
                    self.logger.error("API返回的评估结果格式不正确")
                    return None
                
                self.logger.info(f"评估完成，得分: {result.get('score', 0)}")
                return result
                
            except json.JSONDecodeError as e:
                self.logger.error(f"解析API响应JSON失败: {str(e)}")
                self.logger.debug(f"原始响应: {response_content}")
                
                # 尝试提取分数（降级处理）
                return self._extract_score_fallback(response_content)
                
        except Exception as e:
            self.logger.error(f"评估过程发生错误: {str(e)}")
            return None
    
    def _validate_evaluation_result(self, result: Dict[str, Any]) -> bool:
        """验证评估结果格式"""
        
        # 检查必需字段
        required_fields = ['score', 'reason']
        for field in required_fields:
            if field not in result:
                self.logger.error(f"缺少必需字段: {field}")
                return False
        
        # 检查分数范围
        score = result.get('score')
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            self.logger.error(f"分数超出范围 [0-100]: {score}")
            return False
        
        # 检查维度分数（可选）
        if 'dimensions' in result:
            dimensions = result['dimensions']
            if not isinstance(dimensions, dict):
                self.logger.error("dimensions字段格式错误")
                return False
            
            # 检查维度分数总和
            total_dimension_score = sum(dimensions.values())
            if abs(total_dimension_score - score) > 1:  # 允许1分的误差
                self.logger.warning(f"维度分数总和({total_dimension_score})与总分({score})不匹配")
        
        return True
    
    def _extract_score_fallback(self, content: str) -> Optional[Dict[str, Any]]:
        """降级处理：从文本中提取分数"""
        
        import re
        
        try:
            # 尝试提取分数
            score_patterns = [
                r'"score"\s*:\s*(\d+)',
                r'分数[：:](\d+)',
                r'得分[：:](\d+)',
                r'(\d+)分'
            ]
            
            for pattern in score_patterns:
                match = re.search(pattern, content)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 100:
                        self.logger.info(f"降级处理成功，提取分数: {score}")
                        return {
                            'score': score,
                            'reason': '降级处理提取的分数',
                            'raw_response': content
                        }
            
            self.logger.error("无法从响应中提取有效分数")
            return None
            
        except Exception as e:
            self.logger.error(f"降级处理失败: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """测试API连接"""
        
        try:
            self.logger.info("测试DeepSeek API连接...")
            
            test_messages = [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'连接测试成功'"}
            ]
            
            response = self.chat_completion(test_messages, temperature=0)
            
            if response and "连接测试成功" in response:
                self.logger.info("API连接测试成功")
                return True
            else:
                self.logger.warning(f"API连接测试异常，响应: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"API连接测试失败: {str(e)}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """获取客户端信息"""
        
        return {
            'model': self.model,
            'base_url': config.deepseek.base_url,
            'max_retries': self.max_retries,
            'request_timeout': self.request_timeout,
            'request_interval': self.request_interval,
            'api_key_configured': bool(config.deepseek.api_key)
        }

if __name__ == '__main__':
    # 测试客户端
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = DeepSeekClient()
        
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