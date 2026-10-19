"""
Ghorak - Regras Avançadas de Segurança e Performance
"""
import re

def analyze_security(filename, content):
    """Análise de segurança"""
    issues = []
    lines = content.split('\n')
    
    # 1. Hardcoded secrets (senhas, chaves API, tokens)
    secret_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'Senha hardcoded'),
        (r'api_key\s*=\s*["\'][^"\']+["\']', 'API key hardcoded'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'Secret hardcoded'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'Token hardcoded'),
    ]
    
    for i, line in enumerate(lines):
        for pattern, title in secret_patterns:
            if re.search(pattern, line, re.IGNORECASE) and not line.strip().startswith('#'):
                issues.append({
                    'severity': 'critical',
                    'title': title,
                    'description': f'Linha {i+1} contém credencial hardcoded.',
                    'suggestion': 'Use variáveis de ambiente (os.environ) ou arquivo .env.'
                })
    
    # 2. SQL Injection (concatenação de strings em queries)
    if filename.endswith('.py'):
        for i, line in enumerate(lines):
            if ('execute(' in line or 'executemany(' in line) and '+' in line:
                issues.append({
                    'severity': 'critical',
                    'title': 'Possível SQL Injection',
                    'description': f'Linha {i+1} usa concatenação em query SQL.',
                    'suggestion': 'Use parâmetros (? ou :name) em vez de concatenação.'
                })
    
    # 3. Path Traversal
    if filename.endswith('.py'):
        for i, line in enumerate(lines):
            if 'open(' in line and 'request' in line and 'path' in line:
                if 'normalize' not in line and 'realpath' not in line:
                    issues.append({
                        'severity': 'high',
                        'title': 'Possível Path Traversal',
                        'description': f'Linha {i+1} abre arquivo com path do usuário sem validação.',
                        'suggestion': 'Use os.path.realpath() e valide se está dentro do diretório permitido.'
                    })
    
    return issues

def analyze_performance(filename, content):
    """Análise de performance"""
    issues = []
    lines = content.split('\n')
    
    if filename.endswith('.py'):
        # 1. Queries dentro de loops
        in_loop = False
        for i, line in enumerate(lines):
            if line.strip().startswith('for ') or line.strip().startswith('while '):
                in_loop = True
            elif in_loop and ('execute(' in line or 'query(' in line):
                issues.append({
                    'severity': 'high',
                    'title': 'Query dentro de loop',
                    'description': f'Linha {i+1} executa query dentro de loop.',
                    'suggestion': 'Use bulk operations ou JOINs para reduzir queries.'
                })
                in_loop = False
            elif in_loop and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                in_loop = False
        
        # 2. List comprehension vs loop append (sugestão de otimização)
        for i, line in enumerate(lines):
            if '.append(' in line and i > 0 and 'for ' in lines[i-1]:
                issues.append({
                    'severity': 'low',
                    'title': 'List comprehension possível',
                    'description': f'Linha {i+1} usa append em loop.',
                    'suggestion': 'Considere usar list comprehension para melhor performance.'
                })
    
    return issues
