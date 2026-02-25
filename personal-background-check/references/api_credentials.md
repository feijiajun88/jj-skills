# API配置指南

本文档说明如何申请和配置第三方API服务，以获取更稳定的查询能力。

---

## 概述

虽然本技能主要依赖官方免费公开平台，但部分第三方API服务可以提供：
- 更稳定的数据接口
- 结构化的返回数据
- 更高的查询成功率
- 更快的响应速度

**注意**：第三方API服务通常需要付费，且可能需要企业认证。

---

## 一、推荐API服务商

### 1. 极证云 (jizhengyun.com)

**特点**：
- 数据覆盖广（司法、税务、工商等）
- 接口稳定
- 提供沙盒环境测试

**申请步骤**：
1. 访问 https://www.jizhengyun.com/
2. 注册企业账号
3. 完成实名认证
4. 申请API权限
5. 获取 AppKey 和 AppSecret

**配置方法**：
```python
# 在 config.py 中配置
JIZHENGYUN_CONFIG = {
    'app_key': 'your_app_key',
    'app_secret': 'your_app_secret',
    'base_url': 'https://api.jizhengyun.com'
}
```

---

### 2. 爱企查 (aiqicha.baidu.com)

**特点**：
- 百度旗下，数据质量高
- 企业信息查询强大
- 个人背景调查功能完善

**申请步骤**：
1. 访问 https://aiqicha.baidu.com/
2. 注册账号
3. 申请API接入
4. 获取 Access Token

**配置方法**：
```python
AIQICHA_CONFIG = {
    'access_token': 'your_access_token',
    'base_url': 'https://aiqicha.baidu.com/api'
}
```

---

### 3. 企查查 (qcc.com)

**特点**：
- 老牌企业信息查询平台
- API文档完善
- 支持多种查询场景

**申请步骤**：
1. 访问 https://www.qcc.com/
2. 注册企业账号
3. 申请API服务
4. 获取 Key 和 SecretKey

**配置方法**：
```python
QCC_CONFIG = {
    'key': 'your_key',
    'secret_key': 'your_secret_key',
    'base_url': 'https://api.qcc.com'
}
```

---

### 4. 天眼查 (tianyancha.com)

**特点**：
- 数据量大
- 更新及时
- 界面友好

**申请步骤**：
1. 访问 https://www.tianyancha.com/
2. 注册企业账号
3. 联系商务申请API
4. 获取 API Token

**配置方法**：
```python
TIANYANCHA_CONFIG = {
    'api_token': 'your_api_token',
    'base_url': 'https://api.tianyancha.com'
}
```

---

### 5. 简缴数据 (jianjiaoshuju.com)

**特点**：
- 专注司法数据
- 价格相对较低
- 适合批量查询

**申请步骤**：
1. 访问 https://www.jianjiaoshuju.com/
2. 注册账号
3. 充值购买查询次数
4. 获取 AppKey

**配置方法**：
```python
JIANJIAO_CONFIG = {
    'app_key': 'your_app_key',
    'base_url': 'https://apigateway.jianjiaoshuju.com'
}
```

---

## 二、配置文件模板

创建 `config.py` 文件：

```python
"""
个人背景调查技能 - API配置
请根据实际情况填写以下配置
"""

# ============================================================
# 第三方API配置（可选）
# ============================================================

# 极证云配置
JIZHENGYUN_CONFIG = {
    'enabled': False,  # 是否启用
    'app_key': '',
    'app_secret': '',
    'base_url': 'https://api.jizhengyun.com'
}

# 爱企查配置
AIQICHA_CONFIG = {
    'enabled': False,
    'access_token': '',
    'base_url': 'https://aiqicha.baidu.com/api'
}

# 企查查配置
QCC_CONFIG = {
    'enabled': False,
    'key': '',
    'secret_key': '',
    'base_url': 'https://api.qcc.com'
}

# 天眼查配置
TIANYANCHA_CONFIG = {
    'enabled': False,
    'api_token': '',
    'base_url': 'https://api.tianyancha.com'
}

# 简缴数据配置
JIANJIAO_CONFIG = {
    'enabled': False,
    'app_key': '',
    'base_url': 'https://apigateway.jianjiaoshuju.com'
}

# ============================================================
# 查询设置
# ============================================================

QUERY_CONFIG = {
    # 最大重试次数
    'max_retry': 5,
    
    # 重试间隔（秒）
    'retry_delays': [1, 2, 5, 10, 30],
    
    # 请求超时时间（秒）
    'timeout': 30,
    
    # 是否使用第三方API（优先使用）
    'prefer_api': False,
    
    # 并行查询线程数
    'max_workers': 3,
    
    # 查询结果缓存时间（小时）
    'cache_hours': 24
}

# ============================================================
# 报告设置
# ============================================================

REPORT_CONFIG = {
    # 默认输出格式
    'default_format': 'docx',  # docx / pdf / md
    
    # 默认输出目录
    'output_dir': './reports',
    
    # 是否包含详细附录
    'include_appendix': True,
    
    # 风险等级颜色
    'risk_colors': {
        'none': '00B050',      # 绿色
        'low': 'FFC000',       # 黄色
        'medium': 'FF6600',    # 橙色
        'high': 'FF0000'       # 红色
    }
}

# ============================================================
# 日志设置
# ============================================================

LOG_CONFIG = {
    'level': 'INFO',
    'file': './logs/background_check.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
```

