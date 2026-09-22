# -*- coding: utf-8 -*-
"""
Fiyat motoru: Twelve Data API üzerinden anlık fiyat ve OHLCV çeker.
RSI, MACD, EMA hesaplamalarını sıfır bağımlılıkla yapar.
"""

import requests
import statistics
from config import TWELVE_DATA_KEY


# ─── ANLK FİYAT ───────────────────────────────────────────────────────────────

def get_price(ticker: str) -> float:
    try:
        r = requests.get(
            f"https://api.twelvedata.com/price?symbol={ticker}&apikey={TWELVE_DATA_KEY}",
            timeout=6
        ).json()
        return float(r.get("price", 0))
    except:
        return 0.0


# ─── OHLCV VERİSİ ─────────────────────────────────────────────────────────────

def get_ohlcv(ticker: str, interval: str = "5min", bars: int = 60) -> list:
    """
    Twelve Data time_series endpoint.
    Döner: [{"open":..,"high":..,"low":..,"close":..,"volume":..}, ...]
    En yeni bar sonda.
    """
    try:
        r = requests.get(
            "https://api.twelvedata.com/time_series",
            params={
                "symbol":     ticker,
                "interval":   interval,
                "outputsize": bars,
                "apikey":     TWELVE_DATA_KEY,
            },
            timeout=10
        ).json()

        if "values" not in r:
            return []

        bars_data = []
        for v in reversed(r["values"]):   # eski → yeni sırasına koy
            bars_data.append({
                "open":   float(v["open"]),
                "high":   float(v["high"]),
                "low":    float(v["low"]),
                "close":  float(v["close"]),
                "volume": float(v.get("volume", 0)),
            })
        return bars_data
    except:
        return []


# ─── TEKNİK İNDİKATÖRLER ──────────────────────────────────────────────────────

def _closes(bars: list) -> list:
    return [b["close"] for b in bars]


def calc_rsi(bars: list, period: int = 14) -> float:
    """RSI hesapla. Son bar için değer döner."""
    closes = _closes(bars)
    if len(closes) < period + 1:
        return 50.0

    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = statistics.mean(gains[-period:])
    avg_loss = statistics.mean(losses[-period:])

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calc_ema(values: list, period: int) -> list:
    """EMA dizisi döner."""
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    ema = [statistics.mean(values[:period])]
    for v in values[period:]:
        ema.append(v * k + ema[-1] * (1 - k))
    return ema


def calc_macd(bars: list, fast=12, slow=26, signal=9):
    """
    Döner: (macd_line, signal_line, histogram) — hepsi float.
    """
    closes = _closes(bars)
    if len(closes) < slow + signal:
        return 0.0, 0.0, 0.0

    ema_fast = calc_ema(closes, fast)
    ema_slow = calc_ema(closes, slow)

    min_len = min(len(ema_fast), len(ema_slow))
    macd_line = [ema_fast[-min_len + i] - ema_slow[-min_len + i] for i in range(min_len)]

    if len(macd_line) < signal:
        return 0.0, 0.0, 0.0

    signal_line = calc_ema(macd_line, signal)
    if not signal_line:
        return 0.0, 0.0, 0.0

    m = macd_line[-1]
    s = signal_line[-1]
    h = round(m - s, 6)
    return round(m, 6), round(s, 6), h


def calc_ema_value(bars: list, period: int) -> float:
    """Son bar için EMA değeri."""
    closes = _closes(bars)
    ema = calc_ema(closes, period)
    return round(ema[-1], 4) if ema else 0.0


def get_technicals(ticker: str) -> dict:
    """
    Bir hisse için tüm teknik göstergeleri hesaplar.
    Döner: {rsi, macd, macd_signal, macd_hist, ema20, ema50, price, bars_ok}
    """
    bars = get_ohlcv(ticker, interval="5min", bars=60)

    if len(bars) < 30:
        return {"bars_ok": False}

    price      = bars[-1]["close"]
    rsi        = calc_rsi(bars, 14)
    macd, sig, hist = calc_macd(bars)
    ema20      = calc_ema_value(bars, 20)
    ema50      = calc_ema_value(bars, 50)

    return {
        "bars_ok":    True,
        "price":      round(price, 4),
        "rsi":        rsi,
        "macd":       macd,
        "macd_sig":   sig,
        "macd_hist":  hist,
        "ema20":      ema20,
        "ema50":      ema50,
    }
