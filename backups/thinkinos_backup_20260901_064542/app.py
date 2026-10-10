print("🟢 [INÍCIO] app.py começou a carregar...")
import re
from dotenv import load_dotenv, set_key, find_dotenv
from flask import redirect,  session, request, jsonify,  session, Flask, session, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from groq import Groq
import json
import random
import os
from datetime import datetime
import sqlite3
import sqlite3









# === CONFIGURAÇÃO DE ARQUIVOS ===
UPLOAD_FOLDER = '/home/lps/thinkinos-platform/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# ================================

# === CONEXÃO COM BANCO DE DADOS ===
DB_PATH = '/home/lps/thinkinos-platform/thinkinos.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_cursor():
    conn = get_db()
    return conn.cursor()

# ================================


load_dotenv()

app = Flask(__name__)
app.secret_key = '81b1e840f53b20492a2890d3a51805bdb56ad9d331c6fb4845ac1904d91a9080'  # Chave secreta para sessões seguras

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERRO: GROQ_API_KEY não encontrada!", file=sys.stderr)
    sys.exit(1)

client = Groq(api_key=api_key)
print(f"Groq OK: {api_key[:8]}...")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.db")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CURRENT_PROFILE = 'personal'
AGENTS_CONFIG = {}

def load_agents_config(profile_filter=None):
    """Carrega assistentes do arquivo JSON (fonte única de verdade)"""
    try:
        import json
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assistants.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            assistentes = json.load(f)
        
        config = {}
        for agent in assistentes:
            if not agent.get('active', True):
                continue
            if profile_filter and agent.get('profile') != profile_filter:
                continue
            
            # Usa o display_name como chave para bater exatamente com o que o frontend envia
            key = agent.get('display_name', agent.get('name', '')).strip()
            config[key] = {
                'prompt': agent.get('prompt', ''),
                'display_name': agent.get('display_name', key),
                'color': agent.get('color', '#1CC54B'),
                'category': agent.get('specialty', agent.get('category', ''))
            }
        
        print(f"✅ {len(config)} assistentes carregados do JSON (chaves: {list(config.keys())})")
        return config
    except Exception as e:
        print(f"❌ ERRO ao carregar assistentes do JSON: {e}")
        return {}
# Inicializa config
AGENTS_CONFIG = load_agents_config(CURRENT_PROFILE)




