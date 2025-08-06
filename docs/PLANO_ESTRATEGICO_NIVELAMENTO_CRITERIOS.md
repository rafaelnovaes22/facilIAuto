# 🎯 PLANO ESTRATÉGICO: NIVELAMENTO DE CRITÉRIOS

## 📋 **OBJETIVO PRINCIPAL**

**Elevar os perfis urbano, viagem e família ao mesmo nível de precisão do trabalho/negócios (98.5%)**

## 🚨 **SITUAÇÃO ATUAL vs META**

| Perfil | Status Atual | Meta | Gap |
|--------|-------------|------|-----|
| 💼 **Trabalho** | ✅ 98.5% (24.62/25) | ✅ Mantido | 0% |
| 🚗 **Urbano** | ❌ 12.7% (3.17/25) | 🎯 90%+ | +77.3% |
| ✈️ **Viagem** | ❌ 14.0% (3.50/25) | 🎯 90%+ | +76.0% |
| 👨‍👩‍👧‍👦 **Família** | ❌ 12.0% (3.00/25) | 🎯 90%+ | +78.0% |

---

# 🚗 **FASE 1: PERFIL URBANO**

## 🎯 **Subsegmentos Identificados**

### 1. **Primeiro Carro** (Jovens 18-25 anos)
- **Perfil**: Estudantes, primeiro emprego, orçamento limitado
- **Prioridades**: Economia máxima, segurança, facilidade manutenção
- **Exemplos**: Gol, Palio, Ka, Celta

### 2. **Executivo Urbano** (25-45 anos)
- **Perfil**: Profissionais, renda média-alta, imagem importante
- **Prioridades**: Conforto, tecnologia, status, economia moderada
- **Exemplos**: Civic, Corolla, Jetta, A3

### 3. **Aposentado Urbano** (60+ anos)
- **Perfil**: Uso eventual, facilidade operação, conforto
- **Prioridades**: Simplicidade, confiabilidade, baixa manutenção
- **Exemplos**: Etios, Logan, Sandero, March

### 4. **Família Urbana** (Casal + 1-2 filhos)
- **Perfil**: Uso misto cidade/família, versatilidade
- **Prioridades**: Espaço moderado, segurança, praticidade
- **Exemplos**: Onix, HB20, Virtus, Polo

## ⚖️ **Critérios Técnicos Específicos (9 critérios)**

### 🔥 **PESO ALTO (20% cada)**

#### 1. **Economia Combustível Urbana** (20%)
```python
"economia_combustivel_urbana": {
    "peso": 20,
    "consumo_cidade_minimo": 12,  # km/l
    "cilindradas_ideais": [1.0, 1.4],
    "marcas_economicas": ["Honda", "Toyota", "Chevrolet", "Nissan"],
    "tecnologias_eco": ["flex", "start_stop", "híbrido"]
}
```

#### 2. **Facilidade Manobra/Estacionamento** (20%)
```python
"facilidade_manobra": {
    "peso": 20,
    "categorias_ideais": ["Hatch", "Sedan Compacto"],
    "comprimento_max": 4.2,  # metros
    "raio_giro_max": 5.0,    # metros
    "sistemas_assistencia": ["sensores", "camera_re", "park_assist"]
}
```

### 📊 **PESO MÉDIO (15% cada)**

#### 3. **Tecnologia Conectividade** (15%)
```python
"tecnologia_conectividade": {
    "peso": 15,
    "essenciais": ["central_multimidia", "bluetooth", "usb"],
    "desejados": ["android_auto", "apple_carplay", "wifi"],
    "navegacao": ["gps_integrado", "waze_nativo"],
    "subsegmento_boost": {"executivo": 1.5}  # 50% mais peso
}
```

#### 4. **Segurança Trânsito Urbano** (15%)
```python
"seguranca_urbana": {
    "peso": 15,
    "basicos_obrigatorios": ["abs", "airbag_duplo", "cintos_3pontos"],
    "avancados": ["controle_estabilidade", "assistente_frenagem"],
    "visibilidade": ["faróis_led", "retrovisores_eletricos"],
    "subsegmento_boost": {"primeiro_carro": 1.3}
}
```

### 📋 **PESO BAIXO (10% ou menos)**

#### 5. **Custo Manutenção Urbana** (10%)
```python
"custo_manutencao_urbana": {
    "peso": 10,
    "marcas_economicas": ["Chevrolet", "Fiat", "Volkswagen", "Renault"],
    "pecas_disponiveis": True,
    "rede_autorizada": ["ampla", "acessivel"],
    "intervalos_revisao": {"ideal_km": 10000, "max_km": 15000}
}
```

