#!/bin/bash
PYTHON="/home/lps/thinkinos-platform/venv/bin/python3"
SCRIPT="/home/lps/thinkinos-platform/backups/auto_backup.py"

case "$1" in
    daily) $PYTHON $SCRIPT daily ;;
    weekly) $PYTHON $SCRIPT weekly ;;
    list) $PYTHON $SCRIPT list ;;
    cron)
        (crontab -l 2>/dev/null | grep -v "auto_backup.py"; echo "0 2 * * * cd /home/lps/thinkinos-platform && $PYTHON $SCRIPT daily >> /home/lps/thinkinos-platform/backups/cron.log 2>&1"; echo "0 3 * * 0 cd /home/lps/thinkinos-platform && $PYTHON $SCRIPT weekly >> /home/lps/thinkinos-platform/backups/cron.log 2>&1") | crontab -
        echo "✅ Cron configurado! (Diário 02:00, Semanal Domingo 03:00)"
        crontab -l | grep auto_backup
        ;;
    *)
        echo "Uso: ./backup_manager.sh {daily|weekly|list|cron}"
        ;;
esac
