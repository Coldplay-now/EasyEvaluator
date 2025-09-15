#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义评估引擎模块
负责核心的语义相似度评估逻辑
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from config.config import config
from src.deepseek_client import DeepSeekClient
from src.local_api_client import LocalAPIClient

@dataclass
class TestCase:
    """测试用例数据类"""
    id: str
    question: str
    category: str = "general"
    expected_aspects: List[str] = None
    priority: str = "medium"
    scenario: str = "general"
    
    def __post_init__(self):
        if self.expected_aspects is None:
            self.expected_aspects = []

@dataclass
class EvaluationResult:
    """评估结果数据类"""
    test_id: str
    question: str
    answer: str
    semantic_score: int
    evaluation_reason: str
    dimension_scores: Dict[str, int]
    scenario: str
    timestamp: str
    api_response_time: float = 0.0
    raw_response: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

class SemanticEvaluator:
    """语义评估器"""
    
    def __init__(self, use_local_api: bool = False, local_api_url: str = "http://localhost:8000"):
        """初始化评估器
        
        Args:
            use_local_api: 是否使用本地API客户端
            local_api_url: 本地API服务器地址
        """
        self.logger = logging.getLogger(__name__)
        
        # 根据参数选择客户端
        if use_local_api:
            self.api_client = LocalAPIClient(local_api_url)
            self.logger.info(f"使用本地API客户端: {local_api_url}")
        else:
            self.api_client = DeepSeekClient()
            self.logger.info("使用DeepSeek API客户端")
            
        # 保持向后兼容性
        self.deepseek_client = self.api_client if not use_local_api else None
        
        self.results: List[EvaluationResult] = []
        
        # 统计信息
        self.stats = {
            'total_tests': 0,
            'completed_tests': 0,
            'failed_tests': 0,
            'average_score': 0.0,
            'total_api_time': 0.0,
            'start_time': None,
            'end_time': None
        }
        
        self.logger.info("语义评估器初始化完成")
    
    def load_test_cases(self, test_file: str) -> List[TestCase]:
        """加载测试用例"""
        
        test_path = Path(test_file)
        if not test_path.exists():
            raise FileNotFoundError(f"测试用例文件不存在: {test_file}")
        
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_cases = []
            
            # 支持两种格式：直接列表或包含test_cases字段的对象
            if isinstance(data, list):
                cases_data = data
            elif isinstance(data, dict) and 'test_cases' in data:
                cases_data = data['test_cases']
            else:
                raise ValueError("测试用例文件格式不正确")
            
            for case_data in cases_data:
                test_case = TestCase(
                    id=case_data.get('id', f"test_{len(test_cases)+1}"),
                    question=case_data['question'],
                    category=case_data.get('category', 'general'),
                    expected_aspects=case_data.get('expected_aspects', []),
                    priority=case_data.get('priority', 'medium'),
                    scenario=case_data.get('scenario', 'general')
                )
                test_cases.append(test_case)
            
            self.logger.info(f"成功加载 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            self.logger.error(f"加载测试用例失败: {str(e)}")
            raise
    
    def get_easychat_response(self, question: str) -> Optional[str]:
        """获取EasyChat的回答"""
        
        # 这里应该调用EasyChat API
        # 目前使用模拟回答进行测试
        
        import requests
        
        try:
            self.logger.debug(f"向EasyChat发送问题: {question[:50]}...")
            
            # 构建请求
            url = f"{config.easychat.url}/chat"
            payload = {
                "message": question,
                "session_id": "eval_session"
            }
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=config.easychat.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', data.get('message', ''))
                self.logger.debug(f"EasyChat回答: {answer[:50]}...")
                return answer
            else:
                self.logger.warning(f"EasyChat API返回错误状态: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"EasyChat API调用失败: {str(e)}")
            # 返回模拟回答用于测试
            return self._get_mock_answer(question)
        except Exception as e:
            self.logger.error(f"获取EasyChat回答时发生错误: {str(e)}")
            return None
    
    def _get_mock_answer(self, question: str) -> str:
        """获取模拟回答（用于测试）"""
        
        mock_answers = {
            "什么是人工智能": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            "如何学习编程": "学习编程可以从选择一门编程语言开始，比如Python，然后通过在线教程、书籍和实践项目来逐步提高技能。",
            "推荐一部电影": "我推荐《肖申克的救赎》，这是一部关于希望和友谊的经典电影，情节感人，演技出色。",
            "今天天气怎么样": "抱歉，我无法获取实时天气信息。建议您查看天气预报应用或网站获取准确的天气信息。"
        }
        
        # 简单的关键词匹配
        for key, answer in mock_answers.items():
            if key in question:
                return answer
        
        return "这是一个很好的问题，我会尽力为您提供帮助。不过我需要更多信息才能给出准确的回答。"
    
    def evaluate_single(self, test_case: TestCase) -> Optional[EvaluationResult]:
        """评估单个测试用例"""
        
        try:
            self.logger.info(f"开始评估测试用例: {test_case.id}")
            
            # 获取AI回答
            start_time = time.time()
            answer = self.get_easychat_response(test_case.question)
            
            if not answer:
                self.logger.error(f"无法获取测试用例 {test_case.id} 的回答")
                return None
            
            # 进行语义评估
            api_start_time = time.time()
            evaluation = self.api_client.evaluate_semantic_similarity(
                test_case.question, 
                answer, 
                test_case.scenario
            )
            api_response_time = time.time() - api_start_time
            
            if not evaluation:
                self.logger.error(f"测试用例 {test_case.id} 的语义评估失败")
                return None
            
            # 构建评估结果
            result = EvaluationResult(
                test_id=test_case.id,
                question=test_case.question,
                answer=answer,
                semantic_score=evaluation['score'],
                evaluation_reason=evaluation['reason'],
                dimension_scores=evaluation.get('dimensions', {}),
                scenario=test_case.scenario,
                timestamp=datetime.now().isoformat(),
                api_response_time=api_response_time,
                raw_response=evaluation.get('raw_response')
            )
            
            self.logger.info(f"测试用例 {test_case.id} 评估完成，得分: {result.semantic_score}")
            return result
            
        except Exception as e:
            self.logger.error(f"评估测试用例 {test_case.id} 时发生错误: {str(e)}")
            return None
    
    def evaluate_batch(self, test_cases: List[TestCase], 
                      progress_callback=None) -> List[EvaluationResult]:
        """批量评估测试用例"""
        
        self.logger.info(f"开始批量评估 {len(test_cases)} 个测试用例")
        
        # 初始化统计信息
        self.stats['total_tests'] = len(test_cases)
        self.stats['start_time'] = datetime.now().isoformat()
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # 评估单个用例
                result = self.evaluate_single(test_case)
                
                if result:
                    results.append(result)
                    self.stats['completed_tests'] += 1
                    self.stats['total_api_time'] += result.api_response_time
                else:
                    self.stats['failed_tests'] += 1
                
                # 进度回调 - 在评估完成后调用
                if progress_callback:
                    progress_callback(i, len(test_cases), test_case.id)
                
                # 显示进度（仅在没有进度回调时显示）
                if not progress_callback:
                    progress = (i + 1) / len(test_cases) * 100
                    self.logger.info(f"进度: {progress:.1f}% ({i+1}/{len(test_cases)})")
                
            except KeyboardInterrupt:
                self.logger.warning("用户中断评估过程")
                break
            except Exception as e:
                self.logger.error(f"处理测试用例时发生错误: {str(e)}")
                self.stats['failed_tests'] += 1
                # 即使出错也要更新进度
                if progress_callback:
                    progress_callback(i, len(test_cases), test_case.id)
                continue
        
        # 更新统计信息
        self.stats['end_time'] = datetime.now().isoformat()
        if results:
            self.stats['average_score'] = sum(r.semantic_score for r in results) / len(results)
        
        self.results = results
        self.logger.info(f"批量评估完成，成功: {len(results)}, 失败: {self.stats['failed_tests']}")
        
        return results
    
    def save_results(self, output_file: str) -> bool:
        """保存评估结果"""
        
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 构建完整的报告数据
            report_data = {
                'metadata': {
                    'evaluation_time': datetime.now().isoformat(),
                    'evaluator_version': '2.0.0',
                    'total_tests': len(self.results),
                    'statistics': self.stats
                },
                'results': [result.to_dict() for result in self.results],
                'summary': self._generate_summary()
            }
            
            # 保存JSON报告
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 生成并保存Markdown报告
            md_output_file = str(output_path).replace('.json', '.md')
            self.save_markdown_summary(md_output_file)
            
            self.logger.info(f"评估结果已保存到: {output_file}")
            self.logger.info(f"Markdown摘要已保存到: {md_output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存评估结果失败: {str(e)}")
            return False
    
    def save_markdown_summary(self, output_file: str) -> bool:
        """保存Markdown格式的评估摘要报告"""
        
        try:
            if not self.results:
                return False
            
            summary = self._generate_summary()
            md_content = self._generate_markdown_report(summary)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"保存Markdown摘要失败: {str(e)}")
            return False
    
    def _generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """生成Markdown格式的评估报告"""
        
        md_lines = []
        
        # 标题和基本信息
        md_lines.append("# 语义评估结果摘要")
        md_lines.append("")
        md_lines.append(f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"**评估器版本**: 2.0.0")
        md_lines.append("")
        
        # 总体统计
        md_lines.append("## 📊 总体统计")
        md_lines.append("")
        md_lines.append(f"- **总测试数**: {summary['total_tests']}")
        md_lines.append(f"- **平均分数**: {summary['average_score']:.1f}")
        md_lines.append(f"- **最高分数**: {summary['max_score']}")
        md_lines.append(f"- **最低分数**: {summary['min_score']}")
        md_lines.append("")
        
        # 分数分布
        md_lines.append("## 📈 分数分布")
        md_lines.append("")
        dist = summary['score_distribution']
        md_lines.append("| 等级 | 分数范围 | 数量 | 百分比 |")
        md_lines.append("|------|----------|------|--------|")
        total = summary['total_tests']
        md_lines.append(f"| 🌟 优秀 | 90-100 | {dist['excellent']} | {dist['excellent']/total*100:.1f}% |")
        md_lines.append(f"| 👍 良好 | 80-89 | {dist['good']} | {dist['good']/total*100:.1f}% |")
        md_lines.append(f"| 😐 一般 | 70-79 | {dist['average']} | {dist['average']/total*100:.1f}% |")
        md_lines.append(f"| 😕 较差 | 60-69 | {dist['poor']} | {dist['poor']/total*100:.1f}% |")
        md_lines.append(f"| 😞 很差 | 0-59 | {dist['very_poor']} | {dist['very_poor']/total*100:.1f}% |")
        md_lines.append("")
        
        # 场景统计
        md_lines.append("## 🎯 场景统计")
        md_lines.append("")
        md_lines.append("| 场景 | 测试数量 | 平均分数 |")
        md_lines.append("|------|----------|----------|")
        for scenario, stats in summary['scenario_statistics'].items():
            md_lines.append(f"| {scenario} | {stats['count']} | {stats['average_score']:.1f} |")
        md_lines.append("")
        
        # 性能指标
        md_lines.append("## ⚡ 性能指标")
        md_lines.append("")
        perf = summary['performance_metrics']
        md_lines.append(f"- **成功率**: {perf['success_rate']:.1f}%")
        md_lines.append(f"- **总API时间**: {perf['total_api_time']:.2f} 秒")
        md_lines.append(f"- **平均API时间**: {perf['average_api_time']:.2f} 秒")
        md_lines.append("")
        
        # 详细结果（仅显示前10个）
        md_lines.append("## 📋 详细结果 (前10个)")
        md_lines.append("")
        md_lines.append("| 测试ID | 场景 | 分数 | 评估理由 |")
        md_lines.append("|--------|------|------|----------|")
        
        for i, result in enumerate(self.results[:10]):
            reason_short = result.evaluation_reason[:50] + "..." if len(result.evaluation_reason) > 50 else result.evaluation_reason
            md_lines.append(f"| {result.test_id} | {result.scenario} | {result.semantic_score} | {reason_short} |")
        
        if len(self.results) > 10:
            md_lines.append(f"| ... | ... | ... | 还有 {len(self.results) - 10} 个结果 |")
        
        md_lines.append("")
        
        # 生成时间戳
        md_lines.append("---")
        md_lines.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(md_lines)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成评估摘要"""
        
        if not self.results:
            return {}
        
        scores = [r.semantic_score for r in self.results]
        
        # 分数分布
        score_distribution = {
            'excellent': len([s for s in scores if s >= 90]),
            'good': len([s for s in scores if 80 <= s < 90]),
            'average': len([s for s in scores if 70 <= s < 80]),
            'poor': len([s for s in scores if 60 <= s < 70]),
            'very_poor': len([s for s in scores if s < 60])
        }
        
        # 场景统计
        scenario_stats = {}
        for result in self.results:
            scenario = result.scenario
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {'count': 0, 'total_score': 0}
            scenario_stats[scenario]['count'] += 1
            scenario_stats[scenario]['total_score'] += result.semantic_score
        
        # 计算场景平均分
        for scenario, stats in scenario_stats.items():
            stats['average_score'] = stats['total_score'] / stats['count']
        
        return {
            'total_tests': len(self.results),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'score_distribution': score_distribution,
            'scenario_statistics': scenario_stats,
            'performance_metrics': {
                'total_api_time': self.stats['total_api_time'],
                'average_api_time': self.stats['total_api_time'] / len(self.results),
                'success_rate': len(self.results) / self.stats['total_tests'] * 100
            }
        }
    
    def print_summary(self):
        """打印评估摘要"""
        
        if not self.results:
            print("没有评估结果")
            return
        
        summary = self._generate_summary()
        
        print("\n" + "="*50)
        print("语义评估结果摘要")
        print("="*50)
        
        print(f"总测试数: {summary['total_tests']}")
        print(f"平均分数: {summary['average_score']:.1f}")
        print(f"最高分数: {summary['max_score']}")
        print(f"最低分数: {summary['min_score']}")
        
        print("\n分数分布:")
        dist = summary['score_distribution']
        print(f"  优秀 (90-100): {dist['excellent']} 个")
        print(f"  良好 (80-89):  {dist['good']} 个")
        print(f"  一般 (70-79):  {dist['average']} 个")
        print(f"  较差 (60-69):  {dist['poor']} 个")
        print(f"  很差 (0-59):   {dist['very_poor']} 个")
        
        print("\n场景统计:")
        for scenario, stats in summary['scenario_statistics'].items():
            print(f"  {scenario}: {stats['count']} 个测试，平均分 {stats['average_score']:.1f}")
        
        print("\n性能指标:")
        perf = summary['performance_metrics']
        print(f"  成功率: {perf['success_rate']:.1f}%")
        print(f"  总API时间: {perf['total_api_time']:.2f} 秒")
        print(f"  平均API时间: {perf['average_api_time']:.2f} 秒")
        
        print("="*50)

def main():
    """主函数"""
    
    import argparse
    import sys
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, config.log.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log.file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='语义相似度评估工具')
    parser.add_argument('--test-file', '-t', 
                       default='tests/test_cases.json',
                       help='测试用例文件路径')
    parser.add_argument('--output', '-o',
                       default=None,
                       help='输出文件路径')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 创建评估器
        evaluator = SemanticEvaluator()
        
        # 测试API连接
        print("测试DeepSeek API连接...")
        if not evaluator.deepseek_client.test_connection():
            print("❌ API连接失败，请检查配置")
            return 1
        print("✅ API连接正常")
        
        # 加载测试用例
        print(f"\n加载测试用例: {args.test_file}")
        test_cases = evaluator.load_test_cases(args.test_file)
        print(f"✅ 成功加载 {len(test_cases)} 个测试用例")
        
        # 进度回调函数
        def progress_callback(current, total, test_id):
            progress = (current + 1) / total * 100
            print(f"\r进度: {progress:.1f}% - 正在评估: {test_id}", end='', flush=True)
        
        # 开始评估
        print("\n开始语义评估...")
        results = evaluator.evaluate_batch(test_cases, progress_callback)
        print()  # 换行
        
        # 显示摘要
        evaluator.print_summary()
        
        # 保存结果
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"results/semantic_eval_{timestamp}.json"
        
        if evaluator.save_results(output_file):
            print(f"\n✅ 评估结果已保存到: {output_file}")
        else:
            print("\n❌ 保存评估结果失败")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n用户中断评估")
        return 1
    except Exception as e:
        print(f"\n❌ 评估过程发生错误: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())