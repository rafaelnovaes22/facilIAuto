# 🔒 LGPD e Uso de Dados - FacilIAuto

## Princípio Fundamental

**"Se sua avó não entende, é muito técnico"**

Toda comunicação sobre dados deve usar linguagem simples e clara.

## Dados que Coletamos

### 1. Dados Obrigatórios (para funcionar)
- ✅ Orçamento para compra do carro
- ✅ Tipo de uso (família, trabalho, etc.)
- ✅ Número de pessoas que vão usar
- ✅ Prioridades (economia, espaço, etc.)

### 2. Dados Opcionais (melhoram recomendações)
- 💰 Faixa de renda mensal
- 📍 Cidade e estado
- 🚗 Marcas e tipos preferidos
- ⚙️ Preferência de câmbio

## Como Usamos os Dados

### Faixa de Renda (Opcional)

**Para o usuário:**
- Mostrar quanto vai gastar por mês (parcela + combustível + seguro + IPVA)
- Recomendar carros que cabem no bolso
- Calcular parcelas que consegue pagar
- Indicar se o carro "cabe no orçamento"

**Para melhorar o sistema:**
- Dados anônimos ajudam a treinar a IA
- Melhorar recomendações para todos
- Entender padrões de compra

**O que NUNCA fazemos:**
- ❌ Vender dados
- ❌ Compartilhar com terceiros
- ❌ Enviar spam
- ❌ Vincular à identidade do usuário

## Glossário de Termos Simplificados

Use sempre a linguagem da DIREITA:

| ❌ Termo Técnico | ✅ Linguagem Simples |
|-----------------|---------------------|
| TCO (Total Cost of Ownership) | Custo mensal total / Quanto você vai gastar por mês |
| Financiamento | Parcelas do carro |
| IPVA | Imposto do carro |
| Depreciação | Quanto o carro desvaloriza |
| Manutenção | Consertos e revisões |
| Machine Learning / IA | Sistema que aprende e melhora |
| Anonimização | Seus dados sem seu nome |
| LGPD | Lei que protege seus dados |
| Consentimento | Autorização / Permissão |
| Dados pessoais | Suas informações |

## Implementação de Consentimento

### Quando Coletar Consentimento

**SIM - Precisa de consentimento explícito:**
- Faixa de renda mensal
- Dados financeiros detalhados
- Uso para ML/IA (se identificável)

**NÃO - Não precisa (necessário para o serviço):**
- Orçamento para compra
- Preferências de carro
- Prioridades de uso

### Como Pedir Consentimento

```typescript
// ✅ BOM - Linguagem simples
"Ajuda a mostrar quanto você vai gastar por mês e 
recomendar carros que cabem no seu bolso"

// ❌ RUIM - Linguagem técnica
"Permite calcular TCO e otimizar recomendações 
através de algoritmos de ML"
```

### Estrutura do Modal de Consentimento

1. **Título claro**: "Como usamos sua renda mensal"
2. **O que coletamos**: Explicar de forma simples
3. **Como usamos**: Benefícios concretos para o usuário
4. **O que NUNCA fazemos**: Lista de garantias
5. **Segurança**: Ícones e linguagem tranquilizadora
6. **Direitos**: "Você pode mudar de ideia"

## Anonimização para ML

### Dados que PODEM ser usados para ML

```python
# ✅ Dados anonimizados
ml_data = {
    "user_hash": "abc123...",  # Hash irreversível
    "income_bracket": "5000-8000",  # Faixa, não valor exato
    "region": "SP",  # Estado, não cidade
    "budget_range": (50000, 100000),
    "accepted_tco_percentage": 0.35,
    "clicked_categories": ["SUV", "Sedan"],
    "behavior_pattern": "price_conscious"
}
```

### Dados que NÃO PODEM ser usados

```python
# ❌ Dados identificáveis
forbidden_data = {
    "name": "João Silva",
    "cpf": "123.456.789-00",
    "email": "joao@email.com",
    "phone": "(11) 99999-9999",
    "exact_income": 7500,
    "address": "Rua X, 123"
}
```

