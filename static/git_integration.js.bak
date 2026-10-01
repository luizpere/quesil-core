// Git Integration Module for ThinkinOS Editor
(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        initGitIntegration();
    });
    
    function initGitIntegration() {
        console.log(" Git Integration initializing...");
        
        // Encontrar toolbar e adicionar botão
        const toolbar = document.querySelector('.toolbar div:last-child');
        if (!toolbar) {
            console.error("Toolbar not found!");
            return;
        }
        
        const gitBtn = document.createElement('button');
        gitBtn.id = 'btn-git';
        gitBtn.className = 'btn ready';
        gitBtn.innerHTML = ' Git';
        gitBtn.onclick = openGitModal;
        gitBtn.style.cssText = 'background:#2ea44f;color:white;border:none;padding:6px 16px;cursor:pointer;border-radius:3px;font-size:13px;margin-left:8px;';
        
        toolbar.insertBefore(gitBtn, toolbar.firstChild);
        
        createGitModal();
        console.log("✅ Git button added");
    }
    
    function createGitModal() {
        const modal = document.createElement('div');
        modal.id = 'git-modal';
        modal.style.cssText = 'display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:1000;justify-content:center;align-items:center;';
        modal.onclick = function(e) { if(e.target === this) closeModal(); };
        
        modal.innerHTML = `
            <div style="background:#252526;width:600px;max-height:70vh;border-radius:8px;overflow:hidden;display:flex;flex-direction:column;">
                <div style="background:#333;padding:15px;border-bottom:1px solid #444;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:bold;font-size:16px;color:#fff;">🔀 Git Commit & Push</span>
                    <button onclick="closeModal()" style="background:#cc3333;color:white;border:none;padding:4px 12px;cursor:pointer;border-radius:3px;">✕</button>
                </div>
                <div style="padding:15px;overflow-y:auto;flex:1;">
                    <div style="margin-bottom:10px;color:#ccc;font-size:13px;">Arquivos modificados:</div>
                    <div id="git-file-list" style="margin-bottom:15px;max-height:150px;overflow-y:auto;border:1px solid #333;border-radius:4px;">
                        <div style="padding:20px;color:#666;text-align:center;">Carregando status...</div>
                    </div>
                    <div style="margin-top:15px;">
                        <label style="color:#ccc;font-size:13px;display:block;margin-bottom:5px;">Mensagem de commit:</label>
                        <textarea id="git-commit-msg" style="width:100%;background:#3c3c3c;color:#fff;border:1px solid #555;padding:10px;border-radius:4px;font-size:14px;outline:none;resize:vertical;min-height:80px;box-sizing:border-box;" placeholder="Descreva suas alterações..."></textarea>
                    </div>
                    <div style="display:flex;gap:10px;margin-top:15px;justify-content:flex-end;">
                        <button onclick="gitCommit()" style="background:#2ea44f;color:white;border:none;padding:8px 20px;cursor:pointer;border-radius:3px;">💾 Commit</button>
                        <button onclick="gitPush()" style="background:#0e639c;color:white;border:none;padding:8px 20px;cursor:pointer;border-radius:3px;">⬆️ Push</button>
                    </div>
                    <div id="git-output" style="display:none;margin-top:15px;padding:10px;background:#1a1a1a;border-radius:4px;font-family:monospace;font-size:12px;color:#ccc;white-space:pre-wrap;max-height:150px;overflow-y:auto;"></div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    window.openGitModal = async function() {
        const modal = document.getElementById('git-modal');
        if (modal) {
            modal.style.display = 'flex';
            document.getElementById('git-output').style.display = 'none';
            document.getElementById('git-commit-msg').value = '';
            await loadGitStatus();
        }
    };
    
    window.closeModal = function() {
        const modal = document.getElementById('git-modal');
        if (modal) modal.style.display = 'none';
    };
    
    async function loadGitStatus() {
        const listDiv = document.getElementById('git-file-list');
        if (!listDiv) return;
        listDiv.innerHTML = '<div style="padding:10px;color:#666;text-align:center;">Consultando git...</div>';
        
        try {
            const res = await fetch('/api/git/status');
            const data = await res.json();
            
            if (!data.success || !data.files || data.files.length === 0) {
                listDiv.innerHTML = '<div style="padding:15px;color:#7ee787;text-align:center;">✅ Workspace limpo!</div>';
                return;
            }
            
            listDiv.innerHTML = data.files.map(f => {
                let color = '#6a1b9a';
                let label = '?';
                if (f.status.includes('M')) { color = '#d69e2e'; label = 'M'; }
                else if (f.status.includes('A')) { color = '#2ea44f'; label = 'A'; }
                else if (f.status.includes('D')) { color = '#cc3333'; label = 'D'; }
                
                return `<div style="padding:6px 10px;border-bottom:1px solid #333;display:flex;align-items:center;gap:8px;font-family:monospace;font-size:12px;">
                    <span style="background:${color};color:#fff;padding:2px 6px;border-radius:3px;font-weight:bold;font-size:10px;min-width:16px;text-align:center;">${label}</span>
                    <span style="color:#ccc;">${f.file}</span>
                </div>`;
            }).join('');
            
        } catch(e) {
            listDiv.innerHTML = `<div style="padding:10px;color:#f48771;text-align:center;">Erro: ${e.message}</div>`;
        }
    }
    
    window.gitCommit = async function() {
        const msg = document.getElementById('git-commit-msg').value.trim();
        if (!msg) { alert('Digite uma mensagem de commit!'); return; }
        
        const out = document.getElementById('git-output');
        out.style.display = 'block';
        out.textContent = '⏳ Executando git add & commit...\n';
        out.style.color = '#ccc';
        
        try {
            const res = await fetch('/api/git/commit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            
            if (data.success) {
                out.textContent += `✅ Sucesso!\n${data.output}`;
                out.style.color = '#7ee787';
                document.getElementById('git-commit-msg').value = '';
                await loadGitStatus();
            } else {
                out.textContent += `❌ Erro: ${data.error}`;
                out.style.color = '#f48771';
            }
        } catch(e) {
            out.textContent += ` Falha: ${e.message}`;
            out.style.color = '#f48771';
        }
    };
    
    window.gitPush = async function() {
        const out = document.getElementById('git-output');
        out.style.display = 'block';
        out.textContent = '⏳ Executando git push...\n';
        out.style.color = '#ccc';
        
        try {
            const res = await fetch('/api/git/push', {method: 'POST'});
            const data = await res.json();
            
            if (data.success) {
                out.textContent += `✅ Push realizado!\n${data.output}`;
                out.style.color = '#7ee787';
            } else {
                out.textContent += `❌ Erro: ${data.error}`;
                out.style.color = '#f48771';
            }
        } catch(e) {
            out.textContent += `❌ Falha: ${e.message}`;
            out.style.color = '#f48771';
        }
    };
})();
