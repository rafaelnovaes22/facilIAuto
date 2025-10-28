# 🎯 Perfis de Uso Detalhados - FacilIAuto

## 📋 Visão Geral

Documentação completa dos 6 perfis de uso suportados pelo FacilIAuto, com requisitos específicos, prioridades recomendadas e modelos ideais para cada caso.

**Última atualização**: 15 de Outubro, 2025

---

## 🚗 Perfis Suportados

1. **Família** - Transporte familiar com segurança e espaço
2. **Trabalho** - Deslocamento diário profissional
3. **Lazer** - Viagens e passeios recreativos
4. **Comercial** - Uso profissional e entregas
5. **Primeiro Carro** - Iniciantes na compra de veículos
6. **Transporte de Passageiros** - Uber, 99 e similares

---


## 👨‍👩‍👧‍👦 PERFIL 1: FAMÍLIA

### **Características do Perfil**

**Uso Principal**: Transporte de família (cônjuge, filhos, idosos)  
**Frequência**: Diária (escola, trabalho, compras, lazer)  
**Prioridade #1**: Segurança  
**Prioridade #2**: Espaço  
**Prioridade #3**: Conforto

### **Requisitos Essenciais**

#### **Segurança (Prioridade Máxima)**
- ✅ **6 airbags** (mínimo: frontal + lateral + cortina)
- ✅ **ISOFIX** (fixação de cadeirinha infantil)
- ✅ **Controle de estabilidade** (ESP/ESC)
- ✅ **Freios ABS** com EBD
- ✅ **Assistente de partida em rampa**
- ✅ **Câmera de ré** ou sensores
- ✅ **Estrutura reforçada** (bom resultado em crash tests)

#### **Espaço (Muito Importante)**
- ✅ **5 lugares reais** (não apertados)
- ✅ **Porta-malas**: Mínimo 300L (ideal: 400L+)
- ✅ **Espaço traseiro**: Mínimo 70cm entre bancos
- ✅ **Portas traseiras amplas** (fácil acesso com cadeirinha)
- ✅ **Compartimentos de armazenamento** (porta-objetos, porta-copos)

#### **Conforto (Importante)**
- ✅ **Ar-condicionado** (preferencialmente digital/automático)
- ✅ **Direção elétrica/hidráulica**
- ✅ **Vidros e travas elétricas**
- ✅ **Bancos com regulagem de altura**
- ✅ **Suspensão confortável**
- ✅ **Isolamento acústico** adequado

### **Categorias Ideais**

1. **SUV Compacto** (Melhor opção)
   - Espaço elevado
   - Boa visibilidade
   - Porta-malas generoso
   - Sensação de segurança

2. **SUV Médio** (Famílias grandes)
   - Máximo espaço
   - 7 lugares (opcional)
   - Conforto superior

3. **Sedan Médio** (Alternativa econômica)
   - Porta-malas grande
   - Conforto de rodagem
   - Menor custo

4. **Minivan/Van** (Famílias muito grandes)
   - 7-8 lugares
   - Máximo espaço interno
   - Versatilidade

### **Top 15 Modelos Recomendados**

#### **Faixa R$ 80.000 - R$ 120.000**
1. **Jeep Compass Sport** - R$ 95.990
   - 6 airbags, ISOFIX, ESP
   - Porta-malas: 438L
   - Espaço traseiro: excelente
   
2. **Nissan Kicks SV** - R$ 98.990
   - 6 airbags, ISOFIX
   - Porta-malas: 432L
   - Tecnologia embarcada

3. **Hyundai Creta Comfort** - R$ 105.990
   - 6 airbags, ISOFIX, ESP
   - Porta-malas: 431L
   - Garantia 5 anos

4. **Volkswagen T-Cross Comfortline** - R$ 109.990
   - 6 airbags, ISOFIX
   - Porta-malas: 373L
   - Qualidade VW

5. **Chevrolet Tracker Premier** - R$ 112.990
   - 6 airbags, ISOFIX
   - Porta-malas: 401L
   - OnStar integrado

