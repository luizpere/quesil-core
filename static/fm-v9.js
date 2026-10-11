// File Manager v9.0 - Compatível com FM v7.0
console.log('🚀 FM v9.0 - Script carregado');

var fmCurrentView = 'grid';
var fmAllFiles = [];
var fmFilteredFiles = [];
var fmSelectedFile = null;
var fmDragCounter = 0;

// === ABRIR/FECHAR MODAL ===
window.openFileManager = function() {
    console.log(' openFileManager() chamado');
    var overlay = document.getElementById('fm-overlay');
    var modal = document.getElementById('fm-modal');
    
    if (overlay) overlay.classList.add('active');
    if (modal) {
        modal.classList.add('active');
        modal.style.display = 'flex';
        console.log('✅ Modal aberto');
    }
    
    loadFMFiles();
    initDragDrop();
};

window.closeFileManager = function() {
    var overlay = document.getElementById('fm-overlay');
    var modal = document.getElementById('fm-modal');
    
    if (overlay) overlay.classList.remove('active');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
    }
    fmSelectedFile = null;
    fmDragCounter = 0;
    hideDropOverlay();
};

// Alias para compatibilidade com código antigo
window.openFM = window.openFileManager;

// === CARREGAR ARQUIVOS ===
function loadFMFiles() {
    console.log('📡 loadFMFiles() chamado');
    
    var loading = document.getElementById('fm-loading');
    var empty = document.getElementById('fm-empty');
    var grid = document.getElementById('fm-grid');
    var list = document.getElementById('fm-list');

    if (loading) loading.style.display = 'block';
    if (empty) empty.style.display = 'none';
    if (grid) grid.style.display = 'none';
    if (list) list.style.display = 'none';

    fetch('/api/files/list')
        .then(function(res) {
            console.log('📡 Status:', res.status);
            return res.json();
        })
        .then(function(data) {
            console.log('📦 Dados recebidos:', data);
            
            var filesArray = [];
            if (Array.isArray(data)) {
                filesArray = data;
            } else if (data && Array.isArray(data.files)) {
                filesArray = data.files;
            }

            console.log('📊 Total de arquivos:', filesArray.length);

            if (filesArray.length > 0) {
                fmAllFiles = filesArray;
                fmFilteredFiles = filesArray.slice();
                renderFMFiles();
            } else {
                if (empty) empty.style.display = 'block';
            }
        })
        .catch(function(err) {
            console.error('❌ Erro ao carregar:', err);
            if (empty) empty.style.display = 'block';
        })
        .finally(function() {
            if (loading) loading.style.display = 'none';
        });
}

// Alias para compatibilidade
window.loadFM = loadFMFiles;

// === RENDERIZAR ARQUIVOS ===
function renderFMFiles() {
    console.log(' renderFMFiles() chamado, view:', fmCurrentView, 'arquivos:', fmFilteredFiles.length);
    
    var grid = document.getElementById('fm-grid');
    var list = document.getElementById('fm-list');
    var empty = document.getElementById('fm-empty');

    if (fmFilteredFiles.length === 0) {
        if (grid) grid.style.display = 'none';
        if (list) list.style.display = 'none';
        if (empty) {
            empty.style.display = 'block';
            var searchInput = document.getElementById('fm-search-input') || document.getElementById('fm-search');
            if (searchInput && searchInput.value) {
                empty.innerHTML = '<div style="font-size: 64px; margin-bottom: 20px;">🔍</div><p>Nenhum arquivo encontrado para "' + searchInput.value + '"</p>';
            } else {
                empty.innerHTML = '<div style="font-size: 64px; margin-bottom: 20px;">📂</div><p>Nenhum arquivo encontrado</p>';
            }
        }
        updateStatus();
        return;
    }
    if (empty) empty.style.display = 'none';

    if (fmCurrentView === 'grid') {
        if (grid) {
            grid.style.display = 'grid';
            var html = '';
            fmFilteredFiles.forEach(function(file) {
                var safeName = file.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                html += '<div class="fm-file-card" onclick="selectFMFile(this, \'' + safeName + '\')">';
                html += '<div class="fm-file-icon">' + getFMFileIcon(file.name) + '</div>';
                html += '<div class="fm-file-name">' + file.name + '</div>';
                html += '</div>';
            });
            grid.innerHTML = html;
        }
        if (list) list.style.display = 'none';
    } else {
        if (list) {
            list.style.display = 'flex';
            var html = '';
            fmFilteredFiles.forEach(function(file) {
                var safeName = file.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                html += '<div class="fm-list-item" onclick="selectFMFile(this, \'' + safeName + '\')">';
                html += '<div class="fm-list-icon">' + getFMFileIcon(file.name) + '</div>';
                html += '<div class="fm-list-name">' + file.name + '</div>';
                html += '<div class="fm-list-size">' + formatFMSize(file.size) + '</div>';
                html += '</div>';
            });
            list.innerHTML = html;
        }
        if (grid) grid.style.display = 'none';
    }

    updateStatus();
}

