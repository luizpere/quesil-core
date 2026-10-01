// === TERMINAL WEB V4.0 - Socket.IO ===
let terminal = null;
let socket = null;
let currentContainerId = null;

function openTerminal(containerId, containerName) {
    console.log("🔧 [NOVO] Abrindo terminal para:", containerId, containerName);
    currentContainerId = containerId;
    document.getElementById('terminal-container-name').textContent = containerName;
    document.getElementById('terminal-modal').classList.add('active');
    
    // Fechar conexão anterior
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    if (terminal) {
        terminal.dispose();
        terminal = null;
    }
    
    // Inicializar xterm.js
    terminal = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: '"Courier New", Courier, monospace',
        theme: { background: '#1e1e1e', foreground: '#d4d4d4', cursor: '#00ff00' }
    });
    
    const fitAddon = new FitAddon.FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(document.getElementById('terminal-container'));
    setTimeout(() => fitAddon.fit(), 100);
    
    let currentLine = '';
    terminal.onKey(e => {
        const ev = e.domEvent;
        if (ev.key === 'Enter') {
            console.log("⌨️ [NOVO] Enter pressionado, comando:", currentLine);
            terminal.write('\r\n');
            if (socket && socket.connected) {
                console.log(" [NOVO] Enviando comando via Socket.IO:", currentLine);
                socket.emit('terminal_input', { 
                    container_id: currentContainerId, 
                    command: currentLine 
                });
            } else {
                console.error("❌ Socket não está conectado!");
                terminal.write('\r\n\x1b[31mErro: Socket não conectado\x1b[0m\r\n');
            }
            currentLine = '';
        } else if (ev.key === 'Backspace') {
            if (currentLine.length > 0) {
                currentLine = currentLine.slice(0, -1);
                terminal.write('\b \b');
            }
        } else if (e.key.length === 1) {
            currentLine += e.key;
            terminal.write(e.key);
        }
    });
    
    // Conectar Socket.IO
    socket = io();
    
    socket.on('connect', () => {
        console.log("✅ [NOVO] Socket.IO conectado, ID:", socket.id);
        terminal.write(`\r\n\x1b[32mConectado ao container ${containerId}\x1b[0m\r\n$ `);
    });
    
    socket.on('terminal_output', (data) => {
        console.log("📥 [NOVO] Recebido do servidor:", data.output);
        terminal.write(data.output);
        if (!data.output.endsWith('\n')) {
            terminal.write('\r\n$ ');
        } else {
            terminal.write('$ ');
        }
    });
    
    socket.on('disconnect', () => {
        console.log(" [NOVO] Socket.IO desconectado");
        terminal.write('\r\n\x1b[31mConexão perdida.\x1b[0m\r\n');
    });
    
    window.addEventListener('resize', () => {
        if (fitAddon) fitAddon.fit();
    });
}

function closeTerminal() {
    console.log("Fechando terminal");
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    if (terminal) {
        terminal.dispose();
        terminal = null;
    }
    document.getElementById('terminal-modal').classList.remove('active');
}

window.openTerminal = openTerminal;
window.closeTerminal = closeTerminal;


function clearTerminal() {
    if (terminal) {
        terminal.clear();
        terminal.write('\r\n\x1b[32mTela limpa. Digite um comando:\x1b[0m\r\n$ ');
    }
}
