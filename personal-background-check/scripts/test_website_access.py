"""
简化的司法网站访问测试脚本
用于测试网站是否可以正常访问
"""

import requests
import time
from bs4 import BeautifulSoup
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_website_access(url):
    """测试网站访问"""
    print(f"\n测试访问: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 响应大小: {len(response.content)} 字节")

        # 保存响应内容
        filename = url.split('/')[-2] + '.html'
        filepath = f'/Users/jj/CodeBuddy/skill/personal-background-check/reports/{filename}'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ 响应已保存: {filepath}")

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找输入框
        inputs = soup.find_all('input', {'type': ['text', 'text', None]})
        print(f"✓ 找到 {len(inputs)} 个文本输入框")

        for i, input_tag in enumerate(inputs[:5]):
            print(f"  输入框 {i+1}:")
            if input_tag.get('id'):
                print(f"    ID: {input_tag.get('id')}")
            if input_tag.get('name'):
                print(f"    Name: {input_tag.get('name')}")
            if input_tag.get('placeholder'):
                print(f"    Placeholder: {input_tag.get('placeholder')}")

        # 查找按钮
        buttons = soup.find_all(['button', 'input'], {'type': 'submit'}) + soup.find_all('button')
        print(f"✓ 找到 {len(buttons)} 个按钮")

        for i, btn in enumerate(buttons[:5]):
            print(f"  按钮 {i+1}:")
            if btn.get('value'):
                print(f"    Value: {btn.get('value')}")
            if btn.get_text(strip=True):
                print(f"    Text: {btn.get_text(strip=True)}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ 访问失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("司法网站访问测试")
    print("=" * 60)

    urls = [
        'https://zxgk.court.gov.cn/zhixing/',
        'https://zxgk.court.gov.cn/shixin/',
        'https://zxgk.court.gov.cn/xgl/',
    ]

    results = []
    for url in urls:
        result = test_website_access(url)
        results.append((url, result))
        time.sleep(2)  # 避免请求过于频繁

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for url, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{status}: {url}")


if __name__ == '__main__':
    main()