#### **Faixa R$ 120.000 - R$ 180.000**
6. **Toyota Corolla XEi** - R$ 139.990
   - 7 airbags, ISOFIX, TSS
   - Porta-malas: 470L
   - Confiabilidade Toyota

7. **Honda Civic EXL** - R$ 149.990
   - 6 airbags, ISOFIX, VSA
   - Porta-malas: 519L
   - Honda Sensing

8. **Jeep Compass Longitude** - R$ 145.990
   - 7 airbags, ISOFIX
   - Porta-malas: 438L
   - 4x4 (opcional)

9. **Hyundai Tucson GLS** - R$ 159.990
   - 6 airbags, ISOFIX
   - Porta-malas: 513L
   - Espaço superior

10. **Volkswagen Tiguan Allspace** - R$ 169.990
    - 7 lugares, 7 airbags
    - Porta-malas: 700L (5 lugares)
    - Máximo espaço

#### **Faixa R$ 180.000+**
11. **Toyota Corolla Cross XRE** - R$ 189.990
    - 7 airbags, ISOFIX, TSS
    - Porta-malas: 487L
    - SUV + confiabilidade

12. **Honda CR-V Touring** - R$ 219.990
    - 6 airbags, ISOFIX
    - Porta-malas: 589L
    - Espaço premium

13. **Jeep Commander Longitude** - R$ 229.990
    - 7 lugares, 7 airbags
    - Porta-malas: 233L (7 lugares)
    - SUV robusto

14. **Volvo XC40 T4** - R$ 249.990
    - 7 airbags, ISOFIX
    - Segurança Volvo
    - Tecnologia avançada

15. **Toyota SW4 SRX** - R$ 329.990
    - 7 lugares, 7 airbags
    - 4x4, robustez
    - Máxima segurança

### **Prioridades Recomendadas (1-5)**

```json
{
  "seguranca": 5,      // Máxima prioridade
  "espaco": 5,         // Muito importante
  "conforto": 4,       // Importante
  "economia": 3,       // Moderado
  "performance": 2     // Menos importante
}
```

### **Filtros Eliminatórios**

```json
{
  "must_haves": [
    "ISOFIX",
    "6_airbags",
    "controle_estabilidade",
    "abs_ebd"
  ],
  "ano_minimo": 2018,
  "km_maxima": 80000,
  "portas": 4,
  "lugares": 5
}
```

### **Perguntas Adicionais no Questionário**

1. **Tamanho da família?**
   - 2-3 pessoas → Sedan/SUV compacto
   - 4-5 pessoas → SUV médio
   - 6+ pessoas → SUV 7 lugares/Minivan

2. **Tem crianças?**
   - Sim → ISOFIX obrigatório, portas traseiras amplas
   - Não → Flexibilidade maior

3. **Tem idosos?**
   - Sim → Entrada alta (SUV), bancos confortáveis
   - Não → Flexibilidade maior

4. **Viagens longas frequentes?**
   - Sim → Conforto e porta-malas maiores
   - Não → Pode priorizar cidade

### **Justificativas de Recomendação**

Quando recomendar para família, destacar:
- ✅ "6 airbags para máxima proteção da família"
- ✅ "ISOFIX para fixação segura de cadeirinha"
- ✅ "Porta-malas de 438L comporta compras e bagagens"
- ✅ "Espaço traseiro amplo para conforto das crianças"
- ✅ "Controle de estabilidade para segurança em curvas"

### **Custo de Propriedade (5 anos)**

**Exemplo: Jeep Compass Sport**
```
Compra:           R$ 95.990
Combustível:      R$ 72.000 (12.000 km/ano, R$ 6/L, 10 km/L)
Manutenção:       R$ 15.000 (revisões + peças)
Seguro:           R$ 18.000 (R$ 3.600/ano)
IPVA:             R$ 19.200 (4% ao ano)
Depreciação:      R$ 28.800 (30% em 5 anos)
──────────────────────────────
TOTAL 5 anos:     R$ 248.990
Custo/mês:        R$ 4.150
```

### **Comparação: Família vs Outros Perfis**

| Aspecto | Família | Trabalho | Lazer |
|---------|---------|----------|-------|
| Segurança | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Espaço | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Economia | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Performance | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Conforto | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

