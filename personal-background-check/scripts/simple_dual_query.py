#!/usr/bin/env python3
"""
简化版司法信息查询脚本
只查询两个网站：
1. 中国裁判文书网 (https://wenshu.court.gov.cn)
2. 中国执行信息公开网 (https://zxgk.court.gov.cn/zhzxgk/)

特性：
- 自动重试直到查询成功
- 支持命令行参数输入姓名和身份证号
- 自动保存查询截图
- 智能反爬虫策略
"""

import os
import sys
import time
import random
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


class DualSiteJudicialQuery:
    """双站点司法信息查询器 - 自动重试直到成功"""

    # 查询网站URL
    URLS = {
        'wenshu': 'https://wenshu.court.gov.cn/',
        'zhixing': 'https://zxgk.court.gov.cn/zhzxgk/'
    }

    def __init__(self, headless: bool = False, max_attempts: int = 10):
        """
        初始化查询器
        
        Args:
            headless: 是否无头模式（默认False，可看到浏览器操作）
            max_attempts: 最大尝试次数（默认10次）
        """
        self.headless = headless
        self.max_attempts = max_attempts
        self.driver = None
        self.screenshot_dir = '/Users/jj/CodeBuddy/skill/personal-background-check/screenshots'
        self.reports_dir = '/Users/jj/CodeBuddy/skill/personal-background-check/reports'
        
        # 确保目录存在
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    def _init_chrome_driver(self) -> Optional[webdriver.Chrome]:
        """初始化Chrome浏览器驱动"""
        try:
            options = Options()

            if self.headless:
                options.add_argument('--headless=new')

            # 基础设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--window-size=1920,1080')

            # 真实用户代理
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
            ]
            options.add_argument(f'user-agent={random.choice(user_agents)}')

            # 禁用自动化控制标志
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=options)

            # 使用 CDP 命令隐藏 webdriver 特征
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
                    window.chrome = { runtime: {} };
                '''
            })

            return driver

        except Exception as e:
            print(f"✗ Chrome驱动初始化失败: {str(e)}")
            return None

    def _human_typing(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
        """模拟人类打字"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    def _random_scroll(self, times: int = 2):
        """随机滚动页面"""
        for _ in range(times):
            scroll_height = random.randint(100, 400)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            time.sleep(random.uniform(0.3, 0.6))

    def _take_screenshot(self, name: str) -> str:
        """截图保存"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.screenshot_dir, f'{name}_{timestamp}.png')
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"  → 截图失败: {str(e)}")
            return ""

    def _check_anti_crawler(self) -> Tuple[bool, str]:
        """检测是否遇到反爬虫页面，返回(是否触发, 类型)"""
        page_source = self.driver.page_source.lower()
        
        # 验证码相关
        captcha_keywords = ['验证码', 'captcha', '请输入验证码', '点击验证']
        for keyword in captcha_keywords:
            if keyword in page_source:
                return True, 'captcha'
        
        # 访问限制
        limit_keywords = ['访问频率过高', '请求过于频繁', 'ip被封', '请稍后再试']
        for keyword in limit_keywords:
            if keyword in page_source:
                return True, 'rate_limit'
        
        # 安全验证
        security_keywords = ['安全验证', '人机验证', '检测到异常访问']
        for keyword in security_keywords:
            if keyword in page_source:
                return True, 'security_check'
        
        return False, ''

    def _wait_for_page_load(self, timeout: int = 15):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(random.uniform(1, 2))
        except TimeoutException:
            pass

    def _retry_with_backoff(self, attempt: int) -> float:
        """计算重试等待时间（指数退避）"""
        # 基础延迟 + 随机抖动
        base_delay = min(2 ** attempt, 60)  # 最大60秒
        jitter = random.uniform(0, 5)
        return base_delay + jitter

    def query_wenshu(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        查询裁判文书网
        
        Args:
            name: 姓名
            id_card: 身份证号
            
        Returns:
            查询结果字典
        """
        result = {
            'site': '裁判文书网 (wenshu.court.gov.cn)',
            'name': name,
            'id_card_masked': id_card[:3] + '*' * 11 + id_card[-4:],
            'success': False,
            'records_count': 0,
            'screenshots': [],
            'attempts': 0,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n{'='*80}")
        print(f"【查询裁判文书网】{name}")
        print(f"{'='*80}")

        for attempt in range(1, self.max_attempts + 1):
            result['attempts'] = attempt
            print(f"\n尝试 #{attempt}/{self.max_attempts}")
            print("-" * 80)

            try:
                # 初始化驱动
                if self.driver is None:
                    self.driver = self._init_chrome_driver()
                    if self.driver is None:
                        raise Exception("浏览器驱动初始化失败")

                # 访问网站
                print("  → 访问裁判文书网...")
                self.driver.get(self.URLS['wenshu'])
                self._wait_for_page_load()

                # 截图
                screenshot = self._take_screenshot(f"wenshu_page_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)

                # 检测反爬虫
                is_anti_crawler, anti_type = self._check_anti_crawler()
                if is_anti_crawler:
                    print(f"  → 检测到反爬虫 ({anti_type})，等待后重试...")
                    delay = self._retry_with_backoff(attempt)
                    print(f"  → 等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                    
                    # 关闭当前驱动，重新初始化
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                    continue

                # 随机滚动
                self._random_scroll(times=2)

                # 查找搜索框（裁判文书网通常有高级搜索）
                print("  → 查找搜索框...")
                
                # 尝试多种选择器
                search_selectors = [
                    (By.ID, 'searchBtn'),
                    (By.CLASS_NAME, 'search-input'),
                    (By.XPATH, "//input[@placeholder='请输入搜索内容']"),
                    (By.XPATH, "//input[@type='text']"),
                    (By.CSS_SELECTOR, '.search-wrap input'),
                ]
                
                search_box = None
                for by, value in search_selectors:
                    try:
                        search_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, value))
                        )
                        print(f"  → 找到搜索框: {by}={value}")
                        break
                    except:
                        continue

                if search_box is None:
                    print("  → 未找到搜索框，尝试通过页面特征查找...")
                    # 打印页面部分源代码用于调试
                    page_source = self.driver.page_source[:500]
                    print(f"  → 页面内容: {page_source}...")
                    raise Exception("未找到搜索输入框")

                # 输入搜索内容
                search_box.clear()
                search_text = f"{name}"
                print(f"  → 输入搜索内容: {search_text}")
                self._human_typing(search_box, search_text)
                time.sleep(random.uniform(0.5, 1))

                # 查找并点击搜索按钮
                print("  → 点击搜索按钮...")
                button_selectors = [
                    (By.ID, 'searchBtn'),
                    (By.CLASS_NAME, 'search-btn'),
                    (By.XPATH, "//button[contains(text(),'搜索')]"),
                    (By.XPATH, "//input[@type='submit']"),
                    (By.CSS_SELECTOR, '.search-wrap button'),
                ]
                
                search_button = None
                for by, value in button_selectors:
                    try:
                        search_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by, value))
                        )
                        break
                    except:
                        continue

                if search_button:
                    search_button.click()
                else:
                    # 尝试按回车键
                    from selenium.webdriver.common.keys import Keys
                    search_box.send_keys(Keys.RETURN)

                # 等待结果
                print("  → 等待查询结果...")
                time.sleep(random.uniform(3, 5))
                self._wait_for_page_load(timeout=10)

                # 截图结果
                screenshot = self._take_screenshot(f"wenshu_result_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)

                # 分析结果
                page_source = self.driver.page_source
                
                # 检查是否无结果
                no_result_keywords = ['暂无数据', '没有找到', '0条', '共0条']
                has_no_result = any(keyword in page_source for keyword in no_result_keywords)
                
                # 检查是否有结果
                result_keywords = ['共', '条', '裁判文书', '搜索结果']
                has_result = any(keyword in page_source for keyword in result_keywords) and not has_no_result

                if has_no_result:
                    print("  → ✓ 查询成功，无相关裁判文书")
                    result['success'] = True
                    result['records_count'] = 0
                    result['status'] = '查询成功，无记录'
                    return result

                if has_result:
                    print("  → ✓ 查询成功，发现相关裁判文书")
                    result['success'] = True
                    result['status'] = '查询成功，有记录'
                    
                    # 尝试提取记录数
                    import re
                    count_match = re.search(r'共\s*([\d,]+)\s*条', page_source)
                    if count_match:
                        result['records_count'] = int(count_match.group(1).replace(',', ''))
                    
                    return result

                # 如果无法确定状态，继续重试
                print("  → 无法确定查询结果，继续重试...")
                delay = self._retry_with_backoff(attempt)
                time.sleep(delay)

            except Exception as e:
                error_msg = str(e)
                print(f"  → 查询出错: {error_msg}")
                result['error'] = error_msg
                
                # 截图错误
                screenshot = self._take_screenshot(f"wenshu_error_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)
                
                # 关闭驱动，下次重试时重新初始化
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                # 等待后重试
                delay = self._retry_with_backoff(attempt)
                print(f"  → 等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)

        # 所有尝试都失败
        result['error'] = f"经过{self.max_attempts}次尝试后仍未成功"
        result['status'] = '查询失败'
        return result

    def query_zhixing(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        查询执行信息公开网
        
        Args:
            name: 姓名
            id_card: 身份证号
            
        Returns:
            查询结果字典
        """
        result = {
            'site': '执行信息公开网 (zxgk.court.gov.cn)',
            'name': name,
            'id_card_masked': id_card[:3] + '*' * 11 + id_card[-4:],
            'success': False,
            'records_count': 0,
            'screenshots': [],
            'attempts': 0,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n{'='*80}")
        print(f"【查询执行信息公开网】{name}")
        print(f"{'='*80}")

        for attempt in range(1, self.max_attempts + 1):
            result['attempts'] = attempt
            print(f"\n尝试 #{attempt}/{self.max_attempts}")
            print("-" * 80)

            try:
                # 初始化驱动
                if self.driver is None:
                    self.driver = self._init_chrome_driver()
                    if self.driver is None:
                        raise Exception("浏览器驱动初始化失败")

                # 访问网站
                print("  → 访问执行信息公开网...")
                self.driver.get(self.URLS['zhixing'])
                self._wait_for_page_load()

                # 截图
                screenshot = self._take_screenshot(f"zhixing_page_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)

                # 检测反爬虫
                is_anti_crawler, anti_type = self._check_anti_crawler()
                if is_anti_crawler:
                    print(f"  → 检测到反爬虫 ({anti_type})，等待后重试...")
                    delay = self._retry_with_backoff(attempt)
                    print(f"  → 等待 {delay:.1f} 秒...")
                    time.sleep(delay)
                    
                    # 关闭当前驱动，重新初始化
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                    continue

                # 随机滚动
                self._random_scroll(times=2)

                # 查找姓名输入框
                print("  → 查找姓名输入框...")
                name_selectors = [
                    (By.NAME, 'pname'),
                    (By.ID, 'pname'),
                    (By.NAME, 'name'),
                    (By.ID, 'name'),
                    (By.XPATH, "//input[@placeholder='请输入姓名']"),
                ]
                
                name_input = None
                for by, value in name_selectors:
                    try:
                        name_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, value))
                        )
                        print(f"  → 找到姓名输入框: {by}={value}")
                        break
                    except:
                        continue

                if name_input is None:
                    print("  → 未找到姓名输入框，尝试通过页面特征查找...")
                    # 尝试找到第一个文本输入框
                    try:
                        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
                        for inp in inputs:
                            if inp.get_attribute('type') == 'text':
                                name_input = inp
                                print("  → 使用第一个文本输入框作为姓名输入框")
                                break
                    except Exception as e:
                        print(f"  → 查找输入框失败: {e}")
                        raise Exception("未找到姓名输入框")

                # 输入姓名
                name_input.clear()
                print(f"  → 输入姓名: {name}")
                self._human_typing(name_input, name)
                time.sleep(random.uniform(0.5, 1))

                # 查找身份证号输入框
                print("  → 查找身份证号输入框...")
                id_selectors = [
                    (By.NAME, 'cardNum'),
                    (By.ID, 'cardNum'),
                    (By.NAME, 'idcard'),
                    (By.ID, 'idcard'),
                    (By.XPATH, "//input[@placeholder='请输入身份证号']"),
                ]
                
                id_input = None
                for by, value in id_selectors:
                    try:
                        id_input = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, value))
                        )
                        print(f"  → 找到身份证输入框: {by}={value}")
                        break
                    except:
                        continue

                if id_input is None:
                    # 尝试找到第二个文本输入框
                    try:
                        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
                        text_inputs = [inp for inp in inputs if inp.get_attribute('type') == 'text']
                        if len(text_inputs) >= 2:
                            id_input = text_inputs[1]
                            print("  → 使用第二个文本输入框作为身份证输入框")
                    except Exception as e:
                        print(f"  → 查找身份证输入框失败: {e}")

                # 输入身份证号（如果找到输入框）
                if id_input:
                    id_input.clear()
                    print(f"  → 输入身份证号")
                    self._human_typing(id_input, id_card)
                    time.sleep(random.uniform(0.5, 1))

                # 查找并点击查询按钮
                print("  → 点击查询按钮...")
                button_selectors = [
                    (By.ID, 'searchBtn'),
                    (By.NAME, 'query'),
                    (By.XPATH, "//input[@type='submit']"),
                    (By.XPATH, "//button[contains(text(),'查询')]"),
                    (By.XPATH, "//input[@value='查询']"),
                ]
                
                search_button = None
                for by, value in button_selectors:
                    try:
                        search_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((by, value))
                        )
                        break
                    except:
                        continue

                if search_button:
                    search_button.click()
                    print("  → 已点击查询按钮")
                else:
                    print("  → 未找到查询按钮，尝试按回车键...")
                    from selenium.webdriver.common.keys import Keys
                    name_input.send_keys(Keys.RETURN)

                # 等待结果
                print("  → 等待查询结果...")
                time.sleep(random.uniform(3, 5))
                self._wait_for_page_load(timeout=10)

                # 截图结果
                screenshot = self._take_screenshot(f"zhixing_result_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)

                # 分析结果
                page_source = self.driver.page_source
                
                # 检查是否无结果
                no_result_keywords = ['暂无数据', '未找到', '0条', '共 0 条', '查询结果为空']
                has_no_result = any(keyword in page_source for keyword in no_result_keywords)
                
                # 检查是否有结果
                result_keywords = ['被执行人', '失信', '限制消费', '共', '条记录']
                has_result = any(keyword in page_source for keyword in result_keywords) and not has_no_result

                if has_no_result:
                    print("  → ✓ 查询成功，无相关执行信息")
                    result['success'] = True
                    result['records_count'] = 0
                    result['status'] = '查询成功，无记录'
                    return result

                if has_result:
                    print("  → ✓ 查询成功，发现相关执行信息")
                    result['success'] = True
                    result['status'] = '查询成功，有记录'
                    
                    # 尝试提取记录数
                    import re
                    count_match = re.search(r'共\s*([\d,]+)\s*条', page_source)
                    if count_match:
                        result['records_count'] = int(count_match.group(1).replace(',', ''))
                    
                    return result

                # 如果无法确定状态，继续重试
                print("  → 无法确定查询结果，继续重试...")
                delay = self._retry_with_backoff(attempt)
                time.sleep(delay)

            except Exception as e:
                error_msg = str(e)
                print(f"  → 查询出错: {error_msg}")
                result['error'] = error_msg
                
                # 截图错误
                screenshot = self._take_screenshot(f"zhixing_error_{attempt}")
                if screenshot:
                    result['screenshots'].append(screenshot)
                
                # 关闭驱动，下次重试时重新初始化
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                # 等待后重试
                delay = self._retry_with_backoff(attempt)
                print(f"  → 等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)

        # 所有尝试都失败
        result['error'] = f"经过{self.max_attempts}次尝试后仍未成功"
        result['status'] = '查询失败'
        return result

    def query_all(self, name: str, id_card: str) -> Dict[str, Any]:
        """
        查询两个网站的所有信息
        
        Args:
            name: 姓名
            id_card: 身份证号
            
        Returns:
            所有查询结果汇总
        """
        print(f"\n{'#'*80}")
        print(f"# 双站点司法信息查询")
        print(f"# 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 查询对象: {name}")
        print(f"# 身份证号: {id_card[:3]}***********{id_card[-4:]}")
        print(f"# 最大尝试次数: {self.max_attempts}")
        print(f"{'#'*80}")

        # 查询执行信息公开网
        zhixing_result = self.query_zhixing(name, id_card)
        
        # 关闭驱动，准备查询下一个网站
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        # 等待一段时间再查询下一个网站
        print(f"\n  → 等待 5-10 秒后查询下一个网站...")
        time.sleep(random.uniform(5, 10))
        
        # 查询裁判文书网
        wenshu_result = self.query_wenshu(name, id_card)
        
        # 关闭驱动
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

        # 汇总结果
        final_result = {
            'query_time': datetime.now().isoformat(),
            'person_info': {
                'name': name,
                'id_card_masked': id_card[:3] + '*' * 11 + id_card[-4:]
            },
            'queries': {
                'zhixing': zhixing_result,
                'wenshu': wenshu_result
            },
            'summary': {
                'total_sites': 2,
                'successful_sites': sum(1 for r in [zhixing_result, wenshu_result] if r.get('success')),
                'total_records': sum(r.get('records_count', 0) for r in [zhixing_result, wenshu_result]),
                'has_records': any(r.get('records_count', 0) > 0 for r in [zhixing_result, wenshu_result])
            }
        }

        # 保存结果
        self._save_result(final_result)
        
        return final_result

    def _save_result(self, result: Dict[str, Any]):
        """保存查询结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = result['person_info']['name']
        
        output_file = os.path.join(self.reports_dir, f'查询结果_{name}_{timestamp}.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 查询结果已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='双站点司法信息查询')
    parser.add_argument('--name', '-n', required=True, help='查询姓名')
    parser.add_argument('--id-card', '-i', required=True, help='查询身份证号')
    parser.add_argument('--headless', action='store_true', help='无头模式（不显示浏览器窗口）')
    parser.add_argument('--max-attempts', '-m', type=int, default=10, help='最大尝试次数（默认10）')
    
    args = parser.parse_args()
    
    # 验证身份证号格式
    if len(args.id_card) != 18:
        print("✗ 身份证号格式错误，必须为18位")
        sys.exit(1)
    
    # 创建查询器并执行查询
    query = DualSiteJudicialQuery(
        headless=args.headless,
        max_attempts=args.max_attempts
    )
    
    result = query.query_all(args.name, args.id_card)
    
    # 打印摘要
    print(f"\n{'#'*80}")
    print(f"# 查询完成")
    print(f"{'#'*80}")
    print(f"总站点数: {result['summary']['total_sites']}")
    print(f"成功查询: {result['summary']['successful_sites']}")
    print(f"总记录数: {result['summary']['total_records']}")
    
    if result['summary']['has_records']:
        print(f"⚠ 发现相关记录！")
    else:
        print(f"✓ 未发现相关记录")
    
    print(f"{'#'*80}")
    
    # 详细结果
    for site, site_result in result['queries'].items():
        print(f"\n{site}:")
        print(f"  网站: {site_result['site']}")
        print(f"  状态: {'✓ 成功' if site_result['success'] else '✗ 失败'}")
        print(f"  尝试次数: {site_result['attempts']}")
        print(f"  记录数: {site_result.get('records_count', 0)}")
        print(f"  状态描述: {site_result.get('status', 'N/A')}")
        
        if site_result.get('error'):
            print(f"  错误: {site_result['error']}")
        
        if site_result.get('screenshots'):
            print(f"  截图: {len(site_result['screenshots'])} 张")
            for screenshot in site_result['screenshots']:
                print(f"    - {screenshot}")


if __name__ == '__main__':
    main()
