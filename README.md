# Graham Value Investment Analyzer for A-Shares
# 格雷厄姆价值投资A股分析系统

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

基于格雷厄姆价值投资理论的智能化A股分析系统，实现自动化数据采集、价值评估和投资建议生成。

## 特性

- 自动采集东方财富网的行业数据和个股数据
- 基于格雷厄姆价值投资算法的股票筛选和评估
- 多维度财务分析和风险评估
- 可视化界面展示分析结果和投资建议
- 定时任务自动更新数据
- RESTful API服务
- **🆕 线程池支持** - 高效并发爬取
- **🆕 IP代理池** - 防止IP封禁
- **🆕 速率限制** - 智能频率控制

## 技术栈

### 后端
- Python 3.9+
- Flask - Web框架
- SQLAlchemy - ORM
- Selenium - 数据爬取
- APScheduler - 定时任务

### 前端
- React 18
- Ant Design - UI组件
- ECharts - 数据可视化
- Vite - 构建工具

### 数据库
- SQLite (默认)
- PostgreSQL (可选)

## 项目结构

\`\`\`
code_F/
├── doc/                          # 文档目录
│   └── 程序设计文稿.md
├── src/                          # 源代码目录
│   ├── crawler/                  # 数据爬虫模块
│   │   ├── base_crawler.py
│   │   ├── industry_crawler.py
│   │   ├── stock_list_crawler.py
│   │   └── stock_detail_crawler.py
│   ├── models/                   # 数据模型
│   │   ├── database.py
│   │   ├── industry.py
│   │   ├── stock.py
│   │   ├── financial.py
│   │   └── valuation.py
│   ├── analysis/                 # 分析模块
│   │   ├── graham_algorithm.py
│   │   ├── financial_analysis.py
│   │   ├── industry_analysis.py
│   │   └── risk_assessment.py
│   ├── api/                      # API服务
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── controllers.py
│   ├── tasks/                    # 定时任务
│   │   ├── scheduler.py
│   │   └── daily_tasks.py
│   └── utils/                    # 工具函数
│       ├── config.py
│       ├── logger.py
│       └── helpers.py
├── frontend/                     # 前端代码
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── data/                         # 数据目录
├── logs/                         # 日志目录
├── config/                       # 配置文件
│   └── config.yaml
├── requirements.txt
├── run.py
└── README.md
\`\`\`

## 安装与运行

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- Chrome/Chromium浏览器（用于Selenium）
- macOS / Linux / Windows

### 2. 后端安装

\`\`\`bash
# 克隆项目
cd /home/bestfunc/code/code_win/code_F

# 安装Python依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env
# 编辑.env文件，配置相关参数（如有需要）

# 初始化数据库
python -c "from src.models.database import init_db; init_db()"
\`\`\`

### 3. 前端安装

\`\`\`bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
\`\`\`

### 4. 运行项目

#### 启动后端服务

\`\`\`bash
# 在项目根目录
python run.py
\`\`\`

后端服务将在 http://localhost:5000 启动

#### 启动前端服务

\`\`\`bash
# 在frontend目录
npm run dev
\`\`\`

前端服务将在 http://localhost:3000 启动

### 5. 访问应用

打开浏览器访问: http://localhost:3000

## 使用说明

### API接口

#### 行业相关
- `GET /api/v1/industries` - 获取所有行业列表
- `GET /api/v1/industries/{code}` - 获取特定行业详情
- `GET /api/v1/industries/ranking` - 获取行业排名

#### 股票相关
- `GET /api/v1/stocks` - 获取股票列表
- `GET /api/v1/stocks/{code}` - 获取股票详情
- `GET /api/v1/stocks/{code}/financial` - 获取财务数据
- `GET /api/v1/stocks/{code}/valuation` - 获取估值分析

#### 分析相关
- `GET /api/v1/analysis/recommendations` - 获取推荐股票列表
- `GET /api/v1/analysis/graham/{code}` - 获取格雷厄姆分析结果

### 定时任务

系统自动运行以下定时任务：
- **交易日数据更新**: 每个交易日15:30更新
- **行业数据更新**: 每小时更新
- **实时行情更新**: 每分钟更新（仅交易时间）
- **周末深度分析**: 周六10:00执行

### 手动触发数据爬取

\`\`\`bash
# 爬取行业数据
python -c "from src.crawler import IndustryCrawler; IndustryCrawler().run()"

# 爬取股票列表
python -c "from src.crawler import StockListCrawler; StockListCrawler('SZ').run(max_pages=2)"
\`\`\`

## 核心算法

### 格雷厄姆内在价值计算

系统实现了三种内在价值计算模型：

1. **简化格雷厄姆公式**
   \`\`\`
   内在价值 = (EPS × (8.5 + 2g)) × 4.4 / Y
   其中：
   - EPS: 每股收益
   - g: 预期年增长率
   - Y: AAA公司债收益率
   \`\`\`

2. **净资产价值法** - 适用于资产型公司

3. **盈利能力模型** - 基于利润增长的估值

### 综合评分系统 (100分)

- **财务健康度** (25分): 流动比率、速动比率、资产负债率等
- **盈利能力** (25分): ROE、净利率、毛利率等
- **估值水平** (25分): PE、PB、PEG比率
- **安全边际** (25分): 当前价格与内在价值的差距

### 投资建议分级

- **90-100分**: 强烈推荐
- **75-89分**: 推荐
- **60-74分**: 可考虑
- **60分以下**: 不推荐

## 配置说明

主要配置文件：`config/config.yaml`

\`\`\`yaml
# 格雷厄姆算法配置
graham:
  filter:
    min_market_cap: 500000000  # 最小市值5亿
    max_pe_ratio: 25
    max_pb_ratio: 3
    min_roe: 0.1               # 最小ROE 10%
    max_debt_ratio: 0.6        # 最大资产负债率60%

  safety_margin:
    excellent: 0.5             # 优秀: 50%
    good: 0.3                  # 良好: 30%
    acceptable: 0.2            # 可接受: 20%
\`\`\`

## 开发说明

### 添加新的爬虫

1. 继承 `BaseCrawler` 类
2. 实现 `crawl()` 方法
3. 在 `__init__.py` 中导出

\`\`\`python
from src.crawler.base_crawler import BaseCrawler

class MyCrawler(BaseCrawler):
    def crawl(self):
        # 实现爬取逻辑
        pass
\`\`\`

### 添加新的分析模块

在 `src/analysis/` 目录下创建新的分析器类。

### 扩展API接口

1. 在 `src/api/controllers.py` 添加控制器方法
2. 在 `src/api/routes.py` 注册路由

## 注意事项

⚠️ **重要提示**:

1. **数据使用**: 本系统仅供学习和研究使用，爬取的数据请遵守网站的robots.txt和使用条款
2. **投资风险**: 本系统不构成投资建议，投资有风险，入市需谨慎
3. **爬虫频率**: 请合理控制爬虫频率，避免对目标网站造成过大压力
4. **数据准确性**: 爬取的数据可能存在延迟或错误，请以官方数据为准

## 线程池和代理池

### 线程池使用

支持多线程并发爬取，提高效率：

\`\`\`python
from src.utils.thread_pool import ThreadPool

pool = ThreadPool(max_workers=5)
results = pool.submit_tasks(crawl_func, items)
\`\`\`

### 代理池使用

防止IP被封禁，支持大规模爬取：

\`\`\`python
from src.utils.proxy_pool import proxy_pool

# 从文件加载代理
proxy_pool.add_proxies_from_file('config/proxies.txt')

# 测试代理
proxy_pool.test_all_proxies()

# 获取可用代理
proxy_dict = proxy_pool.get_proxy_dict()
\`\`\`

详细使用指南请查看 [PROXY_GUIDE.md](PROXY_GUIDE.md)

## 测试结果

已完成网络访问测试：

✅ **测试状态**: 全部通过
✅ **访问正常**: 无封禁、无验证码
✅ **风险等级**: 🟢 低

详细测试报告请查看 [TEST_RESULTS.md](TEST_RESULTS.md)

## 常见问题

### Q: 爬虫运行失败怎么办？
A:
1. 检查网络连接
2. 确认Chrome/Chromium已安装
3. 检查目标网站结构是否变化
4. 查看日志文件排查问题
5. 运行测试脚本: `python tests/test_simple.py`

### Q: 如何修改数据源？
A: 修改 `config/config.yaml` 中的URL配置，并相应调整爬虫解析逻辑。

### Q: 数据库在哪里？
A: 默认使用SQLite，数据库文件位于 `data/database/stocks.db`

### Q: 如何部署到生产环境？
A:
1. 使用PostgreSQL替代SQLite
2. 使用Gunicorn运行Flask应用
3. 使用Nginx作为反向代理
4. 配置定时任务cron
5. 启用日志监控

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 免责声明

本系统仅供学习和研究使用，不构成任何投资建议。使用本系统进行投资决策的风险由用户自行承担。作者不对使用本系统造成的任何损失负责。

---

**开发者**: AI Assistant
**版本**: v1.0.0
**最后更新**: 2024-01-01
