# Requirements: Questionário Simplificado para Usuários Leigos

## 📋 Introdução

O questionário atual usa termos técnicos que usuários comuns não entendem (ISOFIX, ESP, ABS, etc.). Precisamos simplificar a linguagem para tornar a experiência mais acessível e amigável.

## 🎯 Glossário

- **Usuário Leigo**: Pessoa sem conhecimento técnico sobre carros
- **Linguagem Simples**: Termos do dia-a-dia, sem jargão automotivo
- **Pergunta Contextual**: Pergunta baseada em situação real, não em especificação técnica

---

## 📝 Requirements

### Requirement 1: Linguagem Acessível no Questionário

**User Story**: Como usuário sem conhecimento técnico de carros, quero responder perguntas simples sobre meu uso, para que eu possa encontrar o carro ideal sem precisar entender termos técnicos.

#### Acceptance Criteria

1. WHEN o usuário acessa o questionário, THE Sistema SHALL apresentar perguntas em linguagem cotidiana
2. WHEN o usuário vê uma pergunta, THE Sistema SHALL evitar termos técnicos como "ISOFIX", "ESP", "ABS", "airbags"
3. WHEN o usuário precisa de esclarecimento, THE Sistema SHALL fornecer explicações visuais ou exemplos práticos
4. WHEN o usuário responde perguntas, THE Sistema SHALL traduzir respostas simples em requisitos técnicos internamente
5. THE Sistema SHALL usar ícones e imagens para facilitar compreensão

---

### Requirement 2: Perguntas Baseadas em Situações Reais

**User Story**: Como usuário, quero responder perguntas sobre como vou usar o carro, para que o sistema entenda minhas necessidades sem eu precisar saber especificações técnicas.

#### Acceptance Criteria

1. WHEN o usuário seleciona "Família", THE Sistema SHALL perguntar sobre situações reais (ex: "Você tem crianças pequenas?")
2. WHEN o usuário responde sobre crianças, THE Sistema SHALL automaticamente inferir necessidade de ISOFIX
3. WHEN o usuário indica viagens longas, THE Sistema SHALL inferir necessidade de porta-malas grande
4. THE Sistema SHALL converter situações em requisitos técnicos nos bastidores
5. THE Sistema SHALL nunca expor termos técnicos ao usuário

---

### Requirement 3: Explicações Visuais e Contextuais

**User Story**: Como usuário, quero entender o que cada opção significa, para que eu possa fazer escolhas informadas sem conhecimento técnico.

#### Acceptance Criteria

1. WHEN o usuário vê uma opção, THE Sistema SHALL fornecer ícone representativo
2. WHEN o usuário passa mouse sobre opção, THE Sistema SHALL mostrar tooltip explicativo
3. WHEN o usuário seleciona opção complexa, THE Sistema SHALL mostrar exemplo visual
4. THE Sistema SHALL usar linguagem de benefício (ex: "Mais seguro para crianças") ao invés de especificação técnica
5. THE Sistema SHALL fornecer comparações simples (ex: "Espaço como uma sala pequena")

---

### Requirement 4: Tradução Automática de Requisitos

**User Story**: Como sistema, quero traduzir respostas simples do usuário em requisitos técnicos, para que o algoritmo de recomendação funcione corretamente sem confundir o usuário.

#### Acceptance Criteria

1. WHEN o usuário diz "Tenho 2 crianças pequenas", THE Sistema SHALL adicionar requisito "ISOFIX obrigatório"
2. WHEN o usuário diz "Faço viagens longas", THE Sistema SHALL adicionar requisito "Porta-malas > 400L"
3. WHEN o usuário diz "Segurança é muito importante", THE Sistema SHALL adicionar requisito "6+ airbags, ESP, ABS"
4. WHEN o usuário diz "Quero economizar combustível", THE Sistema SHALL adicionar requisito "Consumo > 12 km/L"
5. THE Sistema SHALL manter mapeamento claro entre linguagem simples e requisitos técnicos

---

### Requirement 5: Feedback em Linguagem Simples

**User Story**: Como usuário, quero ver justificativas de recomendação em linguagem simples, para que eu entenda por que cada carro foi recomendado.

