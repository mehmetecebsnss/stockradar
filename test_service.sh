#!/bin/bash
# StockRadar Pro - Servis Test Scripti

echo "========================================"
echo "  StockRadar Pro - Servis Testi"
echo "========================================"

# Servis durumu
echo -e "\n1. Servis Durumu:"
sudo systemctl status stockradar --no-pager

# Log dosyası
echo -e "\n2. Son 20 Log Satırı:"
tail -n 20 ~/AcilPiyasaBotu/stockradar.log

# Process kontrolü
echo -e "\n3. Python Process:"
ps aux | grep bot.py | grep -v grep

# Port kontrolü
echo -e "\n4. Dashboard Port (5050):"
netstat -tlnp 2>/dev/null | grep 5050 || ss -tlnp 2>/dev/null | grep 5050 || echo "netstat/ss komutu bulunamadı"

# Veritabanı kontrolü
echo -e "\n5. Veritabanı:"
if [ -f ~/AcilPiyasaBotu/dashboard.db ]; then
    echo "✅ dashboard.db mevcut"
    echo "Boyut: $(du -h ~/AcilPiyasaBotu/dashboard.db | awk '{print $1}')"
else
    echo "❌ dashboard.db bulunamadı"
fi

# API testi
echo -e "\n6. Dashboard API Testi:"
curl -s http://localhost:5050/api/stats | python3 -m json.tool 2>/dev/null || echo "Dashboard yanıt vermiyor"

echo -e "\n========================================"
echo "  Test Tamamlandı"
echo "========================================"
