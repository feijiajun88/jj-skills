"""
限制消费人员查询模块
数据来源：中国执行信息公开网 (zxgk.court.gov.cn/xgl/)
"""

import requests
import json
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from .utils import RetryWithDelay, create_session, query_logger, logger, format_date


class RestrictionConsumptionQuery:
    """限制消费人员查询器"""
    
    BASE_URL = 'https://zxgk.court.gov.cn/xgl/'
    SEARCH_URL = 'https://zxgk.court.gov.cn/xgl/searchXgl.zxgk'
    
    def __init__(self):
        self.session = create_session()
    
    @RetryWithDelay(max_retries=5)
    def query(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        查询限制消费人员名单
        
        Args:
            name: 被限制人姓名
            id_card: 身份证号
            
        Returns:
            查询结果字典
        """
        logger.info(f"开始查询限制消费名单: {name}")
        
        try:
            # 首先获取页面
            response = self.session.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            
            # 构建查询参数
            params = {
                'pName': name,
                'pCardNum': id_card,
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
                platform='限制消费查询',
                status='成功' if result['has_records'] else '成功（无记录）',
                retries=0
            )
            
            logger.info(f"限制消费查询完成，发现 {result['total']} 条记录")
            return result
            
        except Exception as e:
            query_logger.log(
                platform='限制消费查询',
                status='失败',
                retries=0,
                note=str(e)
            )
            logger.error(f"查询限制消费名单失败: {str(e)}")
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
                'case_code': record.get('caseCode', ''),  # 案号
                'court_name': record.get('courtName', ''),  # 执行法院
                'xi_name': record.get('xiName', ''),  # 被限制人姓名
                'xi_card_num': record.get('xiCardNum', ''),  # 证件号码
                'publish_date': format_date(record.get('publishDate', '')),  # 发布日期
                'limit_content': record.get('limitContent', self._get_default_limit_content())  # 限制消费内容
            })
        
        return formatted
    
    def _parse_html_records(self, rows) -> List[Dict]:
        """解析HTML表格记录"""
        records = []
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                records.append({
                    'case_code': cells[0].get_text(strip=True),
                    'court_name': cells[1].get_text(strip=True),
                    'xi_name': cells[2].get_text(strip=True),
                    'xi_card_num': '',
                    'publish_date': format_date(cells[3].get_text(strip=True)),
                    'limit_content': self._get_default_limit_content()
                })
        
        return records
    
    def _get_default_limit_content(self) -> str:
        """获取默认限制消费内容"""
        return """根据《最高人民法院关于限制被执行人高消费及有关消费的若干规定》，被执行人为自然人的，被采取限制消费措施后，不得有以下高消费及非生活和工作必需的消费行为：
（一）乘坐交通工具时，选择飞机、列车软卧、轮船二等以上舱位；
（二）在星级以上宾馆、酒店、夜总会、高尔夫球场等场所进行高消费；
（三）购买不动产或者新建、扩建、高档装修房屋；
（四）租赁高档写字楼、宾馆、公寓等场所办公；
（五）购买非经营必需车辆；
（六）旅游、度假；
（七）子女就读高收费私立学校；
（八）支付高额保费购买保险理财产品；
（九）乘坐G字头动车组列车全部座位、其他动车组列车一等以上座位等其他非生活和工作必需的消费行为。"""


def query_restriction_consumption(name: str, id_card: str) -> Dict[str, Any]:
    """
    查询限制消费人员名单（便捷函数）
    
    Args:
        name: 被限制人姓名
        id_card: 身份证号
        
    Returns:
        查询结果字典
    """
    query = RestrictionConsumptionQuery()
    
    try:
        return query.query(name, id_card)
    except Exception as e:
        logger.error(f"查询限制消费名单最终失败: {str(e)}")
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
    
    result = query_restriction_consumption(test_name, test_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
