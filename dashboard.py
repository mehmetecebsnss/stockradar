# -*- coding: utf-8 -*-
"""
StockRadar Pro — Web Dashboard
Flask ile çalışır. Herhangi bir cihazdan erişilebilir.
Çalıştırma: python dashboard.py
Port: 5050
"""

import threading
import time
from flask import Flask, jsonify, render_template_string
from dashboard_db import get_stats, get_signals, get_trades, get_logs
from price_engine import get_price
from dashboard_db import update_trade_prices, get_conn

app = Flask(__name__)

# ─── FIYAT GÜNCELLEME THREAD ──────────────────────────────────────────────────

def price_updater():
    """Her 30 saniyede açık işlemlerin fiyatını günceller."""
    while True:
        try:
            conn = get_conn()
            rows = conn.execute(
                "SELECT DISTINCT ticker FROM trades WHERE status='OPEN'"
            ).fetchall()
            conn.close()

            for row in rows:
                ticker = row["ticker"]
                price  = get_price(ticker)
                if price > 0:
                    update_trade_prices(ticker, price)
        except Exception as e:
            pass
        time.sleep(30)


# ─── HTML PANEL ───────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StockRadar Pro — Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
  }

  /* NAV */
  nav {
    background: #111118;
    border-bottom: 1px solid #1e1e2e;
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .logo {
    font-size: 18px;
    font-weight: 700;
    color: #a78bfa;
    letter-spacing: 1px;
  }
  .nav-center {
    display: flex;
    gap: 20px;
    align-items: center;
  }
  .nav-link {
    color: #6b7280;
    text-decoration: none;
    font-size: 13px;
    padding: 6px 12px;
    border-radius: 6px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .nav-link:hover {
    color: #a78bfa;
    background: #1a1a26;
  }
  .nav-link.active {
    color: #a78bfa;
    background: #1e1e2e;
  }
  .nav-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #6b7280;
  }
  .dot-live {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* LAYOUT */
  .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

  /* STAT CARDS */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }
  .stat-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px;
  }
  .stat-label {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }
  .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #e0e0e0;
  }
  .stat-value.green { color: #22c55e; }
  .stat-value.red   { color: #ef4444; }
  .stat-value.purple{ color: #a78bfa; }

  /* TABS */
  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 16px;
    border-bottom: 1px solid #1e1e2e;
    padding-bottom: 0;
  }
  .tab {
    padding: 8px 18px;
    cursor: pointer;
    border-radius: 6px 6px 0 0;
    font-size: 13px;
    color: #6b7280;
    border: 1px solid transparent;
    border-bottom: none;
    transition: all 0.2s;
  }
  .tab:hover { color: #a78bfa; }
  .tab.active {
    background: #111118;
    border-color: #1e1e2e;
    color: #a78bfa;
    font-weight: 600;
  }

  /* PANEL */
  .panel {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    overflow: hidden;
  }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* TABLE */
  table {
    width: 100%;
    border-collapse: collapse;
  }
  thead th {
    background: #0d0d15;
    padding: 10px 14px;
    text-align: left;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6b7280;
    border-bottom: 1px solid #1e1e2e;
  }
  tbody tr {
    border-bottom: 1px solid #1a1a26;
    transition: background 0.15s;
  }
  tbody tr:hover { background: #13131e; }
  tbody td {
    padding: 10px 14px;
    font-size: 13px;
  }
  .mono { font-family: 'Consolas', monospace; }

  /* BADGES */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
  }
  .badge-news   { background: #1d4ed820; color: #60a5fa; border: 1px solid #1d4ed8; }
  .badge-alfa   { background: #6d28d920; color: #a78bfa; border: 1px solid #6d28d9; }
  .badge-long   { background: #16653420; color: #22c55e; border: 1px solid #166534; }
  .badge-short  { background: #7f1d1d20; color: #ef4444; border: 1px solid #7f1d1d; }
  .badge-open   { background: #78350f20; color: #fbbf24; border: 1px solid #78350f; }
  .badge-tp     { background: #16653420; color: #22c55e; border: 1px solid #166534; }
  .badge-sl     { background: #7f1d1d20; color: #ef4444; border: 1px solid #7f1d1d; }

  /* LOG */
  .log-container {
    max-height: 420px;
    overflow-y: auto;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    padding: 12px;
  }
  .log-line { padding: 3px 0; border-bottom: 1px solid #13131e; }
  .log-time { color: #6b7280; margin-right: 8px; }
  .log-INFO    { color: #60a5fa; margin-right: 6px; }
  .log-WARNING { color: #fbbf24; margin-right: 6px; }
  .log-ERROR   { color: #ef4444; margin-right: 6px; }
  .log-source  { color: #a78bfa; margin-right: 8px; }
  .log-msg     { color: #d1d5db; }

  /* PnL renkleri */
  .pnl-pos { color: #22c55e; font-weight: 600; }
  .pnl-neg { color: #ef4444; font-weight: 600; }
  .pnl-neu { color: #9ca3af; }

  /* Refresh bar */
  .refresh-bar {
    text-align: right;
    padding: 8px 14px;
    font-size: 11px;
    color: #6b7280;
    border-top: 1px solid #1e1e2e;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    tbody td:nth-child(n+5) { display: none; }
    thead th:nth-child(n+5) { display: none; }
  }
</style>
</head>
<body>

<nav>
  <div class="logo">⬡ StockRadar Pro</div>
  <div class="nav-center">
    <a href="#" class="nav-link active" onclick="switchPage('dashboard')">
      📊 Dashboard
    </a>
    <a href="#" class="nav-link" onclick="switchPage('trades')">
      💼 İşlemler
    </a>
    <a href="#" class="nav-link" onclick="switchPage('profile')">
      👤 Profil
    </a>
    <a href="#" class="nav-link" onclick="switchPage('settings')">
      ⚙️ Ayarlar
    </a>
  </div>
  <div class="nav-status">
    <div class="dot-live"></div>
    <span id="last-update">Yükleniyor...</span>
  </div>
</nav>

<div class="container">

  <!-- STAT CARDS -->
  <div class="stats-grid" id="stats-grid">
    <!-- JS ile doldurulacak -->
  </div>

  <!-- TABS -->
  <div class="tabs">
    <div class="tab active" onclick="switchTab('trades')">📊 İşlemler</div>
    <div class="tab" onclick="switchTab('signals')">⚡ Sinyaller</div>
    <div class="tab" onclick="switchTab('logs')">📋 Loglar</div>
  </div>

  <!-- PANELLER -->
  <div class="panel">

    <!-- İŞLEMLER -->
    <div id="tab-trades" class="tab-content active">
      <table>
        <thead>
          <tr>
            <th>#</th><th>Mod</th><th>Ticker</th><th>Yön</th>
            <th>Giriş</th><th>Güncel</th><th>TP</th><th>SL</th>
            <th>Miktar</th><th>PnL ($)</th><th>PnL (%)</th>
            <th>Durum</th><th>Açılış</th>
          </tr>
        </thead>
        <tbody id="trades-body"></tbody>
      </table>
    </div>

    <!-- SİNYALLER -->
    <div id="tab-signals" class="tab-content">
      <table>
        <thead>
          <tr>
            <th>#</th><th>Zaman</th><th>Mod</th><th>Ticker</th>
            <th>Yön</th><th>Giriş</th><th>TP</th><th>SL</th><th>Sebep</th>
          </tr>
        </thead>
        <tbody id="signals-body"></tbody>
      </table>
    </div>

    <!-- LOGLAR -->
    <div id="tab-logs" class="tab-content">
      <div class="log-container" id="logs-body"></div>
    </div>

    <div class="refresh-bar" id="refresh-info">Otomatik yenileme: 10s</div>
  </div>

</div>

<script>
let currentTab = 'trades';
let currentPage = 'dashboard';

function switchPage(page) {
  currentPage = page;
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.textContent.includes({
      'dashboard': 'Dashboard',
      'trades': 'İşlemler',
      'profile': 'Profil',
      'settings': 'Ayarlar'
    }[page])) {
      link.classList.add('active');
    }
  });
  
  // Sayfa içeriklerini göster/gizle
  if (page === 'dashboard') {
    document.getElementById('stats-grid').style.display = 'grid';
    document.querySelector('.tabs').style.display = 'flex';
    document.querySelector('.panel').style.display = 'block';
  } else if (page === 'trades') {
    document.getElementById('stats-grid').style.display = 'none';
    document.querySelector('.tabs').style.display = 'flex';
    document.querySelector('.panel').style.display = 'block';
    switchTab('trades');
  } else if (page === 'profile') {
    showProfilePage();
  } else if (page === 'settings') {
    showSettingsPage();
  }
}

function showProfilePage() {
  document.getElementById('stats-grid').style.display = 'none';
  document.querySelector('.tabs').style.display = 'none';
  document.querySelector('.panel').innerHTML = `
    <div style="padding: 30px;">
      <h2 style="color: #a78bfa; margin-bottom: 20px; font-size: 22px;">👤 Profil</h2>
      <div style="max-width: 600px;">
        <div style="background: #0d0d15; border: 1px solid #1e1e2e; border-radius: 8px; padding: 20px; margin-bottom: 16px;">
          <div style="margin-bottom: 12px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Kullanıcı Adı</label>
            <input type="text" value="@gorkemk6" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;" readonly>
          </div>
          <div style="margin-bottom: 12px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Telegram Bot</label>
            <input type="text" value="@stockradarofficialbot" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;" readonly>
          </div>
          <div style="margin-bottom: 12px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Başlangıç Sermayesi</label>
            <input type="text" value="$10,000.00" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;" readonly>
          </div>
        </div>
        <button onclick="switchPage('dashboard')" style="background: #a78bfa; border: none; color: #0a0a0f; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
          ← Dashboard'a Dön
        </button>
      </div>
    </div>
  `;
}

function showSettingsPage() {
  document.getElementById('stats-grid').style.display = 'none';
  document.querySelector('.tabs').style.display = 'none';
  document.querySelector('.panel').innerHTML = `
    <div style="padding: 30px;">
      <h2 style="color: #a78bfa; margin-bottom: 20px; font-size: 22px;">⚙️ Ayarlar</h2>
      <div style="max-width: 600px;">
        <div style="background: #0d0d15; border: 1px solid #1e1e2e; border-radius: 8px; padding: 20px; margin-bottom: 16px;">
          <h3 style="color: #e0e0e0; font-size: 16px; margin-bottom: 16px;">Trading Ayarları</h3>
          
          <div style="margin-bottom: 16px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">News Trader Aralığı (dakika)</label>
            <input type="number" value="15" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;">
          </div>
          
          <div style="margin-bottom: 16px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Alfa Trader Aralığı (dakika)</label>
            <input type="number" value="5" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;">
          </div>
          
          <div style="margin-bottom: 16px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Varsayılan İşlem Miktarı ($)</label>
            <input type="number" value="1000" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;">
          </div>
          
          <div style="margin-bottom: 16px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="checkbox" checked style="width: 16px; height: 16px;">
              <span style="color: #e0e0e0; font-size: 14px;">Otomatik sinyal gönderimi</span>
            </label>
          </div>
          
          <div style="margin-bottom: 16px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="checkbox" checked style="width: 16px; height: 16px;">
              <span style="color: #e0e0e0; font-size: 14px;">Otomatik işlem açma</span>
            </label>
          </div>
        </div>
        
        <div style="background: #0d0d15; border: 1px solid #1e1e2e; border-radius: 8px; padding: 20px; margin-bottom: 16px;">
          <h3 style="color: #e0e0e0; font-size: 16px; margin-bottom: 16px;">API Ayarları</h3>
          
          <div style="margin-bottom: 12px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Twelve Data API Key</label>
            <input type="password" value="98a35e7e983c4d95b930aa0706cb0597" style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;">
          </div>
          
          <div style="margin-bottom: 12px;">
            <label style="color: #6b7280; font-size: 12px; display: block; margin-bottom: 4px;">Gemini API Key</label>
            <input type="password" value="AIzaSy..." style="width: 100%; background: #111118; border: 1px solid #1e1e2e; border-radius: 6px; padding: 8px 12px; color: #e0e0e0; font-size: 14px;">
          </div>
        </div>
        
        <div style="display: flex; gap: 12px;">
          <button onclick="alert('Ayarlar kaydedildi!')" style="background: #a78bfa; border: none; color: #0a0a0f; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
            💾 Kaydet
          </button>
          <button onclick="switchPage('dashboard')" style="background: #1e1e2e; border: 1px solid #2e2e3e; color: #e0e0e0; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
            ← İptal
          </button>
        </div>
      </div>
    </div>
  `;
}

function switchTab(name) {
  currentTab = name;
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', ['trades','signals','logs'][i] === name);
  });
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
}

function pnlClass(v) {
  if (v > 0) return 'pnl-pos';
  if (v < 0) return 'pnl-neg';
  return 'pnl-neu';
}

function formatNum(v, dec=2) {
  return (v >= 0 ? '+' : '') + parseFloat(v).toFixed(dec);
}

async function refresh() {
  const now = new Date().toLocaleTimeString('tr-TR');

  // Stats
  const stats = await fetch('/api/stats').then(r => r.json());
  const pnlColor = stats.total_pnl >= 0 ? 'green' : 'red';
  document.getElementById('stats-grid').innerHTML = `
    <div class="stat-card">
      <div class="stat-label">Sermaye</div>
      <div class="stat-value purple">$${stats.capital.toFixed(2)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Toplam PnL</div>
      <div class="stat-value ${pnlColor}">${formatNum(stats.total_pnl)}$</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Toplam Sinyal</div>
      <div class="stat-value">${stats.total_signals}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Toplam İşlem</div>
      <div class="stat-value">${stats.total_trades}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Açık İşlem</div>
      <div class="stat-value">${stats.open_trades}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">TP / SL</div>
      <div class="stat-value"><span class="pnl-pos">${stats.tp_count}</span> / <span class="pnl-neg">${stats.sl_count}</span></div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Kazanma Oranı</div>
      <div class="stat-value ${stats.win_rate >= 50 ? 'green' : 'red'}">${stats.win_rate}%</div>
    </div>
  `;

  // Trades
  const trades = await fetch('/api/trades').then(r => r.json());
  document.getElementById('trades-body').innerHTML = trades.map(t => `
    <tr>
      <td class="mono" style="color:#6b7280">${t.id}</td>
      <td><span class="badge badge-${t.mode.toLowerCase()}">${t.mode}</span></td>
      <td><strong>${t.ticker}</strong></td>
      <td><span class="badge badge-${t.direction === 'UZUN' ? 'long' : 'short'}">${t.direction}</span></td>
      <td class="mono">${parseFloat(t.entry_price).toFixed(4)}</td>
      <td class="mono">${t.current_price ? parseFloat(t.current_price).toFixed(4) : '-'}</td>
      <td class="mono" style="color:#22c55e">${parseFloat(t.tp_price).toFixed(4)}</td>
      <td class="mono" style="color:#ef4444">${parseFloat(t.sl_price).toFixed(4)}</td>
      <td class="mono">${parseFloat(t.quantity).toFixed(4)}</td>
      <td class="mono ${pnlClass(t.pnl)}">${formatNum(t.pnl)}</td>
      <td class="mono ${pnlClass(t.pnl_pct)}">${formatNum(t.pnl_pct)}%</td>
      <td><span class="badge badge-${t.status.toLowerCase()}">${t.status}</span></td>
      <td style="color:#6b7280;font-size:11px">${t.open_time}</td>
    </tr>
  `).join('');

  // Signals
  const signals = await fetch('/api/signals').then(r => r.json());
  document.getElementById('signals-body').innerHTML = signals.map(s => `
    <tr>
      <td class="mono" style="color:#6b7280">${s.id}</td>
      <td style="color:#6b7280;font-size:11px">${s.timestamp}</td>
      <td><span class="badge badge-${s.mode.toLowerCase()}">${s.mode}</span></td>
      <td><strong>${s.ticker}</strong></td>
      <td><span class="badge badge-${s.direction === 'UZUN' ? 'long' : 'short'}">${s.direction}</span></td>
      <td class="mono">${parseFloat(s.price).toFixed(4)}</td>
      <td class="mono" style="color:#22c55e">${parseFloat(s.tp).toFixed(4)}</td>
      <td class="mono" style="color:#ef4444">${parseFloat(s.sl).toFixed(4)}</td>
      <td style="color:#9ca3af;font-size:12px">${s.reason || '-'}</td>
    </tr>
  `).join('');

  // Logs
  const logs = await fetch('/api/logs').then(r => r.json());
  document.getElementById('logs-body').innerHTML = logs.map(l => `
    <div class="log-line">
      <span class="log-time">${l.timestamp}</span>
      <span class="log-${l.level}">[${l.level}]</span>
      <span class="log-source">${l.source}</span>
      <span class="log-msg">${l.message}</span>
    </div>
  `).join('');

  document.getElementById('last-update').textContent = 'Son güncelleme: ' + now;
  document.getElementById('refresh-info').textContent = 'Son güncelleme: ' + now + ' | Otomatik yenileme: 10s';
}

// API endpoints
// ─── ROUTES ───────────────────────────────────────────────────────────────────
refresh();
setInterval(refresh, 10000); // 10 saniyede bir
</script>
</body>
</html>
"""


# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/signals")
def api_signals():
    return jsonify(get_signals(50))


@app.route("/api/trades")
def api_trades():
    return jsonify(get_trades(50))


@app.route("/api/logs")
def api_logs():
    return jsonify(get_logs(100))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def start_dashboard(host="0.0.0.0", port=5050):
    """Bot ile aynı anda çalıştırmak için thread olarak başlatılır."""
    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True
    )
    t.start()
    print(f"  [DASHBOARD]    http://localhost:{port}  |  Ağdaki IP ile her cihazdan erişilebilir")
    return t


if __name__ == "__main__":
    # Bağımsız çalıştırma (sadece dashboard test için)
    price_thread = threading.Thread(target=price_updater, daemon=True)
    price_thread.start()
    print(f"Panel: http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
