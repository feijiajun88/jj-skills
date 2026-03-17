# 司法信息查询技能 (Judicial Information Query)

> 通过中国执行信息公开网和裁判文书网查询个人司法信息，自动重试直到获取查询结果，生成背景调查报告。

---

## 功能特点

- ✅ **双站点查询**：同时查询执行信息公开网和裁判文书网
- ✅ **自动重试**：查询失败自动重试，直到成功或达到最大尝试次数
- ✅ **截图记录**：自动保存查询过程和结果截图
- ✅ **命令行支持**：支持通过命令行参数输入姓名和身份证号
- ✅ **反爬虫策略**：智能检测并规避反爬虫机制
- ✅ **数据脱敏**：自动对敏感信息进行脱敏处理

---

## 快速开始

### 1. 安装依赖

```bash
cd /Users/jj/CodeBuddy/skill/personal-background-check
pip install -r requirements.txt
```

### 2. 执行查询

```bash
# 使用简化双站点查询脚本（推荐）
# 自动查询执行信息公开网和裁判文书网，直到获取结果
python scripts/simple_dual_query.py --name "张三" --id-card "110101199001011234"

# 无头模式（后台运行，不显示浏览器窗口）
python scripts/simple_dual_query.py --name "张三" --id-card "110101199001011234" --headless

# 增加最大尝试次数（默认10次）
python scripts/simple_dual_query.py --name "张三" --id-card "110101199001011234" --max-attempts 15
```

### 3. 查看报告

生成的报告将保存在 `reports/` 目录下：
- `查询结果_张三_20260304_103000.json` - JSON格式查询结果
- `screenshots/` - 查询过程和结果截图

---

## 使用场景

### 客户背景调查（KYC/尽职调查）

```bash
# 直接通过命令行参数输入客户信息
python scripts/simple_dual_query.py --name "客户姓名" --id-card "客户身份证号"

# 示例
python scripts/simple_dual_query.py --name "张三" --id-card "110101199001011234"
```

### 个人风险筛查

```bash
# 批量查询（配合shell脚本使用）
python scripts/simple_dual_query.py --name "李四" --id-card "310101199002022345" --headless
```

---

## 技能结构

```
personal-background-check/
├── SKILL.md                          # 技能主文档
├── README.md                         # 本文件
├── requirements.txt                  # Python依赖
│
├── scripts/                          # 查询脚本
│   ├── __init__.py                   # 模块初始化
│   ├── simple_dual_query.py          # 【推荐】简化双站点查询脚本
│   ├── utils.py                      # 工具函数
│   └── ...                           # 其他辅助脚本
│
├── references/                       # 参考文档
│
├── docs/                             # 文档目录
│
└── assets/                           # 资源目录
    └── report_template.md            # 报告模板
```

---

## 查询平台覆盖

### 司法类平台（核心）
- **中国执行信息公开网** - 被执行人信息、限制消费令
- **失信被执行人名单** - 失信行为记录
- **中国裁判文书网** - 裁判文书（需要特殊处理）

---

## 脚本说明

### 智能查询脚本（推荐）

`intelligent_judicial_query.py` - 最先进的查询脚本

**特性**：
- 多策略自动回退（undetected-chromedriver → 标准 Selenium）
- 人类行为模拟（随机打字、滚动、点击延迟）
- 智能重试机制（每个策略最多重试 3 次）
- 反检测技术（隐藏 webdriver 特征）
- 完善的日志（截图保存、详细操作记录）

**使用方法**：
```python
# 修改脚本中的查询信息
query = IntelligentJudicialQuery(headless=False, max_retries=3)
results = query.query_all(name, id_card)
```

详细使用说明请参考：`docs/智能查询脚本使用说明.md`

### 增强型查询脚本

`enhanced_judicial_query.py` - 基础查询脚本

**特性**：
- 多个 User-Agent 轮换
- 随机延迟机制
- 手动查询指南生成

### 测试脚本

