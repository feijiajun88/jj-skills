# 查询平台详细说明

本文档详细说明各查询平台的查询规则、API接口、返回数据格式等信息。

---

## 一、法院司法类平台

### 1. 中国执行信息公开网 (zxgk.court.gov.cn)

#### 被执行人信息查询

**平台地址**：https://zxgk.court.gov.cn/

**查询接口**：
- 网页查询：https://zxgk.court.gov.cn/zhixing/
- API接口：需通过第三方服务

**查询参数**：
```json
{
  "pName": "被执行人姓名",
  "pCardNum": "身份证号/组织机构代码",
  "selectCourtId": "执行法院ID",
  "pCode": "验证码"
}
```

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| caseCode | 案号 |
| caseState | 案件状态 |
| execCourtName | 执行法院 |
| partyCardNum | 证件号码 |
| partyName | 当事人姓名 |
| caseCreateTime | 立案日期 |
| execMoney | 执行标的 |

**查询限制**：
- 需要验证码
- 单次查询返回最多10条
- 建议重试次数：5次

---

#### 失信被执行人名单查询

**平台地址**：https://zxgk.court.gov.cn/shixin/

**查询参数**：
```json
{
  "pName": "姓名",
  "pCardNum": "身份证号",
  "pProvince": "省份"
}
```

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| iname | 被执行人姓名 |
| cardNum | 身份证号 |
| caseCode | 案号 |
| courtName | 执行法院 |
| areaName | 省份 |
| gistId | 执行依据文号 |
| regDate | 立案时间 |
| publishDate | 发布时间 |
| duty | 生效法律文书确定的义务 |
| performance | 被执行人的履行情况 |
| disruptTypeName | 失信被执行人行为具体情形 |

---

#### 限制消费人员查询

**平台地址**：https://zxgk.court.gov.cn/xgl/

**查询参数**：
```json
{
  "pName": "姓名",
  "pCardNum": "身份证号"
}
```

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| caseCode | 案号 |
| courtName | 执行法院 |
| xiName | 被限制人姓名 |
| xiCardNum | 证件号码 |
| publishDate | 发布日期 |
| limitContent | 限制消费内容 |

---

### 2. 中国裁判文书网 (wenshu.court.gov.cn)

**平台地址**：https://wenshu.court.gov.cn/

**查询接口**：
- 网页查询（需登录）
- 无公开API，需爬虫技术

**查询参数**：
```json
{
  "keyword": "当事人姓名",
  "caseType": "案件类型",  // 民事/刑事/行政
  "court": "法院名称",
  "dateStart": "开始日期",
  "dateEnd": "结束日期"
}
```

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| caseName | 案件名称 |
| caseNumber | 案号 |
| courtName | 法院名称 |
| caseType | 案件类型 |
| caseDate | 裁判日期 |
| judgmentContent | 裁判内容摘要 |

**注意事项**：
- 网站有反爬机制
- 需要Cookie/Session
- 建议使用Selenium模拟浏览器

---

## 二、信用与金融类平台

### 3. 中国人民银行征信中心

**平台地址**：https://www.pbccrc.org.cn/

**查询方式**：
1. **线上查询**（简版）：注册账号后可查询
2. **线下查询**（详版）：需到人民银行网点

**线上查询地址**：https://ipcrs.pbccrc.org.cn/

**查询结果内容**：
- 个人基本信息
- 信贷记录（贷款、信用卡）
- 公共记录（欠税、民事判决、强制执行等）
- 查询记录

**限制**：
- 简版报告内容有限
- 详版报告需线下查询
- 查询需要本人授权

---

### 4. 国家税务总局

**个人纳税记录查询**：
- 个人所得税APP
- 自然人电子税务局：https://etax.chinatax.gov.cn/

**税务违法信息**：
- 重大税收违法案件公布：http://www.chinatax.gov.cn/

**查询限制**：
- 需要实名认证
- 个人查询需本人账号

---

## 三、社保与就业类平台

### 5. 国家社会保险公共服务平台

**平台地址**：https://si.12333.gov.cn/

**查询功能**：
- 社保参保信息
- 缴费记录
- 转移接续
- 待遇领取

**查询方式**：
1. 网站查询（需注册）
2. 掌上12333 APP
3. 各地社保局官网

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| insuranceType | 险种类型（养老/医疗/失业/工伤/生育）|
| paymentStatus | 缴费状态 |
| paymentBase | 缴费基数 |
| paymentMonth | 缴费月份 |
| paymentAmount | 缴费金额 |
| insuredYears | 参保年限 |

