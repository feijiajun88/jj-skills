#!/usr/bin/env python3
"""
AI Daily Digest 技能包装器
包装 https://github.com/vigorX777/ai-daily-digest 的功能
"""

import sys
import subprocess
import os

def main():
    """运行 AI Daily Digest 工具"""
    # 检查 bun 是否安装
    try:
        subprocess.run(['bun', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 需要先安装 Bun 运行时")
        print("安装指南: https://bun.sh/docs/installation")
        sys.exit(1)
    
    # 检查环境变量
    if not os.getenv('GEMINI_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("警告: 未设置 GEMINI_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("请先设置 API 密钥:")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("  或")
        print("  export OPENAI_API_KEY='your-api-key'")
    
    # 调用原始脚本
    # 注意: 实际使用前需要先克隆仓库
    repo_path = os.path.join(os.path.dirname(__file__), '..', 'references', 'ai-daily-digest')
    digest_script = os.path.join(repo_path, 'scripts', 'digest.ts')
    
    if not os.path.exists(digest_script):
        print(f"错误: 未找到原始仓库文件")
        print(f"请先克隆仓库到 {repo_path}:")
        print(f"  git clone https://github.com/vigorX777/ai-daily-digest.git {repo_path}")
        sys.exit(1)
    
    # 传递所有参数给原始脚本
    cmd = ['bun', digest_script] + sys.argv[1:]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