#### Acceptance Criteria

1. WHEN o sistema mostra recomendação, THE Sistema SHALL usar linguagem de benefício
2. WHEN o sistema menciona segurança, THE Sistema SHALL dizer "Protege bem sua família" ao invés de "6 airbags + ESP"
3. WHEN o sistema menciona espaço, THE Sistema SHALL dizer "Cabe toda a família confortavelmente" ao invés de "Porta-malas 438L"
4. WHEN o sistema menciona economia, THE Sistema SHALL dizer "Gasta pouco combustível" ao invés de "13,2 km/L"
5. THE Sistema SHALL usar comparações do dia-a-dia quando possível

---

## 🎨 Exemplos de Transformação

### ❌ ANTES (Técnico e Confuso)

**Pergunta**: "Seu carro precisa ter ISOFIX?"
- Usuário: "O que é ISOFIX?" 🤔

**Justificativa**: "Este carro tem 6 airbags, ESP, ABS com EBD e ISOFIX"
- Usuário: "Não entendi nada" 😕

---

### ✅ DEPOIS (Simples e Claro)

**Pergunta**: "Você vai transportar crianças pequenas (até 7 anos)?"
- Opções: "Sim" / "Não"
- Tooltip: "Crianças pequenas precisam de cadeirinha especial"
- Usuário: "Sim, tenho 2 filhos pequenos" ✅

**Justificativa**: "✅ Protege bem sua família com sistema de segurança completo"
- Sub-texto (opcional): "Inclui fixação segura para cadeirinha infantil"
- Usuário: "Entendi! É seguro para meus filhos" 😊

---

## 📊 Mapeamento: Linguagem Simples → Requisitos Técnicos

### Família

| Pergunta Simples | Resposta | Requisito Técnico Inferido |
|------------------|----------|----------------------------|
| "Tem crianças pequenas?" | Sim | ISOFIX obrigatório, 6+ airbags |
| "Quantas pessoas vão no carro?" | 4-5 | 5 lugares reais, espaço traseiro > 70cm |
| "Faz viagens longas?" | Sim | Porta-malas > 400L, conforto alto |
| "Segurança é prioridade?" | Sim | 6+ airbags, ESP, ABS, estrutura reforçada |

### Trabalho

| Pergunta Simples | Resposta | Requisito Técnico Inferido |
|------------------|----------|----------------------------|
| "Quantos km por mês?" | > 2.000 km | Economia crítica, consumo > 13 km/L |
| "Trajeto é cidade ou estrada?" | Cidade | Hatch/Sedan compacto, direção leve |
| "Quer gastar pouco?" | Sim | Manutenção < R$ 1.000/ano, seguro baixo |

### Primeiro Carro

| Pergunta Simples | Resposta | Requisito Técnico Inferido |
|------------------|----------|----------------------------|
| "É seu primeiro carro?" | Sim | Direção leve, boa visibilidade, compacto |
| "Tem experiência dirigindo?" | Pouca | Câmbio automático preferível, sensores |
| "Orçamento limitado?" | Sim | Seguro < R$ 3k/ano, evitar modelos visados |

---

## 🎯 Prioridades (Escala 1-5)

### ❌ ANTES (Confuso)

```
Dê nota de 1 a 5 para:
- Economia de combustível
- Espaço interno
- Performance do motor
- Conforto de rodagem
- Segurança veicular
```

Usuário: "Não sei a diferença entre performance e conforto" 🤔

---

### ✅ DEPOIS (Claro)

```
O que é mais importante para você?

🔋 Gastar pouco com combustível
   [Slider 1-5: Pouco importante → Muito importante]
   💡 Carros econômicos gastam menos no dia-a-dia

👨‍👩‍👧 Espaço para família e bagagens
   [Slider 1-5: Pouco importante → Muito importante]
   💡 Importante se você tem família ou faz viagens

⚡ Carro potente e ágil
   [Slider 1-5: Pouco importante → Muito importante]
   💡 Para quem gosta de dirigir com mais emoção

🛋️ Conforto e tecnologia
   [Slider 1-5: Pouco importante → Muito importante]
   💡 Bancos confortáveis, ar-condicionado, multimídia

🛡️ Segurança para você e sua família
   [Slider 1-5: Pouco importante → Muito importante]
   💡 Proteção em caso de acidente
```

