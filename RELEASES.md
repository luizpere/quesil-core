# 📦 Releases - Quesil Core

Histórico de versões e mudanças do Quesil Core.

---

## v2.0.0 (2026-10-20) - 🌌 Quesil Core Launch

### 🎨 Identidade Visual
- **Rebranding completo**: ThinkinOS → Quesil Core
- **Logo SVG**: Kit completo inspirado na constelação de Órion (Principal, Horizontal, Animado, Favicon, Dark, Light)
- **Portal atualizado**: Landing page com nova identidade e favicon personalizado

### 🤖 IA e Assistentes
- **Quesil IA**: Novo prompt com identidade de Órion ("Núcleo Central que comanda o Quesil Core")
- **Nomenclatura**: ThinkinIA → Quesil IA em todo o sistema

### 🔧 Refatoração de Código
- **Arquitetura**: Aplicação do Single Responsibility Principle (SRP)
- **Performance**: Bulk operations com `executemany` no SQLite
- **Correções**: Decorators do Flask reposicionados corretamente
- **Limpeza**: Remoção de código duplicado e dead code

### 🛡️ Qualidade (Ghorak)
- ✅ **Alertas Críticos**: 10 → 0
- ✅ **Alertas Altos**: 4 → 0
- ⚠️ **Alertas Médios**: 2 (URLs de desenvolvimento)
- ⚠️ **Alertas Baixos**: 3 (otimizações sugeridas)

---

## v1.0.0 (2026-09-24) - ThinkinOS Initial Release
- Desktop web com múltiplos assistentes de IA
- Gerenciador de arquivos integrado, Terminal web, Code editor
- Sistema de autenticação e Banco de dados SQLite
