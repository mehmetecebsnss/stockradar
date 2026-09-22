# 🚀 GitHub ve Raspberry Pi Deploy Checklist

## ✅ GitHub'a Atmadan Önce

### 1. Hassas Bilgileri Temizle
- [ ] `config.py` dosyasını sil veya `.gitignore`'da olduğundan emin ol
- [ ] `dashboard.db` dosyasını sil (veritabanı)
- [ ] `*.log` dosyalarını sil
- [ ] Test dosyalarını kontrol et (test_*.py, *_test.py)

### 2. Gerekli Dosyaları Kontrol Et
- [ ] `.gitignore` oluşturuldu
- [ ] `config.example.py` oluşturuldu
- [ ] `requirements.txt` güncel
- [ ] `README_GITHUB.md` hazır (README.md olarak kopyalanacak)
- [ ] `stockradar.service` hazır
- [ ] `install_raspberry.sh` hazır ve çalıştırılabilir

### 3. requirements.txt Kontrol

```bash
pip freeze > requirements_full.txt
# Sadece gerekli paketleri requirements.txt'e ekle
```

**Gerekli paketler:**
```
requests>=2.28.0
pandas>=1.5.0
Flask>=2.3.0
python-telegram-bot>=20.0
```

### 4. Git Komutları

```bash
# Repo oluştur
cd AcilPiyasaBotu
git init
git add .
git status  # config.py görünmemeli!

# README'yi değiştir
mv README.md README_OLD.md
mv README_GITHUB.md README.md

# Commit
git commit -m "Initial commit: StockRadar Pro v1.0"

# GitHub'a push
git remote add origin https://github.com/YOUR_USERNAME/AcilPiyasaBotu.git
git branch -M main
git push -u origin main
```

## ✅ Raspberry Pi Kurulum Adımları

### 1. Raspberry Pi OS Güncellemesi

```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2. Proje İndirme

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/AcilPiyasaBotu.git
cd AcilPiyasaBotu
```

### 3. Otomatik Kurulum

```bash
chmod +x install_raspberry.sh
./install_raspberry.sh
```

**VEYA Manuel:**

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Paketler
pip install --upgrade pip
pip install -r requirements.txt

# Config
cp config.example.py config.py
nano config.py  # API key'leri gir

# Service
sudo cp stockradar.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stockradar
sudo systemctl start stockradar
```

### 4. Test

```bash
chmod +x test_service.sh
./test_service.sh
```

### 5. Dashboard Erişimi

```bash
# Local IP'yi öğren
hostname -I

# Tarayıcıda aç
# http://[RASPBERRY_PI_IP]:5050
# Örnek: http://192.168.1.100:5050
```

## ✅ Servis Yönetimi

### Temel Komutlar

```bash
sudo systemctl start stockradar      # Başlat
sudo systemctl stop stockradar       # Durdur
sudo systemctl restart stockradar    # Yeniden başlat
sudo systemctl status stockradar     # Durum
sudo systemctl enable stockradar     # Otomatik başlat
sudo systemctl disable stockradar    # Otomatik başlatma iptal
```

### Log Takibi

```bash
# Canlı log izle
tail -f ~/AcilPiyasaBotu/stockradar.log

# Son 100 satır
tail -n 100 ~/AcilPiyasaBotu/stockradar.log

# Hata ara
grep ERROR ~/AcilPiyasaBotu/stockradar.log
```

### Kod Güncelleme

```bash
cd ~/AcilPiyasaBotu
git pull
sudo systemctl restart stockradar
```

## ✅ Port Forwarding (İnternetten Erişim İçin)

### Router Ayarları

1. Router admin paneline gir (genelde 192.168.1.1)
2. Port Forwarding / Virtual Server bölümüne git
3. Yeni kural ekle:
   - **External Port:** 8080
   - **Internal Port:** 5050
   - **Internal IP:** [Raspberry Pi IP]
   - **Protocol:** TCP

### Dashboard Erişimi

```
http://[MODEM_PUBLIC_IP]:8080
```

Public IP öğrenmek için: https://whatismyipaddress.com

### Güvenlik (Opsiyonel)

```bash
# Nginx reverse proxy + SSL
sudo apt install nginx certbot python3-certbot-nginx

# Basic auth ekle
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Nginx config
sudo nano /etc/nginx/sites-available/stockradar
```

## ✅ Troubleshooting

### Servis başlamıyor

```bash
# Log kontrol
journalctl -u stockradar.service -n 50

# Manuel başlat (debug için)
cd ~/AcilPiyasaBotu
source venv/bin/activate
python3 bot.py
```

### Dashboard açılmıyor

```bash
# Port kontrol
netstat -tlnp | grep 5050

# Flask hata log
cat ~/AcilPiyasaBotu/stockradar.log | grep Flask
```

### API hatası

```bash
# Config kontrol
cat ~/AcilPiyasaBotu/config.py

# API key test
curl "https://api.twelvedata.com/time_series?symbol=AAPL&interval=1min&apikey=YOUR_KEY"
```

## 📋 Son Kontrol Listesi

- [ ] Bot Telegram'da çalışıyor
- [ ] Dashboard açılıyor (http://[IP]:5050)
- [ ] Sinyaller gruba geliyor
- [ ] Servis otomatik başlıyor (reboot sonrası)
- [ ] Loglar yazılıyor
- [ ] Veritabanı oluşuyor

---

🎉 **Başarıyla Deploy Edildi!**
