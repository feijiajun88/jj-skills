"""
反爬虫策略处理模块
提供多种反爬虫应对策略和人类行为模拟
"""

import time
import random
import logging
from typing import Dict, Any, List, Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger('background_check')


class AntiCrawlerStrategy:
    """反爬虫策略基类"""

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.name = self.__class__.__name__

    def setup(self) -> bool:
        """
        设置策略

        Returns:
            是否设置成功
        """
        return True

    def before_request(self) -> None:
        """请求前操作"""
        pass

    def after_request(self) -> None:
        """请求后操作"""
        pass

    def handle_captcha(self) -> bool:
        """
        处理验证码

        Returns:
            是否处理成功
        """
        return False

    def reset(self) -> None:
        """重置策略"""
        pass


class StealthModeStrategy(AntiCrawlerStrategy):
    """隐身模式策略 - 使用 CDP 命令隐藏自动化特征"""

    def setup(self) -> bool:
        """设置隐身模式"""
        try:
            stealth_script = '''
                // 隐藏 webdriver 特征
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // 添加 navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // 设置 languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });

                // 添加 chrome 对象
                window.chrome = {
                    runtime: {}
                };

                // 设置 permissions
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({state: 'granted'})
                    })
                });

                // 伪装屏幕分辨率
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920
                });

                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1080
                });

                // 伪装连接
                Object.defineProperty(navigator.connection, {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 100,
                        downlink: 10
                    })
                });
            '''

            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': stealth_script
            })

            logger.info("✓ 隐身模式策略设置成功")
            return True

        except Exception as e:
            logger.error(f"✗ 隐身模式策略设置失败: {str(e)}")
            return False


class HumanBehaviorStrategy(AntiCrawlerStrategy):
    """人类行为模拟策略"""

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.typing_speed_range = (0.05, 0.2)  # 打字速度范围（秒/字符）
        self.click_delay_range = (0.5, 1.5)  # 点击延迟范围（秒）
        self.scroll_range = (100, 500)  # 滚动距离范围（像素）
        self.wait_range = (1, 3)  # 随机等待范围（秒）

    def human_typing(self, element, text: str) -> bool:
        """
        模拟人类打字

        Args:
            element: 输入元素
            text: 要输入的文本

        Returns:
            是否成功
        """
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*self.typing_speed_range))
            return True
        except Exception as e:
            logger.error(f"打字模拟失败: {str(e)}")
            return False

    def human_scroll(self, times: int = 3) -> None:
        """
        模拟人类滚动

        Args:
            times: 滚动次数
        """
        try:
            for _ in range(times):
                scroll_distance = random.randint(*self.scroll_range)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            logger.error(f"滚动模拟失败: {str(e)}")

    def human_click(self, element) -> bool:
        """
        模拟人类点击

        Args:
            element: 点击元素

        Returns:
            是否成功
        """
        try:
            time.sleep(random.uniform(*self.click_delay_range))
            element.click()
            return True
        except Exception as e:
            logger.error(f"点击模拟失败: {str(e)}")
            return False

    def random_wait(self, min_seconds: float = None, max_seconds: float = None) -> None:
        """
        随机等待

        Args:
            min_seconds: 最小等待时间
            max_seconds: 最大等待时间
        """
        if min_seconds is None:
            min_seconds = self.wait_range[0]
        if max_seconds is None:
            max_seconds = self.wait_range[1]

        time.sleep(random.uniform(min_seconds, max_seconds))

    def before_request(self) -> None:
        """请求前执行人类行为模拟"""
        self.human_scroll(times=random.randint(1, 3))
        self.random_wait()

    def after_request(self) -> None:
        """请求后执行人类行为模拟"""
        self.random_wait(1, 2)


class ProxyRotationStrategy(AntiCrawlerStrategy):
    """代理轮换策略"""

    def __init__(self, driver: webdriver.Chrome, proxies: List[str] = None):
        """
        初始化代理轮换策略

        Args:
            driver: WebDriver 实例
            proxies: 代理列表 ['ip:port', ...]
        """
        super().__init__(driver)
        self.proxies = proxies or []
        self.current_index = 0
        self.using_proxy = False

    def setup(self) -> bool:
        """设置代理"""
        if not self.proxies:
            logger.info("未配置代理列表，跳过代理设置")
            return False

        proxy = self._get_next_proxy()
        if proxy:
            self._set_proxy(proxy)
            logger.info(f"✓ 代理设置成功: {proxy}")
            return True

        return False

    def _get_next_proxy(self) -> Optional[str]:
        """获取下一个代理"""
        if not self.proxies:
            return None

        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def _set_proxy(self, proxy: str) -> bool:
        """设置代理"""
        try:
            # Selenium 代理设置需要在初始化时完成
            # 这里仅记录，实际使用需要在创建 driver 时配置
            logger.warning(f"代理设置需要在创建 driver 时完成: {proxy}")
            return False
        except Exception as e:
            logger.error(f"设置代理失败: {str(e)}")
            return False

    def reset(self) -> None:
        """重置代理"""
        self.current_index = 0