`test_website_access.py` - 网站访问测试

用于测试司法网站是否可以正常访问，检查输入框和按钮。

`test_optimization.py` - 优化功能测试

用于测试优化后的功能是否正常工作：
- 模块导入测试
- 验证码配置测试
- 目录结构测试
- 依赖包测试
- 查询类测试

---

## 报告格式

生成的报告包含以下内容：

### JSON 结果文件

- **查询时间** - 查询执行的时间戳
- **人员信息** - 姓名、脱敏后的身份证号
- **查询结果**：
  - 被执行人信息
  - 失信被执行人名单
  - 限制消费令
- **汇总统计**：
  - 总查询数
  - 成功查询数
  - 发现的记录数

### 截图文件

- 查询页面截图
- 查询结果截图
- 错误场景截图

---

## 配置要求

### 系统要求

- Python 3.8+
- 稳定的网络连接
- Chrome 浏览器（用于 Selenium 自动化）

### Python 依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `requests` - HTTP请求
- `beautifulsoup4` - HTML解析
- `lxml` - XML解析
- `selenium` - 浏览器自动化
- `undetected-chromedriver` - 反检测驱动（可选但推荐）

---

## 注意事项

1. **隐私保护**：
   - 仅查询公开信息，不涉及隐私数据
   - 自动对身份证号、手机号等敏感信息脱敏
   - 使用时请遵守相关法律法规

2. **数据来源**：
   - 所有数据来自官方公开平台
   - 裁判文书网有反爬机制，建议使用 Selenium

3. **查询限制**：
   - 部分平台可能有查询频率限制
   - 建议合理规划查询频率，避免触发反爬

4. **法律合规**：
   - 本技能仅用于合法的背景调查
   - 不得用于非法目的
   - 用户对查询结果的合法使用负责

---

## 常见问题

### Q1: 查询失败怎么办？

A: 智能查询脚本会自动重试并切换策略。如果仍然失败：
1. 检查网络连接
2. 查看 `screenshots/` 目录下的截图，了解失败原因
3. 稍后重试，避免短时间内多次查询

### Q2: 如何修改查询对象？

A: 编辑对应脚本中的 `main()` 函数：
```python
def main():
    name = "目标姓名"      # 修改为目标姓名
    id_card = "目标身份证号"  # 修改为目标身份证号（18位）
```

### Q3: undetected-chromedriver 安装失败？

A: 执行以下命令：
```bash
pip install undetected-chromedriver
```

### Q4: 如何查看查询结果？

A: 查询结果以 JSON 格式保存在 `reports/` 目录下，可以使用文本编辑器或 JSON 查看工具打开。

### Q5: headless 模式是什么？

A: headless 模式是指不显示浏览器窗口，后台运行查询。
- `headless=True` - 后台运行，无窗口
- `headless=False` - 显示浏览器窗口，可观察查询过程（推荐用于调试）

---

## 技术支持

如遇问题，请参考：
- SKILL.md - 技能完整文档
- 快速开始指南.md - 快速上手指南
- docs/优化说明文档.md - 优化功能详细说明
- docs/智能查询脚本使用说明.md - 智能查询脚本详细说明
- references/ - 详细参考文档
- 各平台官方帮助文档

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v3.0.0 | 2026-03-04 | 简化查询功能，只保留双站点查询；新增自动重试直到成功功能；优化命令行参数支持 |
| v2.1.0 | 2026-02-06 | 新增裁判文书 Selenium 查询、验证码识别、反爬虫策略 |
| v2.0.0 | 2026-02-03 | 重构为仅保留司法查询模块，添加智能查询脚本 |
| v1.0.0 | 2025-02-02 | 初始版本，包含完整功能 |

---

## 免责声明

本技能查询的所有信息均来自官方公开平台，仅供参考使用。不构成任何法律意见或建议。使用本技能应遵守相关法律法规，不得用于非法目的。用户应对查询结果的合法使用负责。
