# Tushare API 替换爬虫设计方案

## 1. 当前问题分析

### 1.1 现有爬虫存在的问题
- **效率低**: Selenium基于浏览器，启动慢、资源消耗大
- **不稳定**: 依赖网页结构，网站改版后需要修改代码
- **易被封**: 频繁访问容易触发反爬虫机制
- **维护成本高**: 需要处理各种异常情况、验证码等

### 1.2 使用Tushare的优势
- **官方API**: 数据稳定可靠，结构化好
- **速度快**: 直接调用接口，无需渲染页面
- **数据全**: 覆盖A股所有基础数据、财务数据、行情数据
- **维护简单**: 接口稳定，无需频繁维护

## 2. 数据映射方案

### 2.1 现有爬虫获取的数据与Tushare API映射

#### 2.1.1 股票基础信息
**原爬虫**: StockListCrawler
**Tushare API**: `stock_basic()`

| 现有字段 | Tushare字段 | 说明 |
|---------|------------|------|
| code | ts_code | 股票代码(需转换格式) |
| name | name | 股票名称 |
| market | market | 市场(SZ/SH) |
| industry_code | industry | 行业 |
| list_date | list_date | 上市日期 |
| - | area | 地域(新增) |

#### 2.1.2 日线行情数据
**原爬虫**: StockListCrawler, StockDetailCrawler
**Tushare API**: `daily()` + `daily_basic()`

| 现有字段 | Tushare API | 字段名 |
|---------|------------|-------|
| trade_date | daily() | trade_date |
| open | daily() | open |
| high | daily() | high |
| low | daily() | low |
| close | daily() | close |
| volume | daily() | vol |
| turnover | daily() | amount |
| change_percent | daily() | pct_chg |
| pe_ratio | daily_basic() | pe |
| pb_ratio | daily_basic() | pb |
| total_market_cap | daily_basic() | total_mv |
| circulating_market_cap | daily_basic() | circ_mv |
| turnover_rate | daily_basic() | turnover_rate |

#### 2.1.3 财务数据
**原爬虫**: StockDetailCrawler
**Tushare API**: `income()` + `balancesheet()` + `cashflow()` + `fina_indicator()`

| 现有字段 | Tushare API | 字段名 |
|---------|------------|-------|
| total_revenue | income() | total_revenue |
| net_profit | income() | n_income |
| eps | fina_indicator() | eps |
| gross_margin | fina_indicator() | grossprofit_margin |
| net_margin | fina_indicator() | netprofit_margin |
| total_assets | balancesheet() | total_assets |
| total_liabilities | balancesheet() | total_liab |
| net_assets | balancesheet() | total_hldr_eqy_exc_min_int |
| debt_ratio | fina_indicator() | debt_to_assets |
| current_ratio | fina_indicator() | current_ratio |
| quick_ratio | fina_indicator() | quick_ratio |
| operating_cash_flow | cashflow() | n_cashflow_act |
| roe | fina_indicator() | roe |
| roa | fina_indicator() | roa |
| bvps | fina_indicator() | bps |

#### 2.1.4 行业数据
**原爬虫**: IndustryCrawler
**Tushare API**: `index_classify()` + `index_daily()` (行业指数)

**说明**: Tushare没有直接的行业板块数据接口，有两种方案：
1. **方案A**: 使用行业指数数据(推荐)
   - API: `index_classify()` 获取行业分类
   - API: `index_daily()` 获取行业指数行情
2. **方案B**: 自行聚合计算
   - 基于个股数据按行业分组统计

**推荐使用方案A**，数据更专业。

## 3. 架构设计

### 3.1 新增模块

```
src/
├── data_source/
│   ├── __init__.py
│   ├── tushare_api.py          # Tushare API封装(已存在框架)
│   └── data_fetcher.py         # 数据获取统一接口(新增)
```

### 3.2 核心类设计

#### 3.2.1 TushareClient (src/data_source/tushare_api.py)
**职责**: 封装所有Tushare API调用

```python
class TushareClient:
    """Tushare数据源客户端"""

    def __init__(self, token: str)

    # 基础数据
    def get_stock_list(self, market=None) -> pd.DataFrame
    def get_trade_calendar(self, start_date, end_date) -> pd.DataFrame

    # 行情数据
    def get_daily_quotes(self, ts_code=None, trade_date=None) -> pd.DataFrame
    def get_daily_basic(self, ts_code=None, trade_date=None) -> pd.DataFrame

    # 财务数据
    def get_income_statement(self, ts_code, period) -> pd.DataFrame
    def get_balance_sheet(self, ts_code, period) -> pd.DataFrame
    def get_cash_flow(self, ts_code, period) -> pd.DataFrame
    def get_financial_indicator(self, ts_code, period) -> pd.DataFrame

    # 行业数据
    def get_industry_index_list() -> pd.DataFrame
    def get_industry_index_daily(self, ts_code, start_date) -> pd.DataFrame
```

#### 3.2.2 DataFetcher (src/data_source/data_fetcher.py)
**职责**: 将Tushare数据转换为系统数据模型

```python
class DataFetcher:
    """数据获取统一接口"""

    def __init__(self, tushare_client: TushareClient)

    def fetch_stocks(self) -> List[Stock]
    def fetch_daily_data(self, stock_codes, date) -> List[StockDailyData]
    def fetch_financial_data(self, stock_code) -> FinancialData
    def fetch_industries() -> List[Industry]
```

### 3.3 调用流程

```
定时任务/API请求
    ↓
DataFetcher (数据转换层)
    ↓
TushareClient (API封装层)
    ↓
Tushare API
```