#### 6. **Praticidade Urbana** (5%)
```python
"praticidade_urbana": {
    "peso": 5,
    "porta_malas_litros": {"minimo": 250, "ideal": 350},
    "altura_solo": {"minimo": 14, "maximo": 18},  # cm
    "portas": {"minimo": 4, "ideal": 5},
    "facilidades": ["vidros_eletricos", "travamento_central"]
}
```

#### 7. **Conforto Urbano** (3%)
```python
"conforto_urbano": {
    "peso": 3,
    "clima": ["ar_condicionado", "ventilacao_eficiente"],
    "ergonomia": ["direcao_assistida", "bancos_regulaveis"],
    "ruido": ["isolamento_acustico", "motor_silencioso"]
}
```

#### 8. **Sustentabilidade Urbana** (2%)
```python
"sustentabilidade_urbana": {
    "peso": 2,
    "tipos_motor": ["flex", "híbrido", "elétrico"],
    "emissoes": ["euro_5", "proconve_l6"],
    "eficiencia": ["baixa_pegada_carbono"]
}
```

---

# ✈️ **FASE 2: PERFIL VIAGEM**

## 🎯 **Subsegmentos Identificados**

### 1. **Turismo Familiar** (Família 4+ pessoas)
- **Perfil**: Viagens de lazer, finais de semana, férias
- **Prioridades**: Espaço, conforto, segurança, bagagem
- **Exemplos**: Tiguan, CR-V, Compass, Tucson

### 2. **Viajante Solo/Casal** (1-2 pessoas)
- **Perfil**: Aventureiros, profissionais, aposentados viajantes
- **Prioridades**: Performance, economia rodovia, prazer dirigir
- **Exemplos**: Corolla Cross, T-Cross, Nivus, Kicks

### 3. **Executivo Viajante** (Profissionais)
- **Perfil**: Viagens trabalho, conforto premium, imagem
- **Prioridades**: Conforto máximo, tecnologia, status
- **Exemplos**: Accord, Passat, A4, Camry

### 4. **Aventureiro Off-Road** (Aventura/Esporte)
- **Perfil**: Trilhas, camping, aventura, robustez
- **Prioridades**: Tração 4x4, altura solo, durabilidade
- **Exemplos**: Hilux, Amarok, Frontier, Triton

## ⚖️ **Critérios Técnicos Específicos (9 critérios)**

### 🔥 **PESO ALTO (20% cada)**

#### 1. **Performance Rodovia** (20%)
```python
"performance_rodovia": {
    "peso": 20,
    "potencia_minima": 120,  # HP
    "torque_minimo": 150,    # Nm
    "aceleracao_max": 12,    # 0-100 km/h em segundos
    "velocidade_cruzeiro": {"confortavel": 120, "maxima": 180},
    "subsegmento_boost": {"executivo": 1.3, "aventureiro": 1.2}
}
```

#### 2. **Segurança Rodoviária** (20%)
```python
"seguranca_rodoviaria": {
    "peso": 20,
    "sistemas_obrigatorios": ["abs", "esp", "controle_tracao"],
    "airbags_minimos": 4,
    "assistencias": ["cruise_control", "alerta_colisao", "frenagem_automatica"],
    "estrutura": ["carroceria_reforçada", "zonas_deformacao"],
    "avaliacao_minima": 4  # estrelas
}
```

### 📊 **PESO MÉDIO (15% cada)**

#### 3. **Espaço Bagagem/Passageiros** (15%)
```python
"espaco_viagem": {
    "peso": 15,
    "porta_malas_litros": {"minimo": 400, "ideal": 600},
    "bagageiro_teto": True,
    "bancos_reclinaveis": True,
    "espaco_pernas": {"traseiro_minimo": 80},  # cm
    "subsegmento_boost": {"turismo_familiar": 1.4}
}
```

#### 4. **Conforto Viagens Longas** (15%)
```python
"conforto_viagem": {
    "peso": 15,
    "bancos": ["ergonomicos", "apoio_lombar", "regulagem_altura"],
    "clima": ["ar_digital", "zonas_independentes"],
    "tecnologia": ["sistema_som_premium", "carregamento_wireless"],
    "conveniencia": ["piloto_automatico", "volante_multifuncional"]
}
```

### 📋 **PESO BAIXO (10% ou menos)**

#### 5. **Autonomia Combustível** (10%)
```python
"autonomia_combustivel": {
    "peso": 10,
    "tanque_minimo": 50,     # litros
    "consumo_rodovia": 8,    # km/l mínimo
    "autonomia_minima": 400, # km
    "indicador_consumo": True
}
```