---

## 四、交通违法类平台

### 6. 交通安全综合服务平台

**平台地址**：https://www.122.gov.cn/

**查询方式**：
1. 网站查询（需注册）
2. 交管12123 APP

**查询内容**：
- 机动车违法记录
- 驾驶证记分
- 驾驶证状态

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| violationTime | 违法时间 |
| violationAddress | 违法地点 |
| violationBehavior | 违法行为 |
| violationCode | 违法代码 |
| fine | 罚款金额 |
| points | 扣分 |
| status | 处理状态 |

---

## 五、不动产与资产类平台

### 7. 不动产登记信息查询

**查询方式**：
- 各地不动产登记中心官网
- 政务服务网（如广东政务服务网）
- 不动产登记APP

**一般查询地址格式**：
- 北京：http://bdc.ghzrzyw.beijing.gov.cn/
- 上海：http://www.shfgj.gov.cn/
- 其他城市：搜索"[城市名] 不动产登记"

**查询内容**：
- 不动产权利人
- 不动产权证号
- 坐落位置
- 建筑面积
- 抵押情况
- 查封情况

**限制**：
- 多数地区需本人查询
- 部分地区支持委托查询
- 可能需要提供权属证明

---

### 8. 国家企业信用信息公示系统

**平台地址**：http://www.gsxt.gov.cn/

**查询内容**：
- 企业/个体户基本信息
- 股东及出资信息
- 主要人员
- 变更记录
- 行政处罚
- 经营异常名录
- 严重违法失信名单

**查询参数**：
```json
{
  "keyword": "企业名称/统一社会信用代码",
  "region": "登记地区"
}
```

**返回数据字段**：
| 字段 | 说明 |
|------|------|
| entName | 企业名称 |
| uniscId | 统一社会信用代码 |
| legalPerson | 法定代表人 |
| regCap | 注册资本 |
| estDate | 成立日期 |
| opState | 经营状态 |
| penaltyInfo | 行政处罚信息 |
| abnormalInfo | 经营异常信息 |

---

## 六、第三方API服务（可选）

### 1. 失信被执行人查询API

**服务商**：api.hackeus.cn

**接口说明**：
```
GET https://api.hackeus.cn/credit/blacklist
参数：
- name: 姓名
- idCard: 身份证号
- apiKey: API密钥
```

### 2. 被执行人查询API

**服务商**：apigateway.jianjiaoshuju.com

**接口说明**：
```
GET https://apigateway.jianjiaoshuju.com/api/v1/executed-person
参数：
- name: 姓名
- idCard: 身份证号
- appKey: 应用密钥
- sign: 签名
```

### 3. 限制高消费查询API

**服务商**：openapi.chinaz.net

**接口说明**：
```
GET https://openapi.chinaz.net/v1/restriction-consumption
参数：
- name: 姓名
- idCard: 身份证号
- token: API Token
```

### 4. 综合信用查询API

**服务商**：极证云、爱企查、企查查等

**特点**：
- 整合多个数据源
- 返回结构化数据
- 需要付费
- 需要企业认证

---

## 七、平台查询优先级与策略

### 查询优先级排序

```
高优先级（必须）：
1. 被执行人信息
2. 失信被执行人名单
3. 限制消费令

中优先级（重要）：
4. 裁判文书
5. 征信报告
6. 税务违法

低优先级（辅助）：
7. 社保记录
8. 交通违法
9. 不动产
10. 企业信息
```

### 查询策略建议

1. **并行查询**：高优先级平台同时发起查询
2. **串行查询**：中低优先级平台按需查询
3. **重试机制**：失败时自动重试，最大5次
4. **缓存策略**：查询结果缓存24小时，避免重复查询
5. **速率控制**：避免触发反爬机制，控制查询频率

---

## 八、常见错误与处理

| 错误类型 | 可能原因 | 处理建议 |
|----------|----------|----------|
| 验证码错误 | 验证码过期或输入错误 | 刷新验证码后重试 |
| 请求过于频繁 | 触发反爬机制 | 增加请求间隔，降低频率 |
| 网络超时 | 网络不稳定 | 重试，最多5次 |
| 无查询结果 | 无相关记录 | 正常情况，记录空结果 |
| 身份验证失败 | Cookie过期或权限不足 | 重新登录或检查权限 |
