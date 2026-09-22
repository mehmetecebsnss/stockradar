#!/bin/bash
# StockRadar Pro - Raspberry Pi Kurulum Scripti

set -e

echo "=================================================="
echo "  StockRadar Pro - Raspberry Pi Kurulumu"
echo "=================================================="

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Sistem güncellemesi
echo -e "${YELLOW}[1/7] Sistem güncelleniyor...${NC}"
sudo apt update
sudo apt upgrade -y

# 2. Python ve pip kurulumu
echo -e "${YELLOW}[2/7] Python ve pip kontrol ediliyor...${NC}"
sudo apt install -y python3 python3-pip python3-venv git

# 3. Proje dizinine git
echo -e "${YELLOW}[3/7] Proje dizini hazırlanıyor...${NC}"
cd ~
if [ -d "AcilPiyasaBotu" ]; then
    echo "Dizin zaten mevcut, güncelleniyor..."
    cd AcilPiyasaBotu
    git pull
else
    echo "GitHub'dan indiriliyor..."
    read -p "GitHub repo URL'inizi girin: " REPO_URL
    git clone "$REPO_URL" AcilPiyasaBotu
    cd AcilPiyasaBotu
fi

# 4. Virtual environment oluştur
echo -e "${YELLOW}[4/7] Virtual environment oluşturuluyor...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Bağımlılıkları kur
echo -e "${YELLOW}[5/7] Python paketleri kuruluyor...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 6. Config dosyası oluştur
echo -e "${YELLOW}[6/7] Konfigürasyon dosyası kontrol ediliyor...${NC}"
if [ ! -f "config.py" ]; then
    echo -e "${RED}config.py bulunamadı!${NC}"
    echo "config.example.py dosyasını config.py olarak kopyalayın ve düzenleyin:"
    echo "  cp config.example.py config.py"
    echo "  nano config.py"
    read -p "Şimdi yapmak ister misiniz? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp config.example.py config.py
        nano config.py
    else
        echo -e "${RED}Kurulum tamamlanamadı. Önce config.py oluşturun.${NC}"
        exit 1
    fi
fi

# 7. Systemd service kurulumu
echo -e "${YELLOW}[7/7] Systemd service kuruluyor...${NC}"

# Service dosyasını düzenle (yol güncellemesi)
CURRENT_DIR=$(pwd)
sed -i "s|/home/pi/AcilPiyasaBotu|$CURRENT_DIR|g" stockradar.service
sed -i "s|/usr/bin/python3|$CURRENT_DIR/venv/bin/python3|g" stockradar.service

# Service dosyasını kopyala
sudo cp stockradar.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stockradar.service

echo -e "${GREEN}=================================================="
echo "  Kurulum Tamamlandı!"
echo "==================================================${NC}"
echo ""
echo "Servis komutları:"
echo "  Başlat:    sudo systemctl start stockradar"
echo "  Durdur:    sudo systemctl stop stockradar"
echo "  Durum:     sudo systemctl status stockradar"
echo "  Log:       tail -f ~/AcilPiyasaBotu/stockradar.log"
echo "  Yeniden:   sudo systemctl restart stockradar"
echo ""
echo "Dashboard: http://$(hostname -I | awk '{print $1}'):5050"
echo ""
read -p "Servisi şimdi başlatmak ister misiniz? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start stockradar
    sleep 3
    sudo systemctl status stockradar
fi
