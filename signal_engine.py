# -*- coding: utf-8 -*-
"""
Sinyal motoru:
- Tekrar onleme (ayni sinyal 4 saat icinde tekrar gonderilmez)
- Premium sinyal formati (3 hedef seviyeli)
- Telegram'a gonderme
"""

import time
import hashlib
import requests
import logging
from datetime import datetime
from config import BOT_TOKEN, GROUP_ID, TICKER_NAMES

logger = logging.getLogger(__name__)

# Gonderilen sinyallerin hash tablosu
_sent_signals = {}
COOLDOWN_SEC  = 4 * 3600


def _signal_hash(ticker, direction, mode):
    key = f"{ticker}:{direction}:{mode}"
    return hashlib.md5(key.encode()).hexdigest()


def is_duplicate(ticker, direction, mode):
    h   = _signal_hash(ticker, direction, mode)
    now = time.time()
    expired = [k for k, v in _sent_signals.items() if now - v > COOLDOWN_SEC]
    for k in expired:
        del _sent_signals[k]
    return h in _sent_signals


def mark_sent(ticker, direction, mode):
    _sent_signals[_signal_hash(ticker, direction, mode)] = time.time()


# ─── PREMIUM SINYAL FORMATI ───────────────────────────────────────────────────

def format_signal(ticker, direction, price, tp_pct, sl_pct, mode, reason=""):
    """
    3 hedef seviyeli premium format (baslik yok):

    🪬NVDA 🟢LONG

    📊 Giris: 219.00$
    🚀 Hedef 1: 230.00$
    🚀 Hedef 2: 241.00$
    🚀 Hedef 3: 252.00$
    🚨 Stop Loss: 210.24$
    📝 Sebep...
    """

    if direction == "UZUN":
        dir_emoji = "\U0001f7e2"   # 🟢
        dir_text  = "LONG"
        h1 = round(price * (1 + tp_pct * 0.50), 2)
        h2 = round(price * (1 + tp_pct),         2)
        h3 = round(price * (1 + tp_pct * 1.50),  2)
        sl = round(price * (1 - sl_pct),          2)
    else:
        dir_emoji = "\U0001f534"   # 🔴
        dir_text  = "SHORT"
        h1 = round(price * (1 - tp_pct * 0.50), 2)
        h2 = round(price * (1 - tp_pct),         2)
        h3 = round(price * (1 - tp_pct * 1.50),  2)
        sl = round(price * (1 + sl_pct),          2)

    lines = [
        f"\U0001fab6{ticker} {dir_emoji}{dir_text}",
        f"\U0001f4ca Giri\u015f: {price}$",
        f"\U0001f680 Hedef 1: {h1}$",
        f"\U0001f680 Hedef 2: {h2}$",
        f"\U0001f680 Hedef 3: {h3}$",
        f"\U0001f6a8 Stop Loss: {sl}$",
    ]

    if reason:
        lines.append(f"\U0001f4dd {reason}")

    return "\n".join(lines)


# ─── TELEGRAM GONDERIM ────────────────────────────────────────────────────────

def send_to_group(text):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": GROUP_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        if r.ok:
            return True
        logger.error(f"Telegram hata: {r.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Telegram baglanti hatasi: {e}")
        return False


def emit_signal(ticker, direction, price, tp_pct, sl_pct, mode, reason=""):
    """
    Sinyal olustur, tekrar kontrolu yap, gruba gonder, DB'ye kaydet.
    """
    if is_duplicate(ticker, direction, mode):
        logger.info(f"Duplicate atlandı: {ticker} {direction} [{mode}]")
        return False

    if price <= 0:
        return False

    # TP/SL referans degerlerini hesapla (DB icin)
    if direction == "UZUN":
        tp_ref = round(price * (1 + tp_pct), 4)
        sl_ref = round(price * (1 - sl_pct), 4)
    else:
        tp_ref = round(price * (1 - tp_pct), 4)
        sl_ref = round(price * (1 + sl_pct), 4)

    text = format_signal(ticker, direction, price, tp_pct, sl_pct, mode, reason)
    ok   = send_to_group(text)

    if ok:
        mark_sent(ticker, direction, mode)
        logger.info(f"Sinyal gonderildi: {ticker} {direction} [{mode}]")
        try:
            from dashboard_db import save_signal, save_log
            save_signal(mode, ticker, direction, price, tp_ref, sl_ref, reason)
            save_log("INFO", mode, f"{ticker} {direction} — Giris: {price}")
        except Exception as e:
            logger.warning(f"DB kayit hatasi: {e}")

    return ok
