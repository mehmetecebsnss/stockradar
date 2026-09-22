# -*- coding: utf-8 -*-
"""
NEWS TRADER MODU
Her NEWS_INTERVAL_SEC saniyede bir haberleri çeker, analiz eder, sinyal üretir.
Gemini API key varsa AI analizi, yoksa keyword bazlı analiz kullanır.
"""

import asyncio
import logging
import requests
import json
import xml.etree.ElementTree as ET
from price_engine  import get_price
from signal_engine import emit_signal
from config        import (
    TWELVE_DATA_KEY, GEMINI_KEY,
    NEWS_INTERVAL_SEC, NEWS_MAX_ARTICLES,
    NEWS_TP_PCT, NEWS_SL_PCT,
)

logger = logging.getLogger(__name__)

# ─── HABER ÇEKME ──────────────────────────────────────────────────────────────

def fetch_news(max_news: int = NEWS_MAX_ARTICLES) -> list:
    url = "https://news.google.com/rss/search?q=nasdaq+OR+stock+market+OR+earnings&hl=en-US&gl=US&ceid=US:en"
    try:
        r    = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(r.content)
        result = []
        for item in root.findall(".//item")[:max_news]:
            title  = item.find("title").text  if item.find("title")  is not None else ""
            source = item.find("source").text if item.find("source") is not None else ""
            if title:
                result.append({"title": title, "source": source})
        return result
    except Exception as e:
        logger.error(f"Haber çekme hatası: {e}")
        return []


# ─── ANALİZ: KEYWORD BAZLI ────────────────────────────────────────────────────

KEYWORD_MAP = {
    "nvidia":    ("UZUN",  "NVDA",  "high"),
    "tesla":     ("UZUN",  "TSLA",  "high"),
    "apple":     ("NÖTR",  "AAPL",  "medium"),
    "microsoft": ("UZUN",  "MSFT",  "medium"),
    "amazon":    ("UZUN",  "AMZN",  "medium"),
    "meta":      ("UZUN",  "META",  "medium"),
    "google":    ("NÖTR",  "GOOGL", "medium"),
    "intel":     ("KISA",  "INTC",  "medium"),
    "amd":       ("UZUN",  "AMD",   "medium"),
    "netflix":   ("NÖTR",  "NFLX",  "medium"),
    "fed":       ("KISA",  "SPY",   "high"),
    "rate hike": ("KISA",  "SPY",   "high"),
    "rate cut":  ("UZUN",  "SPY",   "high"),
    "recession": ("KISA",  "QQQ",   "high"),
    "inflation": ("KISA",  "QQQ",   "high"),
    "earnings beat": ("UZUN",  "SPY", "high"),
    "earnings miss": ("KISA",  "SPY", "high"),
}

POS_WORDS = ["surge","soar","rally","gain","beat","strong","growth","record","upgrade","bullish","jump"]
NEG_WORDS = ["fall","drop","plunge","miss","weak","loss","downgrade","crash","concern","warning","bearish"]


def keyword_analyze(news_list: list) -> list:
    """
    Keyword bazlı analiz. Döner: list of {ticker, direction, reason}
    """
    signals = []
    seen    = set()

    for n in news_list:
        title_lower = n["title"].lower()

        # KEYWORD_MAP kontrolü
        for kw, (direction, ticker, impact) in KEYWORD_MAP.items():
            if kw in title_lower and ticker not in seen:
                if direction == "NÖTR":
                    # Pozitif/negatif kelime var mı?
                    has_pos = any(w in title_lower for w in POS_WORDS)
                    has_neg = any(w in title_lower for w in NEG_WORDS)
                    if has_pos and not has_neg:
                        direction = "UZUN"
                    elif has_neg and not has_pos:
                        direction = "KISA"
                    else:
                        continue   # net sinyal yok, atla

                if impact in ("high", "medium"):
                    signals.append({
                        "ticker":    ticker,
                        "direction": direction,
                        "reason":    f"{n['title'][:80]}",
                    })
                    seen.add(ticker)
                break

    return signals[:5]   # En fazla 5 sinyal


# ─── ANALİZ: GEMİNİ AI ────────────────────────────────────────────────────────

def gemini_analyze(news_list: list) -> list:
    """
    Gemini AI ile analiz. Key yoksa keyword_analyze'e düşer.
    """
    if not GEMINI_KEY:
        return keyword_analyze(news_list)

    news_text = "\n".join([f"{i+1}. {n['title']}" for i, n in enumerate(news_list)])

    prompt = (
        "You are a professional stock trader. Analyze these news headlines and "
        "find max 5 critical trading opportunities.\n\n"
        "NEWS:\n" + news_text + "\n\n"
        "Return ONLY valid JSON, no other text:\n"
        '{"signals":[{"ticker":"AAPL","direction":"LONG or SHORT",'
        '"reason":"one sentence why","confidence":"high or medium"}]}'
    )

    try:
        url  = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r    = requests.post(url, json=data, timeout=30)
        r.raise_for_status()

        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        parsed  = json.loads(text)
        results = []
        for s in parsed.get("signals", []):
            direction = "UZUN" if s.get("direction", "").upper() == "LONG" else "KISA"
            results.append({
                "ticker":    s.get("ticker", "").upper(),
                "direction": direction,
                "reason":    s.get("reason", ""),
            })
        return results

    except Exception as e:
        logger.warning(f"Gemini analiz hatası, keyword analiz kullanılıyor: {e}")
        return keyword_analyze(news_list)


# ─── NEWS TRADER ANA DÖNGÜSÜ ──────────────────────────────────────────────────

async def news_trader_loop():
    """7/24 çalışan ana döngü."""
    mode_str = "Gemini AI" if GEMINI_KEY else "Keyword"
    logger.info(f"NEWS TRADER başladı ({mode_str} modu).")
    print(f"  [NEWS TRADER] Aktif — her {NEWS_INTERVAL_SEC}s haberleri tarar ({mode_str}).")

    while True:
        try:
            news    = fetch_news()
            if not news:
                logger.warning("NEWS TRADER: Haber bulunamadı.")
                await asyncio.sleep(NEWS_INTERVAL_SEC)
                continue

            signals = gemini_analyze(news)

            sent = 0
            for sig in signals:
                ticker    = sig["ticker"]
                direction = sig["direction"]
                price     = get_price(ticker)

                ok = emit_signal(
                    ticker    = ticker,
                    direction = direction,
                    price     = price,
                    tp_pct    = NEWS_TP_PCT,
                    sl_pct    = NEWS_SL_PCT,
                    mode      = "NEWS",
                    reason    = sig.get("reason", ""),
                )
                if ok:
                    sent += 1

            logger.info(f"NEWS TRADER döngüsü tamamlandı. {sent} sinyal gönderildi.")

        except Exception as e:
            logger.error(f"NEWS TRADER hata: {e}")

        await asyncio.sleep(NEWS_INTERVAL_SEC)