def force_portuguese_response(text):
    """Filtra respostas - permite LaTeX/código, só bloqueia se for majoritariamente inglês"""
    if not text:
        return "Desculpe, não entendi. Pode reformular?"
    
    # Contar palavras em inglês vs português
    text_lower = text.lower()
    en_words = ['the ', 'and ', 'is ', 'are ', 'was ', 'were ', 'have ', 'has ', 'will ', 'would ']
    pt_words = ['o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'é ', 'são ', 'foi ', 'foram ', 'tem ', 'vão ']
    
    en_count = sum(1 for word in en_words if word in text_lower)
    pt_count = sum(1 for word in pt_words if word in text_lower)
    
    # Só bloqueia se tiver MUITO mais inglês que português (resposta em inglês)
    if en_count > pt_count and en_count >= 3:
        return "Por favor, reformule sua pergunta em português para que eu possa ajudar melhor."
    
    # Permitir LaTeX e código (são úteis para explicações técnicas)
    return text.strip()

@app.route('/desktop')
def desktop():
    # Ler assistente selecionado da URL (padrão: primeiro assistente ativo)
    selected_assistant = request.args.get('assistant', '')
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM assistants WHERE is_active=1 AND profile=? ORDER BY name", (CURRENT_PROFILE,))
        rows = cursor.fetchall()
        agents = {}
        for row in rows:
            agents[row['name']] = dict(row)
        
        # Se nenhum assistente foi selecionado ou não existe, usar o primeiro
        if not selected_assistant or selected_assistant not in agents:
            selected_assistant = list(agents.keys())[0] if agents else 'Pedro'
    except Exception as e:
        print(f"ERRO ao carregar assistentes: {e}")
        agents = {}
    return render_template('desktop.html', agents=agents, current_profile=CURRENT_PROFILE, selected_assistant=selected_assistant)

@app.route('/chat-window')
def chat_window():
    return render_template('chat-window.html')



def clean_markdown(text):
    """Remove formatação markdown da resposta da IA"""
    if not text:
        return text
    # Remove **texto** -> texto
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove *texto* -> texto
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove __texto__ -> texto
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove _texto_ -> texto
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text


def sanitize_ai_response(text):
    """Filtra respostas inadequadas da IA - versão inteligente"""
    if not text: return text
    
    text_lower = text.lower()
    en_words = ['the ', 'and ', 'is ', 'are ', 'was ', 'were ', 'have ', 'has ', 'will ', 'would ', 'could ', 'should ']
    pt_words = ['o ', 'a ', 'os ', 'as ', 'um ', 'uma ', 'é ', 'são ', 'foi ', 'foram ', 'tem ', 'vão ']
    
    en_count = sum(1 for word in en_words if word in text_lower)
    pt_count = sum(1 for word in pt_words if word in text_lower)
    
    # Só bloqueia se tiver MUITO mais inglês que português
    if en_count > pt_count and en_count >= 3:
        return "Desculpe, não entendi sua pergunta. Pode reformular em português?"
    
    return text.strip()


# === FUNÇÃO DE EXTRAÇÃO DE MEMÓRIAS ===
def extract_and_save_memories(user_msg, ai_response, assistant_name):
    """Usa IA para extrair fatos importantes e salvar no banco"""
    print("🔍 [MEMÓRIA] Iniciando extração para:", assistant_name)
    try:
        import json
        
        extraction_prompt = f"""Analise esta conversa e extraia APENAS fatos importantes sobre o usuário (nome, preferências, alergias, pets, trabalho, hobbies, relacionamentos, etc).
Se não houver fatos novos importantes, responda APENAS com a palavra: NENHUMA_MEMORIA

Conversa:
Usuário: {user_msg}
Assistente: {ai_response}

Responda estritamente em formato JSON, sem markdown, sem explicações:
[{{"key": "categoria", "value": "fato"}}]
Exemplo: [{{"key": "alergia", "value": "camarão"}}, {{"key": "pet", "value": "cachorro Thor"}}]"""
        
        print(" [MEMÓRIA] Chamando API...")
        # Usar o mesmo modelo do chat principal para garantir compatibilidade
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": "Você é um extrator de dados JSON. Responda APENAS o JSON ou a palavra NENHUMA_MEMORIA."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        extracted = response.choices[0].message.content.strip()
        print(f"🔍 [MEMÓRIA] Resposta bruta da API: {extracted}")
        
        if extracted and "NENHUMA_MEMORIA" not in extracted:
            extracted = extracted.replace("```json", "").replace("```", "").strip()
            try:
                memories = json.loads(extracted)
                print(f"🔍 [MEMÓRIA] JSON parseado com sucesso: {memories}")
                
                import sqlite3
                conn_mem = sqlite3.connect(DB_PATH, timeout=10)
                cursor_mem = conn_mem.cursor()
                
                for mem in memories:
                    key = str(mem.get("key", "")).strip()
                    value = str(mem.get("value", "")).strip()
                    if key and value:
                        cursor_mem.execute("SELECT id FROM memories WHERE assistant=? AND key=? AND value=?", 
                                         (assistant_name, key, value))
                        if not cursor_mem.fetchone():
                            cursor_mem.execute("INSERT INTO memories (assistant, key, value, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                                             (assistant_name, key, value))
                            print(f"💾 Memória salva: {key} = {value}")
                        else:
                            print(f"⚠️ Memória já existe: {key} = {value}")
                
                conn_mem.commit()
                conn_mem.close()
            except json.JSONDecodeError as e:
                print(f" [MEMÓRIA] Erro ao parsear JSON: {e} | Texto recebido: {extracted}")
        else:
            print("ℹ️ [MEMÓRIA] Nenhuma memória nova identificada pela IA.")
            
    except Exception as e:
        print(f"❌ [MEMÓRIA] Erro geral na extração: {e}")

@app.route('/api/chat', methods=['POST'])
def chat():
    # Padrões de regex definidos fora da string para evitar erros de escape
    PAT_CLEAN_CJK = r'[\u4e00-\u9fff]+'
    PAT_CLEAN_FIX = r'\(wait.*?\)|\(fix:.*?\)'
    PAT_START_PATTERNS = [
        r'(Ol[áa][!.,\s])',
        r'(Para otimizar|Monitore|Instale)',
        r'(Os módulos|A arquitetura)',
        r'(O mercado|Petroleo|Commodities|Dados mostram)',
        r'(Para organizar|Comece definindo|Use listas)',
        r'(Aqui está|Você pode)'
    ]
    PAT_EN_WORDS = r'\b(Didactic|Portuguese|Check|Constraint|Yes|No|Starts|Ends|Imagine|Output|Input|Draft|Note)\b'
    PAT_PT_SENTENCE = r'[A-ZÀ-Ú][^.!?]*[.!?](?:\s*😊)?'
    
    def clean_response(text):
        if not text: return ""
    
        # Remover tags de raciocínio interno (think) se o modelo usar
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
        # Remover marcadores [FIM] se houver
        if "[FIM]" in text:
            text = text.split("[FIM]")[0].strip()
        
        # Remover caracteres CJK (chinês/japonês/coreano) que às vezes vazam do modelo
        text = re.sub(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+', '', text)
        
        return text.strip()

    data = request.get_json()
    print("\n" + "="*40)
    print("🕵️ DEBUG: Dados brutos recebidos do frontend:", data)
    prompt = data.get('message', data.get('prompt', ''))
    history = data.get('history', [])  # Histórico de mensagens do frontend
    print("️ DEBUG: Texto da pergunta (prompt):", repr(prompt))
    assistant = data.get('assistant', 'Ana')
    print(f" Assistente selecionado: '{assistant}'")
    base_prompt = AGENTS_CONFIG.get(assistant, {}).get('prompt', '')
    if not base_prompt:
        print(f"⚠️ AVISO: Prompt vazio para '{assistant}'! Verifique AGENTS_CONFIG")
        print(f"   Chaves disponíveis: {list(AGENTS_CONFIG.keys())}")
    else:
        print(f"✅ Prompt carregado ({len(base_prompt)} chars): {base_prompt[:150]}...")
    print("="*40 + "\n")
    
    # Construir contexto do histórico
    history_context = ""
    if history and len(history) > 0:
        history_context = "\n\n[HISTÓRICO DA CONVERSA - Últimas mensagens]\n"
        for msg in history:
            role = "Usuário" if msg.get('role') == 'user' else "Assistente"
            content = msg.get('content', '')
            history_context += f"{role}: {content}\n"
        history_context += "\n[NOVA MENSAGEM DO USUÁRIO]\n"
    
    system_prompt = base_prompt + history_context + "\n\n[INSTRUÇÕES OBRIGATÓRIAS]\n- Responda SEMPRE em português brasileiro natural e direto.\n- NÃO use inglês, LaTeX ou formatação técnica excessiva.\n- Seja claro, objetivo e conversacional.\n- Considere o histórico da conversa para manter o contexto."

    try:
        cursor = get_cursor()
        cursor.execute("SELECT key, value FROM memories WHERE assistant=?", (assistant,))
        memories = [dict(row) for row in cursor.fetchall()]
        
        if memories:
            memory_text = "\n\n[CONTEXTO DO USUARIO - USE APENAS SE RELEVANTE]\n"
            for mem in memories:
                memory_text += f"- {mem['key']}: {mem['value']}\n"
            system_prompt += memory_text
    except Exception as e:
        print(f"Aviso: Erro ao carregar memorias: {e}")
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        , reasoning_effort="none")
        ai_response = response.choices[0].message.content
        cleaned = clean_response(ai_response)
        cleaned = clean_markdown(cleaned)  # Remove formatação markdown
        
        # EXTRAIR E SALVAR MEMÓRIAS
        # extract_and_save_memories(prompt, cleaned, assistant)  # Desativado temporariamente para estabilidade (V2.1)
        
        try:
            conn_hist = sqlite3.connect(DB_PATH, timeout=30)
            conn_hist.execute("PRAGMA busy_timeout=30000")
            conn_hist.execute("PRAGMA journal_mode=WAL")
            conn_hist.execute("INSERT INTO messages (assistant, user_msg, ai_response) VALUES (?, ?, ?)",
                     (assistant, prompt, cleaned))
            conn_hist.commit()
            conn_hist.close()
        except Exception as e:
            pass  # Silencioso - não afeta o chat

            
                        # === ATUALIZAÇÃO DE MÉTRICAS (Simplificada) ===
        # Nota: Métricas são opcionais. Se falhar, não afeta o chat.
        try:
            import sqlite3
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Conexão isolada com timeout alto
            conn_temp = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
            conn_temp.execute("PRAGMA busy_timeout=30000")
            conn_temp.execute("PRAGMA journal_mode=WAL")
            
            # Verifica se tabela existe
            cursor = conn_temp.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assistants'")
            if cursor.fetchone():
                conn_temp.execute(
                    "UPDATE assistants SET last_interaction=?, message_count=COALESCE(message_count, 0) + 1 WHERE name=?",
                    (now, assistant)
                )
                print(f"✅ Métricas: {assistant}")
            else:
                print(f"ℹ️ Tabela assistants não existe, pulando métricas")
            
            conn_temp.close()
        except Exception as e:
            # Silencioso - não afeta o chat
            pass
        # ================================
        return jsonify({"response": force_portuguese_response(cleaned)})
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return jsonify({"error": str(e)}), 500





@app.route('/api/files/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        cursor = get_cursor()
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "Arquivo nao encontrado"}), 404

@app.route('/api/history/save', methods=['POST'])
def save_history():
    cursor = get_cursor()
    data = request.get_json()
    try:
        cursor = get_cursor()
        cursor.execute("INSERT INTO messages (assistant, user_msg, ai_response) VALUES (?, ?, ?)",
                 (data.get('assistant','Ana'), data.get('user_msg',''), data.get('ai_response','')))
        return jsonify({"status": "saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/<assistant>', methods=['GET'])
def get_history(assistant):
    try:
        cursor = get_cursor()
        cursor = get_cursor()
        cursor.execute("SELECT * FROM messages WHERE assistant=? ORDER BY timestamp DESC LIMIT 50", (assistant,))
        return jsonify({"messages": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history/clear/<assistant>', methods=['DELETE'])
def clear_history(assistant):
    try:
        cursor = get_cursor()
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/save', methods=['POST'])
def save_memory():
    cursor = get_cursor()
    data = request.get_json()
    try:
        cursor = get_cursor()
        cursor.execute("INSERT OR REPLACE INTO memories (assistant, key, value) VALUES (?, ?, ?)",
                 (data.get('assistant','Ana'), data.get('key',''), data.get('value','')))
        return jsonify({"status": "saved", "key": data.get('key')}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/get/<assistant>', methods=['GET'])
def get_memories(assistant):
    try:
        cursor = get_cursor()
        cursor = get_cursor()
        cursor.execute("SELECT * FROM memories WHERE assistant=? ORDER BY timestamp DESC", (assistant,))
        return jsonify({"memories": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/delete/<assistant>/<key>', methods=['DELETE'])
def delete_memory(assistant, key):
    try:
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def set_profile_route(profile_name):
    cursor = get_cursor()
    global CURRENT_PROFILE
    valid = ['personal', 'devops', 'enterprise']
    if profile_name not in valid:
        return jsonify({"error": "Perfil inválido"}), 400
    
    global AGENTS_CONFIG
    
    return jsonify({"status": "ok", "profile": profile_name}), 200

def get_dock_assistants():
    cursor = get_cursor()
    profile = globals().get('CURRENT_PROFILE', 'personal')
    try:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM assistants WHERE is_active=1 AND profile=? ORDER BY name", (profile,))
        rows = [dict(row) for row in cursor.fetchall()]
        config = {}
        for agent in rows:
            config[agent['name']] = {
                'prompt': agent['system_prompt'],
                'display_name': agent['display_name'],
                'color': agent['color'],
                'category': agent['category']
            }
        return jsonify({"assistants": config, "profile": profile}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/profile/set/<profile_name>', methods=['POST'])
def set_profile_route(profile_name):
    cursor = get_cursor()
    global CURRENT_PROFILE, AGENTS_CONFIG
    valid = ['personal', 'devops', 'enterprise']
    if profile_name not in valid:
        return jsonify({"error": "Perfil inválido"}), 400
    CURRENT_PROFILE = profile_name
    AGENTS_CONFIG = load_agents_config(CURRENT_PROFILE)
    return jsonify({"status": "ok", "profile": profile_name}), 200

def get_all_assistants():
    try:
        cursor = get_cursor()
        cursor = get_cursor()
        cursor.execute("SELECT * FROM assistants WHERE is_active=1 ORDER BY name")
        rows = [dict(row) for row in cursor.fetchall()]
        config = {}
        for agent in rows:
            config[agent['name']] = {
                'prompt': agent.get('system_prompt', ''),
                'display_name': agent.get('display_name', agent['name']),
                'color': agent.get('color', '#7c4dff'),
                'category': agent.get('category', 'general')
            }
        return jsonify({"assistants": config}), 200
    except Exception as e:
        print(f"ERRO CRÍTICO EM /api/assistants: {e}")
        return jsonify({"error": str(e), "assistants": {}}), 500

def toggle_assistant(name):
    try:
        cursor = get_cursor()
        
        # Busca estado atual
        cursor = get_cursor()
        cursor.execute("SELECT is_active FROM assistants WHERE name=?", (name,))
        row = c.fetchone()
        
        if not row:
            return jsonify({"error": "Assistente não encontrado"}), 404
            
        new_status = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE assistants SET is_active=? WHERE name=?", (new_status, name))
        
        status_text = 'activated' if new_status == 1 else 'deactivated'
        return jsonify({"status": status_text, "is_active": new_status}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def delete_assistant(name):
    try:
        cursor = get_cursor()
        cursor = get_cursor()
        cursor.execute("DELETE FROM assistants WHERE name=?", (name,))
        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def get_assistant_metrics(name):
    try:
        cursor = get_cursor()
        cursor = get_cursor()
        cursor.execute("SELECT last_interaction, message_count FROM assistants WHERE name=?", (name,))
        row = c.fetchone()
        
        if not row:
            return jsonify({"error": "Assistente não encontrado"}), 404
            
        return jsonify({
            "last_interaction": row["last_interaction"],
            "message_count": row["message_count"] or 0
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# === ROTAS DE GERENCIAMENTO DE ARQUIVOS ===





# === GERENCIAMENTO DE ARQUIVOS (VERSÃO ÚNICA) ===





# === ROTAS DE ARQUIVOS (ÚNICAS) ===




@app.route('/api/files/list', methods=['GET'])
def api_list_files():
    try:
        files = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                # Ignorar arquivos ocultos do sistema, mas permitir nossa lógica de pasta
                if filename.startswith('.') and filename != '.folder':
                    continue
                
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                stat = os.stat(filepath)
                is_dir = os.path.isdir(filepath)
                
                files.append({
                    "name": filename,
                    "size": stat.st_size if not is_dir else 0,
                    "is_dir": is_dir  # <-- O segredo que o frontend precisa!
                })
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
def api_upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nome vazio"}), 400
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({"status": "success", "filename": file.filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files/create', methods=['POST'])
def api_create_file():
    """Cria um novo arquivo (ou simula pasta via arquivo .folder)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        filename = data.get('filename', '').strip()
        content_file = data.get('content', '')
        
        if not filename:
            return jsonify({"error": "Nome do arquivo obrigatório"}), 400
        
        # Segurança: evitar path traversal
        if '..' in filename or filename.startswith('/'):
            return jsonify({"error": "Nome de arquivo inválido"}), 400
        
        # Criar o arquivo na pasta de uploads
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Criar subpastas se necessário (ex: "MinhaPasta/.folder")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_file)
        
        return jsonify({
            "success": True, 
            "message": f"Arquivo '{filename}' criado com sucesso",
            "filename": filename
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/files/open', methods=['GET'])
def api_open_file():
    filename = request.args.get('name')
    if not filename or '..' in filename or '/' in filename:
        return jsonify({"error": "Arquivo inválido"}), 400
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 404






    except Exception:
        pass












# === ROTAS DE ASSISTENTES (JSON-BASED) ===
def list_assistants():
    try:
        fpath = os.path.join(os.path.dirname(__file__), 'assistants.json')
        if not os.path.exists(fpath):
            return jsonify({'assistants': {}}), 200
        
        with open(fpath, 'r') as f:
            data = json.load(f)
        
        result = {}
        for item in data:
            name = item.get('name', str(len(result)))
            item['active'] = True
            result[name] = item
        
        return jsonify({'assistants': result}), 200
    except Exception as e:
        print("ERRO LIST:", e)
        return jsonify({'assistants': {}, 'error': str(e)}), 200

def create_assistant():
    try:
        data = request.get_json(silent=True)
        if not data: return jsonify({'error': 'JSON invalido'}), 400
        
        name = str(data.get('name', '')).strip()
        specialty = str(data.get('specialty', '')).strip()
        prompt = str(data.get('prompt', '')).strip()
        
        if not name or not specialty:
            return jsonify({'error': 'Nome e especialidade obrigatorios'}), 400
        
        fpath = os.path.join(os.path.dirname(__file__), 'assistants.json')
        assistants = []
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r') as f:
                    txt = f.read().strip()
                    if txt: assistants = json.loads(txt)
            except: assistants = []
        
        new_asst = {
            'id': str(len(assistants) + 1),
            'name': name,
            'specialty': specialty.upper(),
            'prompt': prompt if prompt else ('Especialista em ' + specialty),
            'color': '#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]),
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        assistants.append(new_asst)
        with open(fpath, 'w') as f:
            json.dump(assistants, f, indent=2, ensure_ascii=False)
        
        print("Assistente criado:", name)
        return jsonify({'status': 'success', 'assistant': new_asst}), 201
    except Exception as e:
        print("ERRO CREATE:", e)
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500
# ==========================================



@app.route('/api/assistants')
def list_assistants():
    """Rota isolada: lê apenas de assistants.json, retorna lista"""
    import json as _json
    import os as _os
    
    try:
        fpath = _os.path.join(_os.path.dirname(__file__), 'assistants.json')
        if not _os.path.exists(fpath):
            return jsonify([]), 200
        
        with open(fpath, 'r') as f:
            data = _json.load(f)
        
        # Filtrar apenas assistentes ativos
        active_assistants = [item for item in data if item.get('active', False)]
        
        return jsonify(active_assistants), 200
        
    except Exception as e:
        print("ERRO LIST:", e)
        return jsonify([]), 200



@app.route('/api/assistants/<string:name>/toggle', methods=['POST'])
def toggle_assistant(name):
    try:
        import json
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assistants.json')
        
        if not os.path.exists(fpath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        target = None
        for item in data:
            if item.get('name') == name:
                target = item
                break
        
        if not target:
            return jsonify({'error': f'Assistente {name} não encontrado'}), 404
        
        target['active'] = not target.get('active', True)
        
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Toggle {name}: {'Ativo' if target['active'] else 'Inativo'}")
        return jsonify({'status': 'success', 'active': target['active']}), 200
        
    except Exception as e:
        print(f"❌ Erro toggle: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/assistants/<string:name>', methods=['DELETE'])
def delete_assistant(name):
    try:
        import json
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assistants.json')
        
        if not os.path.exists(fpath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        new_data = [item for item in data if item.get('name') != name]
        
        if len(new_data) == len(data):
            return jsonify({'error': f'Assistente {name} não encontrado'}), 404
        
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Delete {name}")
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Erro delete: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500




@app.route('/api/assistants/create', methods=['POST'])
def handle_create_assistant():
    """Rota dedicada para criação - nome único para evitar conflitos"""
    try:
        import json, random, os
        from datetime import datetime
        
        if not request.is_json:
            return jsonify({'error': 'Content-Type deve ser application/json'}), 400
        
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'JSON inválido'}), 400
        
        name = str(data.get('name', '')).strip()
        specialty = str(data.get('specialty', '')).strip()
        prompt = str(data.get('prompt', '')).strip()
        
        if not name or not specialty:
            return jsonify({'error': 'Nome e especialidade obrigatórios'}), 400
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assistants_file = os.path.join(base_dir, 'assistants.json')
        
        assistants = []
        if os.path.exists(assistants_file):
            try:
                with open(assistants_file, 'r', encoding='utf-8') as f:
                    txt = f.read().strip()
                    if txt: assistants = json.loads(txt)
            except: assistants = []
        
        new_asst = {
            'id': str(len(assistants) + 1),
            'name': name,
            'specialty': specialty.upper(),
            'prompt': prompt if prompt else f'Especialista em {specialty}',
            'color': '#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]),
            'created_at': datetime.now().isoformat(),
            'active': True,
            'profile': 'devops',
            'icon': '🤖'
        }
        
        assistants.append(new_asst)
        
        with open(assistants_file, 'w', encoding='utf-8') as f:
            json.dump(assistants, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Assistente criado: {name}")
        return jsonify({'status': 'success', 'assistant': new_asst}), 201
        
    except Exception as e:
        import traceback
        print(f"❌ ERRO CREATE: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ==========================================================
# ROTAS DE NAVEGAÇÃO DA DOCK (Inseridas antes do app.run)
# ==========================================================
@app.route('/dashboard')
def dashboard_page():
    # Passar listas vazias como padrão para evitar erro "Undefined is not JSON serializable" no template
    return render_template('dashboard.html', datas_grafico=[], valores_grafico=[])

@app.route('/arquivos')
def arquivos_page():
    return render_template('arquivos.html')









@app.route('/perfil')
def perfil_page():
    # Segurança: Usa a sessão do Flask. Fallback seguro para desenvolvimento local.
    current_user = session.get('user', {
        'id': 1, 
        'username': 'luperesil', 
        'email': 'luperesil@thinkinos.local',
        'role': 'Administrador'
    })
    return render_template('perfil.html', user=current_user)

@app.route('/api/perfil/update', methods=['POST'])
def update_profile():
    # Segurança: Validação rigorosa de entrada (Sanitização)
    data = request.get_json()
    new_username = str(data.get('username', '')).strip()
    
    # Previne injeção e limita tamanho
    if not new_username or len(new_username) < 3 or len(new_username) > 30:
        return jsonify({"error": "Nome deve ter entre 3 e 30 caracteres."}), 400
    
    # Remove caracteres perigosos
    import re
    if not re.match(r"^[a-zA-Z0-9_\s\-]+$", new_username):
        return jsonify({"error": "Nome contém caracteres inválidos."}), 400

    # Atualiza a sessão (em um sistema real, atualizaria o banco de dados aqui)
    if 'user' not in session:
        session['user'] = {}
    session['user']['username'] = new_username
    session.modified = True
    
    return jsonify({"success": True, "username": new_username})

@app.route('/api/perfil/delete_data', methods=['POST'])
def delete_user_data():
    # LGPD: Direito ao esquecimento. Limpa dados do usuário atual.
    try:
        user_id = session.get('user', {}).get('id', 1)
        cursor = get_cursor()
        
        # Limpa histórico de mensagens e memórias associadas a este usuário/perfil
        cursor.execute("DELETE FROM messages WHERE profile=?", (CURRENT_PROFILE,))
        cursor.execute("DELETE FROM memories WHERE profile=?", (CURRENT_PROFILE,))
        
        # Limpa a sessão
        session.clear()
        
        return jsonify({"success": True, "message": "Dados excluídos com sucesso."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/configuracoes')
def configuracoes_page():
    return render_template('configuracoes.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html')


# === API DE PERFIL E PRIVACIDADE ===
def api_update_perfil():
    try:
        data = request.get_json()
        new_username = str(data.get('username', '')).strip()
        
        # Validação de segurança
        import re
        if not new_username or len(new_username) < 3 or len(new_username) > 50:
            return jsonify({"error": "Nome inválido (3-50 caracteres)."}), 400
        
        # Sanitização básica
        if not re.match(r"^[a-zA-Z0-9_\s\-\.]+$", new_username):
            return jsonify({"error": "Caracteres especiais não permitidos."}), 400

        # Atualizar na sessão
        if 'user' not in session:
            session['user'] = {'id': 1, 'username': 'user', 'email': ''}
        
        session['user']['username'] = new_username
        session.modified = True
        
        print(f"✅ Nome atualizado para: {new_username}")
        return jsonify({"success": True, "username": new_username})
    except Exception as e:
        print(f" Erro ao atualizar perfil: {e}")
        return jsonify({"error": str(e)}), 500

def api_delete_perfil_data():
    try:
        cursor = get_cursor()
        # Deletar dados do perfil atual
        cursor.execute("DELETE FROM messages WHERE profile=?", (CURRENT_PROFILE,))
        cursor.execute("DELETE FROM memories WHERE profile=?", (CURRENT_PROFILE,))
        
        session.clear()
        print("✅ Dados do usuário excluídos.")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Erro ao excluir dados: {e}")
        return jsonify({"error": str(e)}), 500



# === API DE CONFIGURAÇÕES (GESTÃO) ===
@app.route('/api/config', methods=['GET'])
def get_config():
    load_dotenv()
    # Retorna apenas se a chave está configurada (mascarada) por segurança
    groq_key = os.getenv('GROQ_API_KEY', '')
    openai_key = os.getenv('OPENAI_API_KEY', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    google_key = os.getenv('GOOGLE_API_KEY', '')
    
    return jsonify({
        'groq_api_key': '***' + groq_key[-4:] if len(groq_key) > 4 else '',
        'groq_api_key_configured': bool(groq_key),
        'openai_api_key': '***' + openai_key[-4:] if len(openai_key) > 4 else '',
        'openai_api_key_configured': bool(openai_key),
        'anthropic_api_key': '***' + anthropic_key[-4:] if len(anthropic_key) > 4 else '',
        'anthropic_api_key_configured': bool(anthropic_key),
        'google_api_key': '***' + google_key[-4:] if len(google_key) > 4 else '',
        'google_api_key_configured': bool(google_key),
    })

def save_config():
    try:
        data = request.get_json()
        env_file = find_dotenv()
        
        if data.get('groq_api_key'):
            set_key(env_file, 'GROQ_API_KEY', data['groq_api_key'].strip())
        if data.get('openai_api_key'):
            set_key(env_file, 'OPENAI_API_KEY', data['openai_api_key'].strip())
        if data.get('anthropic_api_key'):
            set_key(env_file, 'ANTHROPIC_API_KEY', data['anthropic_api_key'].strip())
        if data.get('google_api_key'):
            set_key(env_file, 'GOOGLE_API_KEY', data['google_api_key'].strip())
            
        # Recarrega as variáveis de ambiente
        load_dotenv(override=True)
        
        # Atualiza o cliente Groq se a chave mudou
        global client
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/logout')
def logout():
    """Faz logout do usuário e redireciona para desktop"""
    session.clear()
    return redirect('/desktop')

# --- Rotas de Navegação da Dock ---


def arquivos_page():
    return render_template('arquivos.html')










@app.route('/api/assistants', methods=['POST'])
def create_assistant():
    try:
        data = request.json
        ASSISTANTS_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assistants.json")
        
        with open(ASSISTANTS_JSON, 'r', encoding='utf-8') as f:
            assistentes = json.load(f)
        
        # Gera novo ID baseado no maior ID existente
        max_id = max([int(a.get('id', 0)) for a in assistentes], default=0)
        new_id = str(max_id + 1)
        
        new_assistant = {
            "id": new_id,
            "name": data.get('name', '').lower().replace(' ', '_'),
            "display_name": data.get('display_name', ''),
            "specialty": data.get('specialty', ''),
            "description": data.get('description', ''),
            "color": data.get('color', '#1CC54B'),
            "prompt": data.get('prompt', ''),
            "active": True,
            "profile": data.get('profile', 'personal'),
            "icon": "🤖",
            "message_count": 0,
            "active_time_seconds": 0,
            "last_active": None
        }
        
        assistentes.append(new_assistant)
        
        with open(ASSISTANTS_JSON, 'w', encoding='utf-8') as f:
            json.dump(assistentes, f, indent=2, ensure_ascii=False)
            
        return jsonify({"success": True, "assistant": new_assistant})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# === API: EDITAR ASSISTENTE EXISTENTE ===
@app.route('/api/assistants/update', methods=['POST'])
def api_update_assistant():
    import json
    import sqlite3
    
    try:
        data = request.get_json()
        name_id = str(data.get('name', '')).strip()
        display_name = str(data.get('display_name', name_id)).strip()
        specialty = str(data.get('specialty', 'Geral')).strip()
        color = str(data.get('color', '#8b5cf6')).strip()
        prompt = str(data.get('prompt', '')).strip()

        if not name_id:
            return jsonify({'success': False, 'error': 'ID do assistente é obrigatório.'}), 400

        # Conectar com timeout para evitar "database is locked"
        db_path = os.path.join(os.path.dirname(__file__), 'thinkinos.db')
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE assistants 
            SET display_name=?, category=?, color=?, system_prompt=? 
            WHERE name=?
        """, (display_name, specialty, color, prompt, name_id))
        conn.commit()
        conn.close()

        # Atualizar o arquivo assistants.json
        json_path = os.path.join(os.path.dirname(__file__), 'assistants.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                assistants_list = json.load(f)
            
            for a in assistants_list:
                if a.get('name') == name_id:
                    a['display_name'] = display_name
                    a['specialty'] = specialty
                    a['color'] = color
                    a['prompt'] = prompt
                    break
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(assistants_list, f, indent=2, ensure_ascii=False)

        return jsonify({'success': True, 'message': f'Assistente {display_name} atualizado com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
