#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
easyEval2 主运行脚本

提供命令行接口，支持多种运行模式和配置选项。

使用示例:
    python main.py                          # 使用默认配置运行
    python main.py --test-file custom.json  # 指定测试文件
    python main.py --output results.json    # 指定输出文件
    python main.py --verbose                # 详细输出模式
    python main.py --dry-run                # 干运行模式（不调用API）
    python main.py --scenario knowledge     # 指定评估场景
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config import SystemConfig
from src.semantic_eval import SemanticEvaluator
from src.deepseek_client import DeepSeekClient
from src.local_api_client import LocalAPIClient

console = Console()

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='easyEval2 - 语义相似度评估系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                                    # 默认运行
  %(prog)s --test-file tests/custom.json     # 指定测试文件
  %(prog)s --output results/eval.json        # 指定输出文件
  %(prog)s --verbose                         # 详细输出
  %(prog)s --dry-run                         # 干运行（测试配置）
  %(prog)s --scenario knowledge              # 指定评估场景
  %(prog)s --limit 10                       # 限制测试数量
        """
    )
    
    # 输入输出选项
    parser.add_argument(
        '-t', '--test-file',
        type=str,
        default='tests/test_cases.json',
        help='测试用例文件路径 (默认: tests/test_cases.json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='输出文件路径 (默认: 自动生成时间戳文件名)'
    )
    
    # 运行模式选项
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='启用详细输出模式'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='干运行模式，只验证配置不实际调用API'
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        choices=['general', 'knowledge', 'creative', 'technical'],
        help='强制指定评估场景（覆盖测试用例中的设置）'
    )
    
    # 限制选项
    parser.add_argument(
        '--limit',
        type=int,
        help='限制处理的测试用例数量'
    )
    
    parser.add_argument(
        '--skip',
        type=int,
        default=0,
        help='跳过前N个测试用例'
    )
    
    # API选择选项
    parser.add_argument(
        '--use-local-api',
        action='store_true',
        help='使用本地EasyChat API服务器进行评估（默认使用DeepSeek API）'
    )
    
    parser.add_argument(
        '--local-api-url',
        type=str,
        default='http://localhost:8000',
        help='本地API服务器地址（默认: http://localhost:8000）'
    )
    
    # 过滤选项
    parser.add_argument(
        '--category',
        type=str,
        help='只处理指定分类的测试用例'
    )
    
    parser.add_argument(
        '--priority',
        type=str,
        choices=['high', 'medium', 'low'],
        help='只处理指定优先级的测试用例'
    )
    
    # 配置选项
    parser.add_argument(
        '--config',
        type=str,
        help='指定配置文件路径'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='不显示评估摘要'
    )
    
    return parser

def print_banner():
    """打印程序横幅"""
    banner = Text()
    banner.append("easyEval2", style="bold blue")
    banner.append(" - 语义相似度评估系统\n", style="bold")
    banner.append("基于DeepSeek AI的智能对话质量评估工具", style="dim")
    
    console.print(Panel(
        banner,
        border_style="blue",
        padding=(1, 2)
    ))

def validate_args(args):
    """验证命令行参数"""
    errors = []
    
    # 检查测试文件
    if not os.path.exists(args.test_file):
        errors.append(f"测试文件不存在: {args.test_file}")
    
    # 检查输出目录
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                console.print(f"[green]✓[/green] 创建输出目录: {output_dir}")
            except Exception as e:
                errors.append(f"无法创建输出目录 {output_dir}: {e}")
    
    # 检查配置文件
    if args.config and not os.path.exists(args.config):
        errors.append(f"配置文件不存在: {args.config}")
    
    # 检查数值参数
    if args.limit is not None and args.limit <= 0:
        errors.append("limit 参数必须大于0")
    
    if args.skip < 0:
        errors.append("skip 参数不能为负数")
    
    return errors

def print_config_info(config, args):
    """打印配置信息"""
    table = Table(title="配置信息", show_header=True, header_style="bold magenta")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")
    
    # 基本配置
    table.add_row("测试文件", args.test_file)
    table.add_row("输出文件", args.output or "自动生成")
    table.add_row("详细模式", "是" if args.verbose else "否")
    table.add_row("干运行模式", "是" if args.dry_run else "否")
    
    # API配置
    table.add_row("DeepSeek模型", config.deepseek.model)
    table.add_row("API基础URL", config.deepseek.base_url)
    table.add_row("最大重试次数", str(config.request.max_retries))
    table.add_row("请求超时", f"{config.request.timeout}秒")
    
    # EasyChat配置
    table.add_row("EasyChat URL", config.easychat.url)
    table.add_row("EasyChat超时", f"{config.easychat.timeout}秒")
    
    # 过滤条件
    if args.scenario:
        table.add_row("强制场景", args.scenario)
    if args.category:
        table.add_row("分类过滤", args.category)
    if args.priority:
        table.add_row("优先级过滤", args.priority)
    if args.limit:
        table.add_row("数量限制", str(args.limit))
    if args.skip > 0:
        table.add_row("跳过数量", str(args.skip))
    
    console.print(table)
    console.print()

def run_evaluation(args, config):
    """运行评估"""
    try:
        # 创建评估器
        if args.use_local_api:
            evaluator = SemanticEvaluator(use_local_api=True, local_api_url=args.local_api_url)
        else:
            evaluator = SemanticEvaluator()
        
        # 干运行模式
        if args.dry_run:
            console.print("[yellow]🔍 干运行模式 - 验证配置...[/yellow]")
            
            # 测试API连接
            if args.use_local_api:
                client = LocalAPIClient(args.local_api_url)
                api_name = "本地EasyChat API"
            else:
                client = DeepSeekClient()
                api_name = "DeepSeek API"
                
            if client.test_connection():
                console.print(f"[green]✓[/green] {api_name}连接正常")
            else:
                console.print(f"[red]✗[/red] {api_name}连接失败")
            
            # 加载测试用例
            test_cases = evaluator.load_test_cases(args.test_file)
            console.print(f"[green]✓[/green] 成功加载 {len(test_cases)} 个测试用例")
            
            # 应用过滤条件
            filtered_cases = apply_filters(test_cases, args)
            console.print(f"[green]✓[/green] 过滤后剩余 {len(filtered_cases)} 个测试用例")
            
            console.print("[green]✓[/green] 配置验证完成，可以正常运行评估")
            return
        
        # 正常运行模式
        console.print("[blue]🚀 开始语义相似度评估...[/blue]")
        
        # 加载测试用例
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("加载测试用例...", total=None)
            test_cases = evaluator.load_test_cases(args.test_file)
            progress.update(task, description=f"✓ 加载了 {len(test_cases)} 个测试用例")
        
        # 应用过滤条件
        filtered_cases = apply_filters(test_cases, args)
        
        if len(filtered_cases) == 0:
            console.print("[red]❌ 没有符合条件的测试用例[/red]")
            return
        
        console.print(f"[green]📋 将评估 {len(filtered_cases)} 个测试用例[/green]")
        
        # 运行评估 - 带进度条
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            # 创建进度任务
            eval_task = progress.add_task("正在评估...", total=len(filtered_cases))
            
            # 定义进度回调函数
            def progress_callback(current, total, test_id):
                progress.update(
                    eval_task, 
                    completed=current + 1,
                    description=f"正在评估 {test_id} ({current + 1}/{total})"
                )
            
            # 运行评估
            results = evaluator.evaluate_batch(filtered_cases, progress_callback=progress_callback)
        
        # 生成输出文件名
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"results/evaluation_{timestamp}.json"
            os.makedirs("results", exist_ok=True)
        
        # 保存结果
        evaluator.save_results(args.output)
        md_output = args.output.replace('.json', '.md')
        console.print(f"[green]💾 JSON结果已保存到: {args.output}[/green]")
        console.print(f"[green]📄 Markdown摘要已保存到: {md_output}[/green]")
        
        # 显示摘要
        if not args.no_summary:
            evaluator.print_summary()
        
        console.print("[green]🎉 评估完成！[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  用户中断评估[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ 评估过程中发生错误: {e}[/red]")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

def apply_filters(test_cases, args):
    """应用过滤条件"""
    filtered = test_cases
    
    # 分类过滤
    if args.category:
        filtered = [tc for tc in filtered if tc.get('category') == args.category]
    
    # 优先级过滤
    if args.priority:
        filtered = [tc for tc in filtered if tc.get('priority') == args.priority]
    
    # 跳过和限制
    if args.skip > 0:
        filtered = filtered[args.skip:]
    
    if args.limit:
        filtered = filtered[:args.limit]
    
    return filtered

def main():
    """主函数"""
    # 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 打印横幅
    if not args.dry_run:
        print_banner()
    
    # 验证参数
    errors = validate_args(args)
    if errors:
        console.print("[red]❌ 参数验证失败:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        sys.exit(1)
    
    try:
        # 加载配置
        config = SystemConfig(config_file=args.config)
        
        # 显示配置信息
        if args.verbose or args.dry_run:
            print_config_info(config, args)
        
        # 运行评估
        run_evaluation(args, config)
        
    except Exception as e:
        console.print(f"[red]❌ 初始化失败: {e}[/red]")
        if args.verbose:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()