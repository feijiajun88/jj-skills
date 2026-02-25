"""
被执行人信息查询模块
数据来源：中国执行信息公开网 (zxgk.court.gov.cn)
"""

import requests
import json
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .utils import RetryWithDelay, create_session, query_logger, logger, format_date, format_money


class ExecutedPersonsQuery:
    """被执行人信息查询器"""
    
    BASE_URL = 'https://zxgk.court.gov.cn/zhixing/'
    SEARCH_URL = 'https://zxgk.court.gov.cn/zhixing/searchBzxr.zxgk'
    
    def __init__(self):
        self.session = create_session()
    
    @RetryWithDelay(max_retries=5)
    def query(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        查询被执行人信息
        
        Args:
            name: 被执行人姓名
            id_card: 身份证号
            
        Returns:
            查询结果字典
        """
        logger.info(f"开始查询被执行人信息: {name}")
        
        try:
            # 首先获取页面以获取必要的参数
            response = self.session.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            
            # 构建查询参数
            params = {
                'pName': name,
                'pCardNum': id_card,
                'selectCourtId': '',
                'pCode': '',  # 验证码，如果需要的话
            }
            
            # 发送查询请求
            response = self.session.post(
                self.SEARCH_URL,
                data=params,
                timeout=30,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': self.BASE_URL
                }
            )
            response.raise_for_status()
            
            # 解析响应
            result = self._parse_response(response.text)
            
            query_logger.log(
                platform='被执行人查询',
                status='成功' if result['has_records'] else '成功（无记录）',
                retries=0
            )
            
            logger.info(f"被执行人查询完成，发现 {result['total']} 条记录")
            return result
            
        except Exception as e:
            query_logger.log(
                platform='被执行人查询',
                status='失败',
                retries=0,
                note=str(e)
            )
            logger.error(f"查询被执行人信息失败: {str(e)}")
            raise
    
    def _parse_response(self, html_content: str) -> Dict[str, Any]:
        """解析查询响应"""
        result = {
            'has_records': False,
            'total': 0,
            'records': []
        }
        
        try:
            # 尝试解析JSON响应
            data = json.loads(html_content)
            
            if data.get('status') == 'success' and data.get('data'):
                result['has_records'] = True
                result['total'] = len(data['data'])
                result['records'] = self._format_records(data['data'])
                
        except json.JSONDecodeError:
            # 如果不是JSON，尝试解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找结果表格
            table = soup.find('table', class_='search-result')
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头
                if rows:
                    result['has_records'] = True
                    result['total'] = len(rows)
                    result['records'] = self._parse_html_records(rows)
        
        return result
    
    def _format_records(self, records: List[Dict]) -> List[Dict]:
        """格式化记录数据"""
        formatted = []
        
        for record in records:
            formatted.append({
                'case_code': record.get('caseCode', ''),
                'case_state': record.get('caseState', ''),
                'exec_court_name': record.get('execCourtName', ''),
                'party_name': record.get('partyName', ''),
                'party_card_num': record.get('partyCardNum', ''),
                'case_create_time': format_date(record.get('caseCreateTime', '')),
                'exec_money': record.get('execMoney', 0),
                'exec_money_formatted': format_money(record.get('execMoney', 0))
            })
        
        return formatted
    
    def _parse_html_records(self, rows) -> List[Dict]:
        """解析HTML表格记录"""
        records = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 5:
                records.append({
                    'case_code': cells[0].get_text(strip=True),
                    'case_state': cells[1].get_text(strip=True),
                    'exec_court_name': cells[2].get_text(strip=True),
                    'party_name': cells[3].get_text(strip=True),
                    'case_create_time': format_date(cells[4].get_text(strip=True)),
                    'exec_money': 0,
                    'exec_money_formatted': '未知'
                })
        
        return records


def query_executed_persons(name: str, id_card: str) -> Dict[str, Any]:
    """
    查询被执行人信息（便捷函数）
    
    Args:
        name: 被执行人姓名
        id_card: 身份证号
        
    Returns:
        查询结果字典
    """
    query = ExecutedPersonsQuery()
    
    try:
        return query.query(name, id_card)
    except Exception as e:
        logger.error(f"查询被执行人信息最终失败: {str(e)}")
        return {
            'has_records': False,
            'total': 0,
            'records': [],
            'error': str(e),
            'query_status': 'failed'
        }


if __name__ == '__main__':
    # 测试代码
    test_name = "张三"
    test_id = "110101199001011234"
    
    result = query_executed_persons(test_name, test_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