## 4. 实施步骤

### 4.1 第一阶段: 完善TushareClient
- [x] 基础框架已存在
- [ ] 实现所有需要的API方法
- [ ] 添加错误处理和重试机制
- [ ] 添加调用频率限制(Tushare有接口调用限制)

### 4.2 第二阶段: 实现DataFetcher
- [ ] 创建DataFetcher类
- [ ] 实现数据格式转换逻辑
- [ ] 处理股票代码格式转换(600000 ↔ 600000.SH)

### 4.3 第三阶段: 修改定时任务
修改文件: `src/tasks/daily_tasks.py`

替换调用:
```python
# 原来
from src.crawler import IndustryCrawler, StockListCrawler
crawler = StockListCrawler('SZ')
stocks = crawler.crawl()

# 改为
from src.data_source.data_fetcher import DataFetcher
fetcher = DataFetcher()
stocks = fetcher.fetch_stocks()
```

### 4.4 第四阶段: 更新配置文件
修改文件: `config/config.yaml`

```yaml
# 新增Tushare配置
tushare:
  token: "58ed199914f035540b89da2694939ac4fc2305b297792b0759703bef"
  timeout: 30
  retry_count: 3
  retry_delay: 1

  # 接口调用频率限制(次/分钟)
  rate_limit:
    default: 200  # 普通用户200次/分钟
```

### 4.5 第五阶段: 移除爬虫代码(可选)
- [ ] 保留爬虫代码作为备用方案
- [ ] 或完全移除src/crawler目录

## 5. 数据同步策略

### 5.1 股票列表
- **频率**: 每周更新一次(新股上市不频繁)
- **时间**: 周末执行
- **方法**: 全量更新

### 5.2 日线行情
- **频率**: 每交易日收盘后
- **时间**: 15:30 (交易日)
- **方法**: 增量更新当日数据

### 5.3 财务数据
- **频率**: 季报发布期每日更新，其他时间每月更新
- **时间**: 每日22:00
- **方法**: 增量更新最新报告期数据

### 5.4 行业数据
- **频率**: 每交易日
- **时间**: 16:00
- **方法**: 更新当日数据

## 6. 关键技术点

### 6.1 股票代码格式转换
```python
def convert_to_ts_code(code: str, market: str) -> str:
    """
    转换为Tushare格式: 600000 -> 600000.SH
    """
    return f"{code}.{market}"

def convert_from_ts_code(ts_code: str) -> tuple:
    """
    从Tushare格式转换: 600000.SH -> (600000, SH)
    """
    code, market = ts_code.split('.')
    return code, market
```

### 6.2 日期格式处理
```python
# Tushare使用YYYYMMDD格式
trade_date = '20250104'

# 系统使用date对象
from datetime import datetime
date_obj = datetime.strptime(trade_date, '%Y%m%d').date()
```

### 6.3 API调用频率控制
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=200):
    """API调用频率限制装饰器"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

### 6.4 批量获取优化
```python
# 避免循环调用API，使用批量接口
# 不推荐:
for code in stock_codes:
    data = ts_client.get_daily_quotes(code, date)

# 推荐:
all_data = ts_client.get_daily_quotes(trade_date=date)  # 获取全市场
```

## 7. 注意事项

### 7.1 Tushare接口限制
- **普通用户**: 200次/分钟
- **权限积分**: 部分接口需要积分权限
- **数据延迟**: 实时行情可能有延迟

### 7.2 异常处理
- 网络异常: 自动重试3次
- 接口限流: 自动等待后重试
- 无数据: 记录日志但不中断程序

### 7.3 数据验证
- 检查返回数据是否为空
- 验证数据字段完整性
- 检查数据合理性(如价格>0)

### 7.4 兼容性
- 保持数据模型不变，只修改数据来源
- API接口不需要修改
- 前端无需改动

## 8. 预期收益

### 8.1 性能提升
- 数据获取速度: **提升10-20倍**
- 资源占用: **降低80%** (无需启动浏览器)
- 稳定性: **提升95%** (官方API)

### 8.2 维护成本
- 代码维护: **减少70%**
- 异常处理: **减少90%**
- 更新频率: **几乎为0**

## 9. 风险与备用方案

### 9.1 风险点
- **Token失效**: Tushare token过期或被封
- **接口变更**: Tushare接口升级(概率很低)
- **积分不足**: 某些高级接口需要积分

### 9.2 备用方案
- 保留原爬虫代码作为备份
- 实现数据源切换机制(Tushare/爬虫)
- 配置文件控制数据源选择

```yaml
# config.yaml
data_source:
  primary: "tushare"    # tushare | crawler
  fallback: "crawler"   # 备用数据源
```

## 10. 工作量估计

| 阶段 | 工作内容 | 预计工时 |
|-----|---------|---------|
| 1 | 完善TushareClient | 2小时 |
| 2 | 实现DataFetcher | 2小时 |
| 3 | 修改定时任务 | 1小时 |
| 4 | 更新配置和测试 | 1小时 |
| 5 | 文档更新 | 0.5小时 |
| **总计** | | **6.5小时** |

## 11. 后续优化方向

1. **数据缓存**: 实现本地缓存减少API调用
2. **增量更新**: 只更新变化的数据
3. **并发获取**: 使用线程池提升批量获取速度
4. **数据质量**: 添加数据校验和清洗逻辑
5. **监控告警**: 添加数据更新监控和异常告警

---

**文档版本**: v1.0
**创建日期**: 2025-11-04
**作者**: Claude Code
