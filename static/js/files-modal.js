
// === THINKINOS FILES MODAL - VERSÃO FINAL LIMPA ===
(function() {

// === INJEÇÃO SÍNCRONA DO MODAL DE CRIAÇÃO (EXECUTA PRIMEIRO) ===
(function injectCreateModal() {
    if(document.getElementById('create-assistant-modal')) return; // Já existe
    
    const html = `<div id="create-assistant-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:100000;">
        <div style="position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); 
                    background:#1a1a1a; border-radius:16px; padding:24px; 
                    width:450px; max-width:90vw; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                <h2 style="margin:0; color:white; font-size:18px;">✨ Novo Assistente</h2>
                <button id="close-create-modal" style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">&times;</button>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px;">
                <input type="text" id="new-assistant-name" placeholder="Nome (ex: Revisor de Código)" 
                       style="padding:10px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.1); 
                              border-radius:8px; color:white; outline:none;">
                <input type="text" id="new-assistant-specialty" placeholder="Especialidade (ex: Python DevOps)" 
                       style="padding:10px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.1); 
                              border-radius:8px; color:white; outline:none;">
                <textarea id="new-assistant-prompt" placeholder="Prompt base (opcional)..." rows="3"
                          style="padding:10px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.1); 
                                 border-radius:8px; color:white; resize:none; outline:none;"></textarea>
                <button id="btn-save-assistant" style="padding:12px; background:linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); 
                               border:none; border-radius:8px; color:white; font-weight:bold; cursor:pointer; margin-top:8px;">
                    Criar Assistente
                </button>
            </div>
            <p id="create-status" style="text-align:center; margin-top:12px; font-size:12px; min-height:16px;"></p>
        </div>
    </div>`;
    
    document.body.insertAdjacentHTML('beforeend', html);
    
    // Eventos do modal
    document.getElementById('close-create-modal').onclick = () => 
        document.getElementById('create-assistant-modal').style.display = 'none';
        
    document.getElementById('btn-save-assistant').onclick = async () => {
        const name = document.getElementById('new-assistant-name').value.trim();
        const spec = document.getElementById('new-assistant-specialty').value.trim();
        const prompt = document.getElementById('new-assistant-prompt').value.trim();
        const status = document.getElementById('create-status');
        
        if(!name || !spec) { status.innerText = '️ Preencha nome e especialidade'; status.style.color='#fbbf24'; return; }
        
        status.innerText = '⏳ Criando...'; status.style.color='#60a5fa';
        
        try {
            const res = await fetch('/api/assistants/create', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({name, specialty:spec, prompt})
            });
            const data = await res.json();
            if(res.ok) { status.innerText='✅ Criado!'; status.style.color='#4ade80'; setTimeout(()=>location.reload(),800); }
            else { status.innerText='❌ '+data.error; status.style.color='#ef4444'; }
        } catch(e) { status.innerText='❌ Erro de conexão'; status.style.color='#ef4444'; }
    };
    
    console.log('✅ Modal de criação INJETADO SINCRONAMENTE!');

    // Conecta botão "+" (v6 - Pós-injeção síncrona)
    setTimeout(() => {
        const items = document.querySelectorAll('.dock-item');
        if(items.length > 0) {
            const last = items[items.length-1];
            if(!/[a-zA-Z]/.test(last.innerText||'')) {
                last.addEventListener('click', (e) => {
                    e.preventDefault(); e.stopPropagation();
                    const m = document.getElementById('create-assistant-modal');
                    if(m) { m.style.display='block'; console.log('✨ Modal ABERTO!'); }
                    else { console.error('❌ Modal ausente!'); location.reload(); }
                });
                console.log('✅ Botão + conectado!');
            }
        }
    }, 600);

})();
// ============================================================

    console.log(' Files Modal vFINAL carregado');
    
    // Funções definidas PRIMEIRO
    function openFilesModal() {
        const m = document.getElementById('fm-modal-files');
        if(m) {
            m.style.display = 'block';
            loadFilesList();
        }
    }

    async function loadFilesList() {
        const listEl = document.getElementById('fm-list-files');
        if(!listEl) return;
        
        try {
            const res = await fetch('/api/files/list');
            const data = await res.json();
            
            let html = '';
            if(data.files && data.files.length > 0) {
                data.files.forEach(f => {
                    const sizeKB = (f.size / 1024).toFixed(1);
                    const safeName = f.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                    const ext = f.name.split('.').pop().toLowerCase();
                    const action = ['pdf','png','jpg','jpeg','gif','webp','txt','md','html'].includes(ext) ? 'viewFile' : 'forceDownload';
                    
                    html += `<div onclick="${action}('${safeName}', '${safeName}')" 
                             style="display:flex; justify-content:space-between; padding:10px; margin-bottom:6px; 
                                    background:rgba(255,255,255,0.03); border-radius:8px; cursor:pointer;">
                                <span style="color:white;">${f.name}</span>
                                <span style="color:rgba(255,255,255,0.4); font-size:11px;">${sizeKB} KB</span>
                            </div>`;
                });
            } else {
                html = '<p style="text-align:center; opacity:0.5; padding:20px;">Nenhum arquivo.</p>';
            }
            listEl.innerHTML = html;
        } catch(e) { 
            listEl.innerHTML = '<p style="color:red; text-align:center;">Erro ao carregar.</p>'; 
        }
    }

    window.viewFile = function(name) { 
        window.open('/api/files/open?name=' + encodeURIComponent(name), '_blank'); 
    };
    
    window.forceDownload = function(urlName, displayName) {
        const link = document.createElement('a');
        link.href = '/api/files/open?name=' + encodeURIComponent(urlName);
        link.download = displayName;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Injeta Modal (ID fixo para evitar problemas de UID dinâmico)
    const modalHTML = `
    <div id="fm-modal-files" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:99999;">
        <div style="position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); 
                    background:#1a1a1a; border-radius:16px; padding:24px; 
                    width:500px; max-width:90vw; display:flex; flex-direction:column;">
            
            <div style="display:flex; justify-content:space-between; margin-bottom:16px;">
                <h2 style="margin:0; color:white;">📂 Gerenciador de Arquivos</h2>
                <button onclick="document.getElementById('fm-modal-files').style.display='none'" 
                        style="background:none; border:none; color:white; font-size:20px; cursor:pointer;">&times;</button>
            </div>
            
            <div style="display:flex; gap:8px; margin-bottom:16px;">
                <input type="text" id="fm-path-input" placeholder="Cole caminho..." 
                       style="flex:1; padding:10px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.1); 
                              border-radius:8px; color:white;">
                <button id="fm-btn-upload" style="padding:10px 18px; background:#4ade80; border:none; 
                               border-radius:8px; color:#064e3b; font-weight:bold; cursor:pointer;">Enviar</button>
            </div>
            
            <div id="fm-list-files" style="color:white; overflow-y:auto; max-height:300px;"></div>
        </div>
    </div>`;
    
    // Remove modal antigo se existir
    const old = document.getElementById('fm-modal-files');
    if(old) old.remove();
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Evento Upload
    document.getElementById('fm-btn-upload').addEventListener('click', async () => {
        const path = document.getElementById('fm-path-input').value.trim();
        if(!path) return;
        
        try {
            const res = await fetch(path);
            const blob = await res.blob();
            const fd = new FormData();
            fd.append('file', blob, path.split('/').pop());
            
            await fetch('/api/files/upload', {method:'POST', body:fd});
            loadFilesList();
            document.getElementById('fm-path-input').value = '';
        } catch(e) { alert('Erro: ' + e.message); }
    });

    // Expõe GLOBALMENTE
    window.openFilesModal = openFilesModal;
    window.loadFilesList = loadFilesList;
    console.log('✅ Funções globais definidas!');

    // Conecta Dock
    setTimeout(() => {
        document.querySelectorAll('.dock-item').forEach(el => {
            if(el.innerText.includes('Arquivos') && !el.innerText.includes('+')) {
                el.onclick = (e) => { e.preventDefault(); window.openFilesModal(); };
                console.log('✅ Dock conectada!');
            }
        });
    }, 500);


    


    


    


    


    


    // Conecta botão "+" (v6 - Pós-injeção síncrona)
    setTimeout(() => {
        const items = document.querySelectorAll('.dock-item');
        if(items.length > 0) {
            const last = items[items.length-1];
            if(!/[a-zA-Z]/.test(last.innerText||'')) {
                last.addEventListener('click', (e) => {
                    e.preventDefault(); e.stopPropagation();
                    const m = document.getElementById('create-assistant-modal');
                    if(m) { m.style.display='block'; console.log('✨ Modal ABERTO!'); }
                    else { console.error('❌ Modal ausente!'); location.reload(); }
                });
                console.log('✅ Botão + conectado!');
            }
        }
    }, 600);

})();
