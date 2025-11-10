# Feature: Listagem de Marcas e Modelos Disponíveis

## Objetivo

Fornecer ao frontend uma lista completa de todas as marcas disponíveis no estoque e seus respectivos modelos, para uso no questionário de preferências do usuário.

## Implementação

### Backend

#### Novo Endpoint: `/brands-models`

**Método**: `GET`  
**Rota**: `/brands-models`  
**Descrição**: Retorna um dicionário com todas as marcas disponíveis e seus modelos correspondentes

**Resposta**:
```json
{
  "Chevrolet": ["Onix", "Tracker", "S10"],
  "Fiat": ["Argo", "Cronos", "Toro"],
  "Ford": ["Ka", "Ranger"],
  "Honda": ["Civic", "HR-V"],
  "Hyundai": ["HB20", "Creta"],
  "Nissan": ["Kicks", "Versa"],
  "Toyota": ["Corolla", "Hilux"],
  "Volkswagen": ["Gol", "T-Cross", "Virtus"]
}
```

**Características**:
- ✅ Apenas carros disponíveis (`disponivel = true`)
- ✅ Marcas ordenadas alfabeticamente
- ✅ Modelos únicos por marca
- ✅ Modelos ordenados alfabeticamente
- ✅ Cache automático (dados estáticos)

**Arquivo**: `platform/backend/api/main.py`

```python
@app.get("/brands-models")
def list_brands_with_models():
    """
    Listar marcas de carros disponíveis com seus modelos correspondentes
    """
    from collections import defaultdict
    
    brands_models = defaultdict(set)
    
    # Agrupar modelos por marca
    for car in engine.all_cars:
        if car.disponivel:
            brands_models[car.marca].add(car.modelo)
    
    # Converter sets para listas ordenadas
    result = {
        marca: sorted(list(modelos))
        for marca, modelos in sorted(brands_models.items())
    }
    
    return result
```

### Frontend

#### Nova Função no Service Layer

**Arquivo**: `platform/frontend/src/services/api.ts`

```typescript
export const getBrandsWithModels = async (): Promise<Record<string, string[]>> => {
    const { data } = await api.get<Record<string, string[]>>('/brands-models')
    return data
}
```

#### React Query Key

```typescript
export const queryKeys = {
    // ... outras keys
    brandsModels: ['brands-models'] as const,
    // ...
}
```

### Testes

#### Backend Test

**Arquivo**: `platform/backend/tests/test_api_integration.py`

```python
def test_list_brands_with_models(self, client):
    """Teste: listar marcas com modelos"""
    response = client.get("/brands-models")
    assert response.status_code == 200
    data = response.json()
    
    # Deve retornar um dicionário
    assert isinstance(data, dict)
    
    # Cada marca deve ter uma lista de modelos
    for marca, modelos in data.items():
        assert isinstance(marca, str)
        assert isinstance(modelos, list)
        assert len(modelos) > 0
        
        # Modelos devem ser strings únicas e ordenadas
        assert all(isinstance(modelo, str) for modelo in modelos)
        assert modelos == sorted(modelos)  # Verificar ordenação
```

## Uso no Frontend

### Exemplo de Uso com React Query

```typescript
import { useQuery } from '@tanstack/react-query'
import { getBrandsWithModels, queryKeys } from '@/services/api'

function BrandSelector() {
    const { data: brandsModels, isLoading } = useQuery({
        queryKey: queryKeys.brandsModels,
        queryFn: getBrandsWithModels,
        staleTime: 1000 * 60 * 60, // 1 hora (dados raramente mudam)
    })

    if (isLoading) return <Spinner />

    return (
        <Select placeholder="Selecione uma marca">
            {Object.keys(brandsModels || {}).map(marca => (
                <option key={marca} value={marca}>
                    {marca}
                </option>
            ))}
        </Select>
    )
}
```

### Exemplo de Seleção Marca + Modelo

```typescript
function BrandModelSelector() {
    const [selectedBrand, setSelectedBrand] = useState<string>('')
    
    const { data: brandsModels } = useQuery({
        queryKey: queryKeys.brandsModels,
        queryFn: getBrandsWithModels,
        staleTime: 1000 * 60 * 60,
    })

    const availableModels = selectedBrand 
        ? brandsModels?.[selectedBrand] || []
        : []

    return (
        <VStack>
            {/* Seletor de Marca */}
            <Select 
                placeholder="Selecione uma marca"
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
            >
                {Object.keys(brandsModels || {}).map(marca => (
                    <option key={marca} value={marca}>
                        {marca}
                    </option>
                ))}
            </Select>

            {/* Seletor de Modelo (habilitado apenas se marca selecionada) */}
            {selectedBrand && (
                <Select placeholder="Selecione um modelo">
                    {availableModels.map(modelo => (
                        <option key={modelo} value={modelo}>
                            {modelo}
                        </option>
                    ))}
                </Select>
            )}
        </VStack>
    )
}
```