#### 6. **Robustez/Durabilidade** (5%)
```python
"robustez_viagem": {
    "peso": 5,
    "altura_solo": {"minima": 16, "ideal": 20},  # cm
    "suspeensao": ["independente", "amortecedores_gas"],
    "pneus": ["perfil_adequado", "estepe_completo"],
    "subsegmento_boost": {"aventureiro": 2.0}
}
```

#### 7. **Tecnologia Viagem** (3%)
```python
"tecnologia_viagem": {
    "peso": 3,
    "navegacao": ["gps_offline", "mapas_atualizados"],
    "conectividade": ["wifi_hotspot", "multiplas_usb"],
    "entretenimento": ["telas_traseiras", "sistema_audio_premium"]
}
```

#### 8. **Versatilidade** (2%)
```python
"versatilidade_viagem": {
    "peso": 2,
    "configuracoes": ["bancos_rebativeis", "assoalho_plano"],
    "acessorios": ["rack_teto", "engate_reboque"],
    "adaptabilidade": ["diferentes_terrenos", "cargas_variadas"]
}
```

---

# 👨‍👩‍👧‍👦 **FASE 3: PERFIL FAMÍLIA**

## 🎯 **Subsegmentos Identificados**

### 1. **Família Pequena** (Casal + 1-2 filhos pequenos)
- **Perfil**: Crianças 0-10 anos, cadeirinhas, praticidade
- **Prioridades**: Segurança infantil, facilidade acesso, economia
- **Exemplos**: Virtus, Cronos, Argo, Polo

### 2. **Família Média** (Casal + 2-3 filhos)
- **Perfil**: Crianças/adolescentes, versatilidade, espaço
- **Prioridades**: 7 lugares, espaço bagagem, conforto
- **Exemplos**: Spin, Mobilio, BR-V, Stepway

### 3. **Família Grande** (5+ pessoas)
- **Perfil**: Múltiplas crianças, avós, grupos grandes
- **Prioridades**: Máximo espaço, múltiplas cadeirinhas
- **Exemplos**: H1, Stavic, Carnival, Master

### 4. **Família Aventureira** (Esporte/Lazer)
- **Perfil**: Atividades ao ar livre, esportes, camping
- **Prioridades**: SUV, capacidade carga, versatilidade
- **Exemplos**: Duster, EcoSport, Tracker, Creta

## ⚖️ **Critérios Técnicos Específicos (9 critérios)**

### 🔥 **PESO ALTO (25% cada)**

#### 1. **Segurança Familiar Avançada** (25%)
```python
"seguranca_familiar": {
    "peso": 25,
    "sistemas_obrigatorios": ["isofix", "abs", "esp", "airbag_cortina"],
    "airbags_minimos": 6,
    "portas_crianca": True,
    "vidros_temperados": True,
    "avaliacao_minima": 5,  # estrelas
    "subsegmento_boost": {"familia_pequena": 1.2}
}
```

#### 2. **Espaço Passageiros/Configuração** (25%)
```python
"espaco_familiar": {
    "peso": 25,
    "lugares_minimos": {"pequena": 5, "media": 7, "grande": 8},
    "isofix_pontos": {"minimos": 2, "ideais": 3},
    "espaco_pernas": {"traseiro": 85, "terceira_fileira": 70},  # cm
    "altura_interna": {"minima": 95},  # cm
    "configuracoes": ["bancos_rebativeis", "acesso_terceira_fileira"]
}
```

### 📊 **PESO MÉDIO (15% cada)**

#### 3. **Praticidade Familiar** (15%)
```python
"praticidade_familiar": {
    "peso": 15,
    "portas": {"minimas": 4, "ideais": 5},
    "abertura_portas": {"ampla": True, "eletrica": "desejavel"},
    "porta_malas": {"minimo": 300, "ideal": 500, "bancos_rebatidos": 1000},
    "altura_embarque": {"maxima": 65},  # cm
    "facilidades": ["tampa_malas_eletrica", "sensor_estacionamento"]
}
```

#### 4. **Conforto Entretenimento** (15%)
```python
"conforto_entretenimento": {
    "peso": 15,
    "clima": ["ar_traseiro", "zonas_independentes"],
    "bancos": ["capitao", "regulagem_individual"],
    "entretenimento": ["telas_individuais", "entrada_headphones"],
    "conveniencia": ["porta_objetos", "compartimentos_diversos"],
    "subsegmento_boost": {"familia_media": 1.3, "familia_grande": 1.4}
}
```

### 📋 **PESO BAIXO (10% ou menos)**

