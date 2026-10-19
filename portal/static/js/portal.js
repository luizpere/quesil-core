// Portal Quesil Core - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Quesil Core Portal carregado');
    
    // Verificar status do sistema
    checkSystemStatus();
});

async function checkSystemStatus() {
    try {
        const response = await fetch('/portal/api/status');
        const data = await response.json();
        
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = statusIndicator?.nextElementSibling;
        
        if (data.status === 'online') {
            statusIndicator?.classList.add('online');
            if (statusText) statusText.textContent = 'Online';
        } else {
            statusIndicator?.classList.remove('online');
            if (statusText) statusText.textContent = 'Offline';
        }
    } catch (error) {
        console.error('Erro ao verificar status:', error);
    }
}