function updateStatus() {
    var statusCount = document.getElementById('fm-status-count');
    if (statusCount) {
        var total = fmAllFiles.length;
        var filtered = fmFilteredFiles.length;
        if (filtered === total) {
            statusCount.textContent = total + ' itens';
        } else {
            statusCount.textContent = filtered + ' de ' + total + ' itens';
        }
    }
}

// === BUSCA FUNCIONAL (ambos os nomes) ===
function doFilterFiles() {
    var searchInput = document.getElementById('fm-search-input') || document.getElementById('fm-search');
    if (!searchInput) {
        console.log('⚠️ Campo de busca não encontrado');
        return;
    }
    
    var query = searchInput.value.toLowerCase().trim();
    console.log('🔍 Busca: "' + query + '"');
    
    if (!query) {
        fmFilteredFiles = fmAllFiles.slice();
    } else {
        fmFilteredFiles = fmAllFiles.filter(function(file) {
            return file.name.toLowerCase().indexOf(query) !== -1;
        });
    }
    
    console.log('🔍 Resultados:', fmFilteredFiles.length, 'de', fmAllFiles.length);
    renderFMFiles();
}

// Exportar com ambos os nomes para compatibilidade
window.filterFMFiles = doFilterFiles;
window.filterFM = doFilterFiles;

// === DRAG & DROP FUNCIONAL ===
function initDragDrop() {
    console.log('🎯 Inicializando Drag & Drop...');
    
    var modal = document.getElementById('fm-modal');
    if (!modal) {
        console.log('⚠️ Modal não encontrado');
        return;
    }
    
    // Prevenir comportamento padrão
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
        modal.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
    
    // Detectar quando arquivo entra na janela
    document.addEventListener('dragenter', function(e) {
        if (e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types.indexOf('Files') !== -1) {
            fmDragCounter++;
            console.log('🎯 Drag enter, counter:', fmDragCounter);
            showDropOverlay();
        }
    }, false);
    
    document.addEventListener('dragover', function(e) {
        e.preventDefault();
    }, false);
    
    document.addEventListener('dragleave', function(e) {
        fmDragCounter--;
        if (fmDragCounter <= 0) {
            fmDragCounter = 0;
            console.log('🎯 Drag leave, counter:', fmDragCounter);
            hideDropOverlay();
        }
    }, false);
    
    document.addEventListener('drop', function(e) {
        e.preventDefault();
        fmDragCounter = 0;
        hideDropOverlay();
        
        var dt = e.dataTransfer;
        var files = dt.files;
        
        console.log('📥 Drop detectado:', files.length, 'arquivo(s)');
        
        if (files.length > 0) {
            handleFMUpload(files);
        }
    }, false);
    
    console.log('✅ Drag & Drop inicializado');
}

