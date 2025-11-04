# Categorias Uber/99 - Indicação Automática

## Funcionalidade Implementada

Quando o usuário seleciona **"Transporte de Passageiros (Uber/99)"** como uso principal, o sistema agora indica automaticamente **quais categorias de serviço** cada carro recomendado atende.

## Categorias Disponíveis

### 1. UberX / 99Pop
- **Descrição:** Categoria econômica - Carros compactos e sedãs
- **Requisitos:**
  - Ano mínimo: 2015
  - Idade máxima: 10 anos
  - 4 portas, 5 lugares
  - Ar-condicionado
  - Modelos aceitos: Lista oficial Uber/99

### 2. Uber Comfort
- **Descrição:** Categoria intermediária - Carros mais espaçosos e confortáveis
- **Requisitos:**
  - Ano mínimo: 2016
  - Idade máxima: 8 anos
  - Carros maiores e mais confortáveis
  - Ar-condicionado
  - Modelos aceitos: Lista oficial Uber

### 3. Uber Black
- **Descrição:** Categoria premium - Carros de luxo
- **Requisitos:**
  - Ano mínimo: 2018
  - Idade máxima: 6 anos
  - Carros de luxo
  - Ar-condicionado
  - Modelos aceitos: Lista oficial Uber Black

## Como Funciona

### 1. Validação Automática

Para cada carro recomendado, o sistema:
1. Verifica o ano de fabricação
2. Calcula a idade do veículo
3. Consulta a lista oficial de modelos aceitos
4. Valida contra requisitos de cada categoria
5. Retorna todas as categorias que o carro atende

### 2. Score de Adequação

Cada categoria recebe um score (0.0 a 1.0) baseado na idade do carro:

| Idade do Carro | Score | Classificação |
|----------------|-------|---------------|
| 0-2 anos | 1.0 | Muito novo ⭐⭐⭐⭐⭐ |
| 3-5 anos | 0.9 | Novo ⭐⭐⭐⭐ |
| 6-7 anos | 0.7 | Bom ⭐⭐⭐ |
| 8+ anos | 0.5 | Aceitável ⭐⭐ |

### 3. Resposta da API

Quando `uso_principal = "transporte_passageiros"`, a resposta inclui:

```json
{
  "recommendations": [
    {
      "car": {
        "nome": "Hyundai HB20S",
        "marca": "Hyundai",
        "ano": 2025,
        "preco": 78990.0,
        "app_transport_categories": [
          {
            "categoria": "uberx_99pop",
            "nome_exibicao": "UberX / 99Pop",
            "score": 1.0,
            "descricao": "Categoria econômica - Carros compactos e sedãs",
            "ano_minimo": 2015,
            "idade_maxima": 10
          },
          {
            "categoria": "uber_comfort",
            "nome_exibicao": "Uber Comfort",
            "score": 1.0,
            "descricao": "Categoria intermediária - Carros mais espaçosos e confortáveis",
            "ano_minimo": 2016,
            "idade_maxima": 8
          }
        ]
      },
      "match_score": 0.78,
      "match_percentage": 78
    }
  ]
}
```

## Exemplo de Uso

### Requisição

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "orcamento_min": 40000,
    "orcamento_max": 100000,
    "uso_principal": "transporte_passageiros",
    "prioridades": {
      "economia": 5,
      "espaco": 3,
      "performance": 2,
      "conforto": 4,
      "seguranca": 5
    }
  }'
```

### Resposta (Exemplo)

```
Top 3 Recomendações:

1. Hyundai HB20S (2025) - Match: 78%
   ✓ UberX / 99Pop (score: 1.0)
   ✓ Uber Comfort (score: 1.0)

2. Hyundai HB20S (2019) - Match: 77%
   ✓ UberX / 99Pop (score: 0.7)
   ✓ Uber Comfort (score: 0.7)

3. Chevrolet Onix Plus (2020) - Match: 64%
   ✓ UberX / 99Pop (score: 0.9)
   ✓ Uber Comfort (score: 0.9)
```

## Benefícios

### Para o Usuário
- **Transparência:** Sabe exatamente quais categorias pode trabalhar
- **Planejamento:** Pode escolher carro baseado na categoria desejada
- **Economia:** Evita comprar carro que não atende requisitos

### Para a Concessionária
- **Conversão:** Usuário tem certeza que o carro serve
- **Confiança:** Informação oficial e validada
- **Diferencial:** Funcionalidade única no mercado

## Dados de Validação

O sistema usa o arquivo `platform/backend/data/app_transport_vehicles.json` que contém:

- **150+ modelos aceitos** oficialmente
- **Requisitos por categoria** (ano, idade, características)
- **Modelos excluídos em 2025** (atualizações das plataformas)
- **Top modelos por categoria** (recomendações)

## Implementação Técnica

### Arquivos Envolvidos

1. **`services/app_transport_validator.py`**
   - Classe `AppTransportValidator`
   - Método `get_accepted_categories()` - Retorna categorias aceitas
   - Método `is_valid_for_app_transport()` - Valida categoria específica

2. **`api/main.py`**
   - Endpoint `/recommend`
   - Adiciona `app_transport_categories` quando uso = "transporte_passageiros"

3. **`data/app_transport_vehicles.json`**
   - Dados oficiais de modelos aceitos
   - Requisitos por categoria
   - Atualizações 2025

### Fluxo de Validação

```
1. Usuário solicita recomendações (uso = "transporte_passageiros")
   ↓
2. Motor de recomendação filtra e ranqueia carros
   ↓
3. Para cada carro recomendado:
   a. Validador verifica ano e modelo
   b. Consulta lista oficial de modelos aceitos
   c. Valida contra requisitos de cada categoria
   d. Calcula score baseado na idade
   ↓
4. API retorna carros com categorias aceitas
   ↓
5. Frontend exibe badges/tags com categorias
```

## Próximas Melhorias

- [ ] Adicionar categoria "99Taxi"
- [ ] Incluir requisitos de documentação por categoria
- [ ] Calcular estimativa de ganhos por categoria
- [ ] Filtro para mostrar apenas carros de categoria específica
- [ ] Alertas sobre mudanças nos requisitos das plataformas
- [ ] Integração com API oficial Uber/99 (se disponível)

## Observações Importantes

1. **Dados atualizados:** Lista de modelos aceitos é de 2025
2. **Validação oficial:** Baseada em documentação oficial Uber/99
3. **Múltiplas categorias:** Um carro pode atender várias categorias
4. **Score dinâmico:** Considera idade do veículo
5. **Fallback seguro:** Se dados não disponíveis, não bloqueia recomendações

---

**Última atualização:** 04/11/2025
**Versão:** 1.0
**Status:** ✅ Implementado e testado
