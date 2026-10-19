"""
Ghorak - Sugestão e Aplicação de Correções via ThinkinIA
"""
import os
import re
import shutil
from datetime import datetime
from flask import jsonify, request
from groq import Groq
from dotenv import load_dotenv

# Carregar variáveis de ambiente e inicializar cliente Groq
load_dotenv()
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"⚠️ Erro ao inicializar Groq: {e}")
    groq_client = None


def register_fix_routes(app):
    """Registra rotas de sugestão e aplicação de correção com IA"""

    @app.route('/api/code-review/suggest-fix', methods=['POST'])
    def suggest_fix():
        """Sugere correção para uma issue específica usando ThinkinIA"""
        try:
            data = request.json
            filepath = data.get('filepath')
            issue = data.get('issue')

            if not filepath or not issue:
                return jsonify({'error': 'filepath e issue são obrigatórios'}), 400

            if not groq_client:
                return jsonify({'error': 'Cliente Groq não inicializado. Verifique a GROQ_API_KEY.'}), 500

            base_dir = '/home/lps/thinkinos-platform'
            full_path = os.path.join(base_dir, filepath)

            if not os.path.exists(full_path):
                return jsonify({'error': 'Arquivo não encontrado'}), 404

            with open(full_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

            # Extrair apenas a função alvo se for issue de "função muito longa"
            func_name = None
            if 'Função muito longa:' in issue.get('title', ''):
                func_name = issue['title'].split('Função muito longa: ')[1].strip()

            if func_name:
                code_to_send = _extract_function(original_code, func_name)
                context_msg = f"Refatore APENAS a função '{func_name}' abaixo. Não reescreva o arquivo todo."
            else:
                code_to_send = original_code[:2500]
                context_msg = "Refatore o trecho de código abaixo para corrigir o problema."

            system_prompt = (
                "You are an expert Python/JS refactoring engine. "
                "Return ONLY the corrected code block. "
                "Do NOT include markdown formatting like ```python. "
                "Do NOT include explanations. Just the raw code."
            )

            user_prompt = f"""{context_msg}
Problema: {issue.get('description', '')}
Sugestão: {issue.get('suggestion', '')}

Código Alvo:
{code_to_send}
"""

            response = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )

            suggested_code = response.choices[0].message.content.strip()
            # Limpar markdown se a IA insistir
            suggested_code = re.sub(r'^```[a-zA-Z]*\n?', '', suggested_code)
            suggested_code = re.sub(r'\n?```$', '', suggested_code)

            return jsonify({
                'status': 'success',
                'original_code': code_to_send,
                'suggested_code': suggested_code,
                'prompt': user_prompt,
                'is_function_refactor': bool(func_name)
            })

        except Exception as e:
            error_msg = str(e)
            if 'rate_limit' in error_msg.lower() or 'Request too large' in error_msg:
                return jsonify({
                    'status': 'error',
                    'error': 'Limite de tokens do Groq excedido. Tente novamente em 1 minuto.'
                }), 429
            return jsonify({'status': 'error', 'error': error_msg}), 500

    @app.route('/api/code-review/apply-fix', methods=['POST'])
    def apply_fix():
        """Aplica a correção sugerida no arquivo, com backup automático"""
        try:
            data = request.json
            filepath = data.get('filepath')
            original_code = data.get('original_code')
            suggested_code = data.get('suggested_code')

            if not filepath or not original_code or not suggested_code:
                return jsonify({'error': 'Dados incompletos'}), 400

            base_dir = '/home/lps/thinkinos-platform'
            full_path = os.path.join(base_dir, filepath)

            if not os.path.exists(full_path):
                return jsonify({'error': 'Arquivo não encontrado'}), 404

            # 1. Criar backup automático
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{full_path}.backup_{timestamp}"
            shutil.copy2(full_path, backup_path)
            print(f"💾 [GHORAK] Backup criado: {backup_path}")

            # 2. Ler o arquivo atual
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.read()

            # 3. Verificar se o código original ainda está no arquivo
            if original_code not in current_content:
                return jsonify({
                    'error': 'Código original não encontrado no arquivo. O arquivo pode ter sido modificado.',
                    'backup': backup_path
                }), 409

            # 4. Substituir o código original pelo sugerido
            new_content = current_content.replace(original_code, suggested_code, 1)

            # 5. Salvar o arquivo modificado
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ [GHORAK] Correção aplicada em {filepath}")

            return jsonify({
                'status': 'success',
                'message': f'Correção aplicada com sucesso!',
                'backup': backup_path,
                'filepath': filepath
            })

        except Exception as e:
            return jsonify({'status': 'error', 'error': str(e)}), 500


def _extract_function(code, func_name):
    """Extrai apenas o bloco da função alvo do código"""
    lines = code.split('\n')
    start_idx = -1
    end_idx = -1

    # Encontrar início da função
    for i, line in enumerate(lines):
        if re.match(rf'^\s*def\s+{func_name}\s*\(', line):
            start_idx = i
            break

    if start_idx == -1:
        return code[:2500]  # Fallback

    # Encontrar fim da função
    base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        current_indent = len(line) - len(line.lstrip())
        if current_indent <= base_indent and line.strip().startswith('def '):
            end_idx = i
            break

    if end_idx == -1:
        return '\n'.join(lines[start_idx:])
    return '\n'.join(lines[start_idx:end_idx])