#### 5. **Facilidade Acesso** (10%)
```python
"facilidade_acesso": {
    "peso": 10,
    "portas_deslizantes": {"van": True, "desejavel": "outros"},
    "degraus_baixos": True,
    "apoios_mao": True,
    "largura_abertura": {"minima": 65},  # cm
    "subsegmento_boost": {"familia_grande": 1.5}
}
```

#### 6. **Economia Familiar** (5%)
```python
"economia_familiar": {
    "peso": 5,
    "consumo_misto": {"minimo": 8, "ideal": 10},  # km/l
    "tanque_adequado": {"minimo": 45},  # litros
    "autonomia": {"minima": 350},  # km
    "manutencao": ["intervalos_longos", "custos_baixos"]
}
```

#### 7. **Durabilidade Uso Intenso** (3%)
```python
"durabilidade_familiar": {
    "peso": 3,
    "estrutura": ["reforçada", "resistente_desgaste"],
    "interior": ["materiais_laváveis", "resistente_riscos"],
    "mecanica": ["robusta", "baixa_manutencao"],
    "garantia": {"minima": 3}  # anos
}
```

#### 8. **Versatilidade Configuração** (2%)
```python
"versatilidade_familiar": {
    "peso": 2,
    "modularidade": ["bancos_removiveis", "configuracao_variavel"],
    "adaptabilidade": ["carga", "passageiros", "misto"],
    "acessorios": ["ganchos", "redes", "organizadores"]
}
```

---

# 📅 **CRONOGRAMA DE IMPLEMENTAÇÃO**

## **SPRINT 1: Perfil Urbano (Semana 1-2)**
- ✅ Definir subsegmentos e critérios
- ✅ Implementar lógica de scoring
- ✅ Criar sugestões específicas
- ✅ Testes unitários
- ✅ Validação com dados reais

## **SPRINT 2: Perfil Viagem (Semana 3-4)**
- ✅ Definir subsegmentos e critérios
- ✅ Implementar lógica de scoring
- ✅ Criar sugestões específicas
- ✅ Testes unitários
- ✅ Validação com dados reais

## **SPRINT 3: Perfil Família (Semana 5-6)**
- ✅ Definir subsegmentos e critérios
- ✅ Implementar lógica de scoring
- ✅ Criar sugestões específicas
- ✅ Testes unitários
- ✅ Validação com dados reais

## **SPRINT 4: Integração e Validação (Semana 7)**
- ✅ Testes E2E completos
- ✅ Validação comparativa
- ✅ Ajustes finos
- ✅ Documentação final

---

# 📊 **MÉTRICAS DE SUCESSO**

## **KPIs Técnicos**
- **Score mínimo**: 22/25 (88%) para cada perfil
- **Cobertura de critérios**: 9 critérios específicos cada
- **Sugestões**: Mínimo 8 contextualizadas por perfil
- **Testes**: 100% de cobertura unitária

## **KPIs de Qualidade**
- **Precisão**: 90%+ de matching adequado
- **Especificidade**: Valores técnicos concretos
- **Subsegmentação**: 4 subsegmentos por perfil
- **Consistência**: Padrão uniforme entre perfis

## **KPIs de Experiência**
- **Relevância**: Sugestões aplicáveis
- **Clareza**: Critérios compreensíveis
- **Actionabilidade**: Orientações práticas
- **Personalização**: Matching por subsegmento

---

# 🏆 **RESULTADO ESPERADO**

## **ANTES** (Atual)
```
💼 Trabalho: 98.5% precisão
🚗 Urbano:   12.7% precisão  
✈️ Viagem:   14.0% precisão
👨‍👩‍👧‍👦 Família: 12.0% precisão
MÉDIA GERAL: 34.3%
```

## **DEPOIS** (Meta)
```
💼 Trabalho: 98.5% precisão ✅
🚗 Urbano:   90.0% precisão 🎯
✈️ Viagem:   90.0% precisão 🎯  
👨‍👩‍👧‍👦 Família: 90.0% precisão 🎯
MÉDIA GERAL: 92.1%
```

**MELHORIA**: +57.8 pontos percentuais na precisão média do sistema

---

## 🚀 **BENEFÍCIOS ESPERADOS**

### **Para o Sistema**
- ✅ **Consistência total** entre todos os perfis
- ✅ **Qualidade profissional** uniforme
- ✅ **Credibilidade técnica** maximizada

### **Para os Usuários**
- ✅ **Recomendações precisas** independente do perfil
- ✅ **Sugestões contextualizadas** por subsegmento
- ✅ **Orientações técnicas** específicas

### **Para a Concessionária**
- ✅ **Argumentos de venda** técnicos para todos
- ✅ **Conversões otimizadas** por perfil
- ✅ **Diferenciação competitiva** total

**Status**: 🎯 **PLANO APROVADO** - Pronto para implementação