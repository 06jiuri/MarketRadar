import os
import sys
import time
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import yfinance as yf
import requests
from jinja2 import Environment, FileSystemLoader

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, RECIPIENTS, EMAIL_SUBJECT_PREFIX,
    INDEXES, MAGNIFICENT_SEVEN, SEMICONDUCTORS, COMMODITIES, MARKET_INDICATORS,
    CRYPTO_IDS, CRYPTO_NAMES, CRYPTO_VS_CURRENCY, COINGECKO_API,
    COLOR_UP, COLOR_DOWN, COLOR_UNCHANGED, COLOR_BG_HEADER, COLOR_BG_SECTION,
    COLOR_TEXT, COLOR_TEXT_LIGHT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 数据获取
# ============================================================

def fetch_yfinance_batch(symbols):
    """批量拉取 yfinance 数据，返回 {symbol: info_dict}"""
    if not symbols:
        return {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        result = {}
        for sym in symbols:
            try:
                time.sleep(0.5)
                t = tickers.tickers.get(sym)
                if t is None:
                    t = yf.Ticker(sym)
                info = t.info
                hist = t.history(period="5d")
                prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
                current = info.get("regularMarketPrice") or info.get("currentPrice")

                # fallback from history
                if prev_close is None and len(hist) >= 2:
                    prev_close = hist["Close"].iloc[-2]
                if current is None and len(hist) >= 1:
                    current = hist["Close"].iloc[-1]

                high_52w = info.get("fiftyTwoWeekHigh")
                low_52w = info.get("fiftyTwoWeekLow")
                name = info.get("shortName") or sym

                result[sym] = {
                    "name": name,
                    "price": current,
                    "prev_close": prev_close,
                    "high_52w": high_52w,
                    "low_52w": low_52w,
                }
            except Exception as e:
                logger.warning("获取 %s 失败: %s", sym, e)
                result[sym] = {
                    "name": sym, "price": None, "prev_close": None,
                    "high_52w": None, "low_52w": None,
                }
        return result
    except Exception as e:
        logger.error("yfinance 批量请求失败: %s", e)
        return {}


def fetch_crypto_data():
    """从 CoinGecko 获取加密货币数据"""
    try:
        ids = ",".join(CRYPTO_IDS)
        url = f"{COINGECKO_API}/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": CRYPTO_VS_CURRENCY,
            "include_24hr_change": "true",
            "include_24hr_vol": "false",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        result = {}
        for cid in CRYPTO_IDS:
            cdata = data.get(cid, {})
            price = cdata.get(CRYPTO_VS_CURRENCY)
            change_24h = cdata.get(f"{CRYPTO_VS_CURRENCY}_24h_change")
            pct = change_24h
            prev = (price / (1 + pct / 100)) if (price is not None and pct is not None and 1 + pct / 100 > 0) else None
            result[cid] = {
                "name": CRYPTO_NAMES.get(cid, cid),
                "price": price,
                "prev_close": prev,
                "change_pct": pct,
                "high_52w": None,
                "low_52w": None,
            }
        return result
    except Exception as e:
        logger.error("CoinGecko API 请求失败: %s", e)
        return {}


# ============================================================
# 数据处理 & 分析
# ============================================================

def safe_change_pct(current, prev):
    if current is not None and prev is not None and prev != 0:
        return round((current - prev) / prev * 100, 2)
    return None


def safe_52w_position(price, low, high):
    if price is not None and low is not None and high is not None and high > low:
        pos = (price - low) / (high - low) * 100
        return round(min(max(pos, 0), 100), 1)
    return None


def fmt_price(val):
    if val is None:
        return "-"
    if abs(val) >= 1000:
        return f"{val:,.2f}"
    elif abs(val) >= 1:
        return f"{val:,.2f}"
    else:
        return f"{val:.4f}"


def fmt_change(pct):
    if pct is None:
        return "-"
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def build_item(display_name, raw):
    price = raw.get("price")
    prev_close = raw.get("prev_close")
    change_pct = raw.get("change_pct")
    if change_pct is None:
        change_pct = safe_change_pct(price, prev_close)
    pos_52w = safe_52w_position(price, raw.get("low_52w"), raw.get("high_52w"))
    return {
        "name": display_name,
        "price": price,
        "price_fmt": fmt_price(price),
        "change_pct": change_pct,
        "change_fmt": fmt_change(change_pct),
        "pos_52w": pos_52w,
    }


def process_category(category_list, raw_data):
    items = []
    for item in category_list:
        raw = raw_data.get(item["symbol"], {})
        items.append(build_item(item["name"], raw))
    return items


def process_crypto_category(crypto_list, raw_data):
    items = []
    for item in crypto_list:
        data = raw_data.get(item["cid"], {})
        items.append(build_item(item["name"], data))
    return items


def generate_summary(all_items):
    """根据三大指数涨跌生成一句话概述"""
    index_items = all_items.get("indexes", [])
    up_count = sum(1 for i in index_items if i.get("change_pct") is not None and i["change_pct"] > 0)
    down_count = sum(1 for i in index_items if i.get("change_pct") is not None and i["change_pct"] < 0)

    if up_count >= 2:
        trend = "全面上涨"
    elif down_count >= 2:
        trend = "普遍下跌"
    else:
        trend = "涨跌互现"

    # VIX 解读
    vix_val = None
    for item in all_items.get("indicators", []):
        if "VIX" in item.get("name", ""):
            vix_val = item.get("price")
            break

    vix_note = ""
    if vix_val is not None:
        if vix_val > 30:
            vix_note = f"，VIX 报 {vix_val:.0f}，市场处于恐慌状态"
        elif vix_val > 20:
            vix_note = f"，VIX 报 {vix_val:.0f}，市场情绪偏谨慎"
        else:
            vix_note = f"，VIX 报 {vix_val:.0f}，市场情绪稳定"

    return f"昨日美股三大指数{trend}{vix_note}。"


# ============================================================
# 邮件发送
# ============================================================

def render_html(all_data, date_str, summary):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("template.html")
    return template.render(
        title=f"{EMAIL_SUBJECT_PREFIX} - {date_str}",
        date_str=date_str,
        summary=summary,
        color_up=COLOR_UP,
        color_down=COLOR_DOWN,
        color_unchanged=COLOR_UNCHANGED,
        color_bg_header=COLOR_BG_HEADER,
        color_bg_section=COLOR_BG_SECTION,
        color_text=COLOR_TEXT,
        color_text_light=COLOR_TEXT_LIGHT,
        indexes=all_data["indexes"],
        mag7=all_data["mag7"],
        semiconductors=all_data["semiconductors"],
        commodities=all_data["commodities"],
        cryptos=all_data["cryptos"],
        indicators=all_data["indicators"],
    )


def send_email(html_content, date_str):
    if not SMTP_USER or not SMTP_PASS:
        logger.error("SMTP_USER 或 SMTP_PASS 未设置，无法发送邮件")
        return False
    if not RECIPIENTS:
        logger.error("收件人列表为空")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{EMAIL_SUBJECT_PREFIX} - {date_str}"
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(RECIPIENTS)
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())
        server.quit()
        logger.info("邮件发送成功，收件人: %s", RECIPIENTS)
        return True
    except Exception as e:
        logger.error("邮件发送失败: %s", e)
        return False