function showDropOverlay() {
    var overlay = document.getElementById('fm-drop-overlay');
    if (overlay) overlay.classList.add('active');
}

function hideDropOverlay() {
    var overlay = document.getElementById('fm-drop-overlay');
    if (overlay) overlay.classList.remove('active');
}

// === VIEW TOGGLE ===
window.toggleFMView = function(view) {
    fmCurrentView = view;
    var statusView = document.getElementById('fm-status-view');
    if (statusView) statusView.textContent = view === 'grid' ? 'Grade' : 'Lista';
    renderFMFiles();
};

// === SELEÇÃO ===
window.selectFMFile = function(element, filename) {
    var cards = document.querySelectorAll('.fm-file-card, .fm-list-item');
    for (var i = 0; i < cards.length; i++) {
        cards[i].classList.remove('selected');
    }
    element.classList.add('selected');
    fmSelectedFile = filename;
    console.log('📌 Arquivo selecionado:', filename);
};

// === ÍCONES ===
function getFMFileIcon(filename) {
    var ext = filename.split('.').pop().toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'svg'].indexOf(ext) !== -1) return '🖼️';
    if (ext === 'pdf') return '';
    if (ext === 'doc' || ext === 'docx') return '📘';
    if (ext === 'odt') return '';
    if (ext === 'py') return '🐍';
    if (ext === 'js') return '⚡';
    if (ext === 'html') return '🌐';
    if (ext === 'css') return '';
    if (ext === 'json') return '📦';
    if (ext === 'md') return '📝';
    return '📄';
}

function formatFMSize(bytes) {
    if (!bytes) return '-';
    var sizes = ['B', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
}

// === UPLOAD ===
window.handleFMUpload = function(files) {
    if (!files || files.length === 0) return;
    var formData = new FormData();
    for (var i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    var loading = document.getElementById('fm-loading');
    if (loading) {
        loading.style.display = 'block';
        loading.textContent = 'Enviando ' + files.length + ' arquivo(s)...';
    }

    fetch('/api/files/upload', { method: 'POST', body: formData })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                alert(files.length + ' arquivo(s) enviado(s) com sucesso!');
                loadFMFiles();
            } else {
                alert('Erro: ' + (data.error || 'Falha no upload'));
            }
        })
        .catch(function(err) {
            alert('Erro de conexão: ' + err.message);
        })
        .finally(function() {
            if (loading) {
                loading.style.display = 'none';
                loading.textContent = 'Carregando arquivos...';
            }
        });
};

// === CRIAR PASTA ===
window.showNewFMFolderModal = function() {
    var name = prompt('Nome da nova pasta:');
    if (name) {
        fetch('/api/files/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name: name, type: 'folder' })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                alert('Pasta criada com sucesso!');
                loadFMFiles();
            } else {
                alert('Erro: ' + (data.error || 'Falha ao criar pasta'));
            }
        });
    }
};

// === CRIAR ARQUIVO ===
window.showNewFMFileModal = function() {
    var name = prompt('Nome do novo arquivo:');
    if (name) {
        fetch('/api/files/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name: name, type: 'file', content: '' })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                alert('Arquivo criado com sucesso!');
                loadFMFiles();
            } else {
                alert('Erro: ' + (data.error || 'Falha ao criar arquivo'));
            }
        });
    }
};

// === EXCLUIR ===
window.deleteFMFile = function() {
    if (!fmSelectedFile) {
        alert('Selecione um arquivo para excluir.');
        return;
    }
    if (confirm('Tem certeza que deseja excluir "' + fmSelectedFile + '"?')) {
        fetch('/api/files/delete/' + encodeURIComponent(fmSelectedFile), { method: 'DELETE' })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                alert('Arquivo excluído com sucesso!');
                fmSelectedFile = null;
                loadFMFiles();
            } else {
                alert('Erro: ' + (data.error || 'Falha ao excluir'));
            }
        });
    }
};

console.log('✅ FM v9.0 completo carregado com busca e drag & drop!');
