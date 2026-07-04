# 每日市场晨报

每天自动发送 4 封金融邮件到邮箱：**晨报**（68+ 指标数据分析）、**午/晚间要闻**（40+ 来自源翻译新闻）、**周报**（涨跌排行 + 财报日历 + 放量预警）。

[English](#english) | 简体中文

---

## 功能

| 邮件 | 时间 | 内容 |
|------|------|------|
| **每日市场晨报** | 每天 07:00 | 68+ 标的实时数据：涨跌幅、5/20日趋势、52周位置、成交量、简评、放量预警 |
| **午间金融要闻** | 每天 12:00 | 14个来源的金融新闻，自动翻译中文 + 标签分类（利好/利空/关注利率等） |
| **晚间金融要闻** | 每天 18:00 | 午后最新财经新闻，英文摘要自动翻译 |
| **每周市场周报** | 周日 08:00 | 周涨跌 Top5 / Bottom5、下周财报日历（62只个股）、11大指数/黄金/比特币周表现 |

## 覆盖资产（68+ 标的、14 个板块）

| 板块 | 标的 |
|------|------|
| 市场指标 | VIX、VXN（纳指波动）、DXY（美元指数）、美10年/2年国债、中国10年国债、日本10年国债、波罗的海干散货、恐惧贪婪指数 |
| 外汇 | 在岸/离岸人民币、日元、欧元 |
| 三大指数 | 道琼斯、标普500、纳指、纳指100 |
| 亚太指数 | 日经225、韩国KOSPI、台湾加权 |
| 欧洲指数 | 欧洲斯托克50、英国富时100、德国DAX |
| 中国指数 | 上证、恒生科技、科创50 |
| 商品 | 黄金、白银、原油、铜、铝、CRB指数、大豆、棉花、玉米、天然气 |
| 美股七姐妹 | AAPL、MSFT、GOOGL、AMZN、NVDA、META、TSLA |
| 传统蓝筹 | JPM、BRK-B、JNJ、KO、BA |
| 半导体 | MU、STX、INTC、ASML、MRVL、SMH、费城半导体 |
| 机器人与自动化 | ROBO ETF、深证机器人指数 |
| 新能源与锂矿 | LIT、ICLN、隆基绿能、通威(多晶硅) |
| 中国个股 | 茅台、腾讯、新易盛、中际旭创、招行、平安、宁德时代、比亚迪 |
| 加密货币 | BTC、ETH |

## 邮件示例

```
┌──────────────────────────────────┐
│      每日市场晨报 · 2026-07-02    │
├──────────────────────────────────┤
│ 放量预警: NVDA 放量 3.2倍 +3.5%  │
│──────────────────────────────────│
│ 市场指标                         │
│ VIX 15.3 │ DXY 98.2 │ TNX 4.25% │
│──────────────────────────────────│
│ 外汇        CNY 7.25 │ JPY 144   │
│──────────────────────────────────│
│ 三大指数    道指 +0.5% 标普 +0.8%│
│ ...                              │
└──────────────────────────────────┘
```

每条标的显示：**最新价（带货币单位 $ / ¥ / HK$）| 涨跌幅 | 5日趋势 | 20日趋势 | 52周位置 | 成交量 | 自动简评**

红涨绿跌（中国习惯），移动端适配。

## 技术栈

| 组件 | 技术 |
|------|------|
| 数据源 | **Yahoo Finance**（免费，无 API Key）、**CoinGecko**（加密） |
| 新闻翻译 | **Google Translate**（deep-translator） |
| 邮件发送 | **QQ邮箱 SMTP** |
| 定时调度 | **GitHub Actions**（`cron`，4 条独立队列互不干扰） |
| 语言 | **Python 3.11+** |
| 模板 | **Jinja2**（HTML 邮件） |

## 快速开始

### 前置条件

1. **QQ邮箱**（或其他 SMTP 邮箱）
2. **GitHub 账号**

### 部署步骤（3 分钟）

#### 1. Fork 本仓库

点击右上角 **Fork** → 选择你的账号。

#### 2. 获取 QQ邮箱 SMTP 授权码

登录 [QQ邮箱](https://mail.qq.com) → 设置 → 账户 → POP3/SMTP 服务 → 开启 → 记录 16 位授权码。

#### 3. 设置 GitHub Secrets

仓库 → Settings → Secrets and variables → Actions → New repository secret：

| Secret | 值 |
|--------|-----|
| `SMTP_USER` | 你的QQ邮箱，如 `123456@qq.com` |
| `SMTP_PASS` | QQ邮箱 SMTP 授权码（16位字母） |
| `RECIPIENTS` | 收件人邮箱，逗号分隔如 `a@qq.com,b@163.com` |

#### 4. 启用 Workflow

GitHub Actions 可能默认禁用 Fork 仓库的 Workflow。去 Actions 标签页 → 点击 "I understand my workflows, go ahead and enable them"。

#### 5. 手动触发测试

Actions → Morning Report → Run workflow → 选 master 分支 → Run。

---

部署完成！每天早上 7:00 自动收到晨报。

## 自定义

### 加新的股票/指数

编辑 `config.py`，在对应列表加一行：

```python
INDEXES = [
    {"name": "纳斯达克100", "symbol": "^NDX", "unit": ""},
    # 加这行 ↓
    {"name": "富时中国A50", "symbol": "XINA50.FGI", "unit": ""},
]
```

| 字段 | 说明 |
|------|------|
| `name` | 显示名称 |
| `symbol` | Yahoo Finance 代码 |
| `unit` | `$`（美元）、`¥`（人民币）、`HK$`（港币）、`%`（债券）、`""`（指数/外汇） |

### 新增整个板块

1. 在 `config.py` 加新列表（参照现有的 `BLUE_CHIPS`）
2. 在 `main.py` 的 `all_categories` 和 `all_data` 加相应条目
3. 在 `template.html` 加新的 `<div class="section">` 区域

### 调整发送时间

修改对应的 workflow 文件的 `cron` 表达式：

| 文件 | 说明 |
|------|------|
| `.github/workflows/morning-report.yml` | `0 23 * * *` = UTC 23:00 = 北京时间 07:00 |
| `.github/workflows/noon-news.yml` | `0 4 * * *` = 北京时间 12:00 |
| `.github/workflows/evening-news.yml` | `0 10 * * *` = 北京时间 18:00 |
| `.github/workflows/weekly-report.yml` | `0 0 * * 0` = 周日 08:00 |

> UTC = 北京时间 - 8 小时

### 加收件人

更新 `RECIPIENTS` Secret，改成逗号分隔的邮箱列表即可，如：
```
a@qq.com,b@163.com,c@gmail.com
```

### 增加新闻来源

编辑 `news.py` 的 `NEWS_SOURCES` 列表，加任意 Yahoo Finance 支持的 ticker 代码。

## 注意事项

- **GitHub Actions 免费额度**：公开仓库无限、私有仓库 2000 分钟/月。本项目每天消耗约 2-3 分钟。
- **QQ邮箱 SMTP 限额**：每天约 500 封。每个收件人消耗 1 封/封邮件。3 封 × 50 人 = 150 封，安全。
- **cron 延迟**：GitHub Actions cron 在高峰期可能有 5-15 分钟延迟。
- **非交易日的隔夜数据**：周末晨报显示周五收盘价保持不变。
- **A股数据**：基于昨日收盘价，非实时行情。

## 项目结构

```
stock-morning-report/
├── config.py              # 所有标的、板块、颜色配置
├── main.py                # 晨报主脚本
├── news.py                # 新闻采集 + 翻译 + 发送
├── weekly.py              # 周报脚本
├── template.html          # 晨报 HTML 邮件模板
├── requirements.txt       # Python 依赖
├── .github/workflows/     # GitHub Actions 定时
│   ├── morning-report.yml
│   ├── noon-news.yml
│   ├── evening-news.yml
│   └── weekly-report.yml
└── README.md
```

## License

MIT License — 详见 [LICENSE](./LICENSE)

---

## English

A fully automated daily financial digest delivered to your inbox at 07:00, 12:00, 18:00, and Sunday 08:00 (Beijing time). Powered by Yahoo Finance + CoinGecko, running on GitHub Actions at zero cost.

- **Morning Report**: 68+ symbols across 14 categories with price, change%, trends, 52-week range, volume, and AI-generated commentary.
- **Noon/Evening News**: Financial news from 14 sources, auto-translated to Chinese with sentiment tags.
- **Weekly Report**: Top/bottom performers, upcoming earnings calendar for 62 stocks, and key index benchmarks.

### Quick Deploy

1. Fork this repo
2. Set 3 GitHub Secrets: `SMTP_USER`, `SMTP_PASS`, `RECIPIENTS`
3. Enable Actions
4. Done — emails arrive daily

### Tech Stack

Python 3.11+ / Yahoo Finance / CoinGecko / Google Translate / GitHub Actions / Jinja2 / QQ Mail SMTP

**Cost**: $0 (all free-tier services)

**Supports**: Multiple recipients, currency unit display (USD/CNY/HKD), red-up-green-down (Chinese convention), mobile-friendly HTML.
