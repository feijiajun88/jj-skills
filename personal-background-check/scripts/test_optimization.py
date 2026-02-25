"""
测试脚本 - 测试优化后的功能
用于验证各个模块是否正常工作
"""

import sys
import os
import json

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """测试模块导入"""
    print("=" * 80)
    print("【测试 1/5】模块导入测试")
    print("=" * 80)

    try:
        from court_documents_selenium_query import CourtDocumentsSeleniumQuery
        print("✓ court_documents_selenium_query 模块导入成功")
    except Exception as e:
        print(f"✗ court_documents_selenium_query 模块导入失败: {str(e)}")
        return False

    try:
        from captcha_handler import CaptchaHandler
        print("✓ captcha_handler 模块导入成功")
    except Exception as e:
        print(f"✗ captcha_handler 模块导入失败: {str(e)}")
        return False

    try:
        from anti_crawler_strategy import create_default_strategy_manager
        print("✓ anti_crawler_strategy 模块导入成功")
    except Exception as e:
        print(f"✗ anti_crawler_strategy 模块导入失败: {str(e)}")
        return False

    try:
        from intelligent_judicial_query import IntelligentJudicialQuery
        print("✓ intelligent_judicial_query 模块导入成功")
    except Exception as e:
        print(f"✗ intelligent_judicial_query 模块导入失败: {str(e)}")
        return False

    print("\n✓ 所有模块导入成功\n")
    return True


def test_captcha_config():
    """测试验证码配置文件"""
    print("=" * 80)
    print("【测试 2/5】验证码配置文件测试")
    print("=" * 80)

    config_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'references',
        'captcha_api_config.json'
    )

    if not os.path.exists(config_file):
        print(f"✗ 配置文件不存在: {config_file}")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"✓ 配置文件读取成功: {config_file}")

        # 检查配置结构
        for provider in ['baidu', 'aliyun', 'tencent']:
            if provider in config:
                enabled = config[provider].get('enabled', False)
                status = '已启用' if enabled else '未启用'
                print(f"  - {provider}: {status}")

        print("\n✓ 配置文件格式正确\n")
        return True

    except Exception as e:
        print(f"✗ 读取配置文件失败: {str(e)}\n")
        return False


def test_directories():
    """测试必要的目录是否存在"""
    print("=" * 80)
    print("【测试 3/5】目录结构测试")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.dirname(__file__))

    dirs = {
        'scripts': os.path.join(base_dir, 'scripts'),
        'reports': os.path.join(base_dir, 'reports'),
        'screenshots': os.path.join(base_dir, 'screenshots'),
        'docs': os.path.join(base_dir, 'docs'),
        'references': os.path.join(base_dir, 'references'),
    }

    all_exist = True
    for name, path in dirs.items():
        if os.path.exists(path):
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: {path} (不存在)")
            os.makedirs(path, exist_ok=True)
            print(f"  → 已创建目录: {path}")
            all_exist = False

    print("\n✓ 所有必要的目录已存在或已创建\n")
    return True


def test_dependencies():
    """测试依赖包"""
    print("=" * 80)
    print("【测试 4/5】依赖包测试")
    print("=" * 80)

    dependencies = [
        'selenium',
        'requests',
        'beautifulsoup4',
        'PIL',  # Pillow
        'lxml',
    ]

    optional_dependencies = [
        ('baidu_aip', '百度 OCR'),
        ('aliyunsdkcore', '阿里云 SDK'),
        ('tencentcloud', '腾讯云 SDK'),
    ]

    all_installed = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}: 已安装")
        except ImportError:
            print(f"✗ {dep}: 未安装")
            all_installed = False

    print("\n可选依赖:")
    for dep, name in optional_dependencies:
        try:
            __import__(dep)
            print(f"✓ {name} ({dep}): 已安装")
        except ImportError:
            print(f"⊙ {name} ({dep}): 未安装（可选）")

    if all_installed:
        print("\n✓ 所有必需依赖已安装\n")
    else:
        print("\n✗ 部分依赖未安装，请运行: pip install -r requirements.txt\n")

    return all_installed


def test_query_classes():
    """测试查询类初始化"""
    print("=" * 80)
    print("【测试 5/5】查询类初始化测试")
    print("=" * 80)

    try:
        from court_documents_selenium_query import CourtDocumentsSeleniumQuery

        # 测试初始化（不实际执行查询）
        query = CourtDocumentsSeleniumQuery(headless=True, max_retries=1)
        print("✓ CourtDocumentsSeleniumQuery 初始化成功")

        # 检查属性
        if hasattr(query, 'search_url'):
            print(f"  - 查询 URL: {query.search_url}")

    except Exception as e:
        print(f"✗ CourtDocumentsSeleniumQuery 初始化失败: {str(e)}")
        return False

    try:
        from captcha_handler import CaptchaHandler

        # 测试初始化
        handler = CaptchaHandler(driver=None)
        print("✓ CaptchaHandler 初始化成功")

        # 检查配置
        if hasattr(handler, 'api_configs'):
            print(f"  - 已配置 {len(handler.api_configs)} 个 OCR 提供商")

    except Exception as e:
        print(f"✗ CaptchaHandler 初始化失败: {str(e)}")
        return False

    try:
        from anti_crawler_strategy import (
            StealthModeStrategy,
            HumanBehaviorStrategy,
            create_default_strategy_manager
        )

        # 测试策略类
        print("✓ 反爬虫策略模块导入成功")
        print("  - StealthModeStrategy")
        print("  - HumanBehaviorStrategy")
        print("  - create_default_strategy_manager")

    except Exception as e:
        print(f"✗ 反爬虫策略模块导入失败: {str(e)}")
        return False

    print("\n✓ 所有查询类初始化成功\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("技能优化功能测试")
    print("=" * 80 + "\n")

    tests = [
        ("模块导入测试", test_imports),
        ("验证码配置测试", test_captcha_config),
        ("目录结构测试", test_directories),
        ("依赖包测试", test_dependencies),
        ("查询类测试", test_query_classes),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} 测试失败: {str(e)}\n")
            results.append((test_name, False))

    # 输出总结
    print("=" * 80)
    print("测试总结")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n✓ 所有测试通过！技能优化功能正常。")
        print("\n下一步:")
        print("1. 查看快速开始指南: 快速开始指南.md")
        print("2. 编辑查询配置: scripts/intelligent_judicial_query.py")
        print("3. 运行查询: python scripts/intelligent_judicial_query.py")
    else:
        print("\n✗ 部分测试失败，请检查:")
        print("1. 是否安装了所有依赖: pip install -r requirements.txt")
        print("2. 是否配置了 Chrome 浏览器和 ChromeDriver")

    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
