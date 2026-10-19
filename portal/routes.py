from flask import render_template, jsonify, abort
from portal import portal_bp
import os
import json
from datetime import datetime

# Dados simulados (podem ser movidos para JSON/DB no futuro)
BLOG_POSTS = {
    'thinkinos-v2': {
        'title': '🎉 Quesil Core v2.0: O Futuro da IA Pessoal',
        'date': '8 de Outubro, 2026',
        'category': 'Lançamento',
        'content': '''
            <p>O Quesil Core v2.0 representa um marco na evolução dos sistemas operacionais pessoais com Inteligência Artificial. Nesta versão, focamos em estabilidade, segurança e usabilidade.</p>
            <h3>Principais Novidades:</h3>
            <ul>
                <li><strong>Deploy em Produção:</strong> Arquitetura profissional com Nginx, Gunicorn e Systemd.</li>
                <li><strong>HTTPS Nativo:</strong> Suporte completo a certificados SSL locais válidos via mkcert.</li>
                <li><strong>Gerenciador de Arquivos 2.0:</strong> Interface em grid, upload/download e edição de código integrada.</li>
                <li><strong>Dashboard de Métricas:</strong> Monitoramento em tempo real de CPU, RAM e Disco.</li>
            </ul>
            <p>O objetivo é claro: fornecer um ambiente onde a IA não é apenas um chat, mas o núcleo de todo o sistema operacional.</p>
        '''
    },
    'ia-2026': {
        'title': '🤖 O Estado da IA em 2026: Modelos Locais e Privacidade',
        'date': '7 de Outubro, 2026',
        'category': 'Mundo da IA',
        'content': '''
            <p>O ano de 2026 consolidou uma tendência importante: a volta da privacidade e o poder dos modelos de IA rodando localmente ou em ambientes controlados.</p>
            <h3>A Ascensão da IA Pessoal</h3>
            <p>Enquanto grandes modelos de linguagem dominam a nuvem, há uma demanda crescente por assistentes que entendam o contexto pessoal do usuário sem vazar dados. O Quesil Core nasce exatamente para preencher essa lacuna, atuando como uma camada de orquestração entre o usuário e a IA.</p>
            <h3>Por que isso importa?</h3>
            <p>Ter seus dados, arquivos e histórico de conversas processados em seu próprio hardware (ou em um servidor de sua confiança) garante que você seja o único dono da sua informação. O futuro da IA é personalizado, e o Quesil Core é a fundação para isso.</p>
        '''
    }
}

TUTORIALS = {
    'ide-ia': {
        'title': '💻 Dominando o IDE Integrado com IA',
        'level': 'Intermediário',
        'content': '''
            <p>O Quesil Core não é apenas um lugar para conversar com IAs, é um ambiente de desenvolvimento completo. O nosso Editor de Código (baseado no Monaco Editor) possui integração profunda com os assistentes.</p>
            
            <h3>1. Abrindo o Editor</h3>
            <p>Você pode acessar o editor de duas formas:</p>
            <ul>
                <li>Clicando no ícone <strong>&lt;/&gt; Editor</strong> na Dock inferior.</li>
                <li>Clicando diretamente em qualquer arquivo de código (`.py`, `.js`, `.html`, `.txt`) no <strong>Gerenciador de Arquivos</strong>.</li>
            </ul>

            <h3>2. O Poder da IA no Código</h3>
            <p>Com o arquivo aberto, você pode chamar o assistente <strong>Mentor Python</strong> ou <strong>Dev</strong> para:</p>
            <ul>
                <li>Explicar trechos de código complexos.</li>
                <li>Sugerir refatorações para melhorar a performance.</li>
                <li>Gerar testes unitários automaticamente.</li>
                <li>Identificar e corrigir erros de sintaxe (como o temido `SyntaxError`).</li>
            </ul>

            <h3>3. Dica Pro: Live Preview</h3>
            <p>Se você estiver editando um arquivo HTML/CSS, o Quesil Core possui um recurso de <strong>Live Preview</strong>. Salve o arquivo e veja as alterações refletidas instantaneamente no navegador, sem precisar recarregar a página manualmente!</p>
            
            <div style="background: var(--darker); padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; border-left: 4px solid var(--primary);">
                <strong>💡 Exercício Prático:</strong><br>
                1. Crie um arquivo chamado `teste.py` no Gerenciador de Arquivos.<br>
                2. Digite um código Python simples com um erro proposital.<br>
                3. Abra o chat com o assistente "Dev" e peça: "Analise meu código teste.py e corrija o erro".<br>
                4. Veja a mágica acontecer!
            </div>
        '''
    },
    'arquivos': {
        'title': '📁 Dominando o Gerenciador de Arquivos',
        'level': 'Iniciante',
        'content': '''
            <p>O Gerenciador de Arquivos do Quesil Core foi projetado para ser intuitivo, seguro e poderoso.</p>
            <h3>Funcionalidades Principais:</h3>
            <ul>
                <li><strong>Upload Inteligente:</strong> Arraste e solte ou use o botão de upload. Arquivos de até 50MB são suportados.</li>
                <li><strong>Visualização em Grid:</strong> Ícones grandes e claros para cada tipo de arquivo (🐍 para Python, 📘 para Documentos, 🖼️ para Imagens).</li>
                <li><strong>Edição Segura:</strong> Arquivos de texto e código abrem no editor integrado. Arquivos binários (como .pdf ou .doc) mostram apenas a opção de Download, evitando erros de renderização.</li>
                <li><strong>Organização:</strong> Crie pastas para manter seus projetos e documentos organizados.</li>
            </ul>
        '''
    }
}