---

## 📱 Exemplos de Interface

### Step 1: Uso Principal

```
Como você vai usar o carro?

[Card com ícone] 👨‍👩‍👧‍👦 Família
"Levar filhos, fazer compras, viagens"

[Card com ícone] 💼 Trabalho
"Ir e voltar do trabalho todo dia"

[Card com ícone] 🏖️ Lazer
"Viagens e passeios nos finais de semana"

[Card com ícone] 🚚 Trabalho com Carga
"Transportar produtos ou equipamentos"

[Card com ícone] 🎓 Meu Primeiro Carro
"Estou comprando meu primeiro carro"

[Card com ícone] 🚗 Uber/99
"Trabalhar com transporte de passageiros"
```

---

### Step 2: Perguntas Contextuais (Exemplo: Família)

```
Conte mais sobre sua família:

👶 Você tem crianças pequenas (até 7 anos)?
   ○ Sim, tenho
   ○ Não tenho
   💡 Crianças pequenas precisam de cadeirinha especial

👴 Alguém tem dificuldade para entrar/sair do carro?
   ○ Sim
   ○ Não
   💡 Carros mais altos são mais fáceis de entrar

🧳 Você faz viagens longas com frequência?
   ○ Sim, frequentemente
   ○ Às vezes
   ○ Raramente
   💡 Viagens precisam de espaço para bagagens

👨‍👩‍👧‍👦 Quantas pessoas vão no carro normalmente?
   ○ 2-3 pessoas
   ○ 4-5 pessoas
   ○ 6+ pessoas
```

---

### Step 3: Prioridades (Simplificado)

```
O que é mais importante para você?

Use os controles para indicar o que mais importa:

🛡️ Segurança
[━━━━━━━━━━] Muito importante
💡 Proteção para você e sua família

👨‍👩‍👧 Espaço
[━━━━━━━━━━] Muito importante
💡 Cabe toda a família e bagagens

🛋️ Conforto
[━━━━━━━━━━] Importante
💡 Viagens mais agradáveis

🔋 Economia
[━━━━━━━━━━] Moderado
💡 Gasta menos combustível

⚡ Potência
[━━━━━━━━━━] Menos importante
💡 Carro mais ágil e rápido
```

---

## ✅ Checklist de Implementação

### Questionário
- [ ] Remover todos os termos técnicos das perguntas
- [ ] Adicionar ícones para cada opção
- [ ] Adicionar tooltips explicativos
- [ ] Usar linguagem de benefício
- [ ] Adicionar exemplos visuais quando necessário

### Mapeamento
- [ ] Criar dicionário de tradução (simples → técnico)
- [ ] Implementar lógica de inferência de requisitos
- [ ] Testar todos os cenários de uso
- [ ] Validar que requisitos técnicos são gerados corretamente

### Resultados
- [ ] Traduzir justificativas técnicas em linguagem simples
- [ ] Usar comparações do dia-a-dia
- [ ] Destacar benefícios ao invés de especificações
- [ ] Adicionar sub-texto técnico (opcional, colapsado)

### Testes com Usuários
- [ ] Testar com 5+ usuários leigos
- [ ] Coletar feedback sobre clareza
- [ ] Identificar pontos de confusão
- [ ] Iterar até 100% de compreensão

---

## 🎯 Critérios de Sucesso

1. **Compreensão**: 100% dos usuários entendem todas as perguntas
2. **Confiança**: Usuários se sentem confiantes nas respostas
3. **Tempo**: Questionário completo em < 3 minutos
4. **Satisfação**: NPS > 8 na experiência do questionário
5. **Precisão**: Requisitos técnicos inferidos corretamente em 95%+ dos casos

---

**Criado em**: 15 de Outubro, 2025  
**Versão**: 1.0  
**Status**: 📋 REQUIREMENTS DEFINIDOS

