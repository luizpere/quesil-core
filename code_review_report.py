"""
Ghorak - Gerador de Relatórios Periódicos
Módulo standalone para análise agendada via cron
"""
import os
import sys
import json
from datetime import datetime, timedelta

# Adicionar diretório do projeto ao path para importar módulos
PROJECT_DIR = '/home/lps/thinkinos-platform'
sys.path.insert(0, PROJECT_DIR)

from code_review_ai import analyze_file_advanced
from code_review_security import analyze_security, analyze_performance

REPORTS_DIR = os.path.join(PROJECT_DIR, 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def scan_project(hours=24, base_dir=None):
    """Varre o projeto em busca de arquivos modificados"""
    if base_dir is None:
        base_dir = PROJECT_DIR
    
    extensions = ['.py', '.js', '.html', '.css']
    cutoff_time = datetime.now().timestamp() - (hours * 3600)
    
    modified_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'node_modules', 'reports']]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime >= cutoff_time:
                        rel_path = os.path.relpath(filepath, base_dir)
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        modified_files.append({
                            'path': rel_path,
                            'name': file,
                            'modified': datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M'),
                            'content': content,
                            'icon': '🐍' if file.endswith('.py') else '📜' if file.endswith('.js') else '🌐' if file.endswith('.html') else '🎨'
                        })
                except Exception:
                    continue
    
    return modified_files

def generate_report(hours=24, base_dir=None):
    """Gera relatório completo de análise de código"""
    print(f" [GHORAK] Iniciando análise agendada ({datetime.now().strftime('%d/%m/%Y %H:%M')})")
    
    modified_files = scan_project(hours, base_dir)
    print(f"📁 [GHORAK] {len(modified_files)} arquivos modificados encontrados")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'hours_analyzed': hours,
        'total_files': len(modified_files),
        'files': [],
        'summary': {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total_issues': 0
        },
        'top_issues': [],
        'files_with_issues': []
    }
    
    for file_info in modified_files:
        try:
            issues = analyze_file_advanced(file_info['name'], file_info['content'])
            issues.extend(analyze_security(file_info['name'], file_info['content']))
            issues.extend(analyze_performance(file_info['name'], file_info['content']))
            
            file_entry = {
                'path': file_info['path'],
                'name': file_info['name'],
                'modified': file_info['modified'],
                'icon': file_info['icon'],
                'issues': issues,
                'total_issues': len(issues)
            }
            report['files'].append(file_entry)
            
            # Atualizar summary
            for issue in issues:
                severity = issue.get('severity', 'low')
                if severity in report['summary']:
                    report['summary'][severity] += 1
                report['summary']['total_issues'] += 1
            
            if issues:
                report['files_with_issues'].append(file_info['path'])
                
        except Exception as e:
            print(f"⚠️ [GHORAK] Erro ao analisar {file_info['path']}: {e}")
    
    # Top 10 issues mais críticas
    all_issues = []
    for f in report['files']:
        for issue in f['issues']:
            all_issues.append({
                'file': f['path'],
                **issue
            })
    
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
    report['top_issues'] = all_issues[:10]
    
    # Salvar relatório
    report_file = os.path.join(REPORTS_DIR, f"{report['date']}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ [GHORAK] Relatório salvo: {report_file}")
    print(f"📊 [GHORAK] Total de issues: {report['summary']['total_issues']}")
    print(f"   🔴 Críticas: {report['summary']['critical']}")
    print(f"   🟠 Altas: {report['summary']['high']}")
    print(f"   🟡 Médias: {report['summary']['medium']}")
    print(f"   🔵 Baixas: {report['summary']['low']}")
    
    return report

def get_report_history(days=30):
    """Retorna histórico dos últimos N dias de relatórios"""
    history = []
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        report_file = os.path.join(REPORTS_DIR, f"{date_str}.json")
        
        if os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                history.append({
                    'date': date_str,
                    'total_issues': report['summary']['total_issues'],
                    'critical': report['summary']['critical'],
                    'high': report['summary']['high'],
                    'medium': report['summary']['medium'],
                    'low': report['summary']['low'],
                    'files_analyzed': report['total_files']
                })
            except Exception as e:
                print(f"⚠️ Erro ao ler {report_file}: {e}")
        else:
            history.append({
                'date': date_str,
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'files_analyzed': 0,
                'no_report': True
            })
    
    return history

def get_latest_report():
    """Retorna o relatório mais recente"""
    reports = sorted(os.listdir(REPORTS_DIR), reverse=True)
    json_reports = [r for r in reports if r.endswith('.json')]
    
    if json_reports:
        latest = json_reports[0]
        with open(os.path.join(REPORTS_DIR, latest), 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

if __name__ == '__main__':
    # Modo standalone: gerar relatório agora
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    generate_report(hours=hours)
