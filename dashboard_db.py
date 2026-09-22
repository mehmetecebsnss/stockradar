# -*- coding: utf-8 -*-
"""
Dashboard veritabani — SQLite
Sinyalleri, demo islemleri ve loglari saklar.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "dashboard.db")

# Demo baslangic sermayesi
STARTING_CAPITAL = 10000.0


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Sinyaller tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            mode        TEXT NOT NULL,
            ticker      TEXT NOT NULL,
            direction   TEXT NOT NULL,
            price       REAL NOT NULL,
            tp          REAL NOT NULL,
            sl          REAL NOT NULL,
            reason      TEXT
        )
    """)

    # Demo islemler tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            signal_id    INTEGER,
            ticker       TEXT NOT NULL,
            direction    TEXT NOT NULL,
            entry_price  REAL NOT NULL,
            tp_price     REAL NOT NULL,
            sl_price     REAL NOT NULL,
            current_price REAL,
            quantity     REAL NOT NULL,
            status       TEXT DEFAULT 'OPEN',
            pnl          REAL DEFAULT 0,
            pnl_pct      REAL DEFAULT 0,
            open_time    TEXT NOT NULL,
            close_time   TEXT,
            mode         TEXT NOT NULL
        )
    """)

    # Log tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level     TEXT NOT NULL,
            source    TEXT NOT NULL,
            message   TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ─── SİNYAL KAYDET ────────────────────────────────────────────────────────────

def save_signal(mode, ticker, direction, price, tp, sl, reason=""):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO signals (timestamp, mode, ticker, direction, price, tp, sl, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (now, mode, ticker, direction, price, tp, sl, reason))
    signal_id = c.lastrowid
    conn.commit()
    conn.close()

    # Demo islemi otomatik ac
    _open_trade(signal_id, mode, ticker, direction, price, tp, sl)
    return signal_id


def _open_trade(signal_id, mode, ticker, direction, entry, tp, sl):
    """Sinyal geldiginde otomatik demo islem ac."""
    conn = get_conn()
    c = conn.cursor()

    # Her islem icin 500$ ayir
    allocation = 500.0
    quantity   = round(allocation / entry, 6) if entry > 0 else 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO trades
            (signal_id, ticker, direction, entry_price, tp_price, sl_price,
             current_price, quantity, status, pnl, pnl_pct, open_time, mode)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', 0, 0, ?, ?)
    """, (signal_id, ticker, direction, entry, tp, sl, entry, quantity, now, mode))
    conn.commit()
    conn.close()


# ─── İŞLEM GÜNCELLE (fiyat takibi) ───────────────────────────────────────────

def update_trade_prices(ticker, current_price):
    """Acik islemlerin anlık PnL'ini guncelle."""
    conn = get_conn()
    c = conn.cursor()

    rows = c.execute("""
        SELECT id, direction, entry_price, tp_price, sl_price, quantity
        FROM trades
        WHERE ticker = ? AND status = 'OPEN'
    """, (ticker,)).fetchall()

    for row in rows:
        tid       = row["id"]
        direction = row["direction"]
        entry     = row["entry_price"]
        tp        = row["tp_price"]
        sl        = row["sl_price"]
        qty       = row["quantity"]

        if direction == "UZUN":
            pnl     = (current_price - entry) * qty
            pnl_pct = ((current_price - entry) / entry) * 100
        else:
            pnl     = (entry - current_price) * qty
            pnl_pct = ((entry - current_price) / entry) * 100

        # TP veya SL vurdu mu?
        status = "OPEN"
        close_time = None
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if direction == "UZUN":
            if current_price >= tp:
                status     = "TP"
                close_time = now
            elif current_price <= sl:
                status     = "SL"
                close_time = now
        else:
            if current_price <= tp:
                status     = "TP"
                close_time = now
            elif current_price >= sl:
                status     = "SL"
                close_time = now

        c.execute("""
            UPDATE trades
            SET current_price=?, pnl=?, pnl_pct=?, status=?, close_time=?
            WHERE id=?
        """, (round(current_price, 4), round(pnl, 4), round(pnl_pct, 2),
              status, close_time, tid))

    conn.commit()
    conn.close()


# ─── İSTATİSTİKLER ────────────────────────────────────────────────────────────

def get_stats():
    conn = get_conn()
    c = conn.cursor()

    total_signals = c.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    total_trades  = c.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    open_trades   = c.execute("SELECT COUNT(*) FROM trades WHERE status='OPEN'").fetchone()[0]
    tp_count      = c.execute("SELECT COUNT(*) FROM trades WHERE status='TP'").fetchone()[0]
    sl_count      = c.execute("SELECT COUNT(*) FROM trades WHERE status='SL'").fetchone()[0]

    total_pnl_row = c.execute("SELECT COALESCE(SUM(pnl),0) FROM trades").fetchone()
    total_pnl     = round(total_pnl_row[0], 2)

    capital = round(STARTING_CAPITAL + total_pnl, 2)

    win_rate = round((tp_count / (tp_count + sl_count) * 100), 1) if (tp_count + sl_count) > 0 else 0

    conn.close()
    return {
        "capital":       capital,
        "starting":      STARTING_CAPITAL,
        "total_pnl":     total_pnl,
        "total_signals": total_signals,
        "total_trades":  total_trades,
        "open_trades":   open_trades,
        "tp_count":      tp_count,
        "sl_count":      sl_count,
        "win_rate":      win_rate,
    }


def get_signals(limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM signals ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_trades(limit=50):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_logs(limit=100):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_log(level, source, message):
    conn = get_conn()
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO logs (timestamp, level, source, message) VALUES (?, ?, ?, ?)",
        (now, level, source, message)
    )
    conn.commit()
    conn.close()


# Baslangicta tabloları olustur
init_db()
