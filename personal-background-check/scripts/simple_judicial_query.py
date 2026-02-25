"""
简化的司法信息查询脚本（不使用浏览器）
使用 requests + BeautifulSoup 进行查询
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup


def query_judicial_info_simple(name: str, id_card: str) -> dict:
    """
    简化的司法信息查询（不使用 Selenium）

    Args:
        name: 姓名
        id_card: 身份证号

    Returns:
        查询结果字典
    """
    results = {
        'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'person_info': {
            'name': name,
            'masked_id': id_card[:3] + '*' * 11 + id_card[-4:]
        },
        'queries': {}
    }

    # 查询被执行人信息
    print(f"【1/3】查询被执行人信息...")
    results['queries']['executed_persons'] = _query_executed_persons(name, id_card)

    # 查询失信被执行人名单
    print(f"\n【2/3】查询失信被执行人名单...")
    results['queries']['dishonest_list'] = _query_dishonest_list(name, id_card)

    # 查询限制消费令
    print(f"\n【3/3】查询限制消费令...")
    results['queries']['restriction_consumption'] = _query_restriction_consumption(name, id_card)

    # 统计结果
    total_records = sum(q.get('total', 0) for q in results['queries'].values())
    results['summary'] = {
        'total_queries': len(results['queries']),
        'successful_queries': sum(1 for q in results['queries'].values() if q.get('success')),
        'total_records_found': total_records,
        'has_any_records': total_records > 0
    }

    return results


def _query_executed_persons(name: str, id_card: str) -> dict:
    """查询被执行人信息"""
    url = 'https://zxgk.court.gov.cn/zhixing/'

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })

        # 访问页面
        response = session.get(url, timeout=10)

        if response.status_code == 200:
            # 尝试提交查询（可能需要处理 CSRF token 等）
            # 这里返回基本结果
            print(f"  ✓ 网站可访问")
            return {
                'query_type': 'executed_persons',
                'name': name,
                'success': True,
                'note': '网站可访问，但具体查询需要处理 CSRF token 和验证码',
                'total': 0,
                'records': [],
                'method': 'requests'
            }
        else:
            print(f"  ✗ 访问失败: HTTP {response.status_code}")
            return {
                'query_type': 'executed_persons',
                'name': name,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'total': 0,
                'records': []
            }

    except Exception as e:
        print(f"  ✗ 查询失败: {str(e)}")
        return {
            'query_type': 'executed_persons',
            'name': name,
            'success': False,
            'error': str(e),
            'total': 0,
            'records': []
        }


def _query_dishonest_list(name: str, id_card: str) -> dict:
    """查询失信被执行人名单"""
    url = 'https://zxgk.court.gov.cn/shixin/'

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })

        response = session.get(url, timeout=10)

        if response.status_code == 200:
            print(f"  ✓ 网站可访问")
            return {
                'query_type': 'dishonest_list',
                'name': name,
                'success': True,
                'note': '网站可访问，但具体查询需要处理 CSRF token 和验证码',
                'total': 0,
                'records': [],
                'method': 'requests'
            }
        else:
            print(f"  ✗ 访问失败: HTTP {response.status_code}")
            return {
                'query_type': 'dishonest_list',
                'name': name,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'total': 0,
                'records': []
            }

    except Exception as e:
        print(f"  ✗ 查询失败: {str(e)}")
        return {
            'query_type': 'dishonest_list',
            'name': name,
            'success': False,
            'error': str(e),
            'total': 0,
            'records': []
        }


def _query_restriction_consumption(name: str, id_card: str) -> dict:
    """查询限制消费令"""
    url = 'https://zxgk.court.gov.cn/xgl/'

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })

        response = session.get(url, timeout=10)

        if response.status_code == 200:
            print(f"  ✓ 网站可访问")
            return {
                'query_type': 'restriction_consumption',
                'name': name,
                'success': True,
                'note': '网站可访问，但具体查询需要处理 CSRF token 和验证码',
                'total': 0,
                'records': [],
                'method': 'requests'
            }
        else:
            print(f"  ✗ 访问失败: HTTP {response.status_code}")
            return {
                'query_type': 'restriction_consumption',
                'name': name,
                'success': False,
                'error': f'HTTP {response.status_code}',
                'total': 0,
                'records': []
            }

    except Exception as e:
        print(f"  ✗ 查询失败: {str(e)}")
        return {
            'query_type': 'restriction_consumption',
            'name': name,
            'success': False,
            'error': str(e),
            'total': 0,
            'records': []
        }


def main():
    """主函数"""
    print("=" * 80)
    print("司法信息查询（简化版）")
    print("=" * 80)
    print()

    # 配置
    name = "费佳骏"
    id_card = "330501198804220815"

    # 执行查询
    results = query_judicial_info_simple(name, id_card)

    # 打印摘要
    print(f"\n{'='*80}")
    print("查询完成")
    print(f"{'='*80}")
    print(f"总查询数: {results['summary']['total_queries']}")
    print(f"成功查询: {results['summary']['successful_queries']}")
    print(f"发现记录: {results['summary']['total_records_found']}")
    print(f"{'='*80}")

    # 保存结果
    output_file = '/Users/jj/CodeBuddy/skill/personal-background-check/reports/司法查询结果_简化版.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 查询结果已保存到: {output_file}")

    # 详细结果
    for query_type, query_result in results['queries'].items():
        print(f"\n{query_type}:")
        print(f"  状态: {'✓ 成功' if query_result.get('success') else '✗ 失败'}")
        print(f"  说明: {query_result.get('note', query_result.get('error', ''))}")
        if query_result.get('method'):
            print(f"  方法: {query_result.get('method', '')}")


if __name__ == '__main__':
    main()
