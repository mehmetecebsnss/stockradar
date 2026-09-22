# -*- coding: utf-8 -*-
"""
STOCKRADAR PRO — Ana Bot
- Telegram komutlarını dinler
- News Trader ve Alfa Trader modlarını arka planda çalıştırır
- 7/24 kesintisiz
"""

import logging
import asyncio
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config        import BOT_TOKEN, AUTHORIZED_USERS, TICKER_NAMES
from config        import NEWS_TP_PCT, NEWS_SL_PCT, ALFA_TP_PCT, ALFA_SL_PCT
from price_engine  import get_price, get_technicals
from signal_engine import emit_signal, format_signal
from news_trader   import news_trader_loop
from alfa_trader   import alfa_trader_loop
from dashboard     import start_dashboard, price_updater
import threading

logging.basicConfig(
    format  = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level   = logging.INFO,
    handlers= [
        logging.FileHandler("stockradar.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Tekrar önleme
_handled_updates: set = set()

TICKER_SEARCH_LOCAL = {
    "AAPL": "Apple AAPL stock",      "MSFT": "Microsoft MSFT stock",
    "GOOGL": "Google Alphabet stock", "AMZN": "Amazon AMZN stock",
    "TSLA": "Tesla TSLA stock",       "NVDA": "Nvidia NVDA stock",
    "META": "Meta META stock",        "QQQ":  "Nasdaq QQQ ETF",
    "SPY":  "S&P 500 SPY ETF",        "AMD":  "AMD stock",
    "INTC": "Intel stock",            "NFLX": "Netflix stock",
    "UBER": "Uber stock",
}

# ─── YARDIMCI ─────────────────────────────────────────────────────────────────

def is_authorized(user) -> bool:
    if not user or not user.username:
        return False
    return user.username.lower() in [u.lower() for u in AUTHORIZED_USERS]


def clear_queue():
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1",
            timeout=10
        ).json()
        if r["ok"] and r["result"]:
            last_id = r["result"][-1]["update_id"]
            requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_id+1}",
                timeout=10
            )
            print(f"  Kuyruk temizlendi.")
    except:
        pass


async def guard(update: Update) -> bool:
    uid = update.update_id
    if uid in _handled_updates:
        return False
    _handled_updates.add(uid)
    if len(_handled_updates) > 2000:
        _handled_updates.clear()

    user = update.effective_user
    if not is_authorized(user):
        msg = (
            "\u274c <b>Erişim izniniz yok.</b>\n\n"
            "İzin almak için <b>@gorkemk6</b> ile iletişime geçin."
        )
        if update.message:
            await update.message.reply_text(msg, parse_mode="HTML")
        elif update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(msg, parse_mode="HTML")
        return False
    return True


async def send_safe(fn, text: str):
    MAX = 4000
    while text:
        chunk = text[:MAX]
        if len(text) > MAX:
            cut = chunk.rfind("\n")
            if cut > 0:
                chunk = chunk[:cut]
        await fn(chunk, parse_mode="HTML")
        text = text[len(chunk):].lstrip("\n")


def fetch_stock_news(ticker: str) -> list:
    term = TICKER_SEARCH_LOCAL.get(ticker, f"{ticker} stock")
    q    = requests.utils.quote(term)
    url  = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    try:
        r    = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
        result = []
        for item in root.findall(".//item")[:12]:
            title  = item.find("title").text  if item.find("title")  is not None else ""
            source = item.find("source").text if item.find("source") is not None else ""
            if title:
                result.append({"title": title, "source": source})
        return result
    except:
        return []


