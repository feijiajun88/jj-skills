# 更新日志

## [2.1.0] - 2026-02-06

### 新增
- ✨ 创建裁判文书 Selenium 查询模块 (`court_documents_selenium_query.py`)
- ✨ 实现验证码识别和处理模块 (`captcha_handler.py`)
- ✨ 实现反爬虫策略模块 (`anti_crawler_strategy.py`)
- ✨ 集成裁判文书查询到智能查询脚本
- ✨ 支持第三方 OCR API（百度、阿里云、腾讯云）
- ✨ 添加验证码 API 配置文件 (`references/captcha_api_config.json`)
- ✨ 创建优化说明文档 (`docs/优化说明文档.md`)

### 功能特性
- 裁判文书真实查询（支持 Selenium 自动化）
- 多策略反爬虫机制（undetected-chromedriver、标准 Selenium + CDP）
- 验证码自动识别（支持多种 OCR API）
- 人工验证码输入支持
- 人类行为模拟（随机打字、滚动、点击延迟）
- 请求节流和智能重试
- 完整的截图和日志记录
- 策略管理器（组合多种策略）

### 优化
- 🚀 改进查询策略回退机制
- 🚀 增强人类行为模拟
- 🚀 优化依赖库配置（添加爬虫工具）
- 🚀 完善错误处理和日志记录

### 文档
- docs/优化说明文档.md - 详细的使用说明和配置指南
- references/captcha_api_config.json - 验证码 API 配置模板

### Python脚本
- scripts/court_documents_selenium_query.py - 裁判文书 Selenium 查询
- scripts/captcha_handler.py - 验证码识别和处理
- scripts/anti_crawler_strategy.py - 反爬虫策略
- scripts/intelligent_judicial_query.py - 更新：集成裁判文书查询

### 依赖更新
- 新增：fake-useragent>=1.4.0
- 新增：random-user-agent>=1.0.1
- 可选：baidu-aip>=4.16.0（百度 OCR）
- 可选：aliyun-python-sdk-core>=2.13.0（阿里云 SDK）
- 可选：tencentcloud-sdk-python>=3.0.0（腾讯云 SDK）

## [2.0.0] - 2026-02-03

### 重构
- 🔧 重构为仅保留司法查询模块
- 🔧 添加智能查询脚本（`intelligent_judicial_query.py`）
- 🔧 移除非司法类查询模块

### 新增
- ✨ 智能查询脚本（多策略自动回退）
- ✨ 增强型查询脚本
- ✨ 测试网站访问脚本

### 优化
- 🚀 改进反爬虫处理
- 🚀 增强人类行为模拟
- 🚀 完善截图和日志记录

## [1.0.0] - 2025-02-02

### 新增
- ✅ 创建个人背景调查技能完整框架
- ✅ 实现司法类平台查询（被执行人、失信名单、限制高消费、裁判文书）
- ✅ 实现信用与金融类查询（征信报告、税务信息）
- ✅ 实现社保与交通信息查询
- ✅ 实现不动产与企业信息查询
- ✅ 实现风险评估模块（评分、评级、建议生成）
- ✅ 实现Word报告生成模块
- ✅ 实现Markdown报告生成模块
- ✅ 实现智能重试机制
- ✅ 实现数据脱敏功能
- ✅ 完整的文档和参考材料

### 功能特性
- 支持10+个查询平台
- 自动重试机制（最多6次）
- 风险评分模型（0-100分）
- 4级风险评级（无/低/中/高）
- 生成专业Word格式报告
- 生成Markdown格式报告
- 保存原始JSON数据
- 保存查询日志

### 文档
- SKILL.md - 技能主文档
- README.md - 使用说明
- requirements.txt - 依赖列表
- references/platforms.md - 平台查询规则
- references/api_credentials.md - API配置指南
- references/risk_assessment.md - 风险评估标准
- references/report_specification.md - 报告格式规范
- assets/report_template.md - 报告模板
- assets/sample_output.md - 示例输出

### Python脚本
- scripts/__init__.py - 模块初始化
- scripts/utils.py - 工具函数
- scripts/query_executed_persons.py - 被执行人查询
- scripts/query_dishonest_list.py - 失信名单查询
- scripts/query_restriction_consumption.py - 限制高消费查询
- scripts/query_court_documents.py - 裁判文书查询
- scripts/query_credit_report.py - 征信报告查询
- scripts/query_social_security.py - 社保查询
- scripts/query_tax_records.py - 税务信息查询
- scripts/query_traffic_violations.py - 交通违法查询
- scripts/query_real_estate.py - 不动产查询
- scripts/query_enterprise_info.py - 企业信息查询
- scripts/risk_assessment.py - 风险评估
- scripts/generate_report.py - 报告生成
- scripts/full_background_check.py - 完整查询入口

### 待优化
- 裁判文书查询需要Selenium支持或第三方API
- 部分平台需要完善爬虫逻辑
- 可以增加PDF报告生成功能
- 可以增加报告自定义模板功能
