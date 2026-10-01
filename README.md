# ThinkinOS v2.0 - Sistema Adaptativo

## Visao Geral
Plataforma de chat inteligente com assistentes virtuais adaptativos (Leigo, Intermediario ou Avancado).
Status: Producao Estavel (Porta 5000) | Ambiente DEV (Porta 5002)

## Funcionalidades
1. Sistema de 3 Niveis: Leigo (Ana), Intermediario (Carlos), Avancado (ThinkinIA).
2. Assistentes com Personalidades Distintas: Empatico, Mentor, Tecnico.
3. Sistema de Desafios Dinamicos: 17 desafios categorizados com filtro via API.
4. Interface Adaptativa: O botao do editor some automaticamente para usuarios leigos.
5. Identidade Visual: Cores distintas para cada assistente (Rosa, Azul, Roxo).

## Como Rodar
cd ~/thinkinos-platform
source venv/bin/activate
python app.py

## URLs de Acesso
- Leigo: http://192.168.3.7:5000/chat?assistant=Ana&nivel=leigo
- Intermediario: http://192.168.3.7:5000/chat?assistant=Carlos&nivel=intermediario
- Avancado: http://192.168.3.7:5000/chat?assistant=ThinkinIA&nivel=avancado
