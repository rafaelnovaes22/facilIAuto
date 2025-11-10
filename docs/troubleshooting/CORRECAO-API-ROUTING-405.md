# Correção: Erro 405 em /api/recommend

## Problema Identificado

Frontend em produção estava retornando erro 405 (Method Not Allowed) ao chamar `/api/recommend`.

## Diagnóstico

1. **Backend está funcionando corretamente**: Testes com Python confirmaram que tanto `/recommend` quanto `/api/recommend` funcionam perfeitamente
2. **Frontend usa a rota correta**: O código fonte usa `/recommend` (sem prefixo `/api`)
3. **Build está correto**: O arquivo compilado contém a URL correta da API
4. **Causa raiz**: InteractionTracker estava usando URL padrão `http://localhost:8000` em vez da URL de produção

## Correções Aplicadas

### 1. InteractionTracker.ts
**Arquivo**: `platform/frontend/src/services/InteractionTracker.ts`

**Problema**: Instância singleton criada sem passar a URL da API do ambiente

**Antes**:
```typescript
const interactionTracker = new InteractionTracker();
export default interactionTracker;
```

**Depois**:
```typescript
import { API_URL } from '@/config/env';

const interactionTracker = new InteractionTracker(API_URL);
export default interactionTracker;
```

**Impacto**: Agora o InteractionTracker usa a URL correta em produção (`https://faciliauto-backend-production.up.railway.app`)

## Testes Realizados

### Backend (Produção)
```bash
python test_production_api.py
```

Resultados:
- ✅ GET /health: 200 OK
- ✅ GET /api/health: 200 OK  
- ✅ POST /recommend: 200 OK (3 recomendações)
- ✅ POST /api/recommend: 200 OK (3 recomendações)

### Frontend (Build)
```bash
cd platform/frontend
npm run build
```

Resultado:
- ✅ Build concluído com sucesso
- ✅ API URL correta no bundle: `https://faciliauto-backend-production.up.railway.app`

## Próximos Passos

1. ✅ Commit das alterações
2. ⏳ Push para Railway (deploy automático)
3. ⏳ Verificar frontend em produção
4. ⏳ Testar fluxo completo de recomendações

## Arquivos Modificados

- `platform/frontend/src/services/InteractionTracker.ts`
- `platform/frontend/src/services/api.ts` (comentário adicionado)

## Notas Técnicas

- O erro 405 não era do backend, mas sim do InteractionTracker tentando enviar dados para `http://localhost:8000/api/interactions/track`
- O backend Railway está 100% funcional
- A correção garante que TODOS os serviços (api.ts e InteractionTracker.ts) usem a mesma URL de ambiente

## Data
2025-11-06
