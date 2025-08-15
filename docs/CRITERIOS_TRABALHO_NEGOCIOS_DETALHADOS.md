# 💼 CRITÉRIOS DETALHADOS: PERFIL TRABALHO/NEGÓCIOS

## 📋 Definição do Perfil

O perfil "Trabalho/Negócios" abrange **profissionais autônomos**, **microempreendedores**, **pequenos negócios** e **motoristas de aplicativo** que buscam veículos usados em concessionárias para fins profissionais.

## 🎯 Subsegmentos Principais

### 1. **Motoristas de Aplicativo** (Uber, 99, InDrive)
- **Foco**: Veículos econômicos, confortáveis, aceitos pelas plataformas
- **Critérios específicos**: Ano 2012+, 4 portas, ar-condicionado obrigatório

### 2. **Profissionais Autônomos (MEIs)**
- **Exemplos**: Eletricistas, representantes comerciais, técnicos, vendedores
- **Foco**: Espaço para equipamentos, deslocamento frequente

### 3. **Pequenos Negócios e Microempresas**
- **Exemplos**: Restaurantes, lojas, clínicas
- **Foco**: Logística, entregas, atendimento externo

### 4. **Serviços de Entrega e Transporte Leve**
- **Foco**: Utilitários leves, picapes, vans para transporte de mercadorias

## ⚖️ Critérios e Pesos do Algoritmo

### 🔥 **PESO ALTO (20% cada)**

#### 1. **Economia de Combustível** (20%)
- **Consumo mínimo**: 10 km/l na cidade
- **Cilindradas ideais**: 1.0, 1.4, 1.6
- **Impacto**: Fundamental para quem roda muito

#### 2. **Confiabilidade** (20%)
- **Marcas confiáveis**: Toyota, Honda, Chevrolet, Volkswagen
- **Quilometragem máxima**: 80.000 km
- **Impacto**: Uso intenso exige durabilidade

### 📊 **PESO MÉDIO (15% cada)**

#### 3. **Baixo Custo de Manutenção** (15%)
- **Marcas econômicas**: Chevrolet, Fiat, Volkswagen
- **Peças acessíveis**: Facilidade de encontrar componentes
- **Modelos populares**: Boost para Hatch e Sedan Compacto

#### 4. **Espaço e Capacidade** (15%)
- **Categorias versáteis**: Hatch, Sedan, SUV Compacto, Pickup, Van
- **Adaptabilidade**: Para equipamentos, passageiros ou mercadorias

### 📋 **PESO BAIXO (10% ou menos)**

#### 5. **Conforto e Tecnologia** (10%)
- **Essenciais**: Ar-condicionado, direção assistida, conectividade
- **Impacto**: Qualidade de vida no trabalho

#### 6. **Aceitação em Plataformas** (10%)
- **Ano mínimo**: 2012
- **Portas**: 4 portas obrigatórias
- **Ar-condicionado**: Obrigatório
- **Aplicação**: Específico para motoristas de app

#### 7. **Garantia e Procedência** (5%)
- **Concessionária**: Boost para origem confiável
- **Revisado**: Histórico de manutenção transparente

#### 8. **Facilidade de Financiamento** (3%)
- **CNPJ/MEI**: Opções específicas para empresas
- **Crédito empresarial**: Condições diferenciadas

#### 9. **Sustentabilidade** (2%)
- **Tipos de motor**: Flex, híbrido, elétrico
- **Metas ESG**: Para empresas com compromissos ambientais

## 🎯 Matching por Subsegmento

### **Motoristas de Aplicativo**
```python
Ideais: Chevrolet Onix, Logan, HB20, Corolla, Voyage, Fit
Critérios: Baixo consumo + conforto + aceitação plataformas
Peso especial: Aceitação plataformas (15% em vez de 10%)
```

### **Profissionais Autônomos**
```python
Ideais: Sedans, SUVs compactos, Picapes leves (Strada, Saveiro, Duster)
Critérios: Espaço + durabilidade + baixo custo manutenção
Peso especial: Espaço/capacidade (20% em vez de 15%)
```

### **Pequenos Negócios**
```python
Ideais: Utilitários leves, vans pequenas (Fiorino, Kangoo)
Critérios: Capacidade carga + confiabilidade + economia
Peso especial: Garantia/procedência (10% em vez de 5%)
```

### **Serviços de Entrega**
```python
Ideais: Veículos com capacidade de carga
Critérios: Capacidade + baixo custo operacional + acesso traseiro
Peso especial: Espaço/capacidade (25% em vez de 15%)
```

## 🔍 Filtros Aplicados

### **Filtros Primários**
- Ano/modelo aceito em apps (se aplicável)
- Tipo de carroceria por segmento
- Preço máximo definido pelo usuário
- Histórico de manutenção disponível

### **Filtros Secundários**
- Consumo mínimo de combustível
- Quilometragem máxima
- Presença de itens essenciais

## 💡 Sugestões Inteligentes

### **Para Motoristas de App**
- "Para Uber/99: ano 2012+, 4 portas, ar-condicionado obrigatório"
- "Onix, Logan e HB20 são aceitos e econômicos"

### **Para MEIs/Autônomos**
- "Considere espaço para ferramentas/equipamentos"
- "Marcas Chevrolet, Fiat, VW têm manutenção acessível"

### **Para Pequenos Negócios**
- "Concessionárias oferecem garantia e histórico transparente"
- "Facilidades de financiamento para MEI/CNPJ disponíveis"

### **Para Entregas**
- "Vans/pickups para maior capacidade de carga"
- "Fiorino e Kangoo ideais para entregas urbanas"

## 📊 Exemplo de Scoring

```python
Chevrolet Onix 1.4 LT (2018, 45.000km, 4 portas, ar-condicionado):
- Economia combustível: 18/20 (consumo 14 km/l)
- Confiabilidade: 15/20 (Chevrolet + baixa km)
- Baixo custo manutenção: 15/15 (marca econômica)
- Espaço/capacidade: 12/15 (hatch versátil)
- Conforto/tecnologia: 10/10 (tem essenciais)
- Aceitação plataformas: 10/10 (atende critérios)
- Garantia/procedência: 4/5 (concessionária)
- Financiamento: 3/3 (facilidades MEI)
- Sustentabilidade: 2/2 (flex)

TOTAL: 89/100 (Excelente para trabalho/apps)
```

## 🏆 Resultado Esperado

**Recomendações mais assertivas** para cada subsegmento de trabalho/negócios, considerando:
- ✅ **Critérios específicos** por tipo de atividade profissional
- ✅ **Pesos ajustados** conforme importância real
- ✅ **Sugestões contextualizadas** para cada necessidade
- ✅ **Matching inteligente** com características técnicas

---

**Implementação**: Integrada ao `UsoMatcher` em `app/uso_principal_processor.py`  
**Status**: ✅ **IMPLEMENTADO** - Janeiro 2025