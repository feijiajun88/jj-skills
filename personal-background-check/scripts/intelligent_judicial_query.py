"""
智能司法信息查询脚本
实现自动查询直到获得结果，使用多种策略和人类行为模拟
"""

import time
import random
import json
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import sys
from datetime import datetime

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from court_documents_selenium_query import CourtDocumentsSeleniumQuery
from captcha_handler import CaptchaHandler
from anti_crawler_strategy import create_default_strategy_manager


class IntelligentJudicialQuery:
    """智能司法信息查询器 - 自动查询直到获得结果"""

    def __init__(self, headless: bool = False, max_retries: int = 3):
        """
        初始化查询器

        Args:
            headless: 是否无头模式
            max_retries: 每个策略的最大重试次数
        """
        self.headless = headless
        self.max_retries = max_retries
        self.driver = None
        self.current_strategy = None

        # 查询URL
        self.urls = {
            'executed': 'https://zxgk.court.gov.cn/zhixing/',
            'dishonest': 'https://zxgk.court.gov.cn/shixin/',
            'restriction': 'https://zxgk.court.gov.cn/xgl/'
        }

        # 初始化裁判文书查询器
        self.court_query = CourtDocumentsSeleniumQuery(
            headless=headless,
            max_retries=max_retries
        )

    def _init_undetected_chrome(self) -> Optional[webdriver.Chrome]:
        """
        初始化 undetected-chromedriver（策略1）
        使用专业的反检测驱动
        """
        try:
            import undetected_chromedriver as uc

            options = uc.ChromeOptions()

            # 基础设置
            if self.headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')

            # 设置真实用户代理
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # 窗口大小
            options.add_argument('--window-size=1920,1080')

            driver = uc.Chrome(options=options, version_main=120)
            self.current_strategy = 'undetected_chromedriver'

            print("✓ 策略1: 使用 undetected-chromedriver 初始化成功")
            return driver

        except ImportError:
            print("✗ undetected-chromedriver 未安装，将使用标准 Selenium")
            return None
        except Exception as e:
            print(f"✗ undetected-chromedriver 初始化失败: {str(e)}")
            return None

    def _init_standard_chrome(self) -> Optional[webdriver.Chrome]:
        """
        初始化标准 Chrome（策略2）
        使用 CDP 命令隐藏自动化特征
        """
        try:
            options = Options()

            if self.headless:
                options.add_argument('--headless=new')

            # 禁用自动化特征
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')

            # 真实用户代理
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            options.add_argument('--window-size=1920,1080')

            # 禁用自动化控制标志
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=options)

            # 使用 CDP 命令隐藏 webdriver
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en']
                    });
                    
                    window.chrome = {
                        runtime: {}
                    };
                    
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({state: 'granted'})
                        })
                    });
                '''
            })

            self.current_strategy = 'standard_selenium'
            print("✓ 策略2: 使用标准 Selenium + CDP 命令初始化成功")
            return driver

        except Exception as e:
            print(f"✗ 标准 Chrome 初始化失败: {str(e)}")
            return None

    def _human_typing(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
        """
        人类打字行为模拟

        Args:
            element: 输入元素
            text: 要输入的文本
            min_delay: 最小字符间隔（秒）
            max_delay: 最大字符间隔（秒）
        """
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))

    def _human_scroll(self, scroll_times: int = 3):
        """
        人类滚动行为模拟

        Args:
            scroll_times: 滚动次数
        """
        for _ in range(scroll_times):
            scroll_height = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            time.sleep(random.uniform(0.3, 0.8))

    def _human_click_delay(self):
        """人类点击延迟"""
        time.sleep(random.uniform(0.5, 1.5))

    def _take_screenshot(self, name: str):
        """截图保存"""
        try:
            screenshot_dir = '/Users/jj/CodeBuddy/skill/personal-background-check/screenshots'
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(screenshot_dir, f'{name}_{timestamp}.png')
            self.driver.save_screenshot(filepath)
            print(f"  → 截图已保存: {filepath}")
        except Exception as e:
            print(f"  → 截图失败: {str(e)}")

    def _check_anti_crawler_page(self) -> bool:
        """检测是否遇到反爬虫页面"""
        page_source = self.driver.page_source

        # 常见反爬虫页面特征
        anti_crawler_keywords = [
            '请输入验证码',
            '验证码',
            'captcha',
            '请完成人机验证',
            '人机验证',
            '检测到异常访问',
            '安全验证',
            '访问频率过高'
        ]

        return any(keyword in page_source for keyword in anti_crawler_keywords)

    def _wait_and_load_page(self, timeout: int = 10):
        """等待页面加载完成"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(random.uniform(1, 2))
        except TimeoutException:
            print(f"  → 页面加载超时，继续尝试")

    def _find_and_input(self, by: By, value: str, text: str, wait_time: int = 10) -> bool:
        """
        查找元素并输入文本（使用人类打字行为）

        Returns:
            是否成功
        """
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            element.clear()
            self._human_typing(element, text)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"  → 未找到元素 ({by}={value}): {str(e)}")
            return False

    def _find_and_click(self, by: By, value: str, wait_time: int = 10) -> bool:
        """
        查找元素并点击（使用人类点击延迟）

        Returns:
            是否成功
        """
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((by, value))
            )
            self._human_click_delay()
            element.click()
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"  → 未找到或无法点击元素 ({by}={value}): {str(e)}")
            return False

    def query_page(self, url: str, name: str, id_card: str, query_type: str) -> Dict[str, Any]:
        """
        查询指定类型的司法信息

        Args:
            url: 查询页面URL
            name: 姓名
            id_card: 身份证号
            query_type: 查询类型（executed/dishonest/restriction）

        Returns:
            查询结果字典
        """
        result = {
            'query_type': query_type,
            'name': name,
            'id_card': id_card[:3] + '*' * 11 + id_card[-4:],
            'success': False,
            'records': [],
            'total': 0,
            'strategy_used': None,
            'attempts': 0,
            'error': None
        }

        print(f"\n{'='*80}")
        print(f"查询类型: {query_type}")
        print(f"查询对象: {name}")
        print(f"{'='*80}")

        # 策略列表
        strategies = [
            ('undetected_chromedriver', self._init_undetected_chrome),
            ('standard_selenium', self._init_standard_chrome)
        ]

        for strategy_name, init_func in strategies:
            print(f"\n【策略】{strategy_name}")
            print("-" * 80)

            # 初始化驱动
            self.driver = init_func()

            if self.driver is None:
                print(f"→ 策略 {strategy_name} 初始化失败，尝试下一个策略")
                continue

            # 多次重试
            for attempt in range(1, self.max_retries + 1):
                result['attempts'] += 1
                print(f"\n尝试 #{attempt}/{self.max_retries}")

                try:
                    # 访问页面
                    print(f"  → 访问: {url}")
                    self.driver.get(url)
                    self._wait_and_load_page()

                    # 截图
                    self._take_screenshot(f"{query_type}_page")

                    # 检测反爬虫
                    if self._check_anti_crawler_page():
                        print("  → 检测到反爬虫页面")
                        time.sleep(random.uniform(5, 10))
                        continue

                    # 人类滚动行为
                    self._human_scroll(scroll_times=2)

                    # 尝试输入姓名
                    print(f"  → 尝试输入姓名: {name}")
                    name_found = self._find_and_input(By.NAME, 'pname', name) or \
                                self._find_and_input(By.ID, 'pname', name) or \
                                self._find_and_input(By.NAME, 'name', name) or \
                                self._find_and_input(By.ID, 'name', name)

                    if not name_found:
                        print("  → 未找到姓名输入框")
                        continue

                    time.sleep(random.uniform(0.5, 1.0))

                    # 尝试输入身份证号
                    print(f"  → 尝试输入身份证号")
                    id_found = self._find_and_input(By.NAME, 'cardNum', id_card) or \
                              self._find_and_input(By.ID, 'cardNum', id_card) or \
                              self._find_and_input(By.NAME, 'idcard', id_card) or \
                              self._find_and_input(By.ID, 'idcard', id_card)

                    if not id_found:
                        print("  → 未找到身份证输入框")
                        continue

                    time.sleep(random.uniform(0.5, 1.0))

                    # 尝试点击查询按钮
                    print("  → 尝试点击查询按钮")
                    button_found = self._find_and_click(By.XPATH, "//input[@type='submit']") or \
                                  self._find_and_click(By.XPATH, "//button[contains(text(),'查询')]") or \
                                  self._find_and_click(By.XPATH, "//input[@value='查询']") or \
                                  self._find_and_click(By.ID, 'searchBtn') or \
                                  self._find_and_click(By.NAME, 'query')

                    if not button_found:
                        print("  → 未找到查询按钮")
                        continue

                    # 等待结果加载
                    print("  → 等待查询结果...")
                    time.sleep(random.uniform(3, 5))
                    self._wait_and_load_page(timeout=15)

                    # 截图结果页
                    self._take_screenshot(f"{query_type}_result")

                    # 检测是否又遇到反爬虫
                    if self._check_anti_crawler_page():
                        print("  → 查询结果页面检测到反爬虫")
                        time.sleep(random.uniform(5, 10))
                        continue

                    # 检查是否有结果
                    page_source = self.driver.page_source
                    print("  → 分析查询结果...")

                    # 判断是否无结果
                    no_result_keywords = ['暂无记录', '未找到', '查询结果为空', '共 0 条']
                    if any(keyword in page_source for keyword in no_result_keywords):
                        print("  → ✓ 查询成功，无相关记录")
                        result['success'] = True
                        result['total'] = 0
                        result['records'] = []
                        result['strategy_used'] = strategy_name
                        break

                    # 判断是否有结果
                    has_result_keywords = ['查询结果', '共', '条记录', '被执行人', '失信']
                    if any(keyword in page_source for keyword in has_result_keywords):
                        print("  → ✓ 查询成功，发现记录")
                        result['success'] = True
                        result['strategy_used'] = strategy_name

                        # 尝试解析结果
                        try:
                            # 查找记录数量
                            import re
                            total_match = re.search(r'共\s*(\d+)\s*条', page_source)
                            if total_match:
                                result['total'] = int(total_match.group(1))

                            # 记录结果（简化版，实际需要根据页面结构解析）
                            result['records'] = [{
                                'note': '查询成功，详细结果需要根据页面结构进一步解析'
                            }]
                        except Exception as e:
                            print(f"  → 解析结果时出错: {str(e)}")
                            result['records'] = [{'note': '查询成功但解析失败'}]

                        break

                    print("  → 无法确定查询结果状态，继续重试")

                except Exception as e:
                    print(f"  → 查询出错: {str(e)}")
                    self._take_screenshot(f"{query_type}_error_attempt{attempt}")
                    result['error'] = str(e)

                # 重试前等待
                if attempt < self.max_retries:
                    delay = random.uniform(5, 10)
                    print(f"  → 等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)

            # 如果成功，关闭驱动并返回
            if result['success']:
                try:
                    self.driver.quit()
                except:
                    pass
                return result

            # 关闭当前驱动的连接，准备尝试下一个策略
            try:
                self.driver.quit()
            except:
                pass

        # 所有策略都失败
        result['error'] = '所有查询策略均失败'
        return result

    def query_all(self, name: str, id_card: str, include_court_docs: bool = False) -> Dict[str, Any]:
        """
        查询所有类型的司法信息

        Args:
            name: 姓名
            id_card: 身份证号
            include_court_docs: 是否包含裁判文书查询（默认 False，因为需要处理验证码）

        Returns:
            所有查询结果的汇总
        """
        print(f"\n{'#'*80}")
        print(f"# 智能司法信息综合查询")
        print(f"# 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# 查询对象: {name}")
        print(f"# 身份证号: {id_card[:3]}***********{id_card[-4:]}")
        if include_court_docs:
            print(f"# 裁判文书查询: 已启用（可能需要人工处理验证码）")
        else:
            print(f"# 裁判文书查询: 已禁用")
        print(f"{'#'*80}")

        all_results = {
            'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'person_info': {
                'name': name,
                'masked_id': id_card[:3] + '*' * 11 + id_card[-4:]
            },
            'queries': {}
        }

        # 查询被执行人
        print(f"\n{'='*80}")
        print(f"【1/4】查询被执行人信息")
        print(f"{'='*80}")
        executed_result = self.query_page(
            self.urls['executed'], name, id_card, 'executed'
        )
        all_results['queries']['executed_persons'] = executed_result

        # 查询失信名单
        print(f"\n{'='*80}")
        print(f"【2/4】查询失信被执行人名单")
        print(f"{'='*80}")
        dishonest_result = self.query_page(
            self.urls['dishonest'], name, id_card, 'dishonest'
        )
        all_results['queries']['dishonest_list'] = dishonest_result

        # 查询限制消费令
        print(f"\n{'='*80}")
        print(f"【3/4】查询限制消费令")
        print(f"{'='*80}")
        restriction_result = self.query_page(
            self.urls['restriction'], name, id_card, 'restriction'
        )
        all_results['queries']['restriction_consumption'] = restriction_result

        # 查询裁判文书（可选）
        if include_court_docs:
            print(f"\n{'='*80}")
            print(f"【4/4】查询裁判文书")
            print(f"{'='*80}")
            try:
                court_result = self.court_query.query(name, id_card)
                all_results['queries']['court_documents'] = court_result
            except Exception as e:
                print(f"  → 裁判文书查询异常: {str(e)}")
                all_results['queries']['court_documents'] = {
                    'success': False,
                    'error': str(e),
                    'query_type': 'court_documents',
                    'note': '查询过程中出现异常'
                }
        else:
            print(f"\n{'='*80}")
            print(f"【4/4】跳过裁判文书查询（如需查询，请设置 include_court_docs=True）")
            print(f"{'='*80}")
            all_results['queries']['court_documents'] = {
                'success': None,
                'query_type': 'court_documents',
                'note': '查询已跳过（默认配置）',
                'skipped': True
            }

        # 统计结果
        total_records = sum(q.get('total', 0) for q in all_results['queries'].values() if not q.get('skipped'))
        all_results['summary'] = {
            'total_queries': len(all_results['queries']),
            'successful_queries': sum(1 for q in all_results['queries'].values() if q.get('success')),
            'total_records_found': total_records,
            'has_any_records': total_records > 0
        }

        return all_results


def main():
    """主函数"""
    # ============ 配置区域 ============
    name = "费佳骏"
    id_card = "330501198804220815"

    # 查询配置
    headless = False  # 是否无头模式（False 可以看到浏览器操作过程）
    max_retries = 3  # 每个策略的最大重试次数
    include_court_docs = False  # 是否查询裁判文书（需要处理验证码）
    # =================================

    # 创建智能查询器
    query = IntelligentJudicialQuery(headless=headless, max_retries=max_retries)

    # 执行所有查询
    results = query.query_all(name, id_card, include_court_docs=include_court_docs)

    # 打印摘要
    print(f"\n{'#'*80}")
    print(f"# 查询完成")
    print(f"{'#'*80}")
    print(f"总查询数: {results['summary']['total_queries']}")
    print(f"成功查询: {results['summary']['successful_queries']}")
    print(f"发现记录: {results['summary']['total_records_found']}")
    print(f"{'#'*80}")

    # 保存结果
    output_file = '/Users/jj/CodeBuddy/skill/personal-background-check/reports/智能司法查询结果.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 查询结果已保存到: {output_file}")

    # 详细结果
    for query_type, query_result in results['queries'].items():
        print(f"\n{query_type}:")
        if query_result.get('skipped'):
            print(f"  状态: ⊙ 跳过")
            print(f"  说明: {query_result.get('note', '')}")
        else:
            print(f"  状态: {'✓ 成功' if query_result.get('success') else '✗ 失败'}")
            print(f"  策略: {query_result.get('strategy_used', 'N/A')}")
            print(f"  尝试次数: {query_result.get('attempts', 0)}")
            if query_result.get('error'):
                print(f"  错误: {query_result['error']}")


if __name__ == '__main__':
    main()
