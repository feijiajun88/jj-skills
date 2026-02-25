import sys
import json
import subprocess
import re
import urllib.request
import os

def get_repo_info(url):
    """
    通过 git ls-remote 和 HTTP 请求获取仓库信息。
    返回包含名称、描述、最新哈希和 README 内容的字典。
    """
    # 清理 URL（移除末尾的 .git）
    clean_url = url.rstrip('/')
    if clean_url.endswith('.git'):
        clean_url = clean_url[:-4]
    repo_name = clean_url.split('/')[-1]

    # 1. 获取最新提交哈希（使用 git ls-remote 避免完整克隆）
    try:
        result = subprocess.run(
            ['git', 'ls-remote', url, 'HEAD'],
            capture_output=True, text=True, check=True
        )
        latest_hash = result.stdout.split()[0]  # 提取哈希值
    except Exception as e:
        print(f"Error fetching git info: {e}", file=sys.stderr)
        latest_hash = "unknown"

    # 2. 获取 README 内容（依次尝试 main/master 分支）
    readme_content = ""
    readme_url_base = clean_url.replace("github.com", "raw.githubusercontent.com")
    for branch in ["main", "master"]:
        try:
            readme_url = f"{readme_url_base}/{branch}/README.md"
            with urllib.request.urlopen(readme_url) as response:
                readme_content = response.read().decode('utf-8')
            break
        except Exception:
            continue
    # 若未找到，尝试小写文件名 readme.md
    if not readme_content:
        for branch in ["main", "master"]:
            try:
                readme_url = f"{readme_url_base}/{branch}/readme.md"
                with urllib.request.urlopen(readme_url) as response:
                    readme_content = response.read().decode('utf-8')
                break
            except Exception:
                continue

    # 3. 返回结果字典
    return {
        "name": repo_name,
        "url": url,
        "latest_hash": latest_hash,
        "readme": readme_content[:10000]  # 限制 README 长度
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_github_info.py <GitHub_URL>")
        sys.exit(1)
    url = sys.argv[1]
    info = get_repo_info(url)
    print(json.dumps(info, indent=2))
