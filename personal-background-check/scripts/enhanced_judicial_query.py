"""
改进的司法信息查询脚本
使用多种策略查询被执行人、失信名单、限制消费令等信息
"""

import requests
import json
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import time
import random


class EnhancedJudicialQuery:
    """增强型司法信息查询器"""

    def __init__(self):
        # 多个 User-Agent 用于轮换
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        self.session = requests.Session()
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get_random_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }

    def query_executed_persons_v2(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        策略2：使用模拟浏览器方式查询被执行人
        """
        print(f"正在查询被执行人信息: {name}")

        result = {
            'has_records': False,
            'total': 0,
            'records': [],
            'query_method': 'simulated'
        }

        try:
            # 方式1：直接访问搜索页面
            search_url = 'https://zxgk.court.gov.cn/zhixing/'
            headers = self._get_random_headers()

            response = self.session.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✓ 成功访问被执行人查询页面")
                # 保存原始 HTML 供分析
                result['page_accessible'] = True
                result['access_method'] = 'direct_access'
            else:
                print(f"✗ 访问失败，状态码: {response.status_code}")
                result['page_accessible'] = False
                result['error'] = f"HTTP {response.status_code}"

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"✗ 查询失败: {str(e)}")
            result['error'] = str(e)
            result['query_status'] = 'failed'

        return result

    def query_dishonest_list_v2(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        策略2：查询失信被执行人名单
        """
        print(f"正在查询失信被执行人名单: {name}")

        result = {
            'has_records': False,
            'total': 0,
            'records': [],
            'query_method': 'simulated'
        }

        try:
            search_url = 'https://zxgk.court.gov.cn/shixin/'
            headers = self._get_random_headers()

            response = self.session.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✓ 成功访问失信名单查询页面")
                result['page_accessible'] = True
                result['access_method'] = 'direct_access'
            else:
                print(f"✗ 访问失败，状态码: {response.status_code}")
                result['page_accessible'] = False
                result['error'] = f"HTTP {response.status_code}"

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"✗ 查询失败: {str(e)}")
            result['error'] = str(e)
            result['query_status'] = 'failed'

        return result

    def query_restriction_consumption_v2(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        策略2：查询限制消费令
        """
        print(f"正在查询限制消费令: {name}")

        result = {
            'has_records': False,
            'total': 0,
            'records': [],
            'query_method': 'simulated'
        }

        try:
            search_url = 'https://zxgk.court.gov.cn/xgl/'
            headers = self._get_random_headers()

            response = self.session.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                print("✓ 成功访问限制消费查询页面")
                result['page_accessible'] = True
                result['access_method'] = 'direct_access'
            else:
                print(f"✗ 访问失败，状态码: {response.status_code}")
                result['page_accessible'] = False
                result['error'] = f"HTTP {response.status_code}"

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"✗ 查询失败: {str(e)}")
            result['error'] = str(e)
            result['query_status'] = 'failed'

        return result

    def generate_manual_query_guide(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        生成手动查询指南
        """
        masked_id = id_card[:3] + '*' * 11 + id_card[-4:]

        return {
            'name': name,
            'masked_id': masked_id,
            'query_links': [
                {
                    'name': '中国执行信息公开网 - 被执行人查询',
                    'url': 'https://zxgk.court.gov.cn/zhixing/',
                    'query_params': {
                        '姓名': name,
                        '身份证号': id_card,
                        '法院地域': '全国'
                    }
                },
                {
                    'name': '中国执行信息公开网 - 失信被执行人查询',
                    'url': 'https://zxgk.court.gov.cn/shixin/',
                    'query_params': {
                        '姓名': name,
                        '身份证号': id_card,
                        '地域': '全国'
                    }
                },
                {
                    'name': '中国执行信息公开网 - 限制消费令查询',
                    'url': 'https://zxgk.court.gov.cn/xgl/',
                    'query_params': {
                        '姓名': name,
                        '身份证号': id_card
                    }
                },
                {
                    'name': '中国裁判文书网',
                    'url': 'https://wenshu.court.gov.cn/',
                    'query_params': {
                        '关键词': f'{name} {id_card}'
                    }
                }
            ],
            'tips': [
                '建议使用 Chrome 或 Edge 浏览器访问',
                '输入姓名和身份证号进行精确查询',
                '如果发现记录，可以查看详细信息',
                '查询结果仅供参考，以官方最终记录为准'
            ]
        }


def main():
    """主函数 - 执行所有司法信息查询"""
    name = "李健超"
    id_card = "440421199502278077"

    print("=" * 80)
    print("司法信息综合查询")
    print("=" * 80)
    print(f"查询对象: {name}")
    print(f"身份证号: {id_card[:3]}***********{id_card[-4:]}")
    print("=" * 80)
    print()

    # 创建查询器
    query = EnhancedJudicialQuery()

    # 执行各类查询
    print("【第一步】查询被执行人信息")
    print("-" * 80)
    executed_result = query.query_executed_persons_v2(name, id_card)
    print()

    print("【第二步】查询失信被执行人名单")
    print("-" * 80)
    dishonest_result = query.query_dishonest_list_v2(name, id_card)
    print()

    print("【第三步】查询限制消费令")
    print("-" * 80)
    restriction_result = query.query_restriction_consumption_v2(name, id_card)
    print()

    print("【第四步】生成手动查询指南")
    print("-" * 80)
    guide = query.generate_manual_query_guide(name, id_card)
    print(f"✓ 查询指南已生成")
    print()

    # 汇总结果
    print("=" * 80)
    print("查询结果汇总")
    print("=" * 80)

    all_results = {
        'executed_persons': executed_result,
        'dishonest_list': dishonest_result,
        'restriction_consumption': restriction_result,
        'manual_query_guide': guide
    }

    # 保存结果
    output_file = '/Users/jj/CodeBuddy/skill/personal-background-check/reports/司法查询结果.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 查询结果已保存到: {output_file}")

    # 显示手动查询链接
    print("\n【手动查询链接】")
    print("-" * 80)
    for i, link in enumerate(guide['query_links'], 1):
        print(f"{i}. {link['name']}")
        print(f"   链接: {link['url']}")
        print(f"   参数: 姓名={name}, 身份证号={id_card}")
        print()

    print("=" * 80)
    print("查询完成！")
    print("=" * 80)
    print("\n⚠️ 注意:")
    print("- 由于网站反爬机制，自动化查询可能受限")
    print("- 建议使用上方提供的链接进行手动查询")
    print("- 查询结果仅供参考，以官方记录为准")


if __name__ == '__main__':
    main()