DOCS = {
    'instalacao': {
        'title': '🚀 Guia de Instalação',
        'content': '''
            <h3>Requisitos do Sistema</h3>
            <ul>
                <li>Sistema Operacional: Linux (Ubuntu, Pop!_OS, Linux Mint, etc.)</li>
                <li>Python 3.8 ou superior</li>
                <li>Docker (opcional, para recursos de virtualização)</li>
                <li>2GB de RAM livres (mínimo)</li>
            </ul>
            
            <h3>Passo a Passo</h3>
            <ol>
                <li>Clone o repositório: <code>git clone https://github.com/seu-usuario/thinkinos-platform.git</code></li>
                <li>Acesse a pasta: <code>cd thinkinos-platform</code></li>
                <li>Crie o ambiente virtual: <code>python3 -m venv venv</code></li>
                <li>Ative o ambiente: <code>source venv/bin/activate</code></li>
                <li>Instale as dependências: <code>pip install -r requirements.txt</code></li>
                <li>Configure suas variáveis de ambiente (API keys) no arquivo <code>.env</code>.</li>
                <li>Inicie o servidor de desenvolvimento: <code>python3 app.py</code></li>
            </ol>
            
            <h3>Deploy em Produção</h3>
            <p>Para uso contínuo, recomendamos a configuração com Nginx e Gunicorn via Systemd, conforme detalhado na nossa documentação de <a href="#" style="color: var(--primary);">Arquitetura</a>.</p>
        '''
    }
}

@portal_bp.route('/')
def portal_home():
    return render_template('portal/home.html')

@portal_bp.route('/docs')
def docs():
    return render_template('portal/docs.html', docs=DOCS)

@portal_bp.route('/docs/<topic>')
def doc_detail(topic):
    doc = DOCS.get(topic)
    if not doc:
        abort(404)
    return render_template('portal/doc_detail.html', doc=doc, topic=topic)

@portal_bp.route('/blog')
def blog():
    return render_template('portal/blog.html', posts=BLOG_POSTS)

@portal_bp.route('/blog/<post_id>')
def blog_post(post_id):
    post = BLOG_POSTS.get(post_id)
    if not post:
        abort(404)
    return render_template('portal/blog_detail.html', post=post, post_id=post_id)

@portal_bp.route('/tutorials')
def tutorials():
    return render_template('portal/tutorials.html', tutorials=TUTORIALS)

@portal_bp.route('/tutorials/<tutorial_id>')
def tutorial_detail(tutorial_id):
    tutorial = TUTORIALS.get(tutorial_id)
    if not tutorial:
        abort(404)
    return render_template('portal/tutorial_detail.html', tutorial=tutorial, tutorial_id=tutorial_id)

@portal_bp.route('/plugins')
def plugins():
    return render_template('portal/plugins.html')

@portal_bp.route('/community')
def community():
    return render_template('portal/community.html')

@portal_bp.route('/contribute')
def contribute():
    return render_template('portal/contribute.html')

@portal_bp.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'uptime': 'running',
        'timestamp': datetime.now().isoformat()
    })
