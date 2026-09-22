# -*- coding: utf-8 -*-
"""
StockRadar Pro — Konfigürasyon Şablonu
Bu dosyayı 'config.py' olarak kopyalayın ve kendi değerlerinizi girin.
"""

# ─── TELEGRAM ─────────────────────────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"              # @BotFather'dan alın
GROUP_ID  = "-100XXXXXXXXXX"                   # Telegram grup ID'si

# Yetkili kullanıcılar (Telegram username, @ olmadan)
AUTHORIZED_USERS = [
    "your_username",
]

# ─── API KEYS ─────────────────────────────────────────────────────────────────
TWELVE_DATA_KEY = "YOUR_TWELVE_DATA_KEY"       # https://twelvedata.com/pricing
GEMINI_KEY      = ""                           # https://aistudio.google.com/apikey (opsiyonel)

# ─── TRADING AYARLARI ─────────────────────────────────────────────────────────
NEWS_INTERVAL_SEC = 15 * 60   # News Trader aralığı (saniye) - varsayılan 15 dakika
ALFA_INTERVAL_SEC = 5 * 60    # Alfa Trader aralığı (saniye) - varsayılan 5 dakika

DEFAULT_TRADE_SIZE = 1000.0   # Varsayılan işlem büyüklüğü ($)
STARTING_CAPITAL   = 10000.0  # Başlangıç sermayesi ($)

# ─── İZLEME LİSTESİ ───────────────────────────────────────────────────────────
# Alfa Trader tarafından izlenecek hisseler
WATCHLIST = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
    'SPY', 'QQQ', 'DIA', 'ADBE', 'CRM'
]

# Hisse adları (görsel gösterim için)
TICKER_NAMES = {
    'AAPL':  'Apple',
    'MSFT':  'Microsoft',
    'GOOGL': 'Google',
    'AMZN':  'Amazon',
    'TSLA':  'Tesla',
    'NVDA':  'Nvidia',
    'META':  'Meta',
    'NFLX':  'Netflix',
    'AMD':   'AMD',
    'INTC':  'Intel',
    'SPY':   'S&P 500',
    'QQQ':   'Nasdaq 100',
    'DIA':   'Dow Jones',
    'ADBE':  'Adobe',
    'CRM':   'Salesforce',
}

# Haber aramaları için keyword mapping (opsiyonel)
TICKER_SEARCH = {
    'AAPL':  'Apple iPhone stock',
    'GOOGL': 'Google Alphabet stock',
    'AMZN':  'Amazon AWS stock',
    'TSLA':  'Tesla Elon Musk stock',
    'NVDA':  'Nvidia AI chip stock',
    'META':  'Meta Facebook stock',
}
