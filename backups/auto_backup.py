#!/usr/bin/env python3
import os, tarfile, sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/lps/thinkinos-platform")
BACKUP_DIR = BASE_DIR / "backups"
LOG_FILE = BACKUP_DIR / "backup.log"

BACKUP_ITEMS = ["app.py", "templates", "static", ".env", "assistants.json", "chat_history.db"]

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f: f.write(f"[{ts}] {msg}\n")

def run_backup(btype="daily"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bpath = BACKUP_DIR / f"ThinkinOS_{btype}_{ts}.tar.gz"
    log(f"Iniciando backup {btype}...")
    BACKUP_DIR.mkdir(exist_ok=True)
    try:
        with tarfile.open(bpath, "w:gz") as tar:
            for item in BACKUP_ITEMS:
                p = BASE_DIR / item
                if p.exists():
                    tar.add(p, arcname=item)
                    log(f"  + {item}")
        log(f"Sucesso: {bpath.name} ({bpath.stat().st_size/1024/1024:.2f} MB)")
    except Exception as e:
        log(f"Erro: {e}")

def list_backups():
    backups = sorted(BACKUP_DIR.glob("ThinkinOS_*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    print("\nBackups existentes:")
    for b in backups[:10]:
        print(f"  - {b.name} ({b.stat().st_size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list": 
        list_backups()
    else: 
        run_backup(sys.argv[1] if len(sys.argv) > 1 else "daily")
