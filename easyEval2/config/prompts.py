#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统提示词管理模块
负责管理评估意图和提示词模板
"""

class EvaluationPrompts:
    """评估提示词管理类"""
    
    # 基础系统提示词
    SYSTEM_PROMPT = """
你是一个专业的对话质量评估专家。请评估AI回答与用户问题的语义相似度和质量。

评估标准：
1. 相关性(30%): 回答是否直接回应了问题
2. 准确性(25%): 回答内容是否正确
3. 完整性(20%): 回答是否完整
4. 有用性(15%): 回答是否有实际帮助
5. 表达质量(10%): 语言是否清晰流畅

请严格按照以下JSON格式返回评估结果：
{
  "score": 85,
  "reason": "评分理由的详细说明",
  "dimensions": {
    "relevance": 26,
    "accuracy": 22,
    "completeness": 18,
    "usefulness": 13,
    "expression": 8
  }
}

注意：
- score必须是0-100之间的整数
- dimensions中各项分数之和应等于总分
- reason应该简洁明了地说明评分依据
"""
    
    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """
请评估以下问答对的质量：

【用户问题】
{question}

【AI回答】
{answer}

请根据评估标准给出评分和分析。
"""
    
    # 特定场景的提示词
    SCENARIO_PROMPTS = {
        'general': {
            'name': '通用对话评估',
            'system_prompt': SYSTEM_PROMPT,
            'description': '适用于一般性对话的评估'
        },
        
        'knowledge': {
            'name': '知识问答评估',
            'system_prompt': SYSTEM_PROMPT + """

特别注意：
- 对于知识性问题，准确性权重更高
- 回答应该基于事实，避免主观臆测
- 如果涉及专业领域，要求回答具有权威性
""",
            'description': '适用于知识性问答的评估，更注重准确性'
        },
        
        'creative': {
            'name': '创意内容评估',
            'system_prompt': SYSTEM_PROMPT + """

特别注意：
- 对于创意性问题，表达质量和有用性权重更高
- 鼓励有创意和个性化的回答
- 准确性要求可以适当放宽
""",
            'description': '适用于创意性内容的评估，更注重表达和创新'
        },
        
        'technical': {
            'name': '技术问题评估',
            'system_prompt': SYSTEM_PROMPT + """

特别注意：
- 对于技术问题，准确性和完整性权重更高
- 回答应该包含具体的技术细节
- 如果有代码示例，要求语法正确
""",
            'description': '适用于技术性问题的评估，更注重准确性和完整性'
        }
    }
    
    @classmethod
    def get_system_prompt(cls, scenario='general'):
        """获取系统提示词"""
        if scenario in cls.SCENARIO_PROMPTS:
            return cls.SCENARIO_PROMPTS[scenario]['system_prompt']
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def get_user_prompt(cls, question, answer):
        """生成用户提示词"""
        return cls.USER_PROMPT_TEMPLATE.format(
            question=question,
            answer=answer
        )
    
    @classmethod
    def get_available_scenarios(cls):
        """获取可用的评估场景"""
        return {
            scenario: info['name'] 
            for scenario, info in cls.SCENARIO_PROMPTS.items()
        }
    
    @classmethod
    def get_scenario_description(cls, scenario):
        """获取场景描述"""
        if scenario in cls.SCENARIO_PROMPTS:
            return cls.SCENARIO_PROMPTS[scenario]['description']
        return "未知场景"

class PromptBuilder:
    """提示词构建器"""
    
    def __init__(self, scenario='general'):
        self.scenario = scenario
        self.prompts = EvaluationPrompts()
    
    def build_messages(self, question, answer):
        """构建完整的消息列表"""
        return [
            {
                "role": "system",
                "content": self.prompts.get_system_prompt(self.scenario)
            },
            {
                "role": "user",
                "content": self.prompts.get_user_prompt(question, answer)
            }
        ]
    
    def set_scenario(self, scenario):
        """设置评估场景"""
        if scenario in self.prompts.SCENARIO_PROMPTS:
            self.scenario = scenario
        else:
            raise ValueError(f"未知的评估场景: {scenario}")
    
    def get_current_scenario(self):
        """获取当前场景信息"""
        return {
            'scenario': self.scenario,
            'name': self.prompts.SCENARIO_PROMPTS[self.scenario]['name'],
            'description': self.prompts.get_scenario_description(self.scenario)
        }

if __name__ == '__main__':
    # 测试提示词
    builder = PromptBuilder('general')
    
    print("可用场景:")
    for scenario, name in EvaluationPrompts.get_available_scenarios().items():
        print(f"  {scenario}: {name}")
    
    print("\n当前场景:", builder.get_current_scenario())
    
    # 测试消息构建
    messages = builder.build_messages(
        "什么是人工智能？",
        "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"
    )
    
    print("\n构建的消息:")
    for i, msg in enumerate(messages):
        print(f"消息 {i+1} ({msg['role']}):")
        print(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
        print()