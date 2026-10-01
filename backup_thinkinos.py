#!/usr/bin/env python3
"""
Sistema de Backup do ThinkinOS v2.0
Cria backups completos e organizados do sistema
"""
import os
import shutil
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def create_backup():
    """Cria backup completo do ThinkinOS"""
    
    # Configurações
    BASE_DIR = Path('/home/lps/thinkinos-platform')
    BACKUP_DIR = BASE_DIR / 'backups'
    TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
    BACKUP_NAME = f'thinkinos_backup_{TIMESTAMP}'
    BACKUP_PATH = BACKUP_DIR / BACKUP_NAME
    
    print("=" * 60)
    print("🛡️  SISTEMA DE BACKUP - ThinkinOS v2.0")
    print("=" * 60)
    
    # Criar diretório de backups
    BACKUP_DIR.mkdir(exist_ok=True)
    BACKUP_PATH.mkdir(exist_ok=True)
    
    # Arquivos e pastas para backup
    items_to_backup = {
        '📊 Banco de Dados': [
            'thinkinos.db',
            'chat_history.db'
        ],
        '🤖 Assistentes': [
            'assistants.json'
        ],
        '🔧 Configurações': [
            '.env',
            'app.py'
        ],
        '🎨 Templates': [
            'templates/desktop.html',
            'templates/perfil.html',
            'templates/configuracoes.html'
        ],
        '📝 Memórias': [
            'memories.json'
        ]
    }
    
    backed_up_files = []
    skipped_files = []
    
    # Copiar arquivos
    for category, files in items_to_backup.items():
        print(f"\n{category}:")
        for file in files:
            source = BASE_DIR / file
            if source.exists():
                # Criar subdiretório se necessário
                if '/' in file:
                    dest_dir = BACKUP_PATH / file.rsplit('/', 1)[0]
                    dest_dir.mkdir(parents=True, exist_ok=True)
                
                dest = BACKUP_PATH / file
                shutil.copy2(source, dest)
                size = source.stat().st_size
                print(f"  ✅ {file} ({size:,} bytes)")
                backed_up_files.append(file)
            else:
                print(f"  ⚠️  {file} (não encontrado, pulando)")
                skipped_files.append(file)
    
    # Criar arquivo de manifesto
    manifest = {
        'backup_name': BACKUP_NAME,
        'created_at': datetime.now().isoformat(),
        'version': '2.0',
        'files_backed_up': backed_up_files,
        'files_skipped': skipped_files,
        'total_files': len(backed_up_files)
    }
    
    manifest_path = BACKUP_PATH / 'backup_manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Criar arquivo compactado (.zip)
    zip_path = BACKUP_DIR / BACKUP_NAME
    shutil.make_archive(zip_path, 'zip', BACKUP_PATH)
    
    # Calcular tamanho total
    total_size = sum(f.stat().st_size for f in BACKUP_PATH.rglob('*') if f.is_file())
    zip_size = Path(f'{zip_path}.zip').stat().st_size
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DO BACKUP")
    print("=" * 60)
    print(f"📁 Local: {BACKUP_DIR}")
    print(f"📦 Arquivo: {BACKUP_NAME}.zip")
    print(f" Tamanho: {zip_size:,} bytes ({zip_size/1024:.2f} KB)")
    print(f" Arquivos: {len(backed_up_files)}")
    print(f"️  Pulados: {len(skipped_files)}")
    print("=" * 60)
    print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    
    # Limpar backups antigos (manter apenas os 5 mais recentes)
    cleanup_old_backups(BACKUP_DIR, keep=5)
    
    return BACKUP_PATH

def cleanup_old_backups(backup_dir, keep=5):
    """Mantém apenas os N backups mais recentes"""
    backups = sorted(backup_dir.glob('thinkinos_backup_*'))
    
    if len(backups) > keep:
        print(f"\n🧹 Limpando backups antigos (mantendo {keep} mais recentes)...")
        for old_backup in backups[:-keep]:
            if old_backup.is_dir():
                shutil.rmtree(old_backup)
                print(f"  🗑️  Removido: {old_backup.name}")
            zip_file = backup_dir / f"{old_backup.name}.zip"
            if zip_file.exists():
                zip_file.unlink()
                print(f"  🗑️  Removido: {zip_file.name}")

def list_backups():
    """Lista todos os backups disponíveis"""
    backup_dir = Path('/home/lps/thinkinos-platform/backups')
    
    if not backup_dir.exists():
        print("❌ Nenhum backup encontrado.")
        return
    
    backups = sorted(backup_dir.glob('thinkinos_backup_*.zip'), reverse=True)
    
    print("\n" + "=" * 60)
    print("📋 BACKUPS DISPONÍVEIS")
    print("=" * 60)
    
    if not backups:
        print("Nenhum backup encontrado.")
        return
    
    for i, backup in enumerate(backups, 1):
        size = backup.stat().st_size
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{i}. {backup.name}")
        print(f"   Data: {mtime.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Tamanho: {size/1024:.2f} KB")
        print()

def restore_backup(backup_name=None):
    """Restaura o backup mais recente ou um específico"""
    backup_dir = Path('/home/lps/thinkinos-platform/backups')
    
    if backup_name:
        backup_file = backup_dir / f"{backup_name}.zip"
    else:
        backups = sorted(backup_dir.glob('thinkinos_backup_*.zip'), reverse=True)
        if not backups:
            print("❌ Nenhum backup encontrado para restaurar.")
            return
        backup_file = backups[0]
    
    if not backup_file.exists():
        print(f"❌ Backup não encontrado: {backup_file}")
        return
    
    print(f"\n🔄 Restaurando backup: {backup_file.name}")
    print("⚠️  Isso sobrescreverá os arquivos atuais!")
    
    import zipfile
    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
        zip_ref.extractall('/home/lps/thinkinos-platform')
    
    print("✅ Backup restaurado com sucesso!")
    print("🔄 Reinicie o servidor para aplicar as alterações.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'list':
            list_backups()
        elif command == 'restore':
            backup_name = sys.argv[2] if len(sys.argv) > 2 else None
            restore_backup(backup_name)
        else:
            print("Comandos disponíveis:")
            print("  python3 backup_thinkinos.py           - Criar backup")
            print("  python3 backup_thinkinos.py list      - Listar backups")
            print("  python3 backup_thinkinos.py restore   - Restaurar último backup")
    else:
        create_backup()
