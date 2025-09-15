#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本

用于验证easyEval2系统的各个组件是否正常工作。

使用方法:
    python test_system.py              # 运行所有测试
    python test_system.py --quick      # 快速测试（跳过API调用）
    python test_system.py --api-only   # 只测试API连接
"""

import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

console = Console()

def test_imports():
    """测试模块导入"""
    console.print("[blue]🔍 测试模块导入...[/blue]")
    
    tests = [
        ("config.config", "SystemConfig"),
        ("config.prompts", "EvaluationPrompts"),
        ("src.deepseek_client", "DeepSeekClient"),
        ("src.semantic_eval", "SemanticEvaluator"),
    ]
    
    results = []
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            results.append((module_name, "✓", "green"))
        except Exception as e:
            results.append((module_name, f"✗ {e}", "red"))
    
    # 显示结果
    table = Table(title="模块导入测试", show_header=True)
    table.add_column("模块", style="cyan")
    table.add_column("状态", style="white")
    
    for module, status, color in results:
        table.add_row(module, f"[{color}]{status}[/{color}]")
    
    console.print(table)
    return all("✓" in result[1] for result in results)

def test_config():
    """测试配置加载"""
    console.print("\n[blue]⚙️  测试配置加载...[/blue]")
    
    try:
        from config.config import SystemConfig
        config = SystemConfig()
        
        # 检查关键配置
        checks = [
            ("DeepSeek API Key", bool(config.deepseek.api_key and config.deepseek.api_key != "your_deepseek_api_key_here")),
            ("DeepSeek Base URL", bool(config.deepseek.base_url)),
            ("DeepSeek Model", bool(config.deepseek.model)),
            ("EasyChat URL", bool(config.easychat.url)),
            ("Request Timeout", config.request.timeout > 0),
            ("Max Retries", config.request.max_retries > 0),
        ]
        
        table = Table(title="配置检查", show_header=True)
        table.add_column("配置项", style="cyan")
        table.add_column("状态", style="white")
        table.add_column("值", style="dim")
        
        all_passed = True
        for name, passed in checks:
            if passed:
                table.add_row(name, "[green]✓[/green]", "已配置")
            else:
                table.add_row(name, "[red]✗[/red]", "未配置或无效")
                all_passed = False
        
        console.print(table)
        
        if not all_passed:
            console.print("[yellow]⚠️  请检查.env文件中的配置[/yellow]")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ 配置加载失败: {e}[/red]")
        return False

def test_test_cases():
    """测试测试用例文件"""
    console.print("\n[blue]📋 测试测试用例文件...[/blue]")
    
    try:
        from src.semantic_eval import SemanticEvaluator
        evaluator = SemanticEvaluator()
        
        test_file = "tests/test_cases.json"
        if not os.path.exists(test_file):
            console.print(f"[red]❌ 测试用例文件不存在: {test_file}[/red]")
            return False
        
        test_cases = evaluator.load_test_cases(test_file)
        
        # 统计信息
        total = len(test_cases)
        categories = {}
        scenarios = {}
        priorities = {}
        
        for case in test_cases:
            cat = case.category
            categories[cat] = categories.get(cat, 0) + 1
            
            scen = case.scenario
            scenarios[scen] = scenarios.get(scen, 0) + 1
            
            prio = case.priority
            priorities[prio] = priorities.get(prio, 0) + 1
        
        # 显示统计
        table = Table(title="测试用例统计", show_header=True)
        table.add_column("类型", style="cyan")
        table.add_column("数量", style="green")
        
        table.add_row("总数", str(total))
        table.add_row("分类数", str(len(categories)))
        table.add_row("场景数", str(len(scenarios)))
        table.add_row("优先级数", str(len(priorities)))
        
        console.print(table)
        
        # 显示详细分布
        console.print("\n[dim]分类分布:[/dim]")
        for cat, count in categories.items():
            console.print(f"  • {cat}: {count}")
        
        console.print("\n[dim]场景分布:[/dim]")
        for scen, count in scenarios.items():
            console.print(f"  • {scen}: {count}")
        
        return total > 0
        
    except Exception as e:
        console.print(f"[red]❌ 测试用例加载失败: {e}[/red]")
        return False

def test_api_connection():
    """测试API连接"""
    console.print("\n[blue]🌐 测试API连接...[/blue]")
    
    try:
        from config.config import SystemConfig
        from src.deepseek_client import DeepSeekClient
        
        config = SystemConfig()
        client = DeepSeekClient()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("连接DeepSeek API...", total=None)
            
            success = client.test_connection()
            
            if success:
                progress.update(task, description="✓ DeepSeek API连接成功")
                console.print("[green]✓ API连接正常[/green]")
                return True
            else:
                progress.update(task, description="✗ DeepSeek API连接失败")
                console.print("[red]✗ API连接失败[/red]")
                console.print("[yellow]请检查API密钥和网络连接[/yellow]")
                return False
                
    except Exception as e:
        console.print(f"[red]❌ API测试失败: {e}[/red]")
        return False

def test_evaluation_flow():
    """测试评估流程"""
    console.print("\n[blue]🔄 测试评估流程...[/blue]")
    
    try:
        from config.config import SystemConfig
        from src.semantic_eval import SemanticEvaluator, TestCase
        
        config = SystemConfig()
        evaluator = SemanticEvaluator()
        
        # 创建一个简单的测试用例
        test_case = TestCase(
            id="test_flow",
            question="你好，请介绍一下自己",
            category="greeting",
            scenario="general",
            expected_aspects=["礼貌回应", "自我介绍"],
            priority="medium"
        )
        
        console.print("[dim]使用测试用例:[/dim]")
        console.print(f"  问题: {test_case.question}")
        console.print(f"  场景: {test_case.scenario}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("执行评估...", total=None)
            
            # 注意：这里会实际调用API
            result = evaluator.evaluate_single(test_case)
            
            progress.update(task, description="✓ 评估完成")
        
        if result:
            console.print("[green]✓ 评估流程正常[/green]")
            console.print(f"[dim]评估分数: {result.semantic_score}[/dim]")
            return True
        else:
            console.print("[red]✗ 评估流程失败[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ 评估流程测试失败: {e}[/red]")
        return False

def run_all_tests(quick_mode=False, api_only=False):
    """运行所有测试"""
    console.print(Panel(
        "[bold blue]easyEval2 系统测试[/bold blue]\n" +
        "验证系统各组件功能是否正常",
        border_style="blue"
    ))
    
    results = []
    
    if not api_only:
        # 基础测试
        results.append(("模块导入", test_imports()))
        results.append(("配置加载", test_config()))
        results.append(("测试用例", test_test_cases()))
    
    if not quick_mode:
        # API测试
        results.append(("API连接", test_api_connection()))
        
        # 如果API连接成功，测试评估流程
        if results and results[-1][1]:  # 如果API连接成功
            if not api_only:  # 只有在非API-only模式下才测试评估流程
                results.append(("评估流程", test_evaluation_flow()))
    
    # 显示总结
    console.print("\n" + "="*50)
    console.print("[bold]测试结果总结[/bold]")
    
    table = Table(show_header=True)
    table.add_column("测试项", style="cyan")
    table.add_column("结果", style="white")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        if success:
            table.add_row(test_name, "[green]✓ 通过[/green]")
            passed += 1
        else:
            table.add_row(test_name, "[red]✗ 失败[/red]")
    
    console.print(table)
    
    # 总体状态
    if passed == total:
        console.print(f"\n[green]🎉 所有测试通过 ({passed}/{total})[/green]")
        console.print("[green]系统可以正常使用！[/green]")
    else:
        console.print(f"\n[yellow]⚠️  部分测试失败 ({passed}/{total})[/yellow]")
        console.print("[yellow]请检查失败的项目并修复相关问题[/yellow]")
    
    return passed == total

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='easyEval2 系统测试')
    parser.add_argument('--quick', action='store_true', help='快速测试（跳过API调用）')
    parser.add_argument('--api-only', action='store_true', help='只测试API连接')
    
    args = parser.parse_args()
    
    try:
        success = run_all_tests(quick_mode=args.quick, api_only=args.api_only)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  测试被用户中断[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ 测试过程中发生错误: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()