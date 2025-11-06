# 📊 Guia: Atualização de Preços de Combustível

**Frequência**: Mensal ou quando houver variação significativa (>5%)  
**Responsável**: Equipe de Operações  
**Última Atualização**: 06/11/2024

---

## 🎯 Por que atualizar?

Os preços de combustível impactam diretamente o **TCO (Total Cost of Ownership)** calculado para cada veículo. Preços desatualizados podem:
- ❌ Gerar estimativas incorretas de custo mensal
- ❌ Prejudicar decisões de compra dos usuários
- ❌ Reduzir credibilidade da plataforma

---

## 📍 Onde estão os preços?

**Arquivo principal**: `platform/backend/data/fuel_prices.json`

```json
{
  "last_update": "2024-11-06",
  "prices": {
    "Gasolina": {
      "price": 6.17,
      "reference_date": "março 2025"
    },
    "Etanol": {
      "price": 4.28,
      "reference_date": "fevereiro 2025"
    }
  }
}
```

---

## 🔄 Como atualizar (Passo a Passo)

### 1. Consultar Preços Atuais

**Fonte Oficial**: ANP (Agência Nacional do Petróleo)

🔗 **Links úteis**:
- Portal ANP: https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos
- Levantamento de Preços: https://precos.anp.gov.br/

**O que consultar**:
- ✅ Gasolina Comum (preço médio nacional ou por estado)
- ✅ Etanol Comum (preço médio nacional ou por estado)
- ⚠️ Diesel S10 (se aplicável)
- ⚠️ GNV (se aplicável)

### 2. Calcular Preço Flex

O preço Flex é uma **média ponderada** baseada no uso típico:

```
Preço Flex = (0.70 × Gasolina) + (0.30 × Etanol)
```

**Exemplo**:
- Gasolina: R$ 6,17
- Etanol: R$ 4,28
- Flex = (0.70 × 6.17) + (0.30 × 4.28) = 4.32 + 1.28 = **R$ 5,60**

**Por que 70/30?**
- Carros flex geralmente usam mais gasolina devido à maior eficiência energética
- Proporção baseada em dados de mercado e comportamento do consumidor

### 3. Atualizar o Arquivo JSON

Edite `platform/backend/data/fuel_prices.json`:

```json
{
  "last_update": "2024-12-01",  // ← Atualizar data
  "source": "ANP (Agência Nacional do Petróleo)",
  "prices": {
    "Gasolina": {
      "price": 6.25,  // ← Novo preço
      "unit": "R$/litro",
      "reference_date": "dezembro 2024",  // ← Atualizar mês
      "notes": "Gasolina comum"
    },
    "Etanol": {
      "price": 4.35,  // ← Novo preço
      "unit": "R$/litro",
      "reference_date": "dezembro 2024",  // ← Atualizar mês
      "notes": "Etanol comum"
    },
    "Flex": {
      "price": 5.68,  // ← Recalcular: (0.70 × 6.25) + (0.30 × 4.35)
      "unit": "R$/litro",
      "reference_date": "dezembro 2024",
      "notes": "Média ponderada (70% gasolina, 30% etanol)"
    }
  }
}
```

### 4. Validar Cálculos

Execute o teste de validação:

```bash
cd platform/backend
python -c "
from services.tco_calculator import TCOCalculator
prices = TCOCalculator.load_fuel_prices_from_file('data')
print('Preços carregados:')
for fuel, price in prices.items():
    print(f'  {fuel}: R$ {price:.2f}')
"
```

**Saída esperada**:
```
Preços carregados:
  Gasolina: R$ 6.25
  Etanol: R$ 4.35
  Flex: R$ 5.68
  Diesel: R$ 6.00
  GNV: R$ 4.50
```

### 5. Testar TCO

Execute teste completo:

```bash
cd platform/backend
python test_tco_local.py
```

Verifique se o custo de combustível está correto.

### 6. Commit e Deploy

