"""
工具函数模块
"""

import time
import json
import hashlib
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('background_check')


class RetryWithDelay:
    """带延迟的重试装饰器"""
    
    DEFAULT_DELAYS = [1, 2, 5, 10, 30]  # 重试间隔（秒）
    
    def __init__(self, max_retries: int = 5, delays: list = None):
        self.max_retries = max_retries
        self.delays = delays or self.DEFAULT_DELAYS
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} 在第 {attempt} 次重试后成功")
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        delay = self.delays[min(attempt, len(self.delays) - 1)]
                        logger.warning(
                            f"{func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}, "
                            f"{delay}秒后重试..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} 在 {self.max_retries} 次重试后仍然失败"
                        )
            
            raise last_exception
        
        return wrapper


def create_session() -> requests.Session:
    """创建带有重试机制的HTTP会话"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 设置默认请求头
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    
    return session


def mask_id_card(id_card: str) -> str:
    """身份证号脱敏"""
    if not id_card or len(id_card) != 18:
        return id_card
    return id_card[:3] + '*' * 11 + id_card[-4:]


def mask_phone(phone: str) -> str:
    """手机号脱敏"""
    if not phone or len(phone) != 11:
        return phone
    return phone[:3] + '*' * 4 + phone[-4:]


def mask_bank_card(card: str) -> str:
    """银行卡号脱敏"""
    if not card or len(card) < 8:
        return card
    return card[:4] + '*' * (len(card) - 8) + card[-4:]


def calculate_time_decay(record_date: str) -> float:
    """计算时间衰减系数"""
    try:
        record_dt = datetime.strptime(record_date, '%Y-%m-%d')
        now = datetime.now()
        years = (now - record_dt).days / 365.25
        
        if years <= 1:
            return 1.0
        elif years <= 2:
            return 0.8
        elif years <= 3:
            return 0.6
        elif years <= 5:
            return 0.4
        else:
            return 0.2
    except:
        return 1.0


def format_money(amount: float) -> str:
    """格式化金额"""
    if amount is None:
        return '未知'
    if amount >= 100000000:
        return f'¥{amount/100000000:.2f}亿'
    elif amount >= 10000:
        return f'¥{amount/10000:.2f}万'
    else:
        return f'¥{amount:,.2f}'


def format_date(date_str: str) -> str:
    """格式化日期"""
    if not date_str:
        return '未知'
    
    # 尝试多种日期格式
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%Y年%m月%d日']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            continue
    
    return date_str


def save_json(data: Dict[str, Any], filepath: str):
    """保存数据为JSON文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """从JSON文件加载数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def generate_report_id() -> str:
    """生成报告编号"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_suffix = hashlib.md5(
        str(time.time()).encode()
    ).hexdigest()[:6].upper()
    return f'PBC-{timestamp}-{random_suffix}'


def validate_id_card(id_card: str) -> bool:
    """验证身份证号格式"""
    if not id_card or len(id_card) != 18:
        return False
    
    # 基本格式验证
    if not id_card[:-1].isdigit():
        return False
    
    if id_card[-1] not in '0123456789Xx':
        return False
    
    # 校验码验证
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = '10X98765432'
    
    sum_value = sum(int(id_card[i]) * weights[i] for i in range(17))
    check_code = check_codes[sum_value % 11]
    
    return id_card[-1].upper() == check_code


def parse_court_case_number(case_number: str) -> Dict[str, Any]:
    """解析法院案号"""
    # 案号格式：(2023)京0101民初1234号
    import re
    pattern = r'\((\d{4})\)(.+?)(\d+)' 
    match = re.search(pattern, case_number)
    
    if match:
        return {
            'year': match.group(1),
            'court_code': match.group(2),
            'case_type': '',
            'serial_number': match.group(3)
        }
    
    return {}


class QueryLogger:
    """查询日志记录器"""
    
    def __init__(self):
        self.logs = []
    
    def log(self, platform: str, status: str, retries: int = 0, note: str = ''):
        """记录查询日志"""
        self.logs.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'platform': platform,
            'status': status,
            'retries': retries,
            'note': note
        })
    
    def get_logs(self) -> list:
        """获取所有日志"""
        return self.logs
    
    def save(self, filepath: str):
        """保存日志到文件"""
        save_json({'logs': self.logs}, filepath)


# 全局查询日志记录器
query_logger = QueryLogger()
