#!/bin/bash
# ─────────────────────────────────────────────
#  StockRadar Pro — Otomatik Güncelleme Servisi
#  Raspberry Pi'de çalışır.
#  GitHub'da değişiklik varsa çeker, botu yeniden başlatır.
# ─────────────────────────────────────────────

REPO_DIR="/home/pi/stockradar"
SERVICE_NAME="stockradar"
CHECK_INTERVAL=60   # Kaç saniyede bir kontrol (varsayılan: 1 dakika)
LOG_FILE="$REPO_DIR/auto_update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Auto-Update Servisi Başladı ==="
log "Repo: $REPO_DIR"
log "Kontrol aralığı: ${CHECK_INTERVAL}s"

while true; do
    cd "$REPO_DIR" || { log "HATA: Dizin bulunamadı: $REPO_DIR"; sleep 60; continue; }

    # Uzak repo'dan bilgi al
    git fetch origin main --quiet 2>/dev/null

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" != "$REMOTE" ]; then
        log "Güncelleme bulundu! ($LOCAL → $REMOTE)"
        
        # config.py'yi koru (git pull ezmesin)
        git stash 2>/dev/null

        # Güncellemeyi çek
        git pull origin main --quiet
        log "Kod güncellendi."

        # Saklanan config.py'yi geri al
        git stash pop 2>/dev/null

        # Virtual environment varsa pip güncelle
        if [ -f "$REPO_DIR/venv/bin/pip" ]; then
            log "Bağımlılıklar güncelleniyor..."
            "$REPO_DIR/venv/bin/pip" install -r requirements.txt --quiet
        fi

        # Servisi yeniden başlat
        log "Servis yeniden başlatılıyor: $SERVICE_NAME"
        sudo systemctl restart "$SERVICE_NAME"
        sleep 3

        # Başarılı mı kontrol et
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            log "✅ Servis başarıyla yeniden başlatıldı."
        else
            log "❌ Servis başlatılamadı! Log kontrol edin."
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
