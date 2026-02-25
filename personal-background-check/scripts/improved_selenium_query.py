"""
改进的Selenium司法查询脚本 - 支持JavaScript渲染
"""

import time
import json
import traceback
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ImprovedSeleniumQuery:
    """改进的Selenium查询器 - 更好的JavaScript支持"""

    def __init__(self, headless: bool = False):
        """初始化查询器"""
        self.headless = headless
        self.driver = None
        self.wait = None

    def _init_browser(self):
        """初始化浏览器"""
        try:
            chrome_options = Options()

            # 基本配置
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            # 反检测配置
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-maximized')

            # 设置User-Agent
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )

            # 禁用自动化扩展
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # 初始化驱动
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)

            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(20)

            # 执行CDP命令隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })

            print("✓ 浏览器初始化完成")
        except Exception as e:
            print(f"✗ 浏览器初始化失败: {e}")
            print(traceback.format_exc())
            raise

    def _check_page_loaded(self) -> bool:
        """检查页面是否真正加载完成"""
        try:
            # 检查document.readyState
            ready_state = self.driver.execute_script("return document.readyState")
            print(f"  页面状态: {ready_state}")

            # 检查是否有input元素
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            print(f"  输入框数量: {len(inputs)}")

            # 检查body内容
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            print(f"  Body内容长度: {len(body_text)}")

            # 如果有输入框或body有内容，说明页面已加载
            if len(inputs) > 0 or len(body_text) > 100:
                return True

            return False
        except Exception as e:
            print(f"  检查页面状态时出错: {e}")
            return False

    def _wait_for_content(self, max_wait: int = 30):
        """等待页面内容加载"""
        print("→ 等待页面内容加载...")

        for i in range(max_wait):
            time.sleep(1)
            if self._check_page_loaded():
                print(f"✓ 页面内容已加载（耗时 {i+1} 秒）")
                return True

        print("⚠ 页面内容未在规定时间内加载")
        return False

    def query_page(self, url: str, name: str, id_card: str, query_type: str) -> Dict[str, Any]:
        """
        查询页面

        Args:
            url: 页面URL
            name: 姓名
            id_card: 身份证号
            query_type: 查询类型

        Returns:
            查询结果
        """
        print(f"\n{'=' * 60}")
        print(f"查询{query_type}: {name}")
        print(f"{'=' * 60}")

        result = {
            'name': name,
            'id_card': id_card[:3] + '*' * 11 + id_card[-4:],
            'query_type': query_type,
            'url': url,
            'status': 'unknown'
        }

        try:
            if not self.driver:
                raise Exception("浏览器未初始化")

            # 访问页面
            print(f"→ 访问: {url}")
            self.driver.get(url)
            # 访问页面
            print(f"→ 访问: {url}")
            self.driver.get(url)

            # 检查当前URL
            current_url = self.driver.current_url
            print(f"  当前URL: {current_url}")

            # 等待JavaScript执行
            time.sleep(3)

            # 检查页面是否加载
            if not self._check_page_loaded():
                print("⚠ 页面可能被JavaScript保护，尝试等待...")
                if not self._wait_for_content():
                    print("✗ 页面内容未能加载")
                    result['status'] = 'failed'
                    result['error'] = '页面内容未能加载（可能被反爬虫保护）'
                    result['page_state'] = 'empty'
                    return result
            else:
                print("✓ 页面已加载")

            # 截图
            screenshot_path = f'/Users/jj/CodeBuddy/skill/personal-background-check/reports/{query_type}_screenshot.png'
            self.driver.save_screenshot(screenshot_path)
            print(f"✓ 截图已保存: {screenshot_path}")

            # 保存页面源码
            page_source = self.driver.page_source
            html_path = f'/Users/jj/CodeBuddy/skill/personal-background-check/reports/{query_type}_page.html'
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"✓ 页面源码已保存: {html_path}")

            # 查找输入框
            inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or not(@type)]")
            print(f"✓ 找到 {len(inputs)} 个文本输入框")

            if len(inputs) == 0:
                print("⚠ 未找到输入框，无法进行查询")
                result['status'] = 'failed'
                result['error'] = '未找到输入框'
                result['inputs_found'] = 0
                return result

            # 如果找到输入框，尝试填写
            if len(inputs) >= 1:
                print(f"→ 填写第一个输入框（姓名）: {name}")
                input1 = inputs[0]
                input1.clear()
                input1.send_keys(name)
                time.sleep(0.5)

            if len(inputs) >= 2:
                print(f"→ 填写第二个输入框（身份证）: {id_card[:3]}***{id_card[-4:]}")
                input2 = inputs[1]
                input2.clear()
                input2.send_keys(id_card)
                time.sleep(0.5)

            # 查找查询按钮
            print("→ 查找查询按钮...")
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            print(f"  找到 {len(buttons)} 个按钮")

            if len(buttons) == 0:
                # 尝试查找input type=submit
                submit_inputs = self.driver.find_elements(By.XPATH, "//input[@type='submit']")
                if len(submit_inputs) > 0:
                    buttons = submit_inputs
                    print(f"  找到 {len(submit_inputs)} 个提交按钮")

            if len(buttons) > 0:
                try:
                    # 尝试点击第一个按钮
                    print("→ 点击查询按钮...")
                    buttons[0].click()
                    time.sleep(3)

                    # 检查结果
                    print("→ 检查查询结果...")
                    body_text = self.driver.find_element(By.TAG_NAME, 'body').text

                    # 保存结果截图
                    result_screenshot = f'/Users/jj/CodeBuddy/skill/personal-background-check/reports/{query_type}_result.png'
                    self.driver.save_screenshot(result_screenshot)
                    print(f"✓ 结果截图已保存: {result_screenshot}")

                    # 简单的结果判断
                    if '查询到' in body_text or '共' in body_text:
                        result['status'] = 'success'
                        result['has_records'] = True
                        result['result_summary'] = '页面显示有查询结果'
                    elif '未查询到' in body_text or '无记录' in body_text:
                        result['status'] = 'success'
                        result['has_records'] = False
                        result['result_summary'] = '页面显示无记录'
                    else:
                        result['status'] = 'unknown'
                        result['result_summary'] = '无法确定查询结果'

                except Exception as e:
                    print(f"✗ 点击按钮失败: {e}")
                    result['status'] = 'partial'
                    result['error'] = f'点击按钮失败: {e}'
            else:
                print("⚠ 未找到查询按钮")
                result['status'] = 'partial'
                result['error'] = '未找到查询按钮'

            result['inputs_found'] = len(inputs)
            result['buttons_found'] = len(buttons)
            result['page_state'] = 'loaded'

        except TimeoutException as e:
            print(f"✗ 页面加载超时: {e}")
            result['status'] = 'failed'
            result['error'] = f'页面加载超时: {e}'
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)

        return result

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✓ 浏览器已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """主函数"""
    name = "李健超"
    id_card = "440421199502278077"

    print("=" * 60)
    print("改进的司法信息查询")
    print("=" * 60)
    print(f"查询对象: {name}")
    print(f"身份证号: {id_card[:3]}***********{id_card[-4:]}")

    try:
        # 创建查询器
        query = ImprovedSeleniumQuery(headless=False)
        query._init_browser()

        queries = [
            ('被执行人', 'https://zxgk.court.gov.cn/zhixing/'),
            ('失信被执行人', 'https://zxgk.court.gov.cn/shixin/'),
            ('限制消费令', 'https://zxgk.court.gov.cn/xgl/'),
        ]

        results = []
        for query_type, url in queries:
            try:
                result = query.query_page(url, name, id_card, query_type)
                results.append(result)
                time.sleep(2)  # 查询间隔
            except Exception as e:
                print(f"✗ 查询{query_type}时出错: {e}")
                print(traceback.format_exc())
                results.append({
                    'name': name,
                    'id_card': id_card[:3] + '*' * 11 + id_card[-4:],
                    'query_type': query_type,
                    'url': url,
                    'status': 'failed',
                    'error': str(e)
                })

        # 保存结果
        output_file = '/Users/jj/CodeBuddy/skill/personal-background-check/reports/improved_selenium_result.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("查询结果汇总")
        print("=" * 60)
        for result in results:
            status_map = {
                'success': '✓ 成功',
                'partial': '⚠ 部分',
                'failed': '✗ 失败',
                'unknown': '? 未知'
            }
            status = status_map.get(result.get('status'), result.get('status'))
            print(f"{status}: {result['query_type']}")
            if 'error' in result:
                print(f"  错误: {result['error']}")
            if 'has_records' in result:
                print(f"  记录: {'有' if result['has_records'] else '无'}")

        print(f"\n✓ 详细结果已保存: {output_file}")

        query.close()

    except Exception as e:
        print(f"✗ 程序运行失败: {e}")
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
