# 📊 StockRadar Pro

**AI-Powered Trading Signal Bot** — Haber analizi ve teknik indikatörlerle otomatik trading sinyalleri üreten Telegram bot sistemi.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Özellikler

### 🔵 News Trader Modu
- Google News RSS'den gerçek zamanlı haber taraması
- Gemini AI ile haber sentiment analizi (opsiyonel)
- Keyword tabanlı otomatik sinyal üretimi
- Her 15 dakikada bir güncelleme

### 🟣 Alfa Trader Modu
- RSI, MACD, EMA teknik indikatör analizi
- 15 hisse için sürekli tarama
- Her 5 dakikada bir sinyal kontrolü
- ATR bazlı stop loss hesaplama

### 📱 Telegram Bot
- Otomatik sinyal gönderimi
- Yetki kontrolü
- Manuel komutlar (/hisse, /fiyat, /sinyal)
- 7/24 kesintisiz çalışma

### 🌐 Web Dashboard
- Gerçek zamanlı işlem takibi
- Kar/zarar raporlama
- Log görüntüleme
- Profil ve ayarlar yönetimi

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.8+
- Telegram Bot Token ([BotFather](https://t.me/BotFather))
- Twelve Data API Key ([Ücretsiz](https://twelvedata.com/pricing))

### 1. Kurulum (Windows/Mac/Linux)

```bash
git clone https://github.com/YOUR_USERNAME/AcilPiyasaBotu.git
cd AcilPiyasaBotu
pip install -r requirements.txt
```

### 2. Konfigürasyon

```bash
cp config.example.py config.py
nano config.py  # Kendi bilgilerinizi girin
```

**config.py'de düzenlenecekler:**
```python
BOT_TOKEN = "123456:ABC-DEF..."        # Telegram bot token
GROUP_ID  = "-1001234567890"           # Telegram grup ID
TWELVE_DATA_KEY = "your_api_key"       # Twelve Data API key
AUTHORIZED_USERS = ["your_username"]   # Yetkili kullanıcılar
```

### 3. Çalıştırma

```bash
python bot.py
```

Dashboard: http://localhost:5050

## 🔧 Raspberry Pi Kurulumu

### Otomatik Kurulum

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/AcilPiyasaBotu.git
cd AcilPiyasaBotu
chmod +x install_raspberry.sh
./install_raspberry.sh
```

### Manuel Kurulum

```bash
# 1. Bağımlılıkları kur
sudo apt update && sudo apt install -y python3 python3-pip git

# 2. Projeyi indir
cd ~ && git clone https://github.com/YOUR_USERNAME/AcilPiyasaBotu.git
cd AcilPiyasaBotu

# 3. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Config oluştur
cp config.example.py config.py
nano config.py  # Ayarları düzenle

# 5. Systemd service
sudo cp stockradar.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stockradar
sudo systemctl start stockradar
```

### Servis Komutları

```bash
sudo systemctl start stockradar      # Başlat
sudo systemctl stop stockradar       # Durdur
sudo systemctl restart stockradar    # Yeniden başlat
sudo systemctl status stockradar     # Durum kontrol
tail -f ~/AcilPiyasaBotu/stockradar.log  # Log takibi
```

## 📂 Proje Yapısı

```
AcilPiyasaBotu/
├── bot.py                  # Ana bot + scheduler
├── config.py               # Konfigürasyon (GİZLİ)
├── config.example.py       # Konfigürasyon şablonu
├── news_trader.py          # Haber bazlı sinyal motoru
├── alfa_trader.py          # Teknik analiz motoru
├── signal_engine.py        # Sinyal formatı + Telegram gönderimi
├── price_engine.py         # Fiyat + OHLCV verisi + RSI/MACD
├── dashboard.py            # Web panel (Flask)
├── dashboard_db.py         # SQLite veritabanı
├── requirements.txt        # Python bağımlılıkları
├── stockradar.service      # Systemd service
└── install_raspberry.sh    # Otomatik kurulum scripti
```

## 🎯 Kullanım

### Telegram Komutları

```
/start          Karşılama mesajı ve menü
/hisse AAPL     Apple için özel haber analizi
/fiyat NVDA     Nvidia anlık fiyat
/sinyal         Güncel trading sinyali
/yardim         Yardım menüsü
```

### Web Dashboard

- **Ana Sayfa:** Sermaye, PnL, açık işlemler
- **İşlemler:** Tüm işlem geçmişi ve canlı fiyatlar
- **Sinyaller:** Geçmiş sinyal listesi
- **Loglar:** Sistem log'ları
- **Profil:** Kullanıcı bilgileri
- **Ayarlar:** Trading parametreleri, API key'ler

## 🔐 Güvenlik

- `config.py` dosyası `.gitignore`'da — GitHub'a atılmaz
- API key'ler environment variable olarak da kullanılabilir
- Telegram yetki kontrolü aktif
- Dashboard local network'te erişilebilir (port forwarding ile internete açılabilir)

## 📊 Sinyal Formatı

```
🪬NVDA 🟢LONG
📊 Giriş: 219.00$
🚀 Hedef 1: 230.00$
🚀 Hedef 2: 241.00$
🚀 Hedef 3: 252.00$
🚨 Stop Loss: 210.24$
📝 Nvidia AI chip stock soars on earnings beat
```

## 🛠️ Geliştirme

### Test Modu

```bash
# Sadece dashboard
python dashboard.py

# Tek sinyal testi
python -c "from signal_engine import emit_signal; emit_signal('AAPL', 'UZUN', 150, 0.10, 0.04, 'NEWS', 'Test')"
```

### Yeni Özellik Ekleme

1. Yeni modül oluştur (örn: `my_trader.py`)
2. `bot.py`'de import et
3. `main()` fonksiyonunda scheduler'a ekle

## 📝 TODO

- [ ] Binance entegrasyonu (gerçek işlem)
- [ ] Discord bot desteği
- [ ] Web3 wallet entegrasyonu
- [ ] Backtesting modülü
- [ ] Risk yönetimi (max drawdown, position sizing)
- [ ] Multi-language support

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit atın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## ⚠️ Sorumluluk Reddi

Bu bot sadece **eğitim ve araştırma amaçlıdır**. Yatırım tavsiyesi değildir. Gerçek paralarla kullanmadan önce demo hesaplarda test edin. Mali kayıplardan sorumlu değiliz.

## 📞 İletişim

- GitHub Issues: [Sorun bildirin](https://github.com/YOUR_USERNAME/AcilPiyasaBotu/issues)
- Telegram: @gorkemk6

---

⭐ Beğendiyseniz yıldız vermeyi unutmayın!
