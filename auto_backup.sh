#!/bin/bash
# ThinkinOS - Sistema de Backup Automático Diário

PROJECT_DIR="/home/lps/thinkinos-platform"
BACKUP_DIR="/home/lps/thinkinos-backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🔄 Iniciando backup do ThinkinOS..."

# 1. Criar pasta de backup local se não existir
mkdir -p "$BACKUP_DIR"
cd "$PROJECT_DIR" || exit

# 2. Backup Local (arquivo compactado, ignorando arquivos pesados)
echo "📦 Criando backup local..."
tar -czf "$BACKUP_DIR/thinkinos_backup_$DATE.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='uploads' \
    --exclude='*.db' \
    .
echo "✅ Backup local criado: thinkinos_backup_$DATE.tar.gz"

# 3. Backup no GitHub
echo "📤 Enviando alterações para o GitHub..."
git add .
git commit -m "Auto-backup: $DATE"
git push origin main
echo "✅ Backup no GitHub concluído!"

# 4. Limpeza (mantém apenas os 5 backups locais mais recentes para não encher o disco)
cd "$BACKUP_DIR"
ls -t thinkinos_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
echo "🧹 Backups locais antigos limpos."

echo "🎉 Backup do ThinkinOS concluído com sucesso!"
