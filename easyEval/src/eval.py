#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
easyEval 核心评估脚本
实现对话完成率评估的主要逻辑
"""

import json
import time
import subprocess
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm

# 导入配置
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config import CONFIG

class EasyEvalCore:
    """easyEval 核心评估类"""
    
    def __init__(self):
        self.config = CONFIG
        self.setup_logging()
        self.results = []
        self.failed_cases = []
        self.start_time = None
        
    def setup_logging(self):
        """设置日志"""
        log_config = self.config["logging"]
        logging.basicConfig(
            level=getattr(logging, log_config["level"]),
            format=log_config["format"],
            handlers=[
                logging.FileHandler(log_config["file"]),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_test_cases(self) -> List[Dict]:
        """加载测试用例"""
        test_file = self.config["test_cases_file"]
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
            self.logger.info(f"加载了 {len(test_cases)} 个测试用例")
            return test_cases
        except FileNotFoundError:
            self.logger.error(f"测试用例文件不存在: {test_file}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"测试用例文件格式错误: {e}")
            return []
            
    def run_single_test(self, test_case: Dict) -> Dict:
        """执行单个测试用例（带重试机制）"""
        test_id = test_case.get("id", "unknown")
        prompt = test_case.get("prompt", "")
        expected_keywords = test_case.get("expected_keywords", [])
        category = test_case.get("category", "unknown")
        priority = test_case.get("priority", "medium")
        
        self.logger.info(f"执行测试用例: {test_id} [{category}]")
        
        result = {
            "test_id": test_id,
            "prompt": prompt,
            "category": category,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response": "",
            "error": None,
            "execution_time": 0,
            "retry_count": 0,
            "details": {}
        }
        
        max_retries = self.config["evaluation"].get("max_retries", 3)
        start_time = time.time()
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"重试测试用例 {test_id} (第 {attempt} 次)")
                    time.sleep(1)  # 重试前等待1秒
                
                # 执行 EasyChat
                response = self._execute_easychat(prompt)
                result["response"] = response
                result["execution_time"] = time.time() - start_time
                result["retry_count"] = attempt
                
                # 评估响应质量
                success = self._evaluate_response(response, expected_keywords)
                result["success"] = success
                
                # 记录详细信息
                keywords_found = self._check_keywords(response, expected_keywords)
                result["details"] = {
                    "response_length": len(response),
                    "keywords_found": keywords_found,
                    "keywords_count": len(keywords_found),
                    "expected_keywords_count": len(expected_keywords),
                    "has_response": len(response.strip()) > 0,
                    "response_preview": response[:100] + "..." if len(response) > 100 else response
                }
                
                # 如果成功，跳出重试循环
                if success:
                    break
                    
                # 如果不成功但有响应，也跳出循环（避免无意义重试）
                if len(response.strip()) > 0:
                    break
                    
            except Exception as e:
                result["error"] = str(e)
                result["execution_time"] = time.time() - start_time
                result["retry_count"] = attempt
                
                # 如果是最后一次尝试，记录错误并退出
                if attempt == max_retries:
                    self.logger.error(f"测试用例 {test_id} 执行失败 (已重试 {max_retries} 次): {e}")
                    break
                else:
                    self.logger.warning(f"测试用例 {test_id} 第 {attempt + 1} 次尝试失败: {e}")
            
        return result
        
    def _execute_easychat(self, prompt: str) -> str:
        """执行 EasyChat 并获取响应"""
        easychat_main = self.config["easychat_main"]
        timeout = self.config["evaluation"]["response_timeout"]
        
        # 构建命令
        cmd = ["python", str(easychat_main)]
        
        try:
            # 执行命令并传入提示
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.config["easychat_root"]
            )
            
            # 发送提示并获取响应
            stdout, stderr = process.communicate(
                input=f"{prompt}\nexit\n",
                timeout=timeout
            )
            
            if process.returncode != 0:
                raise Exception(f"EasyChat 执行失败: {stderr}")
                
            return self._extract_response(stdout)
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception(f"EasyChat 执行超时 ({timeout}秒)")
        except Exception as e:
            raise Exception(f"执行 EasyChat 时出错: {e}")
            
    def _extract_response(self, output: str) -> str:
        """从 EasyChat 输出中提取实际响应"""
        lines = output.strip().split('\n')
        response_lines = []
        
        # 简单的响应提取逻辑
        # 跳过系统提示和用户输入，提取AI响应
        for line in lines:
            line = line.strip()
            if line and not line.startswith('>'):
                response_lines.append(line)
                
        return '\n'.join(response_lines)
        
    def _evaluate_response(self, response: str, expected_keywords: List[str]) -> bool:
        """评估响应质量"""
        if not response or len(response.strip()) == 0:
            return False
            
        # 检查关键词匹配
        if expected_keywords:
            keywords_found = self._check_keywords(response, expected_keywords)
            return len(keywords_found) > 0
            
        # 如果没有指定关键词，只要有响应就算成功
        return True
        
    def _check_keywords(self, response: str, keywords: List[str]) -> List[str]:
        """检查响应中包含的关键词"""
        response_lower = response.lower()
        found_keywords = []
        
        for keyword in keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)
                
        return found_keywords
        
    def run_evaluation(self) -> Dict:
        """运行完整评估"""
        self.start_time = time.time()
        self.logger.info("开始运行评估")
        
        # 加载测试用例
        test_cases = self.load_test_cases()
        if not test_cases:
            return {"error": "没有可用的测试用例"}
            
        print(f"\n🚀 开始执行 {len(test_cases)} 个测试用例...")
        
        # 执行所有测试（带进度条）
        results = []
        failed_cases = []
        
        with tqdm(total=len(test_cases), desc="执行测试", unit="个") as pbar:
            for i, test_case in enumerate(test_cases):
                pbar.set_description(f"执行测试 [{i+1}/{len(test_cases)}]: {test_case.get('id', 'unknown')}")
                
                result = self.run_single_test(test_case)
                results.append(result)
                
                if not result["success"]:
                    failed_cases.append({
                        "id": result["test_id"],
                        "reason": result.get("error", "响应不符合预期"),
                        "details": result.get("details", {})
                    })
                
                # 更新进度条状态
                success_count = sum(1 for r in results if r["success"])
                pbar.set_postfix({
                    "成功": success_count,
                    "失败": len(results) - success_count,
                    "完成率": f"{success_count/len(results)*100:.1f}%" if results else "0%"
                })
                
                pbar.update(1)
                
                # 短暂延迟，避免过快执行
                time.sleep(0.1)
        
        # 计算统计信息
        stats = self._calculate_statistics(results)
        total_time = time.time() - self.start_time
        
        # 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "total_execution_time": total_time,
            "statistics": stats,
            "failed_cases": failed_cases,
            "results": results
        }
        
        # 保存结果
        self._save_results(report)
        
        # 显示完成信息
        print(f"\n✅ 评估完成！")
        print(f"📊 对话完成率: {stats['success_rate']:.2%}")
        print(f"⏱️  总执行时间: {total_time:.2f}秒")
        
        if failed_cases:
            print(f"❌ 失败用例数: {len(failed_cases)}")
            
        self.logger.info(f"评估完成，对话完成率: {stats['success_rate']:.2%}")
        return report
        
    def _calculate_statistics(self, results: List[Dict]) -> Dict:
        """计算详细统计信息"""
        total = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total - successful
        
        avg_time = sum(r["execution_time"] for r in results) / total if total > 0 else 0
        total_retries = sum(r.get("retry_count", 0) for r in results)
        
        # 按分类统计
        category_stats = {}
        for result in results:
            category = result.get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {"total": 0, "successful": 0, "failed": 0}
            
            category_stats[category]["total"] += 1
            if result["success"]:
                category_stats[category]["successful"] += 1
            else:
                category_stats[category]["failed"] += 1
        
        # 计算每个分类的成功率
        for category in category_stats:
            stats = category_stats[category]
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        # 按优先级统计
        priority_stats = {}
        for result in results:
            priority = result.get("priority", "medium")
            if priority not in priority_stats:
                priority_stats[priority] = {"total": 0, "successful": 0, "failed": 0}
            
            priority_stats[priority]["total"] += 1
            if result["success"]:
                priority_stats[priority]["successful"] += 1
            else:
                priority_stats[priority]["failed"] += 1
        
        # 计算每个优先级的成功率
        for priority in priority_stats:
            stats = priority_stats[priority]
            stats["success_rate"] = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
        
        # 响应时间统计
        execution_times = [r["execution_time"] for r in results if r["execution_time"] > 0]
        min_time = min(execution_times) if execution_times else 0
        max_time = max(execution_times) if execution_times else 0
        
        return {
            "total_tests": total,
            "successful_tests": successful,
            "failed_tests": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_execution_time": avg_time,
            "min_execution_time": min_time,
            "max_execution_time": max_time,
            "total_retries": total_retries,
            "threshold_met": (successful / total) >= self.config["evaluation"]["success_threshold"] if total > 0 else False,
            "category_breakdown": category_stats,
            "priority_breakdown": priority_stats
        }
        
    def _save_results(self, report: Dict):
        """保存评估结果（JSON和文本格式）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON格式报告
        json_filename = f"eval_report_{timestamp}.json"
        json_filepath = self.config["results_dir"] / json_filename
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存文本格式摘要
        txt_filename = f"eval_summary_{timestamp}.txt"
        txt_filepath = self.config["results_dir"] / txt_filename
        
        self._generate_text_summary(report, txt_filepath)
        
        self.logger.info(f"评估结果已保存到:")
        self.logger.info(f"  JSON报告: {json_filepath}")
        self.logger.info(f"  文本摘要: {txt_filepath}")
        
        return json_filepath, txt_filepath
    
    def _generate_text_summary(self, report: Dict, filepath: Path):
        """生成文本格式的评估摘要"""
        stats = report["statistics"]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("easyEval 对话完成率评估报告\n")
            f.write("=" * 60 + "\n\n")
            
            # 基本信息
            f.write(f"评估时间: {report['timestamp']}\n")
            f.write(f"总执行时间: {report.get('total_execution_time', 0):.2f}秒\n\n")
            
            # 总体统计
            f.write("📊 总体统计\n")
            f.write("-" * 30 + "\n")
            f.write(f"总测试数: {stats['total_tests']}\n")
            f.write(f"成功数: {stats['successful_tests']}\n")
            f.write(f"失败数: {stats['failed_tests']}\n")
            f.write(f"对话完成率: {stats['success_rate']:.2%}\n")
            f.write(f"平均执行时间: {stats['average_execution_time']:.2f}秒\n")
            f.write(f"最短执行时间: {stats['min_execution_time']:.2f}秒\n")
            f.write(f"最长执行时间: {stats['max_execution_time']:.2f}秒\n")
            f.write(f"总重试次数: {stats['total_retries']}\n")
            f.write(f"是否达到阈值: {'✅ 是' if stats['threshold_met'] else '❌ 否'}\n\n")
            
            # 按分类统计
            if "category_breakdown" in stats:
                f.write("📋 按分类统计\n")
                f.write("-" * 30 + "\n")
                for category, cat_stats in stats["category_breakdown"].items():
                    f.write(f"{category}:\n")
                    f.write(f"  总数: {cat_stats['total']}\n")
                    f.write(f"  成功: {cat_stats['successful']}\n")
                    f.write(f"  失败: {cat_stats['failed']}\n")
                    f.write(f"  成功率: {cat_stats['success_rate']:.2%}\n\n")
            
            # 按优先级统计
            if "priority_breakdown" in stats:
                f.write("🎯 按优先级统计\n")
                f.write("-" * 30 + "\n")
                for priority, pri_stats in stats["priority_breakdown"].items():
                    f.write(f"{priority}:\n")
                    f.write(f"  总数: {pri_stats['total']}\n")
                    f.write(f"  成功: {pri_stats['successful']}\n")
                    f.write(f"  失败: {pri_stats['failed']}\n")
                    f.write(f"  成功率: {pri_stats['success_rate']:.2%}\n\n")
            
            # 失败用例详情
            if "failed_cases" in report and report["failed_cases"]:
                f.write("❌ 失败用例详情\n")
                f.write("-" * 30 + "\n")
                for i, failed_case in enumerate(report["failed_cases"], 1):
                    f.write(f"{i}. {failed_case['id']}\n")
                    f.write(f"   原因: {failed_case['reason']}\n")
                    if "details" in failed_case and failed_case["details"]:
                        f.write(f"   详情: {failed_case['details']}\n")
                    f.write("\n")
            
            f.write("=" * 60 + "\n")
            f.write("报告生成完成\n")
        
