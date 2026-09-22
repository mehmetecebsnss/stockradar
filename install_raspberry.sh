#!/bin/bash
# ─────────────────────────────────────────────
#  StockRadar Pro — Raspberry Pi Kurulum Scripti
#  Çalıştır: chmod +x install_raspberry.sh && ./install_raspberry.sh
# ─────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_URL="https://github.com/mehmetecebsnss/stockradar.git"
REPO_DIR="/home/pi/stockradar"

echo -e "${GREEN}"
echo "=================================================="
echo "   StockRadar Pro — Raspberry Pi Kurulumu"
echo "=================================================="
echo -e "${NC}"

# 1. Sistem güncelleme
echo -e "${YELLOW}[1/8] Sistem güncelleniyor...${NC}"
sudo apt update -q
sudo apt install -y python3 python3-pip python3-venv git curl

# 2. Repo indir veya güncelle
echo -e "${YELLOW}[2/8] Repo indiriliyor...${NC}"
if [ -d "$REPO_DIR" ]; then
    echo "  Mevcut repo güncelleniyor..."
    cd "$REPO_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 3. Virtual environment
echo -e "${YELLOW}[3/8] Virtual environment oluşturuluyor...${NC}"
python3 -m venv "$REPO_DIR/venv"
source "$REPO_DIR/venv/bin/activate"

# 4. Bağımlılıklar
echo -e "${YELLOW}[4/8] Python paketleri kuruluyor...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "  ✅ Paketler kuruldu."

# 5. Config
echo -e "${YELLOW}[5/8] Konfigürasyon...${NC}"
if [ ! -f "$REPO_DIR/config.py" ]; then
    cp "$REPO_DIR/config.example.py" "$REPO_DIR/config.py"
    echo -e "${RED}"
    echo "  ⚠️  config.py oluşturuldu ama düzenlenmesi gerekiyor!"
    echo "  Şimdi nano ile açıyoruz, API key'leri girin:"
    echo -e "${NC}"
    sleep 2
    nano "$REPO_DIR/config.py"
else
    echo "  ✅ config.py zaten mevcut."
fi

# 6. auto_update.sh çalıştırma izni
echo -e "${YELLOW}[6/8] Scriptlere izin veriliyor...${NC}"
chmod +x "$REPO_DIR/auto_update.sh"

# 7. Pi kullanıcısına sudo yetkisi (servis restart için)
echo -e "${YELLOW}[7/8] Sudo yetkisi ayarlanıyor...${NC}"
SUDOERS_LINE="pi ALL=(ALL) NOPASSWD: /bin/systemctl restart stockradar, /bin/systemctl restart stockradar-updater"
if ! sudo grep -qF "stockradar" /etc/sudoers; then
    echo "$SUDOERS_LINE" | sudo tee -a /etc/sudoers > /dev/null
    echo "  ✅ Sudo yetkisi eklendi."
else
    echo "  ✅ Sudo yetkisi zaten mevcut."
fi

# 8. Systemd servisleri kur
echo -e "${YELLOW}[8/8] Systemd servisleri kuruluyor...${NC}"
sudo cp "$REPO_DIR/stockradar.service" /etc/systemd/system/
sudo cp "$REPO_DIR/stockradar-updater.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable stockradar
sudo systemctl enable stockradar-updater

echo ""
echo -e "${GREEN}=================================================="
echo "   ✅ Kurulum Tamamlandı!"
echo "==================================================${NC}"
echo ""
echo "  Başlatmak için:"
echo "    sudo systemctl start stockradar"
echo "    sudo systemctl start stockradar-updater"
echo ""
echo "  Durum kontrolü:"
echo "    sudo systemctl status stockradar"
echo ""
echo "  Log takibi:"
echo "    tail -f $REPO_DIR/stockradar.log"
echo ""
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "  Dashboard: http://${LOCAL_IP}:5050"
echo ""

read -p "Servisleri şimdi başlatmak ister misiniz? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start stockradar
    sudo systemctl start stockradar-updater
    sleep 3
    echo ""
    sudo systemctl status stockradar --no-pager
fi
