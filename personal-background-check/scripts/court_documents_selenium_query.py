"""
裁判文书网 Selenium 查询模块
数据来源：中国裁判文书网 (wenshu.court.gov.cn)
使用 Selenium 自动化查询，支持多种反爬虫策略
"""

import time
import random
import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


class CourtDocumentsSeleniumQuery:
    """裁判文书网 Selenium 查询器"""

    def __init__(self, headless: bool = False, max_retries: int = 3, screenshot_dir: str = None):
        """
        初始化查询器

        Args:
            headless: 是否无头模式
            max_retries: 每个策略的最大重试次数
            screenshot_dir: 截图保存目录
        """
        self.headless = headless
        self.max_retries = max_retries
        self.driver = None
        self.current_strategy = None

        # 裁判文书网 URL
        self.search_url = 'https://wenshu.court.gov.cn/website/wenshu/181010CARHS5BS3C/index.html'

        # 截图目录
        self.screenshot_dir = screenshot_dir or '/Users/jj/CodeBuddy/skill/personal-background-check/screenshots'
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _init_undetected_chrome(self) -> Optional[webdriver.Chrome]:
        """
        初始化 undetected-chromedriver（策略1）
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
            options.add_argument('--start-maximized')

            # 真实用户代理
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            driver = uc.Chrome(options=options, version_main=120)
            self.current_strategy = 'undetected_chromedriver'

            print("  ✓ 策略1: undetected-chromedriver 初始化成功")
            return driver

        except ImportError:
            print("  ✗ undetected-chromedriver 未安装")
            return None
        except Exception as e:
            print(f"  ✗ undetected-chromedriver 初始化失败: {str(e)}")
            return None

    def _init_standard_chrome(self) -> Optional[webdriver.Chrome]:
        """
        初始化标准 Chrome（策略2）
        """
        try:
            options = Options()

            if self.headless:
                options.add_argument('--headless=new')

            # 反检测设置
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--start-maximized')

            # 真实用户代理
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # 禁用自动化控制标志
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=options)

            # CDP 命令隐藏 webdriver
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
            print("  ✓ 策略2: 标准 Selenium + CDP 初始化成功")
            return driver

        except Exception as e:
            print(f"  ✗ 标准 Chrome 初始化失败: {str(e)}")
            return None

    def _human_typing(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.2):
        """人类打字行为模拟"""
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(min_delay, max_delay))
        except Exception as e:
            print(f"    → 打字失败: {str(e)}")
            raise

    def _human_scroll(self, scroll_times: int = 3):
        """人类滚动行为模拟"""
        try:
            for _ in range(scroll_times):
                scroll_height = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                time.sleep(random.uniform(0.3, 0.8))
        except Exception:
            pass

    def _human_click_delay(self):
        """人类点击延迟"""
        time.sleep(random.uniform(0.5, 1.5))

    def _random_wait(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """随机等待"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def _take_screenshot(self, name: str):
        """截图保存"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(self.screenshot_dir, f'court_docs_{name}_{timestamp}.png')
            self.driver.save_screenshot(filepath)
            print(f"    → 截图已保存: {filepath}")
        except Exception as e:
            print(f"    → 截图失败: {str(e)}")

    def _check_anti_crawler_page(self) -> bool:
        """检测反爬虫页面"""
        try:
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
                '访问频率过高',
                '系统繁忙',
                '验证您的身份',
                '滑动验证',
                '点击验证'
            ]

            return any(keyword in page_source for keyword in anti_crawler_keywords)
        except Exception:
            return False

    def _wait_for_page_load(self, timeout: int = 15):
        """等待页面加载"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(random.uniform(1, 2))
        except TimeoutException:
            print("    → 页面加载超时")

    def _handle_captcha_if_needed(self) -> bool:
        """
        处理验证码（人工介入）

        Returns:
            是否处理成功
        """
        if not self._check_anti_crawler_page():
            return True

        print("    → 检测到验证码，需要人工处理")
        self._take_screenshot('captcha_detected')

        if self.headless:
            print("    → 无头模式下无法处理验证码，请切换到非无头模式")
            return False

        # 提示用户手动处理验证码
        print("    → 请在浏览器中完成验证码，验证完成后按 Enter 继续...")
        input("    → [按 Enter 继续]...")

        # 等待验证完成
        time.sleep(3)

        if self._check_anti_crawler_page():
            print("    → 验证码仍然存在")
            return False

        print("    → 验证码处理成功")
        return True

    def _find_and_input(self, by: By, value: str, text: str, wait_time: int = 10) -> bool:
        """查找元素并输入文本"""
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            self._human_typing(element, text)
            return True
        except (TimeoutException, NoSuchElementException) as e:
            print(f"    → 未找到输入框 ({by}={value}): {str(e)}")
            return False

    def _find_and_click(self, by: By, value: str, wait_time: int = 10) -> bool:
        """查找元素并点击"""
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((by, value))
            )
            self._human_click_delay()
            element.click()
            return True
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"    → 未找到或无法点击按钮 ({by}={value}): {str(e)}")
            return False

    def _parse_query_results(self) -> Dict[str, Any]:
        """
        解析查询结果页面

        Returns:
            解析结果
        """
        try:
            page_source = self.driver.page_source

            result = {
                'success': True,
                'has_records': False,
                'total': 0,
                'records': []
            }

            # 检查是否无结果
            no_result_keywords = ['暂无', '未找到', '无记录', '查询结果为空', '共 0 条']
            if any(keyword in page_source for keyword in no_result_keywords):
                print("    → ✓ 查询成功，无相关记录")
                result['has_records'] = False
                result['total'] = 0
                return result

            # 查找记录数量
            total_match = re.search(r'共\s*(\d+)\s*条', page_source)
            if total_match:
                result['total'] = int(total_match.group(1))
                result['has_records'] = result['total'] > 0

            # 尝试提取文书列表
            # 注意：实际解析逻辑需要根据页面结构调整
            result['records'] = self._extract_document_list(page_source)

            return result

        except Exception as e:
            print(f"    → 解析结果时出错: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'has_records': False,
                'total': 0,
                'records': []
            }

    def _extract_document_list(self, page_source: str) -> List[Dict]:
        """
        从页面源码中提取文书列表

        Args:
            page_source: 页面 HTML 源码

        Returns:
            文书记录列表
        """
        records = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'lxml')

            # 尝试查找文书项
            # 注意：选择器需要根据实际页面结构调整
            doc_items = soup.find_all(['div', 'li', 'tr'], class_=re.compile(r'(item|record|row)', re.I))

            for item in doc_items[:10]:  # 最多提取10条
                try:
                    record = self._parse_single_document(item)
                    if record:
                        records.append(record)
                except Exception:
                    continue

        except ImportError:
            # 如果没有 BeautifulSoup，返回基本信息
            records.append({
                'note': '需要安装 beautifulsoup4 来解析详细内容'
            })
        except Exception as e:
            print(f"    → 提取文书列表失败: {str(e)}")

        return records

    def _parse_single_document(self, item) -> Dict:
        """
        解析单个文书记录

        Args:
            item: BeautifulSoup 元素对象

        Returns:
            文书记录字典
        """
        try:
            # 尝试提取文书信息
            text_content = item.get_text(strip=True)

            # 查找案号
            case_number_match = re.search(r'（\d{4}）\w+[\d]+号', text_content)
            case_number = case_number_match.group(0) if case_number_match else ''

            # 查找案件名称
            case_name = text_content[:100]  # 简化处理

            return {
                'case_number': case_number,
                'case_name': case_name,
                'court_name': '',
                'case_type': '',
                'case_date': '',
                'raw_text': text_content[:200]
            }
        except Exception:
            return {}

    def query(self, name: str, id_card: str = '') -> Dict[str, Any]:
        """
        查询裁判文书

        Args:
            name: 姓名
            id_card: 身份证号（可选）

        Returns:
            查询结果字典
        """
        result = {
            'query_type': 'court_documents',
            'name': name,
            'id_card': id_card[:3] + '*' * 11 + id_card[-4:] if id_card else '',
            'success': False,
            'records': [],
            'total': 0,
            'strategy_used': None,
            'attempts': 0,
            'error': None
        }

        print(f"\n{'='*80}")
        print(f"裁判文书查询")
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
                    print("  → 访问裁判文书网...")
                    self.driver.get(self.search_url)
                    self._wait_for_page_load()

                    # 截图
                    self._take_screenshot('page_loaded')

                    # 检测反爬虫
                    if self._check_anti_crawler_page():
                        print("  → 检测到反爬虫页面")
                        if not self._handle_captcha_if_needed():
                            time.sleep(random.uniform(5, 10))
                            continue

                    # 人类滚动
                    self._human_scroll(scroll_times=2)

                    # 尝试多种方式查找姓名输入框
                    print(f"  → 尝试输入姓名: {name}")
                    name_selectors = [
                        (By.NAME, 'qw'),
                        (By.ID, 'qw'),
                        (By.CLASS_NAME, 'search-input'),
                        (By.CSS_SELECTOR, 'input[placeholder*="当事人"]'),
                        (By.CSS_SELECTOR, 'input[placeholder*="姓名"]'),
                    ]

                    name_found = False
                    for selector_type, selector_value in name_selectors:
                        if self._find_and_input(selector_type, selector_value, name, wait_time=5):
                            name_found = True
                            break

                    if not name_found:
                        # 尝试通过 JS 输入
                        try:
                            self.driver.execute_script(f"document.querySelector('input[type=\"text\"]').value = '{name}';")
                            name_found = True
                        except Exception as e:
                            print(f"    → JS 输入失败: {str(e)}")

                    if not name_found:
                        print("  → 未找到姓名输入框")
                        continue

                    self._random_wait(0.5, 1.0)

                    # 如果有身份证号，尝试输入
                    if id_card:
                        print(f"  → 尝试输入身份证号")
                        id_card_selectors = [
                            (By.NAME, 'sfzh'),
                            (By.ID, 'sfzh'),
                            (By.CSS_SELECTOR, 'input[placeholder*="身份证"]'),
                        ]

                        for selector_type, selector_value in id_card_selectors:
                            if self._find_and_input(selector_type, selector_value, id_card, wait_time=3):
                                break

                    self._random_wait(0.5, 1.0)

                    # 尝试点击查询按钮
                    print("  → 尝试点击查询按钮")
                    button_selectors = [
                        (By.XPATH, "//input[@value='查询']"),
                        (By.XPATH, "//button[contains(text(),'查询')]"),
                        (By.CSS_SELECTOR, '.search-btn'),
                        (By.CSS_SELECTOR, 'input[type="submit"]'),
                        (By.CLASS_NAME, 'btn-query'),
                    ]

                    button_found = False
                    for selector_type, selector_value in button_selectors:
                        if self._find_and_click(selector_type, selector_value, wait_time=5):
                            button_found = True
                            break

                    if not button_found:
                        # 尝试通过 JS 点击
                        try:
                            self.driver.execute_script("document.querySelector('button').click();")
                            button_found = True
                        except Exception as e:
                            print(f"    → JS 点击失败: {str(e)}")

                    if not button_found:
                        print("  → 未找到查询按钮")
                        continue

                    # 等待结果加载
                    print("  → 等待查询结果...")
                    self._random_wait(3, 5)
                    self._wait_for_page_load(timeout=20)

                    # 截图结果页
                    self._take_screenshot('result')

                    # 检测结果页是否又有验证码
                    if self._check_anti_crawler_page():
                        print("  → 结果页检测到验证码")
                        if not self._handle_captcha_if_needed():
                            time.sleep(random.uniform(5, 10))
                            continue

                    # 解析结果
                    print("  → 分析查询结果...")
                    parse_result = self._parse_query_results()

                    result['success'] = parse_result.get('success', False)
                    result['has_records'] = parse_result.get('has_records', False)
                    result['total'] = parse_result.get('total', 0)
                    result['records'] = parse_result.get('records', [])
                    result['strategy_used'] = strategy_name

                    if result['success']:
                        if result['has_records']:
                            print(f"  → ✓ 查询成功，发现 {result['total']} 条记录")
                        else:
                            print("  → ✓ 查询成功，无相关记录")
                        break
                    else:
                        print("  → 查询失败，继续重试")

                except Exception as e:
                    print(f"  → 查询出错: {str(e)}")
                    self._take_screenshot(f'error_attempt{attempt}')
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

            # 关闭当前驱动
            try:
                self.driver.quit()
            except:
                pass

        # 所有策略都失败
        result['error'] = '所有查询策略均失败'
        return result


def query_court_documents_selenium(name: str, id_card: str = '', headless: bool = False) -> Dict[str, Any]:
    """
    查询裁判文书（便捷函数）

    Args:
        name: 姓名
        id_card: 身份证号（可选）
        headless: 是否无头模式

    Returns:
        查询结果字典
    """
    query = CourtDocumentsSeleniumQuery(headless=headless)
    return query.query(name, id_card)


if __name__ == '__main__':
    # 测试代码
    test_name = "张三"
    test_id = "110101199001011234"

    result = query_court_documents_selenium(test_name, test_id, headless=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
