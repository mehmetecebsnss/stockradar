# -*- coding: utf-8 -*-
"""
ALFA TRADER MODU
Her ALFA_INTERVAL_SEC saniyede bir WATCHLIST'teki hisseleri tarar.
RSI + MACD + EMA kesişimlerine göre sinyal üretir.
"""

import asyncio
import logging
from price_engine  import get_technicals
from signal_engine import emit_signal
from config        import (
    WATCHLIST, ALFA_INTERVAL_SEC,
    ALFA_TP_PCT, ALFA_SL_PCT,
    ALFA_RSI_OVERSOLD, ALFA_RSI_OVERBOUGHT,
)

logger = logging.getLogger(__name__)


def analyze_ticker(ticker: str):
    """
    Tek bir hisse için teknik analiz yapar.
    Sinyal varsa dict döner, yoksa None.

    Sinyal koşulları:
    UZUN  → RSI < oversold VE MACD hist > 0 (yukarı kesişim) VE fiyat > EMA20
    KISA  → RSI > overbought VE MACD hist < 0 (aşağı kesişim) VE fiyat < EMA20
    """
    t = get_technicals(ticker)

    if not t.get("bars_ok"):
        return None

    rsi   = t["rsi"]
    hist  = t["macd_hist"]
    price = t["price"]
    ema20 = t["ema20"]

    signal    = None
    direction = None
    reasons   = []

    # UZUN sinyali
    if rsi < ALFA_RSI_OVERSOLD and hist > 0 and price > ema20:
        direction = "UZUN"
        reasons   = [
            f"RSI {rsi:.1f} (aşırı satım)",
            f"MACD yukarı kesişim",
            f"Fiyat EMA20 üstünde",
        ]

    # KISA sinyali
    elif rsi > ALFA_RSI_OVERBOUGHT and hist < 0 and price < ema20:
        direction = "KISA"
        reasons   = [
            f"RSI {rsi:.1f} (aşırı alım)",
            f"MACD aşağı kesişim",
            f"Fiyat EMA20 altında",
        ]

    if direction:
        return {
            "ticker":    ticker,
            "direction": direction,
            "price":     price,
            "reason":    " · ".join(reasons),
            "rsi":       rsi,
        }

    return None


async def alfa_trader_loop():
    """7/24 çalışan ana döngü."""
    logger.info("ALFA TRADER başladı.")
    print("  [ALFA TRADER] Aktif — her %d saniyede tarama yapılıyor." % ALFA_INTERVAL_SEC)

    while True:
        try:
            signals_found = 0
            for ticker in WATCHLIST:
                result = analyze_ticker(ticker)
                if result:
                    ok = emit_signal(
                        ticker    = result["ticker"],
                        direction = result["direction"],
                        price     = result["price"],
                        tp_pct    = ALFA_TP_PCT,
                        sl_pct    = ALFA_SL_PCT,
                        mode      = "ALFA",
                        reason    = result["reason"],
                    )
                    if ok:
                        signals_found += 1

                # Rate limit: 8 istek/dakika (Twelve Data free)
                await asyncio.sleep(8)

            logger.info(f"ALFA TRADER tarama tamamlandı. {signals_found} sinyal gönderildi.")

        except Exception as e:
            logger.error(f"ALFA TRADER hata: {e}")

        await asyncio.sleep(ALFA_INTERVAL_SEC)
