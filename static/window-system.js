(function() {
    let highestZIndex = 1000;
    const windows = new Map();

    window.createWindow = function(options) {
        const { id, title, icon, content, width = 800, height = 600, x, y } = options;
        
        if (windows.has(id)) {
            const existing = windows.get(id);
            if (existing.classList.contains('minimized')) existing.classList.remove('minimized');
            bringToFront(existing);
            return existing;
        }

        const win = document.createElement('div');
        win.className = 'thinkinos-window';
        win.id = id;
        win.style.width = width + 'px';
        win.style.height = height + 'px';
        win.style.left = (x || (window.innerWidth - width) / 2) + 'px';
        win.style.top = (y || (window.innerHeight - height) / 2) + 'px';

        win.innerHTML = `
            <div class="window-titlebar">
                <div class="window-title">${icon || ''} ${title}</div>
                <div class="window-controls">
                    <button class="window-btn minimize" title="Minimizar"></button>
                    <button class="window-btn maximize" title="Maximizar"></button>
                    <button class="window-btn close" title="Fechar"></button>
                </div>
            </div>
            <div class="window-content">${content}</div>
            <div class="window-resizer"></div>
        `;

        document.body.appendChild(win);
        windows.set(id, win);
        bringToFront(win);

        win.querySelector('.minimize').addEventListener('click', () => win.classList.add('minimized'));
        win.querySelector('.maximize').addEventListener('click', () => win.classList.toggle('maximized'));
        win.querySelector('.close').addEventListener('click', () => { win.remove(); windows.delete(id); });

        const titlebar = win.querySelector('.window-titlebar');
        let isDragging = false, startX, startY, initialX, initialY;

        titlebar.addEventListener('mousedown', (e) => {
            if (e.target.classList.contains('window-btn') || win.classList.contains('maximized')) return;
            isDragging = true;
            startX = e.clientX; startY = e.clientY;
            initialX = win.offsetLeft; initialY = win.offsetTop;
            bringToFront(win);
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            win.style.left = (initialX + e.clientX - startX) + 'px';
            win.style.top = (initialY + e.clientY - startY) + 'px';
        });

        document.addEventListener('mouseup', () => { isDragging = false; });

        const resizer = win.querySelector('.window-resizer');
        let isResizing = false, startWidth, startHeight, startMouseX, startMouseY;

        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            startWidth = win.offsetWidth; startHeight = win.offsetHeight;
            startMouseX = e.clientX; startMouseY = e.clientY;
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            win.style.width = Math.max(400, startWidth + e.clientX - startMouseX) + 'px';
            win.style.height = Math.max(300, startHeight + e.clientY - startMouseY) + 'px';
        });

        document.addEventListener('mouseup', () => { isResizing = false; });
        win.addEventListener('mousedown', () => bringToFront(win));
        
        console.log('✅ Janela criada:', title);
        return win;
    };

    function bringToFront(win) {
        highestZIndex++;
        win.style.zIndex = highestZIndex;
    }

    window.closeWindow = function(id) {
        const win = windows.get(id);
        if (win) { win.remove(); windows.delete(id); }
    };

    console.log('✅ Sistema de Janelas ThinkinOS (Clean) inicializado');
})();
