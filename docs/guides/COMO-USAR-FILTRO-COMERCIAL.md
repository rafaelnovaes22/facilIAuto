# 🚚 Como Usar o Filtro de Veículos Comerciais

## Visão Geral

O sistema agora valida automaticamente se um veículo é adequado para uso comercial profissional, rejeitando pickups médias/grandes que são projetadas para lazer.

## Para Desenvolvedores

### Uso Básico

```python
from services.commercial_vehicle_validator import validator

# Validar um veículo
is_valid, reason = validator.is_commercial_vehicle(
    marca="Fiat",
    modelo="Strada Endurance",
    versao="Endurance",
    categoria="Pickup"
)

if is_valid:
    print(f"✅ Veículo comercial válido: {reason}")
else:
    print(f"❌ Veículo rejeitado: {reason}")
```

### Exemplos de Validação

#### ✅ Aceitos (Comerciais)

```python
# Pickups pequenas
validator.is_commercial_vehicle("Fiat", "Strada Endurance")
# (True, "Pickup comercial (versão Endurance)")

validator.is_commercial_vehicle("Volkswagen", "Saveiro Robust")
# (True, "Pickup comercial (versão Robust)")

validator.is_commercial_vehicle("Chevrolet", "Montana LS")
# (True, "Pickup comercial")

# Furgões
validator.is_commercial_vehicle("Fiat", "Fiorino")
# (True, "Furgão/van comercial")

validator.is_commercial_vehicle("Renault", "Kangoo Express")
# (True, "Furgão/van comercial")

validator.is_commercial_vehicle("Mercedes-Benz", "Sprinter 415")
# (True, "Furgão/van comercial")
```

#### ❌ Rejeitados (Lazer/Aventura)

```python
# Pickups médias/grandes
validator.is_commercial_vehicle("Fiat", "Toro Ranch")
# (False, "Fiat Toro é pickup de lazer/aventura, não comercial")

validator.is_commercial_vehicle("Nissan", "Frontier Attack")
# (False, "Nissan Frontier é pickup de lazer/aventura, não comercial")

validator.is_commercial_vehicle("Toyota", "Hilux SR")
# (False, "Toyota Hilux é pickup de lazer/aventura, não comercial")

# Versões de lazer em pickups pequenas
validator.is_commercial_vehicle("Fiat", "Strada", versao="Ranch")
# (False, "Versão Ranch é para lazer, não comercial")
```

### Integração com Motor de Recomendação

O filtro é aplicado automaticamente quando `uso_principal = "comercial"`:

```python
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine

# Criar perfil comercial
profile = UserProfile(
    uso_principal="comercial",
    orcamento_min=80000,
    orcamento_max=150000,
    prioridades={
        "capacidade_carga": 5,
        "durabilidade": 5,
        "economia": 4
    }
)

# Obter recomendações
engine = UnifiedRecommendationEngine()
recommendations = engine.recommend(profile, limit=10)

# Apenas veículos comerciais válidos serão retornados
# Pickups médias/grandes serão automaticamente rejeitadas
```

### Logs de Depuração

O sistema gera logs detalhados:

```
[FILTRO COMERCIAL] Fiat Toro rejeitado: Fiat Toro é pickup de lazer/aventura, não comercial
[FILTRO COMERCIAL] Nissan Frontier rejeitado: Nissan Frontier é pickup de lazer/aventura, não comercial
[FILTRO COMERCIAL] 5 de 15 carros válidos para uso comercial
[FILTRO COMERCIAL] 10 veículos rejeitados (pickups de lazer, SUVs, etc)
```

## Para Product Managers

### Critérios de Validação

**✅ Veículos Comerciais**:
- **Pickups Pequenas**: Strada, Saveiro, Montana, Oroch (básicas)
- **Furgões**: Fiorino, Kangoo, Ducato, Master, Sprinter, Berlingo
- **Características**: Caçamba curta, motor básico, foco em carga

**❌ Veículos de Lazer** (não comerciais):
- **Pickups Médias/Grandes**: Toro, Frontier, L200, Hilux, Ranger, S10, Amarok
- **Características**: Caçamba longa, motor potente, 4x4, conforto

### Impacto no Negócio

**Antes da correção**:
- Sistema recomendava Toro (R$ 149k) para entregas
- Custo operacional: R$ 3.550/mês
- ROI negativo para uso profissional

**Depois da correção**:
- Sistema recomenda Strada (R$ 89k) para entregas
- Custo operacional: R$ 2.050/mês
- **Economia**: R$ 1.500/mês = R$ 18.000/ano
- ROI positivo para uso profissional

## Para Usuários Finais

### Perfil Comercial - O que esperar

Quando você seleciona **"Uso Comercial"** no questionário:

**Você receberá**:
- Pickups pequenas (Strada, Saveiro, Montana)
- Furgões (Fiorino, Kangoo, Ducato)
- Vans (Master, Sprinter)

**Você NÃO receberá**:
- Pickups grandes (Toro, Frontier, Hilux)
- SUVs (Compass, Kicks)
- Sedans ou Hatches

### Por que essa diferença?

**Veículos Comerciais** são projetados para:
- ✅ Transportar carga pesada diariamente
- ✅ Baixo custo de manutenção
- ✅ Economia de combustível
- ✅ Durabilidade em uso intenso
- ✅ Peças acessíveis

**Pickups de Lazer** são projetadas para:
- 🏖️ Viagens e aventuras
- 🏔️ Off-road e trilhas
- 🚗 Conforto e tecnologia
- 💰 Alto custo operacional

## Perguntas Frequentes

### 1. Por que a Toro não é comercial?

A Fiat Toro é uma pickup **média** projetada para lazer e aventura:
- Motor 1.8 ou 2.0 turbo (alto consumo)
- Cabine dupla (menos espaço para carga)
- Foco em conforto e tecnologia
- Custo de manutenção elevado

Para uso comercial, use a **Strada** (pickup pequena).

### 2. E a Hilux? Não é usada para trabalho?

A Toyota Hilux é uma pickup **grande** de alto desempenho:
- Preço: R$ 220k+ (vs R$ 90k da Strada)
- Consumo: 8-10 km/L (vs 12-14 km/L da Strada)
- Manutenção: R$ 600/mês (vs R$ 300/mês da Strada)

É usada em trabalhos específicos (construção pesada, mineração), mas não é econômica para entregas urbanas.

### 3. Posso usar um furgão para entregas?

**Sim!** Furgões são ideais para entregas:
- ✅ Carga protegida (fechada)
- ✅ Maior volume que pickups
- ✅ Economia de combustível
- ✅ Manutenção acessível

Recomendados: Fiorino, Kangoo, Berlingo, Ducato, Master.

### 4. E se eu precisar de uma pickup grande?

Se você precisa de uma pickup grande para trabalhos específicos (construção, mineração, fazenda), considere o perfil **"Lazer"** ou **"Trabalho Pesado"** (futuro).

O perfil **"Comercial"** é otimizado para entregas urbanas e transporte de carga leve/média.

## Referências

- [Perfis de Uso Detalhados](../business/PERFIS-LAZER-COMERCIAL-PRIMEIRO.md)
- [Correção Técnica](../technical/CORRECAO-VEICULOS-COMERCIAIS.md)
- [Dados de Perfis](../../platform/backend/data/usage_profiles.json)

---

**Atualizado em**: 04 de Novembro, 2025  
**Versão**: 1.0