class UserAgentRotationStrategy(AntiCrawlerStrategy):
    """User-Agent 轮换策略"""

    def __init__(self, driver: webdriver.Chrome):
        super().__init__(driver)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.current_index = 0

    def get_user_agent(self) -> str:
        """获取一个随机 User-Agent"""
        return random.choice(self.user_agents)

    def get_next_user_agent(self) -> str:
        """按顺序获取下一个 User-Agent"""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua

    def setup(self) -> bool:
        """设置 User-Agent（需要在初始化 driver 时完成）"""
        logger.info("User-Agent 轮换策略需要在创建 driver 时配置")
        return False


class RequestThrottlingStrategy(AntiCrawlerStrategy):
    """请求节流策略 - 控制请求频率"""

    def __init__(self, driver: webdriver.Chrome, min_interval: float = 2.0, max_interval: float = 5.0):
        """
        初始化请求节流策略

        Args:
            driver: WebDriver 实例
            min_interval: 最小请求间隔（秒）
            max_interval: 最大请求间隔（秒）
        """
        super().__init__(driver)
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.last_request_time = 0

    def before_request(self) -> None:
        """请求前检查并节流"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            logger.info(f"请求节流，等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)
        else:
            # 随机延迟
            delay = random.uniform(0, self.max_interval - self.min_interval)
            time.sleep(delay)

        self.last_request_time = time.time()


class RetryStrategy(AntiCrawlerStrategy):
    """重试策略"""

    def __init__(self, driver: webdriver.Chrome, max_retries: int = 3, backoff_factor: float = 1.5):
        """
        初始化重试策略

        Args:
            driver: WebDriver 实例
            max_retries: 最大重试次数
            backoff_factor: 退避因子（每次重试的延迟乘数）
        """
        super().__init__(driver)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数，失败时自动重试

        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"执行尝试 #{attempt}/{self.max_retries}")
                result = func(*args, **kwargs)
                if attempt > 1:
                    logger.info(f"✓ 在第 {attempt} 次尝试后成功")
                return result
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = (2 ** (attempt - 1)) * self.backoff_factor
                    logger.warning(f"尝试 #{attempt} 失败: {str(e)}, {delay} 秒后重试...")
                    time.sleep(delay)

        logger.error(f"所有重试失败")
        raise last_exception


class StrategyManager:
    """策略管理器 - 组合多种反爬虫策略"""

    def __init__(self, driver: webdriver.Chrome):
        """
        初始化策略管理器

        Args:
            driver: WebDriver 实例
        """
        self.driver = driver
        self.strategies: List[AntiCrawlerStrategy] = []

    def add_strategy(self, strategy: AntiCrawlerStrategy) -> None:
        """添加策略"""
        self.strategies.append(strategy)
        logger.info(f"添加策略: {strategy.name}")

    def setup_all(self) -> bool:
        """设置所有策略"""
        logger.info("开始设置所有策略...")
        all_success = True

        for strategy in self.strategies:
            try:
                success = strategy.setup()
                if not success:
                    logger.warning(f"策略 {strategy.name} 设置失败，但继续执行")
                    all_success = False
            except Exception as e:
                logger.error(f"设置策略 {strategy.name} 时出错: {str(e)}")
                all_success = False

        return all_success

    def before_request_all(self) -> None:
        """所有策略的请求前操作"""
        for strategy in self.strategies:
            try:
                strategy.before_request()
            except Exception as e:
                logger.error(f"策略 {strategy.name} before_request 出错: {str(e)}")

    def after_request_all(self) -> None:
        """所有策略的请求后操作"""
        for strategy in self.strategies:
            try:
                strategy.after_request()
            except Exception as e:
                logger.error(f"策略 {strategy.name} after_request 出错: {str(e)}")

    def reset_all(self) -> None:
        """重置所有策略"""
        for strategy in self.strategies:
            try:
                strategy.reset()
            except Exception as e:
                logger.error(f"重置策略 {strategy.name} 时出错: {str(e)}")

    def check_captcha_and_handle(self) -> bool:
        """检查并处理验证码"""
        for strategy in self.strategies:
            try:
                if strategy.handle_captcha():
                    return True
            except Exception as e:
                logger.error(f"策略 {strategy.name} handle_captcha 出错: {str(e)}")

        return False


def create_default_strategy_manager(driver: webdriver.Chrome) -> StrategyManager:
    """
    创建默认的策略管理器（包含常用策略）

    Args:
        driver: WebDriver 实例

    Returns:
        策略管理器实例
    """
    manager = StrategyManager(driver)

    # 添加常用策略
    manager.add_strategy(StealthModeStrategy(driver))
    manager.add_strategy(HumanBehaviorStrategy(driver))
    manager.add_strategy(RequestThrottlingStrategy(driver, min_interval=2.0, max_interval=5.0))

    return manager
