# Documentacao da API - ThinkinOS v2.0
Base URL: http://192.168.3.7:5000

## Endpoints Principais
- GET /chat : Renderiza a pagina principal. Params: assistant, nivel.
- GET /api/challenge : Retorna um desafio aleatorio filtrado por nivel.
- POST /api/chat : Envia mensagem para a IA. Body: {message, assistant, nivel, history}.
- GET /editor : Renderiza o editor de codigo Monaco (com protecao de arquivos sensíveis).
- POST /api/file/save : Salva o conteudo de um arquivo editado.
