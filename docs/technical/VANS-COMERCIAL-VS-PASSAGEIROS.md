# 🚐 Vans: Comercial vs Passageiros

**Data**: 04 de Novembro, 2025  
**Status**: ✅ IMPLEMENTADO (26/26 testes passando)

## Problema

"Van" pode significar duas coisas completamente diferentes:
1. **Van Comercial** (transporte de carga)
2. **Van de Passageiros** (transporte de pessoas)

## Solução: Diferenciação Clara

### 1. Van Comercial (Carga) ✅

**Uso**: Transporte de **mercadorias/carga**  
**Perfil**: **Comercial** (entregas)  
**CNH**: B  
**Aceito**: ✅ SIM

**Características**:
- Sem bancos traseiros (ou poucos)
- Espaço amplo para carga
- Porta lateral ou traseira grande
- Foco em volume de carga

**Exemplos**:
- Renault Master **Furgão**
- Fiat Ducato **Cargo**
- Mercedes-Benz Sprinter **Furgão**
- Volkswagen Transporter **Cargo**
- Iveco Daily **Furgão**

**Versões**: Furgão, Cargo, Baú

---

### 2. Van de Passageiros (Pessoas) ❌

**Uso**: Transporte de **8-16 passageiros**  
**Perfil**: **Transporte de Passageiros** (fretamento, escolar, turismo)  
**CNH**: D (categoria especial)  
**Aceito para Comercial**: ❌ NÃO

**Características**:
- Múltiplos bancos (8-16 lugares)
- Conforto para passageiros
- Ar condicionado, janelas amplas
- Foco em transporte de pessoas

**Exemplos**:
- Renault Master **Minibus**
- Fiat Ducato **Minibus**
- Mercedes-Benz Sprinter **Executiva**
- Volkswagen Kombi **Lotação**
- Iveco Daily **Minibus**

**Versões**: Minibus, Executiva, Lotação, Escolar, Passageiros

---

## Comparação

| Aspecto | Van Comercial (Carga) | Van de Passageiros |
|---------|----------------------|-------------------|
| **Uso** | Entregas, carga | Fretamento, escolar, turismo |
| **Perfil** | Comercial ✅ | Transporte de Passageiros |
| **CNH** | B | D |
| **Bancos** | 2-3 (motorista + ajudante) | 8-16 (múltiplos passageiros) |
| **Carga** | 1.000-2.000 kg | Limitada (bagagens) |
| **Volume** | 8-15 m³ | Reduzido (bancos ocupam espaço) |
| **Uber/99** | ❌ Não | ❌ Não (exceto Uber Van) |
| **Aceito Comercial** | ✅ SIM | ❌ NÃO |

---

## Identificação Automática

### Por Versão/Modelo

**Palavras-chave de Passageiros**:
- "Minibus"
- "Executiva"
- "Lotação"
- "Escolar"
- "Passageiros"

**Palavras-chave Comerciais**:
- "Furgão"
- "Cargo"
- "Baú"

### Exemplos

```python
# Van Comercial (ACEITA)
validator.is_commercial_vehicle("Renault", "Master Furgão")
# (True, "Furgão/van comercial (carga)")

# Van de Passageiros (REJEITA)
validator.is_commercial_vehicle("Renault", "Master Minibus")
# (False, "Van de passageiros (8+ pessoas), não para entregas comerciais")
```

---

## Classificação por Adequação

### Van Comercial (Carga)

```json
{
  "nivel": "ideal",
  "score": 1.0,
  "tipo": "furgao_van",
  "avisos": [],
  "requer_cnh": "B",
  "recomendado": true
}
```

### Van de Passageiros

```json
{
  "nivel": "inadequado",
  "score": 0.0,
  "tipo": "van_passageiros",
  "avisos": [
    "⚠️ Van de passageiros (8+ pessoas)",
    "⚠️ Não é para entregas comerciais",
    "⚠️ Use perfil 'Transporte de Passageiros'",
    "⚠️ Não é aceita em Uber/99 (exceto Uber Van)"
  ],
  "requer_cnh": "D",
  "recomendado": false
}
```

---

## Casos de Uso

### ✅ Caso 1: Entregas de Volume (Comercial)
**Necessidade**: Transportar mercadorias  
**Recomendação**: Renault Master Furgão  
**Resultado**: ✅ Aceito (van comercial)

### ❌ Caso 2: Transporte Escolar
**Necessidade**: Transportar 12 crianças  
**Veículo**: Fiat Ducato Minibus  
**Perfil Comercial**: ❌ Rejeitado (van de passageiros)  
**Perfil Correto**: Transporte de Passageiros

### ❌ Caso 3: Fretamento Corporativo
**Necessidade**: Transportar funcionários  
**Veículo**: Mercedes Sprinter Executiva  
**Perfil Comercial**: ❌ Rejeitado (van de passageiros)  
**Perfil Correto**: Transporte de Passageiros

---

## Perfis do FacilIAuto

### Perfil "Comercial"
**Aceita**:
- ✅ Pickups pequenas (Strada, Saveiro)
- ✅ Furgões (Fiorino, Kangoo)
- ✅ **Vans comerciais** (Master Furgão, Ducato Cargo)
- ⚠️ VUCs (HR, Bongo) - com avisos

**Rejeita**:
- ❌ Pickups de lazer (Toro, Frontier)
- ❌ **Vans de passageiros** (Master Minibus, Sprinter Executiva)
- ❌ SUVs, Sedans

### Perfil "Transporte de Passageiros"
**Aceita**:
- ✅ Sedans (Uber/99)
- ✅ SUVs (Uber Comfort/Black)
- ✅ **Vans de passageiros** (fretamento, escolar)

**Rejeita**:
- ❌ Pickups
- ❌ Furgões
- ❌ **Vans comerciais** (são para carga)

---

## Requisitos CNH

| Veículo | CNH | Motivo |
|---------|-----|--------|
| **Van Comercial** (Furgão) | B | Até 3.500 kg, até 8 passageiros |
| **Van de Passageiros** (Minibus) | D | Mais de 8 passageiros |

**Nota**: Van de passageiros sempre requer CNH D, independente do peso.

---

## Uber/99

### Van Comercial (Furgão)
- ❌ **Não aceita** em Uber/99
- Motivo: Não tem bancos para passageiros

### Van de Passageiros (Minibus)
- ⚠️ **Parcialmente aceita** (apenas Uber Van em algumas cidades)
- Requisitos: CNH D, documentação especial
- Não é comum/recomendado

**Conclusão**: Nenhum tipo de van é ideal para Uber/99. Use sedans ou SUVs.

---

## Testes

✅ **26/26 testes passando**:
- Van comercial aceita
- Van de passageiros rejeitada
- Diferenciação por versão
- Classificação correta
- Avisos apropriados

---

## Documentação Relacionada

- **Perfil Comercial**: `docs/business/PERFIS-LAZER-COMERCIAL-PRIMEIRO.md`
- **Perfil Transporte**: `docs/business/CARROS-TRANSPORTE-APP.md`
- **Validador**: `platform/backend/services/commercial_vehicle_validator.py`

---

**Implementado por**: AI Engineer  
**Testado**: 26/26 testes passando ✅  
**Diferenciação**: Van comercial vs passageiros  
**Status**: Pronto para produção 🚀