```bash
git add platform/backend/data/fuel_prices.json
git commit -m "chore: update fuel prices - [MÊS/ANO]

- Gasolina: R$ X.XX (fonte: ANP)
- Etanol: R$ X.XX (fonte: ANP)
- Flex: R$ X.XX (calculado)
"
git push
```

### 7. Deploy em Produção

Se estiver usando Railway:
1. Push automático vai triggerar deploy
2. Aguardar 2-3 minutos
3. Verificar em produção: `https://[backend-url]/health`

---

## 📅 Calendário de Atualização

### Frequência Recomendada

| Situação | Ação |
|----------|------|
| **Mensal** | Verificar preços no início do mês |
| **Variação >5%** | Atualizar imediatamente |
| **Notícia de reajuste** | Atualizar após confirmação oficial |

### Checklist Mensal

- [ ] Dia 1-5 do mês: Consultar ANP
- [ ] Comparar com preços atuais no sistema
- [ ] Se variação >5%: Atualizar
- [ ] Se variação <5%: Manter e documentar
- [ ] Registrar em log de atualizações

---

## 🔍 Monitoramento

### Alertas Automáticos (Futuro)

Implementar script que:
1. Consulta API da ANP semanalmente
2. Compara com preços no sistema
3. Envia alerta se variação >5%
4. Sugere novos valores

**Script sugerido**: `scripts/check_fuel_prices.py`

### Dashboard de Preços (Futuro)

Criar endpoint na API:
```
GET /api/fuel-prices
```

Retorna:
```json
{
  "current_prices": {...},
  "last_update": "2024-11-06",
  "days_since_update": 15,
  "needs_update": false
}
```

---

## 📊 Histórico de Atualizações

| Data | Gasolina | Etanol | Flex | Fonte | Responsável |
|------|----------|--------|------|-------|-------------|
| 2024-11-06 | R$ 6,17 | R$ 4,28 | R$ 5,50 | ANP | Kiro AI |
| 2024-12-01 | R$ 6,25 | R$ 4,35 | R$ 5,68 | ANP | [Nome] |

---

## ❓ FAQ

### P: E se a ANP não tiver dados atualizados?

**R**: Use a última informação disponível e documente no campo `notes`. Considere usar média dos últimos 3 meses.

### P: Devo usar preço nacional ou regional?

**R**: Depende do escopo:
- **Nacional**: Mais simples, boa aproximação
- **Regional**: Mais preciso, mas requer lógica por estado

Atualmente usamos **preço nacional médio**.

### P: Como lidar com variações sazonais?

**R**: Combustíveis têm variação sazonal (férias, safra de cana). Considere:
- Atualizar mais frequentemente em períodos de alta volatilidade
- Usar média móvel de 3 meses para suavizar variações

### P: E se esquecer de atualizar?

**R**: Sistema continua funcionando com preços antigos. Mas:
- ⚠️ TCO pode ficar impreciso
- ⚠️ Usuários podem questionar valores
- ⚠️ Credibilidade da plataforma pode ser afetada

**Solução**: Configurar lembrete mensal no calendário.

---

## 🚀 Melhorias Futuras

1. **Integração com API da ANP**
   - Atualização automática
   - Sem intervenção manual

2. **Preços por Estado**
   - Maior precisão regional
   - Melhor experiência do usuário

3. **Histórico de Preços**
   - Gráficos de evolução
   - Análise de tendências

4. **Alertas Proativos**
   - Notificação quando preço varia >5%
   - Sugestão automática de atualização

---

## 📞 Suporte

**Dúvidas sobre atualização?**
- Documentação técnica: `platform/backend/services/tco_calculator.py`
- Arquivo de dados: `platform/backend/data/fuel_prices.json`
- Issues: https://github.com/rafaelnovaes22/facilIAuto/issues

---

**Última revisão**: 06/11/2024  
**Próxima revisão**: 01/12/2024