## Integração com Questionário

### Passo 4: Preferências

No questionário, o usuário poderá:

1. **Selecionar marcas preferidas** (múltipla escolha)
   - Lista todas as marcas disponíveis
   - Permite seleção de múltiplas marcas
   - Opcional (pode pular)

2. **Selecionar modelos específicos** (opcional)
   - Após selecionar marca(s), mostra modelos disponíveis
   - Permite refinar ainda mais a busca
   - Útil para quem já sabe o que quer

### Exemplo de UI

```
┌─────────────────────────────────────────┐
│ Tem alguma marca preferida?             │
│                                         │
│ ☐ Chevrolet (8 modelos)                │
│ ☐ Fiat (12 modelos)                    │
│ ☐ Ford (5 modelos)                     │
│ ☐ Honda (6 modelos)                    │
│ ☐ Hyundai (7 modelos)                  │
│ ☐ Nissan (4 modelos)                   │
│ ☐ Toyota (9 modelos)                   │
│ ☐ Volkswagen (11 modelos)              │
│                                         │
│ [Pular] [Continuar]                    │
└─────────────────────────────────────────┘

Se selecionar "Chevrolet":

┌─────────────────────────────────────────┐
│ Algum modelo específico da Chevrolet?   │
│                                         │
│ ☐ Onix                                  │
│ ☐ Onix Plus                             │
│ ☐ Tracker                               │
│ ☐ S10                                   │
│ ☐ Spin                                  │
│ ☐ Montana                               │
│ ☐ Cruze                                 │
│ ☐ Equinox                               │
│                                         │
│ [Voltar] [Pular] [Continuar]           │
└─────────────────────────────────────────┘
```

## Benefícios

### UX
- ✅ Usuário vê apenas marcas/modelos realmente disponíveis
- ✅ Evita frustração de buscar algo indisponível
- ✅ Facilita navegação com dados reais do estoque
- ✅ Permite refinamento progressivo (marca → modelo)

### Performance
- ✅ Endpoint leve e rápido (apenas agregação)
- ✅ Dados podem ser cacheados por longo período
- ✅ Reduz chamadas desnecessárias à API

### Manutenção
- ✅ Dados sempre sincronizados com estoque real
- ✅ Não precisa manter lista hardcoded no frontend
- ✅ Atualização automática quando novos carros são adicionados

## Dados de Exemplo (Estoque Atual)

Com base no estoque atual da RobustCar, o endpoint retornaria:

```json
{
  "Chevrolet": ["Onix", "Onix Plus", "Tracker", "S10"],
  "Fiat": ["Argo", "Cronos", "Toro", "Strada"],
  "Ford": ["Ka", "EcoSport", "Ranger"],
  "Honda": ["Civic", "HR-V", "City"],
  "Hyundai": ["HB20", "Creta", "Tucson"],
  "Nissan": ["Kicks", "Versa"],
  "Toyota": ["Corolla", "Hilux", "Yaris"],
  "Volkswagen": ["Gol", "Polo", "T-Cross", "Virtus"]
}
```

## Próximos Passos

1. ✅ **Backend**: Endpoint implementado
2. ✅ **Frontend**: Service layer atualizado
3. ✅ **Testes**: Teste de integração adicionado
4. ⏳ **UI**: Criar componente de seleção de marca/modelo
5. ⏳ **Questionário**: Integrar no Passo 4 (Preferências)
6. ⏳ **Validação**: Testar com usuários reais

## Arquivos Modificados

### Backend
- ✅ `platform/backend/api/main.py` - Novo endpoint `/brands-models`
- ✅ `platform/backend/tests/test_api_integration.py` - Teste do endpoint

### Frontend
- ✅ `platform/frontend/src/services/api.ts` - Nova função `getBrandsWithModels()`

## Comandos para Testar

### Backend
```bash
cd platform/backend
pytest tests/test_api_integration.py::TestCarsAPI::test_list_brands_with_models -v
```

### Manual (curl)
```bash
curl http://localhost:8000/brands-models
```

### Frontend (console do navegador)
```javascript
const response = await fetch('http://localhost:8000/brands-models')
const data = await response.json()
console.log(data)
```

---

**Data**: 2025-11-07  
**Tipo**: Feature - API Enhancement  
**Prioridade**: Média  
**Status**: ✅ Backend Completo | ⏳ Frontend UI Pendente
