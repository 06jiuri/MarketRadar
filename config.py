import os

# ============================================================
# SMTP 邮箱配置
# ============================================================
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 587
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

# 收件人列表（GitHub Secrets 中逗号分隔，格式: a@qq.com,b@163.com）
_RECIPIENTS_RAW = os.environ.get("RECIPIENTS", "")
RECIPIENTS = [r.strip() for r in _RECIPIENTS_RAW.split(",") if r.strip()]

# 邮件标题前缀
EMAIL_SUBJECT_PREFIX = "每日市场晨报"

# ============================================================
# 美股标的配置
# 格式: { "name": 显示名称, "symbol": yfinance代码 }
# ============================================================

# 三大指数
INDEXES = [
    {"name": "道琼斯工业", "symbol": "^DJI"},
    {"name": "标普500",   "symbol": "^GSPC"},
    {"name": "纳斯达克",  "symbol": "^IXIC"},
]

# 美股七姐妹
MAGNIFICENT_SEVEN = [
    {"name": "苹果",   "symbol": "AAPL"},
    {"name": "微软",   "symbol": "MSFT"},
    {"name": "谷歌",   "symbol": "GOOGL"},
    {"name": "亚马逊", "symbol": "AMZN"},
    {"name": "英伟达", "symbol": "NVDA"},
    {"name": "Meta",   "symbol": "META"},
    {"name": "特斯拉", "symbol": "TSLA"},
]

# 半导体
SEMICONDUCTORS = [
    {"name": "闪迪(WD)", "symbol": "WDC"},
    {"name": "美光",      "symbol": "MU"},
    {"name": "费城半导体", "symbol": "^SOX"},
]

# 商品期货
COMMODITIES = [
    {"name": "黄金", "symbol": "GC=F"},
    {"name": "白银", "symbol": "SI=F"},
    {"name": "原油", "symbol": "CL=F"},
]

# 市场指标
MARKET_INDICATORS = [
    {"name": "VIX 恐慌指数", "symbol": "^VIX"},
    {"name": "美元指数 DXY", "symbol": "DX-Y.NYB"},
    {"name": "10年美债收益率", "symbol": "^TNX"},
]

# ============================================================
# 加密货币配置（CoinGecko API）
# ============================================================
CRYPTO_IDS = ["bitcoin"]
CRYPTO_NAMES = {"bitcoin": "比特币 BTC"}
CRYPTO_VS_CURRENCY = "usd"

# CoinGecko API 基础 URL
COINGECKO_API = "https://api.coingecko.com/api/v3"

# ============================================================
# 邮件模板颜色配置（中国习惯：红涨绿跌）
# ============================================================
COLOR_UP = "#d32f2f"      # 涨 - 红色
COLOR_DOWN = "#2e7d32"    # 跌 - 绿色
COLOR_UNCHANGED = "#616161" # 平 - 灰色
COLOR_BG_HEADER = "#1a1a2e"
COLOR_BG_SECTION = "#f5f5f5"
COLOR_TEXT = "#333333"
COLOR_TEXT_LIGHT = "#757575"

# ============================================================
# 分析指标
# ============================================================
# 52周高低区间（用于判断当前价格在什么位置）