---

## 三、环境变量配置

如果你不想将API密钥直接写在代码中，可以使用环境变量：

### 1. 设置环境变量

**Linux/macOS**：
```bash
export JIZHENGYUN_APP_KEY="your_app_key"
export JIZHENGYUN_APP_SECRET="your_app_secret"
export QCC_KEY="your_key"
export QCC_SECRET_KEY="your_secret_key"
```

**Windows**：
```cmd
set JIZHENGYUN_APP_KEY=your_app_key
set JIZHENGYUN_APP_SECRET=your_app_secret
```

### 2. 在Python中使用

```python
import os
from config import JIZHENGYUN_CONFIG

# 从环境变量读取
JIZHENGYUN_CONFIG['app_key'] = os.getenv('JIZHENGYUN_APP_KEY', '')
JIZHENGYUN_CONFIG['app_secret'] = os.getenv('JIZHENGYUN_APP_SECRET', '')
```

---

## 四、API调用示例

### 示例1：调用极证云API查询失信名单

```python
import requests
import hashlib
import time
from config import JIZHENGYUN_CONFIG

def query_dishonest_list(name, id_card):
    """查询失信被执行人名单"""
    if not JIZHENGYUN_CONFIG['enabled']:
        return None
    
    timestamp = str(int(time.time()))
    sign_str = f"{JIZHENGYUN_CONFIG['app_key']}{timestamp}{JIZHENGYUN_CONFIG['app_secret']}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    url = f"{JIZHENGYUN_CONFIG['base_url']}/credit/dishonest"
    params = {
        'app_key': JIZHENGYUN_CONFIG['app_key'],
        'timestamp': timestamp,
        'sign': sign,
        'name': name,
        'idCard': id_card
    }
    
    response = requests.get(url, params=params, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None
```

### 示例2：调用简缴数据API查询被执行人

```python
import requests
from config import JIANJIAO_CONFIG

def query_executed_persons(name, id_card):
    """查询被执行人信息"""
    if not JIANJIAO_CONFIG['enabled']:
        return None
    
    url = f"{JIANJIAO_CONFIG['base_url']}/api/v1/executed-person"
    headers = {
        'appKey': JIANJIAO_CONFIG['app_key']
    }
    params = {
        'name': name,
        'idCard': id_card
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None
```

---

## 五、费用参考

各API服务商的收费标准（仅供参考，以实际为准）：

| 服务商 | 计费方式 | 参考价格 |
|--------|----------|----------|
| 极证云 | 按次计费 | 0.1-0.5元/次 |
| 爱企查 | 包月/按次 | 99元/月起 |
| 企查查 | 包月/按次 | 199元/月起 |
| 天眼查 | 包月/按次 | 199元/月起 |
| 简缴数据 | 按次计费 | 0.05-0.3元/次 |

**建议**：
- 低频查询：使用官方免费渠道
- 中高频查询：选择简缴数据等性价比高的服务商
- 企业级应用：选择极证云、爱企查等稳定服务商

---

## 六、注意事项

1. **合法性**：确保使用API的目的合法合规
2. **隐私保护**：妥善处理查询到的个人信息
3. **数据安全**：妥善保管API密钥，避免泄露
4. **使用限制**：遵守各平台的API使用协议
5. **成本控制**：合理规划查询频率，控制费用
