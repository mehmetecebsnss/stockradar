# 🚀 NASDAQ Borsa Haber Analiz & Telegram Bot

Gerçek zamanlı borsa haberlerini analiz edip, trading sinyalleri üreten ve Telegram'a gönderen otomatik sistem.

## ✨ Özellikler

- 📰 **Gerçek Zamanlı Haber Akışı**: Google News RSS'den NASDAQ/borsa haberleri
- 🤖 **AI Analiz**: Gemini AI ile sentiment analizi ve kritik haber tespiti
- 📊 **Trading Sinyalleri**: AL/SAT/BEKLE sinyalleri + güven skorları
- 📱 **Telegram Entegrasyonu**: Otomatik bildirimler
- 💰 **Fiyat Bilgileri**: Twelve Data API ile anlık fiyatlar
- ⏰ **Otomatik Çalışma**: 30 dakikada bir güncelleme (opsiyonel)

## 🎯 Nasıl Çalışır?

```
1. Haber Akışı → 2. AI Analizi → 3. Sinyal Üretimi → 4. Telegram
```

### Adım 1: Haberler
- Google News RSS'den son 30 haber çekilir
- NASDAQ, stock market, stocks anahtar kelimeleri

### Adım 2: AI Analizi
- Gemini AI haberleri analiz eder
- Kritik haberleri seçer (Fed, kazançlar, anlaşmalar)
- İlgili hisse senetlerini bulur (AAPL, MSFT, TSLA vb.)
- Sentiment analizi (pozitif/negatif/nötr)

### Adım 3: Trading Sinyalleri
- Her hisse için sentiment skorları toplanır
- AL/SAT/BEKLE kararı verilir
- Güven seviyesi hesaplanır

### Adım 4: Telegram
- Analiz raporu ve sinyaller Telegram'a gönderilir
- HTML formatında güzel görünüm

## 📦 Kurulum

### 1. Gereksinimleri yükleyin

```bash
pip install requests
```

### 2. API Keylerini ayarlayın

`FULL_SYSTEM.py` dosyasında:

```python
GEMINI_API_KEY = "buraya_gemini_api_key"  # https://ai.google.dev/
TELEGRAM_BOT_TOKEN = "8907377963:AAET-SGNSRzNZEXRX-FnZAhkES-OS1F7HOo"
TWELVE_DATA_API_KEY = "98a35e7e983c4d95b930aa0706cb0597"
```

### 3. Telegram Bot'u Başlatın

1. Telegram'da botu açın: https://t.me/stockradarofficialbot
2. `/start` komutunu gönderin

### 4. Sistemi Çalıştırın

```bash
python FULL_SYSTEM.py
```

## 🛠️ Dosya Yapısı

```
📁 AcilPiyasaBotu/
├── 📄 FULL_SYSTEM.py          # Tam otomatik sistem
├── 📄 step1_haber_akisi.py    # Sadece haber çekme
├── 📄 step2_gemini_MOCK.py    # AI analiz (mock)
├── 📄 step3_telegram_bot.py   # Telegram entegrasyonu
├── 📄 nasdaq_data_test.py     # Fiyat verileri testi
├── 📄 hizli_test.py           # Hızlı çoklu hisse testi
├── 📄 README.md               # Bu dosya
└── 📄 requirements.txt        # Bağımlılıklar
```

## ⚙️ Yapılandırma

`FULL_SYSTEM.py` içinde:

```python
# Mock AI kullan (test için)
USE_MOCK_AI = True  # False = Gerçek Gemini AI

# Otomatik çalışma aralığı (saniye)
AUTO_RUN_INTERVAL = 1800  # 30 dakika

# Maksimum haber sayısı
MAX_NEWS = 30
```

## 📊 Örnek Çıktı

### Telegram Mesajı:

```
📊 BORSA ANALİZ RAPORU
2026-09-18 18:00

1. 🟢 Nasdaq Jumps 1.7% As Stock Market Gains Post-Fed
📈 QQQ, SPY
💭 Pozitif sinyal, Fed kararı sonrası yükseliş

2. 🔴 Fed Raises Interest Rates
📈 SPY, QQQ, DIA
💭 Negatif etki bekleniyor

💰 TRADING SİNYALLERİ

🟢 QQQ - AL
💵 Fiyat: $425.30
📊 Güven: Yüksek
📝 3+ / 1- / 0○

🔴 SPY - SAT
💵 Fiyat: $545.80
📊 Güven: Orta
📝 1+ / 3- / 1○

⚠️ Yatırım tavsiyesi değildir.
```

## 🔧 Gelişmiş Kullanım

### Otomatik Döngü Açma

`FULL_SYSTEM.py` sonunda:

```python
# Yorumu kaldırın:
while True:
    time.sleep(AUTO_RUN_INTERVAL)
    run_analysis()
```

### Gerçek Gemini AI Kullanma

1. Doğru API key alın: https://ai.google.dev/
2. `FULL_SYSTEM.py` içinde:

```python
USE_MOCK_AI = False
GEMINI_API_KEY = "dogru_api_key_buraya"
```

## 🧪 Test Dosyaları

### Haber Akışı Testi
```bash
python step1_haber_test.py
```

### Gemini AI Testi (Mock)
```bash
python step2_gemini_MOCK.py
```

### Telegram Bot Testi
```bash
python step3_telegram_bot.py
```

### Hisse Fiyatları Testi
```bash
python nasdaq_data_test.py
```

## ⚠️ Önemli Notlar

1. **Yatırım Tavsiyesi Değildir**: Bu sistem sadece haber analizi yapar
2. **API Limitleri**: 
   - Twelve Data: 800 istek/gün
   - Gemini: Ayda 1500 istek (ücretsiz)
3. **Gecikme**: Ücretsiz haber kaynakları 15-20 dakika gecikmeli olabilir
4. **Doğruluk**: AI analizi %100 doğru değildir, kendi araştırmanızı yapın

## 🐛 Sorun Giderme

### "Chat ID bulunamadı" hatası
- Telegram'da `/start` gönderdiğinizden emin olun
- Scripti tekrar çalıştırın

### "API key not valid" hatası
- Gemini API key'in doğru olduğundan emin olun
- `USE_MOCK_AI = True` yapıp test edin

### "Haber bulunamadı" hatası
- İnternet bağlantınızı kontrol edin
- Google News RSS erişilebilir olmalı

## 📈 Sonraki Adımlar

- [ ] Gerçek Gemini API entegrasyonu
- [ ] Teknik analiz ekleme (RSI, MACD, SMA)
- [ ] Birden fazla haber kaynağı
- [ ] Web dashboard oluşturma
- [ ] Portföy takibi
- [ ] Stop loss / take profit hesaplamaları
- [ ] Backtest özelliği

## 📞 Destek

Sorularınız için issue açabilirsiniz.

## 📄 Lisans

Bu proje MIT lisansı altındadır.

---

**⚠️ Uyarı**: Bu sistem yatırım tavsiyesi vermez. Tüm yatırım kararları sizin sorumluluğunuzdadır. Lütfen kendi araştırmanızı yapın ve gerekirse profesyonel danışmanlık alın.