# ─── KOMUTLAR ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return

    user = update.effective_user
    saat = datetime.now().hour
    sel  = "Günaydın" if 6 <= saat < 12 else ("İyi günler" if 12 <= saat < 18 else "İyi akşamlar")
    sep  = "\u2501" * 22

    msg = (
        f"\U0001f48e <b>StockRadar Pro</b>\n"
        f"{sep}\n\n"
        f"\U0001f44b {sel}, <b>{user.first_name}</b>!\n\n"
        f"\U0001f535 <b>News Trader</b>  — Haber bazlı sinyal\n"
        f"\U0001f7e3 <b>Alfa Trader</b>  — Teknik analiz sinyali\n\n"
        f"{sep}\n"
        f"  /hisse AAPL  \u2192  Hisse analizi + sinyal\n"
        f"  /fiyat AAPL  \u2192  Anlık fiyat\n"
        f"  /teknik AAPL \u2192  RSI / MACD / EMA\n"
        f"  /durum       \u2192  Bot durumu\n"
        f"  /yardim      \u2192  Tüm komutlar\n"
        f"{sep}\n"
        f"<i>\u26a0\ufe0f Yatırım tavsiyesi değildir.</i>"
    )

    keyboard = [[
        InlineKeyboardButton("\U0001f50e  Hisse Analizi", callback_data="hisse_sor"),
        InlineKeyboardButton("\u26a1  Fiyat Sorgula",    callback_data="fiyat_sor"),
    ]]

    await update.message.reply_text(msg, parse_mode="HTML",
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def fiyat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args:
        await update.message.reply_text(
            "\u2139\ufe0f Kullanım: <code>/fiyat AAPL</code>", parse_mode="HTML")
        return

    ticker = context.args[0].upper()
    name   = TICKER_NAMES.get(ticker, ticker)
    price  = get_price(ticker)
    sep    = "\u2501" * 22

    if price > 0:
        msg = (
            f"\U0001f4b0 <b>{ticker}</b>  ({name})\n"
            f"{sep}\n"
            f"Güncel Fiyat:  <code>${price:.4f}</code>\n"
            f"\u23f0  {datetime.now().strftime('%H:%M:%S')}"
        )
    else:
        msg = f"\u274c <b>{ticker}</b> için fiyat alınamadı."
    await update.message.reply_text(msg, parse_mode="HTML")


async def teknik_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args:
        await update.message.reply_text(
            "\u2139\ufe0f Kullanım: <code>/teknik AAPL</code>", parse_mode="HTML")
        return

    ticker  = context.args[0].upper()
    name    = TICKER_NAMES.get(ticker, ticker)
    bekleme = await update.message.reply_text(
        f"\U0001f504 <b>{ticker}</b> teknik analiz hesaplanıyor...", parse_mode="HTML")

    t   = get_technicals(ticker)
    sep = "\u2501" * 22
    await bekleme.delete()

    if not t.get("bars_ok"):
        await update.message.reply_text(
            f"\u274c <b>{ticker}</b> için veri alınamadı.", parse_mode="HTML")
        return

    # RSI yorumu
    rsi = t["rsi"]
    if rsi < 35:
        rsi_yorum = "Aşırı Satım \U0001f7e2"
    elif rsi > 65:
        rsi_yorum = "Aşırı Alım \U0001f534"
    else:
        rsi_yorum = "Nötr \U0001f7e1"

    # MACD yorumu
    hist = t["macd_hist"]
    if hist > 0:
        macd_yorum = "Yukarı momentum \U0001f4c8"
    elif hist < 0:
        macd_yorum = "Aşağı momentum \U0001f4c9"
    else:
        macd_yorum = "Nötr"

    # EMA yorumu
    price = t["price"]
    ema20 = t["ema20"]
    ema50 = t["ema50"]
    if price > ema20 > ema50:
        ema_yorum = "Yükseliş trendi \U0001f7e2"
    elif price < ema20 < ema50:
        ema_yorum = "Düşüş trendi \U0001f534"
    else:
        ema_yorum = "Karışık \U0001f7e1"

    msg = (
        f"\U0001f4ca <b>Teknik Analiz — {ticker}</b>  ({name})\n"
        f"{sep}\n"
        f"\U0001f4b0 Fiyat:     <code>{price:.4f}</code>\n\n"
        f"RSI (14):  <code>{rsi:.1f}</code>  — {rsi_yorum}\n"
        f"MACD:      <code>{t['macd']:.4f}</code>  — {macd_yorum}\n"
        f"MACD Sig:  <code>{t['macd_sig']:.4f}</code>\n"
        f"MACD Hist: <code>{hist:.4f}</code>\n\n"
        f"EMA 20:    <code>{ema20:.4f}</code>\n"
        f"EMA 50:    <code>{ema50:.4f}</code>\n"
        f"Trend:     {ema_yorum}\n"
        f"{sep}\n"
        f"<i>\u23f0 {datetime.now().strftime('%H:%M:%S')}</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def hisse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    if not context.args:
        await update.message.reply_text(
            "\u2139\ufe0f Kullanım: <code>/hisse AAPL</code>", parse_mode="HTML")
        return

    ticker  = context.args[0].upper()
    name    = TICKER_NAMES.get(ticker, ticker)
    bekleme = await update.message.reply_text(
        f"\U0001f504 <b>{ticker}</b> analiz ediliyor...", parse_mode="HTML")

    # Paralel veri al
    news  = fetch_stock_news(ticker)
    price = get_price(ticker)
    t     = get_technicals(ticker)
    await bekleme.delete()

    if price <= 0:
        await update.message.reply_text(
            f"\u274c <b>{ticker}</b> için veri alınamadı.", parse_mode="HTML")
        return

    # Haber sentiment
    pos_kw = ["surge","soar","rally","gain","beat","strong","growth","record","upgrade","bullish","jump"]
    neg_kw = ["fall","drop","plunge","miss","weak","loss","downgrade","crash","concern","bearish"]
    pos_c = neg_c = 0
    for n in news:
        tl = n["title"].lower()
        if any(w in tl for w in pos_kw):
            pos_c += 1
        elif any(w in tl for w in neg_kw):
            neg_c += 1

    # Teknik sinyal
    direction = None
    if t.get("bars_ok"):
        rsi  = t["rsi"]
        hist = t["macd_hist"]
        p    = t["price"]
        e20  = t["ema20"]
        if rsi < 35 and hist > 0 and p > e20:
            direction = "UZUN"
        elif rsi > 65 and hist < 0 and p < e20:
            direction = "KISA"

    # Haber sinyali (override olabilir)
    if pos_c > neg_c and pos_c >= 2:
        news_direction = "UZUN"
    elif neg_c > pos_c and neg_c >= 2:
        news_direction = "KISA"
    else:
        news_direction = None

    final_direction = direction or news_direction

    sep = "\u2501" * 22

    if final_direction:
        tp_pct = NEWS_TP_PCT
        sl_pct = NEWS_SL_PCT
        if final_direction == "UZUN":
            tp = round(price * (1 + tp_pct), 4)
            sl = round(price * (1 - sl_pct), 4)
        else:
            tp = round(price * (1 - tp_pct), 4)
            sl = round(price * (1 + sl_pct), 4)

        source_tag = "\U0001f535 Haber+Teknik" if (direction and news_direction) else (
                     "\U0001f7e3 Teknik" if direction else "\U0001f535 Haber")

        msg = (
            f"{source_tag}\n"
            f"{sep}\n"
            f"\U0001fab6 <b>{ticker}</b>  ({name})\n"
            f"\U0001f680 <b>Yön: {final_direction}</b>\n"
            f"Giriş:         <code>{price:.4f}</code>\n"
            f"Kar Al:        <code>{tp:.4f}</code>\n"
            f"Zarar Durdur:  <code>{sl:.4f}</code>\n"
            f"{sep}\n"
            f"\U0001f4f0 Haber: {pos_c}\u2b06\ufe0f  {neg_c}\u2b07\ufe0f"
        )
        if t.get("bars_ok"):
            msg += f"\n\U0001f4ca RSI: {t['rsi']:.1f}  |  EMA20: {t['ema20']:.2f}"
    else:
        msg = (
            f"\U0001f7e1 <b>{ticker}</b>  — Net sinyal yok\n"
            f"{sep}\n"
            f"\U0001f4b0 Fiyat: <code>{price:.4f}</code>\n"
            f"\U0001f4f0 Haber: {pos_c}\u2b06\ufe0f  {neg_c}\u2b07\ufe0f\n"
        )
        if t.get("bars_ok"):
            msg += f"\U0001f4ca RSI: {t['rsi']:.1f}  |  EMA20: {t['ema20']:.2f}"

    await send_safe(update.message.reply_text, msg)


async def durum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    sep = "\u2501" * 22
    msg = (
        f"\U0001f916 <b>Bot Durumu</b>\n"
        f"{sep}\n\n"
        f"\U0001f535 News Trader:  \u2705 Aktif\n"
        f"\U0001f7e3 Alfa Trader:  \u2705 Aktif\n\n"
        f"\u23f0 Sunucu saati: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        f"{sep}\n"
        f"<i>Sinyaller otomatik olarak gruba iletilmektedir.</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def yardim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard(update):
        return
    sep = "\u2501" * 22
    msg = (
        f"\u2753 <b>Yardım</b>\n"
        f"{sep}\n\n"
        f"/start        \u2192  Ana ekran\n"
        f"/hisse AAPL   \u2192  Hisse analizi + sinyal\n"
        f"/fiyat AAPL   \u2192  Anlık fiyat\n"
        f"/teknik AAPL  \u2192  RSI / MACD / EMA\n"
        f"/durum        \u2192  Bot durumu\n"
        f"/yardim       \u2192  Bu menü\n\n"
        f"{sep}\n"
        f"\U0001f535 News Trader  — haber bazlı sinyal (15 dk)\n"
        f"\U0001f7e3 Alfa Trader  — teknik analiz sinyali (5 dk)\n\n"
        f"<i>\u26a0\ufe0f Yatırım tavsiyesi değildir.</i>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_authorized(query.from_user):
        await query.message.reply_text(
            "\u274c Erişim izniniz yok. <b>@gorkemk6</b> ile iletişime geçin.",
            parse_mode="HTML")
        return
    if query.data == "hisse_sor":
        await query.message.reply_text(
            "\U0001f50e Analiz etmek istediğin hisseyi yaz:\n<code>/hisse AAPL</code>",
            parse_mode="HTML")
    elif query.data == "fiyat_sor":
        await query.message.reply_text(
            "\u26a1 Fiyatını görmek istediğin hisseyi yaz:\n<code>/fiyat AAPL</code>",
            parse_mode="HTML")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def build_app():
    """Telegram Application nesnesini oluşturur."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",   start))
    application.add_handler(CommandHandler("fiyat",   fiyat_command))
    application.add_handler(CommandHandler("teknik",  teknik_command))
    application.add_handler(CommandHandler("hisse",   hisse_command))
    application.add_handler(CommandHandler("durum",   durum_command))
    application.add_handler(CommandHandler("yardim",  yardim_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    return application


def run_traders():
    """News Trader + Alfa Trader'ı ayrı bir thread'de çalıştırır."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run():
        await asyncio.gather(
            news_trader_loop(),
            alfa_trader_loop(),
        )

    loop.run_until_complete(_run())


def main():
    print("\n" + "=" * 55)
    print("  STOCKRADAR PRO — BAŞLIYOR")
    print("=" * 55)
    print(f"  Bot    : @stockradarofficialbot")
    print(f"  Yetkili: {', '.join(['@' + u for u in AUTHORIZED_USERS])}")
    print("=" * 55)

    # 1. Kuyruk temizle
    clear_queue()

    # 2. Dashboard (arka plan thread)
    start_dashboard(port=5050)

    # 3. Fiyat güncelleme (arka plan thread)
    pt = threading.Thread(target=price_updater, daemon=True)
    pt.start()

    # 4. News + Alfa Trader (arka plan thread)
    trader_thread = threading.Thread(target=run_traders, daemon=True)
    trader_thread.start()

    print("  [BOT]          Dinleniyor...")
    print("  [NEWS TRADER]  Başlatılıyor...")
    print("  [ALFA TRADER]  Başlatılıyor...")
    print("  [DASHBOARD]    http://localhost:5050\n")

    # 5. Telegram bot ana thread'de çalışır (run_polling kendi loop'unu yönetir)
    app = build_app()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
