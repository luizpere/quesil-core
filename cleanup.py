#!/usr/bin/env python3
"""
ThinkinOS v2.0 - Script de Limpeza
Remove assistentes de teste e mantém apenas os 5 essenciais
"""

import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/home/lps/thinkinos-platform")
ASSISTANTS_JSON = BASE_DIR / "assistants.json"
DB_PATH = BASE_DIR / "thinkinos.db"
CHAT_DB_PATH = BASE_DIR / "chat_history.db"
BACKUP_DIR = BASE_DIR / "backups" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# IDs dos assistentes a MANTER
IDS_MANTER = ["8", "9", "10", "12", "13"]  # Pedro(analise), Ana, Lena, ThinkinIA, Carlos

# Nomes dos assistentes a REMOVER
NOMES_REMOVER = ["andre", "devops_junior", "devops_pleno", "thinkai"]
IDS_REMOVER = ["3", "4", "5", "6", "11"]  # + Pedro devops (id 11)

def criar_backup():
    """Cria backup completo antes da limpeza"""
    print("📦 [1/4] Criando backup...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    if ASSISTANTS_JSON.exists():
        shutil.copy(ASSISTANTS_JSON, BACKUP_DIR / "assistants_backup.json")
        print(f"   ✅ assistants.json backupado")
    
    if DB_PATH.exists():
        shutil.copy(DB_PATH, BACKUP_DIR / "thinkinos_backup.db")
        print(f"   ✅ thinkinos.db backupado")
    
    if CHAT_DB_PATH.exists():
        shutil.copy(CHAT_DB_PATH, BACKUP_DIR / "chat_history_backup.db")
        print(f"   ✅ chat_history.db backupado")
    
    print(f"   📁 Backup em: {BACKUP_DIR}\n")

def limpar_json():
    """Limpa o arquivo assistants.json"""
    print("🗂️  [2/4] Limpando assistants.json...")
    
    if not ASSISTANTS_JSON.exists():
        print("   ️  assistants.json não encontrado")
        return
    
    with open(ASSISTANTS_JSON, 'r', encoding='utf-8') as f:
        assistentes = json.load(f)
    
    print(f"   📊 Total atual: {len(assistentes)} assistentes")
    
    # Filtrar: manter apenas os 5 essenciais
    assistentes_filtrados = [a for a in assistentes if a["id"] in IDS_MANTER]
    assistentes_removidos = [a for a in assistentes if a["id"] not in IDS_MANTER]
    
    # Mostrar o que será removido
    for a in assistentes_removidos:
        print(f"   🗑️  Removendo: {a['display_name']} (id: {a['id']})")
    
    # Mostrar o que será mantido
    print()
    for a in assistentes_filtrados:
        print(f"   ✅ Mantendo: {a['display_name']} - {a['specialty']}")
    
    # Salvar arquivo limpo
    with open(ASSISTANTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(assistentes_filtrados, f, indent=2, ensure_ascii=False)
    
    print(f"\n   ✅ assistants.json limpo: {len(assistentes_filtrados)} assistentes\n")

def limpar_banco():
    """Limpa o banco de dados SQLite"""
    print("🗄️  [3/4] Limpando banco de dados...")
    
    if not DB_PATH.exists():
        print("   ⚠️  thinkinos.db não encontrado")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        print(f"   📋 Tabelas encontradas: {tabelas}")
        
        # Limpar tabela assistants se existir
        if 'assistants' in tabelas:
            cursor.execute("SELECT COUNT(*) FROM assistants")
            total = cursor.fetchone()[0]
            print(f"   📊 Total de registros em 'assistants': {total}")
            
            # Remover assistentes de teste
            placeholders = ','.join(['?' for _ in IDS_REMOVER])
            cursor.execute(f"DELETE FROM assistants WHERE id IN ({placeholders})", IDS_REMOVER)
            removidos = cursor.rowcount
            print(f"   🗑️  Removidos {removidos} assistentes de teste")
            
            # Verificar restantes
            cursor.execute("SELECT COUNT(*) FROM assistants")
            restantes = cursor.fetchone()[0]
            print(f"   ✅ Restantes: {restantes} assistentes")
        
        conn.commit()
        conn.close()
        print("   ✅ Banco de dados limpo!\n")
        
    except Exception as e:
        print(f"   ❌ Erro ao limpar banco: {e}\n")

def limpar_chat_history():
    """Limpa histórico de chat dos assistentes removidos"""
    print("💬 [4/4] Limpando histórico de chat...")
    
    if not CHAT_DB_PATH.exists():
        print("   ⚠️  chat_history.db não encontrado")
        return
    
    try:
        conn = sqlite3.connect(CHAT_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        if 'messages' in tabelas:
            # Remover mensagens dos assistentes removidos
            for nome in NOMES_REMOVER:
                cursor.execute("DELETE FROM messages WHERE assistant_name = ?", (nome,))
                if cursor.rowcount > 0:
                    print(f"   🗑️  Removidas {cursor.rowcount} mensagens de '{nome}'")
        
        conn.commit()
        conn.close()
        print("   ✅ Histórico limpo!\n")
        
    except Exception as e:
        print(f"   ❌ Erro ao limpar histórico: {e}\n")

def gerar_relatorio():
    """Gera relatório da limpeza"""
    relatorio = BACKUP_DIR / "relatorio.txt"
    
    with open(relatorio, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("THINKINOS V2.0 - RELATÓRIO DE LIMPEZA\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("ASSISTENTES MANTIDOS (5):\n")
        f.write("-" * 40 + "\n")
        with open(ASSISTANTS_JSON, 'r', encoding='utf-8') as jf:
            assistentes = json.load(jf)
            for a in assistentes:
                f.write(f"✓ {a['display_name']} - {a['specialty']}\n")
        
        f.write("\nASSISTENTES REMOVIDOS (5):\n")
        f.write("-" * 40 + "\n")
        f.write(" André (Inspeção de Segurança)\n")
        f.write("✗ DevOps Junior (Linux Admin)\n")
        f.write("✗ DevOps Pleno (Kubernetes)\n")
        f.write("✗ ThinkAI (Gestão de IAs)\n")
        f.write("✗ Pedro (DevOps Senior)\n")
    
    print(f"📋 Relatório salvo em: {relatorio}\n")

def main():
    print("\n" + "=" * 60)
    print("🧹 THINKINOS V2.0 - LIMPEZA DE ASSISTENTES")
    print("=" * 60 + "\n")
    
    print("Este script irá:")
    print("1. Criar backup completo de todos os dados")
    print("2. Remover 5 assistentes de teste do JSON")
    print("3. Limpar banco de dados SQLite")
    print("4. Limpar histórico de chat relacionado")
    print("5. Gerar relatório da operação")
    print()
    
    resposta = input("️  Deseja continuar? (s/n): ").strip().lower()
    if resposta != 's':
        print("❌ Operação cancelada")
        return
    
    print("\n🚀 Iniciando limpeza...\n")
    
    criar_backup()
    limpar_json()
    limpar_banco()
    limpar_chat_history()
    gerar_relatorio()
    
    print("=" * 60)
    print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print(f"\n📁 Backup em: {BACKUP_DIR}")
    print(" Sistema pronto com 5 assistentes essenciais:")
    print("   • ThinkinIA (Core)")
    print("   • Ana (General)")
    print("   • Pedro (Análise e Lógica)")
    print("   • Lena (Produtividade)")
    print("   • Carlos (Analytics)")
    print("\n⚠️  REINICIE o servidor Flask para aplicar as mudanças:")
    print("   python app.py\n")

if __name__ == "__main__":
    main()