# ============================================================
# 主流程
# ============================================================

def main():
    now = datetime.now()
    today_str = now.strftime("%Y年%m月%d日")

    # 1. 收集所有需要拉取的美股 symbols
    all_symbols = []
    for cat in [INDEXES, MAGNIFICENT_SEVEN, SEMICONDUCTORS, COMMODITIES, MARKET_INDICATORS]:
        for item in cat:
            all_symbols.append(item["symbol"])

    logger.info("开始拉取美股数据，共 %d 个标的...", len(all_symbols))
    raw_equity = fetch_yfinance_batch(all_symbols)

    logger.info("开始拉取加密货币数据...")
    raw_crypto = fetch_crypto_data()

    # 2. 组装各分类数据
    all_data = {
        "indexes": process_category(INDEXES, raw_equity),
        "mag7": process_category(MAGNIFICENT_SEVEN, raw_equity),
        "semiconductors": process_category(SEMICONDUCTORS, raw_equity),
        "commodities": process_category(COMMODITIES, raw_equity),
        "indicators": process_category(MARKET_INDICATORS, raw_equity),
        "cryptos": process_crypto_category(
            [{"cid": cid, "name": CRYPTO_NAMES[cid]} for cid in CRYPTO_IDS],
            raw_crypto
        ),
    }

    # 3. 生成概述
    summary = generate_summary(all_data)
    logger.info("概述: %s", summary)

    # 4. 渲染 HTML
    html = render_html(all_data, today_str, summary)
    logger.info("HTML 渲染完成")

    # 5. 发送邮件
    success = send_email(html, today_str)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
