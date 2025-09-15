#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI对话系统生态 - 快速启动脚本

这个脚本提供了一个统一的入口点来启动和使用三个子项目：
- EasyChat: AI对话系统
- easyEval: 对话完成率评估工具
- easyEval2: 语义相似度评估工具

使用方法:
    python start.py
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional


class ProjectLauncher:
    """项目启动器"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.projects = {
            'easychat': {
                'name': 'EasyChat - AI对话系统',
                'path': self.root_dir / 'easychat',
                'main': 'main.py',
                'description': '基于DeepSeek API的流式问答程序，支持CLI和API模式'
            },
            'easyeval': {
                'name': 'easyEval - 对话完成率评估',
                'path': self.root_dir / 'easyEval' / 'src',
                'main': 'eval.py',
                'description': '快速评估对话系统的完成率和关键词匹配度'
            },
            'easyeval2': {
                'name': 'easyEval2 - 语义相似度评估',
                'path': self.root_dir / 'easyEval2',
                'main': 'main.py',
                'description': '智能语义相似度评估，支持多种评估场景和详细报告'
            }
        }
    
    def print_banner(self):
        """打印欢迎横幅"""
        print("\n" + "=" * 60)
        print("🤖 AI对话系统生态 - 快速启动工具")
        print("=" * 60)
        print("这个工具集包含完整的AI对话系统开发、测试和评估解决方案")
        print("=" * 60 + "\n")
    
    def print_menu(self):
        """打印主菜单"""
        print("📋 请选择要启动的功能：\n")
        
        print("🗣️  对话功能:")
        print("  1. EasyChat CLI模式    - 命令行交互式聊天")
        print("  2. EasyChat API模式    - 启动HTTP API服务器")
        
        print("\n📊 评估功能:")
        print("  3. easyEval 快速评估   - 对话完成率评估")
        print("  4. easyEval2 智能评估  - 语义相似度评估")
        print("  5. easyEval2 本地API   - 使用本地API进行评估")
        
        print("\n🔧 工具功能:")
        print("  6. 环境检查            - 检查依赖和配置")
        print("  7. 项目信息            - 显示项目详细信息")
        
        print("\n  0. 退出")
        print("\n" + "-" * 60)
    
    def check_environment(self):
        """检查环境和依赖"""
        print("\n🔍 检查项目环境...\n")
        
        # 检查Python版本
        python_version = sys.version_info
        print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查项目目录
        for key, project in self.projects.items():
            project_path = project['path']
            main_file = project_path / project['main']
            
            if project_path.exists() and main_file.exists():
                print(f"✅ {project['name']}: 项目文件完整")
            else:
                print(f"❌ {project['name']}: 项目文件缺失")
        
        # 检查配置文件
        config_files = [
            ('easychat/.env', 'EasyChat环境配置'),
            ('easyEval2/.env', 'easyEval2环境配置'),
            ('easychat/systemprompt.md', 'EasyChat系统提示词'),
            ('easyEval/tests/test_cases.json', 'easyEval测试用例'),
            ('easyEval2/tests/test_cases.json', 'easyEval2测试用例')
        ]
        
        print("\n📁 配置文件检查:")
        for file_path, description in config_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"✅ {description}: 存在")
            else:
                print(f"⚠️  {description}: 缺失")
        
        print("\n💡 提示: 如果有文件缺失，请参考各项目的README文件进行配置")
    
    def show_project_info(self):
        """显示项目详细信息"""
        print("\n📖 项目详细信息:\n")
        
        for key, project in self.projects.items():
            print(f"🔹 {project['name']}")
            print(f"   路径: {project['path']}")
            print(f"   描述: {project['description']}")
            print(f"   主文件: {project['main']}")
            print()
        
        print("📚 更多信息:")
        print("  - 项目总览: README.md")
        print("  - EasyChat: easychat/README.md")
        print("  - easyEval: easyEval/README.md")
        print("  - easyEval2: easyEval2/README.md")
    
    def run_project(self, project_key: str, args: list = None):
        """运行指定项目"""
        if project_key not in self.projects:
            print(f"❌ 未知项目: {project_key}")
            return False
        
        project = self.projects[project_key]
        project_path = project['path']
        main_file = project_path / project['main']
        
        if not main_file.exists():
            print(f"❌ 项目文件不存在: {main_file}")
            return False
        
        print(f"\n🚀 启动 {project['name']}...")
        print(f"📁 工作目录: {project_path}")
        
        # 构建命令
        cmd = [sys.executable, str(main_file)]
        if args:
            cmd.extend(args)
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        print("-" * 60)
        
        try:
            # 切换到项目目录并运行
            result = subprocess.run(cmd, cwd=project_path, check=False)
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断操作")
            return False
        except Exception as e:
            print(f"\n❌ 运行出错: {e}")
            return False
    
    def run_interactive(self):
        """运行交互式模式"""
        while True:
            self.print_banner()
            self.print_menu()
            
            try:
                choice = input("请输入选项 (0-7): ").strip()
                
                if choice == '0':
                    print("\n👋 感谢使用！再见！")
                    break
                
                elif choice == '1':
                    # EasyChat CLI模式
                    self.run_project('easychat')
                
                elif choice == '2':
                    # EasyChat API模式
                    self.run_project('easychat', ['--api'])
                
                elif choice == '3':
                    # easyEval 快速评估
                    self.run_project('easyeval')
                
                elif choice == '4':
                    # easyEval2 智能评估
                    print("\n🔧 easyEval2 支持多种参数，使用默认配置运行...")
                    print("💡 如需自定义参数，请直接使用: cd easyEval2 && python main.py [参数]")
                    self.run_project('easyeval2')
                
                elif choice == '5':
                    # easyEval2 本地API模式
                    print("\n⚠️  注意: 请确保EasyChat API服务器已启动 (选项2)")
                    input("按回车键继续，或Ctrl+C取消...")
                    self.run_project('easyeval2', ['--use-local-api'])
                
                elif choice == '6':
                    # 环境检查
                    self.check_environment()
                    input("\n按回车键返回主菜单...")
                
                elif choice == '7':
                    # 项目信息
                    self.show_project_info()
                    input("\n按回车键返回主菜单...")
                
                else:
                    print("\n❌ 无效选项，请重新选择")
                    input("按回车键继续...")
            
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用！再见！")
                break
            except EOFError:
                print("\n\n👋 感谢使用！再见！")
                break
    
    def run_direct(self, project: str, args: list = None):
        """直接运行指定项目（非交互模式）"""
        if project not in self.projects:
            print(f"❌ 未知项目: {project}")
            print(f"可用项目: {', '.join(self.projects.keys())}")
            return False
        
        return self.run_project(project, args)


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description='AI对话系统生态快速启动工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                           # 交互式模式
  %(prog)s easychat                  # 直接启动EasyChat CLI模式
  %(prog)s easychat -- --api         # 直接启动EasyChat API模式
  %(prog)s easyeval                  # 直接启动easyEval评估
  %(prog)s easyeval2                 # 直接启动easyEval2评估
  %(prog)s easyeval2 -- --use-local-api # 使用本地API进行评估
  %(prog)s easyeval2 -- --dry-run    # easyEval2干运行模式
        """
    )
    
    parser.add_argument(
        'project',
        nargs='?',
        choices=['easychat', 'easyeval', 'easyeval2'],
        help='要启动的项目名称（不指定则进入交互模式）'
    )
    
    return parser


def main():
    """主函数"""
    # 手动解析参数以支持 -- 分隔符
    if len(sys.argv) > 1 and sys.argv[1] in ['easychat', 'easyeval', 'easyeval2']:
        project = sys.argv[1]
        # 查找 -- 分隔符
        if '--' in sys.argv:
            separator_index = sys.argv.index('--')
            project_args = sys.argv[separator_index + 1:]
        else:
            project_args = sys.argv[2:]
        
        launcher = ProjectLauncher()
        success = launcher.run_direct(project, project_args)
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        parser = create_parser()
        parser.print_help()
        sys.exit(0)
    else:
        # 交互模式
        launcher = ProjectLauncher()
        launcher.run_interactive()


if __name__ == "__main__":
    main()