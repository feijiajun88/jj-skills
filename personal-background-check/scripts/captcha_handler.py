"""
验证码识别和处理模块
支持多种验证码识别方式和人工介入
"""

import time
import os
import base64
import json
from typing import Optional, Dict, Any
from datetime import datetime
from PIL import Image
import io


class CaptchaHandler:
    """验证码处理器"""

    def __init__(self, driver=None, cache_dir: str = None):
        """
        初始化验证码处理器

        Args:
            driver: Selenium WebDriver 实例
            cache_dir: 验证码缓存目录
        """
        self.driver = driver
        self.cache_dir = cache_dir or '/Users/jj/CodeBuddy/skill/personal-background-check/.captcha_cache'
        os.makedirs(self.cache_dir, exist_ok=True)

        # 验证码识别 API 配置
        self.api_configs = {
            'tencent': {
                'enabled': False,
                'secret_id': '',
                'secret_key': '',
                'endpoint': 'https://captcha.tencentcloudapi.com/'
            },
            'aliyun': {
                'enabled': False,
                'access_key_id': '',
                'access_key_secret': '',
                'endpoint': 'https://captcha.cn-shanghai.aliyuncs.com/'
            },
            'baidu': {
                'enabled': False,
                'api_key': '',
                'secret_key': '',
                'endpoint': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
            }
        }

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载验证码识别 API 配置"""
        config_file = os.path.join('/Users/jj/CodeBuddy/skill/personal-background-check', 'references', 'captcha_api_config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for provider, settings in config.items():
                        if provider in self.api_configs:
                            self.api_configs[provider].update(settings)
        except Exception as e:
            print(f"  → 加载验证码配置失败: {str(e)}")

    def detect_captcha_element(self) -> Optional[object]:
        """
        检测页面中的验证码元素

        Returns:
            验证码元素或 None
        """
        if not self.driver:
            return None

        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            # 常见的验证码元素选择器
            selectors = [
                (By.ID, 'captcha'),
                (By.ID, 'verifyCode'),
                (By.ID, 'captchaImage'),
                (By.CLASS_NAME, 'captcha'),
                (By.CLASS_NAME, 'verify-code'),
                (By.CSS_SELECTOR, 'img[alt*="验证码"]'),
                (By.CSS_SELECTOR, 'img[alt*="验证"]'),
                (By.XPATH, '//img[contains(@src, "captcha")]'),
                (By.XPATH, '//img[contains(@src, "verify")]'),
            ]

            for by, value in selectors:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by, value))
                    )
                    print(f"    → 找到验证码元素: {by}={value}")
                    return element
                except Exception:
                    continue

            print("    → 未找到明显的验证码元素")
            return None

        except Exception as e:
            print(f"    → 检测验证码元素失败: {str(e)}")
            return None

    def screenshot_captcha(self, element=None) -> Optional[str]:
        """
        截取验证码图片

        Args:
            element: 验证码元素，如果为 None 则自动检测

        Returns:
            截图文件路径
        """
        try:
            if element is None:
                element = self.detect_captcha_element()

            if not element:
                print("    → 无法截图验证码：未找到验证码元素")
                return None

            # 获取验证码图片位置
            location = element.location
            size = element.size

            # 截取整个页面
            screenshot = self.driver.get_screenshot_as_png()

            # 裁剪验证码区域
            image = Image.open(io.BytesIO(screenshot))
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']

            captcha_img = image.crop((left, top, right, bottom))

            # 保存验证码图片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filepath = os.path.join(self.cache_dir, f'captcha_{timestamp}.png')
            captcha_img.save(filepath)

            print(f"    → 验证码已保存: {filepath}")
            return filepath

        except Exception as e:
            print(f"    → 截取验证码失败: {str(e)}")
            return None

    def recognize_with_api(self, image_path: str, provider: str = 'baidu') -> Optional[str]:
        """
        使用第三方 API 识别验证码

        Args:
            image_path: 验证码图片路径
            provider: API 提供商 (baidu/aliyun/tencent)

        Returns:
            识别结果
        """
        try:
            config = self.api_configs.get(provider)
            if not config or not config.get('enabled'):
                print(f"    → {provider} API 未配置")
                return None

            if provider == 'baidu':
                return self._recognize_baidu(image_path, config)
            elif provider == 'aliyun':
                return self._recognize_aliyun(image_path, config)
            elif provider == 'tencent':
                return self._recognize_tencent(image_path, config)

            return None

        except Exception as e:
            print(f"    → API 识别失败: {str(e)}")
            return None

    def _recognize_baidu(self, image_path: str, config: Dict) -> Optional[str]:
        """使用百度 OCR 识别验证码"""
        try:
            import requests

            # 读取图片
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # 获取 access_token
            token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={config['api_key']}&client_secret={config['secret_key']}"
            response = requests.post(token_url)
            access_token = response.json().get('access_token')

            if not access_token:
                print("    → 获取百度 access_token 失败")
                return None

            # 识别验证码
            ocr_url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
            files = {'image': image_data}
            response = requests.post(ocr_url, files=files)

            result = response.json()
            if 'words_result' in result and result['words_result']:
                return result['words_result'][0]['words']

            return None

        except Exception as e:
            print(f"    → 百度 OCR 识别失败: {str(e)}")
            return None

    def _recognize_aliyun(self, image_path: str, config: Dict) -> Optional[str]:
        """使用阿里云 OCR 识别验证码"""
        # 注意：需要安装 aliyun-python-sdk-core
        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.acs_exception.exceptions import ServerException
            from aliyunsdkocr.request.v20191230.RecognizeGeneralRequest import RecognizeGeneralRequest

            client = AcsClient(
                config['access_key_id'],
                config['access_key_secret'],
                'cn-shanghai'
            )

            with open(image_path, 'rb') as f:
                image_data = f.read()

            request = RecognizeGeneralRequest()
            request.set_body(image_data)

            response = client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))

            if 'Data' in result and 'PrismaticWords' in result['Data']:
                return result['Data']['PrismaticWords']

            return None

        except ImportError:
            print("    → 需要安装 aliyun-python-sdk-core: pip install aliyun-python-sdk-core")
            return None
        except Exception as e:
            print(f"    → 阿里云 OCR 识别失败: {str(e)}")
            return None

    def _recognize_tencent(self, image_path: str, config: Dict) -> Optional[str]:
        """使用腾讯云 OCR 识别验证码"""
        # 注意：需要安装腾讯云 SDK
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.ocr.v20181119 import ocr_client, models

            cred = credential.Credential(config['secret_id'], config['secret_key'])
            http_profile = HttpProfile(endpoint=config['endpoint'])
            client_profile = ClientProfile(httpProfile=http_profile)
            client = ocr_client.OcrClient(cred, "ap-guangzhou", client_profile)

            with open(image_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            req = models.GeneralBasicOCRRequest()
            req.ImageBase64 = image_base64

            resp = client.GeneralBasicOCR(req)

            if resp.TextDetections:
                return resp.TextDetections[0].DetectedText

            return None

        except ImportError:
            print("    → 需要安装腾讯云 SDK: pip install tencentcloud-sdk-python")
            return None
        except Exception as e:
            print(f"    → 腾讯云 OCR 识别失败: {str(e)}")
            return None

    def manual_solve(self, image_path: str = None) -> Optional[str]:
        """
        人工输入验证码

        Args:
            image_path: 验证码图片路径，如果为 None 则自动检测并截图

        Returns:
            用户输入的验证码
        """
        try:
            if image_path is None:
                image_path = self.screenshot_captcha()

            if image_path:
                print(f"\n    验证码图片已保存: {image_path}")
                print("    请查看图片并输入验证码:")

            code = input("    → 请输入验证码: ").strip()

            if code:
                # 保存验证码到缓存（用于后续训练）
                self._save_to_cache(image_path, code)
                return code

            return None

        except Exception as e:
            print(f"    → 人工输入验证码失败: {str(e)}")
            return None

    def _save_to_cache(self, image_path: str, code: str):
        """保存验证码到训练缓存"""
        try:
            cache_file = os.path.join(self.cache_dir, 'captcha_cache.json')
            cache_data = []

            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

            # 将图片转为 base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            cache_data.append({
                'image': image_data,
                'code': code,
                'timestamp': datetime.now().isoformat()
            })

            # 保存缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            print(f"    → 验证码已缓存到: {cache_file}")

        except Exception as e:
            print(f"    → 保存验证码缓存失败: {str(e)}")

    def solve_captcha(self, auto_retry: bool = True) -> Optional[str]:
        """
        自动解决验证码（优先使用 API，失败则人工介入）

        Args:
            auto_retry: 是否自动重试

        Returns:
            验证码识别结果
        """
        print("\n    开始处理验证码...")

        # 截取验证码
        image_path = self.screenshot_captcha()
        if not image_path:
            return None

        # 尝试使用 API 识别
        for provider in ['baidu', 'aliyun', 'tencent']:
            if self.api_configs[provider].get('enabled'):
                print(f"    → 尝试使用 {provider} API 识别...")
                code = self.recognize_with_api(image_path, provider)
                if code:
                    print(f"    → ✓ API 识别成功: {code}")
                    self._save_to_cache(image_path, code)
                    return code

        # API 识别失败，使用人工输入
        print("    → API 识别失败，转为人工输入")
        return self.manual_solve(image_path)

    def input_captcha_to_page(self, captcha_code: str, input_element=None):
        """
        将验证码输入到页面

        Args:
            captcha_code: 验证码
            input_element: 输入框元素，如果为 None 则自动查找
        """
        try:
            if input_element is None:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                # 查找验证码输入框
                input_selectors = [
                    (By.ID, 'captchaInput'),
                    (By.ID, 'verifyCodeInput'),
                    (By.NAME, 'captcha'),
                    (By.CLASS_NAME, 'captcha-input'),
                    (By.CSS_SELECTOR, 'input[placeholder*="验证码"]'),
                ]

                for by, value in input_selectors:
                    try:
                        input_element = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((by, value))
                        )
                        break
                    except Exception:
                        continue

            if input_element:
                input_element.clear()
                for char in captcha_code:
                    input_element.send_keys(char)
                    time.sleep(0.1)
                print(f"    → ✓ 验证码已输入: {captcha_code}")
            else:
                print("    → 未找到验证码输入框")

        except Exception as e:
            print(f"    → 输入验证码失败: {str(e)}")


if __name__ == '__main__':
    # 测试代码
    print("验证码处理器测试")
    print("请先配置 references/captcha_api_config.json")
    print("或使用人工输入模式")