## Direitos do Usuário (LGPD)

### Deve ser fácil para o usuário:

1. **Ver seus dados** - Exportar em formato legível
2. **Apagar seus dados** - Botão "Excluir minha conta"
3. **Corrigir dados** - Editar informações
4. **Revogar consentimento** - Desmarcar checkbox
5. **Portabilidade** - Baixar dados em JSON/CSV

### Implementação Recomendada

```typescript
// Página de Privacidade do Usuário
<PrivacyDashboard>
  <DataExport />        // Baixar meus dados
  <ConsentManager />    // Gerenciar autorizações
  <DataDeletion />      // Excluir minha conta
</PrivacyDashboard>
```

## Retenção de Dados

### Dados de Sessão (temporários)
- **Duração**: Apenas durante a sessão
- **Armazenamento**: Memória / sessionStorage
- **Exemplos**: Faixa de renda, preferências temporárias

### Dados de Conta (permanentes)
- **Duração**: Até o usuário excluir
- **Armazenamento**: Banco de dados
- **Exemplos**: Email, histórico de buscas (se criar conta)

### Dados de ML (anonimizados)
- **Duração**: 2 anos
- **Armazenamento**: Data warehouse
- **Exemplos**: Padrões de comportamento agregados

## Comunicação com o Usuário

### Badges de Segurança

```typescript
// ✅ Use ícones e cores tranquilizadoras
<Alert status="info" colorScheme="blue">
  <AlertIcon as={FaLock} />
  Seus dados são seguros e anônimos
</Alert>

<Badge colorScheme="green">
  <Icon as={FaShieldAlt} />
  Protegido por LGPD
</Badge>
```

### Tooltips Explicativos

```typescript
// ✅ Explicar termos técnicos
<Tooltip label="Custo Total: tudo que você vai gastar por mês">
  <Text>Custo mensal estimado</Text>
</Tooltip>
```

## Checklist de Conformidade LGPD

Antes de coletar qualquer dado financeiro:

- [ ] Explicou em linguagem simples o que coleta?
- [ ] Explicou como vai usar?
- [ ] Deixou claro que é opcional?
- [ ] Mostrou o que NUNCA vai fazer?
- [ ] Ofereceu opção "Prefiro não informar"?
- [ ] Dados serão anonimizados para ML?
- [ ] Usuário pode revogar consentimento?
- [ ] Tem link para política de privacidade?
- [ ] Usa HTTPS (conexão segura)?
- [ ] Tem prazo de retenção definido?

## Exemplos de Comunicação

### ✅ BOM - Linguagem Simples

**Título**: "Qual sua renda mensal? (Opcional)"

**Descrição**: "Ajuda a mostrar quanto você vai gastar por mês e recomendar carros que cabem no seu bolso"

**Modal**: 
- "Mostrar o custo real"
- "Recomendar carros que cabem no bolso"
- "Melhorar para todo mundo"

### ❌ RUIM - Linguagem Técnica

**Título**: "Informe sua capacidade financeira"

**Descrição**: "Permite calcular TCO e otimizar recomendações através de ML"

**Modal**:
- "Calcular Total Cost of Ownership"
- "Treinar modelo de Machine Learning"
- "Anonimizar dados para data warehouse"

## Contato e Suporte

**Email de Privacidade**: privacidade@faciliauto.com.br

**Tempo de Resposta**: Até 48 horas

**Encarregado de Dados (DPO)**: [Nome do responsável]

---

## Referências

- [Lei Geral de Proteção de Dados (LGPD)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Guia LGPD para Startups](https://www.gov.br/anpd/pt-br)
- [Boas Práticas de UX para Privacidade](https://www.nngroup.com/articles/privacy-ux/)

---

**Última atualização**: 2025-01-05
**Versão**: 1.0
**Responsável**: Equipe FacilIAuto