def main():
    """主函数"""
    print("🤖 easyEval - EasyChat 对话完成率评估工具")
    print("=" * 50)
    
    evaluator = EasyEvalCore()
    report = evaluator.run_evaluation()
    
    if "error" in report:
        print(f"❌ 评估失败: {report['error']}")
        return 1
        
    stats = report["statistics"]
    
    # 显示详细统计结果
    print(f"\n📊 === 详细评估结果 === 📊")
    print(f"总测试数: {stats['total_tests']}")
    print(f"成功数: {stats['successful_tests']} ✅")
    print(f"失败数: {stats['failed_tests']} ❌")
    print(f"对话完成率: {stats['success_rate']:.2%}")
    print(f"平均执行时间: {stats['average_execution_time']:.2f}秒")
    print(f"执行时间范围: {stats['min_execution_time']:.2f}s - {stats['max_execution_time']:.2f}s")
    print(f"总重试次数: {stats['total_retries']}")
    print(f"是否达到阈值: {'✅ 是' if stats['threshold_met'] else '❌ 否'}")
    
    # 显示分类统计
    if "category_breakdown" in stats and stats["category_breakdown"]:
        print(f"\n📋 按分类统计:")
        for category, cat_stats in stats["category_breakdown"].items():
            print(f"  {category}: {cat_stats['successful']}/{cat_stats['total']} ({cat_stats['success_rate']:.1%})")
    
    # 显示优先级统计
    if "priority_breakdown" in stats and stats["priority_breakdown"]:
        print(f"\n🎯 按优先级统计:")
        for priority, pri_stats in stats["priority_breakdown"].items():
            print(f"  {priority}: {pri_stats['successful']}/{pri_stats['total']} ({pri_stats['success_rate']:.1%})")
    
    # 显示失败用例摘要
    if "failed_cases" in report and report["failed_cases"]:
        print(f"\n❌ 失败用例摘要 (前5个):")
        for i, failed_case in enumerate(report["failed_cases"][:5], 1):
            print(f"  {i}. {failed_case['id']}: {failed_case['reason']}")
        
        if len(report["failed_cases"]) > 5:
            print(f"  ... 还有 {len(report['failed_cases']) - 5} 个失败用例")
    
    print(f"\n📄 详细报告已保存到 results/ 目录")
    print("=" * 50)
    
    return 0
    
if __name__ == "__main__":
    exit(main())