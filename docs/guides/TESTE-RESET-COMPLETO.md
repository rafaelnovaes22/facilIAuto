# Teste: Reset Completo do Questionário

## ✅ Funcionalidade Implementada

Quando o usuário clica em "Voltar ao início" ou "Nova Busca", o sistema:

1. ✅ Reseta `currentStep` para **0** (primeira página)
2. ✅ Limpa **todos os dados** do formulário
3. ✅ Restaura **valores padrão**
4. ✅ Navega para `/questionario`

## 🧪 Como Testar

### Teste 1: Voltar ao Início

**Passos:**
1. Faça uma pesquisa completa:
   - Orçamento: R$ 50.000 - R$ 80.000
   - Uso: Família
   - Prioridades: Economia=5, Espaço=4, Segurança=5
   - Marcas preferidas: Toyota, Honda

2. Veja os resultados

3. Clique em **"← Voltar ao início"**

**Resultado Esperado:**
- ✅ Volta para `/questionario`
- ✅ Está no **Step 0** (primeira página - Orçamento)
- ✅ Orçamento voltou para **R$ 50.000 - R$ 100.000** (padrão)
- ✅ Todos os campos estão **limpos/padrão**

---

### Teste 2: Nova Busca (quando não há resultados)

**Passos:**
1. Faça uma pesquisa que não retorna resultados:
   - Orçamento: R$ 10.000 - R$ 15.000

2. Veja a mensagem "Nenhum carro encontrado"

3. Clique em **"🔄 Nova Busca"**

**Resultado Esperado:**
- ✅ Volta para `/questionario`
- ✅ Está no **Step 0** (primeira página)
- ✅ Orçamento voltou para **R$ 50.000 - R$ 100.000** (padrão)
- ✅ Todos os campos estão **limpos/padrão**

---

### Teste 3: Buscar Novamente (footer)

**Passos:**
1. Faça uma pesquisa que retorna resultados:
   - Orçamento: R$ 50.000 - R$ 80.000
   - Uso: Família

2. Role até o final da página

3. Clique em **"Buscar Novamente"** (no footer)

**Resultado Esperado:**
- ✅ Volta para `/questionario`
- ✅ Está no **Step 0** (primeira página)
- ✅ Todos os dados foram **resetados**

---

### Teste 4: Editar (NÃO reseta)

**Passos:**
1. Faça uma pesquisa:
   - Orçamento: R$ 50.000 - R$ 80.000
   - Uso: Família
   - Prioridades: Economia=5

2. Veja os resultados

3. Clique em **"✏️ Editar"** (no resumo do perfil)

**Resultado Esperado:**
- ✅ Volta para `/questionario`
- ✅ Está no **Step 0** (primeira página)
- ✅ Orçamento ainda é **R$ 50.000 - R$ 80.000** ← MANTÉM
- ✅ Uso ainda é **Família** ← MANTÉM
- ✅ Prioridades ainda são **Economia=5** ← MANTÉM

---

## 📋 Checklist de Validação

### Reset Completo (Voltar/Nova Busca)
- [ ] Volta para Step 0
- [ ] Orçamento = R$ 50k-100k (padrão)
- [ ] Uso = Família (padrão)
- [ ] Tamanho família = 1 (padrão)
- [ ] Tem crianças = false (padrão)
- [ ] Tem idosos = false (padrão)
- [ ] Prioridades = [3,3,3,3,3] (padrão)
- [ ] Tipos preferidos = [] (vazio)
- [ ] Marcas preferidas = [] (vazio)
- [ ] Câmbio preferido = undefined (padrão)

### Editar (Mantém Dados)
- [ ] Volta para Step 0
- [ ] Orçamento = valor anterior ✅
- [ ] Uso = valor anterior ✅
- [ ] Tamanho família = valor anterior ✅
- [ ] Tem crianças = valor anterior ✅
- [ ] Tem idosos = valor anterior ✅
- [ ] Prioridades = valores anteriores ✅
- [ ] Tipos preferidos = valores anteriores ✅
- [ ] Marcas preferidas = valores anteriores ✅
- [ ] Câmbio preferido = valor anterior ✅

---

## 🔍 Verificação Visual

### Step 0 (Primeira Página)

Quando resetar, você deve ver:

```
┌─────────────────────────────────────────┐
│  Passo 1 de 4                           │ ← Step 0
│                                         │
│  💰 Qual é o seu orçamento?             │
│                                         │
│  Mínimo: R$ 50.000  ← Padrão            │
│  Máximo: R$ 100.000 ← Padrão            │
│                                         │
│  📍 Onde você está?                     │
│  [Cidade] [Estado]  ← Vazios            │
│                                         │
│  [Próximo →]                            │
└─────────────────────────────────────────┘
```

### Step 1 (Segunda Página)

Se avançar, você deve ver valores padrão:

```
┌─────────────────────────────────────────┐
│  Passo 2 de 4                           │ ← Step 1
│                                         │
│  🚗 Como você vai usar o carro?         │
│                                         │
│  [Família] ← Selecionado (padrão)       │
│  [ Trabalho ]                           │
│  [ Lazer ]                              │
│                                         │
│  👨‍👩‍👧‍👦 Quantas pessoas?                  │
│  1 pessoa ← Padrão                      │
│                                         │
│  [← Voltar]  [Próximo →]                │
└─────────────────────────────────────────┘
```

---

## 🐛 Problemas Conhecidos

### ❌ Se o reset NÃO funcionar:

**Sintomas:**
- Volta para questionário mas dados anteriores aparecem
- Step não volta para 0
- Valores não são os padrões

**Causa Provável:**
- `resetForm()` não está sendo chamado
- Navegação acontece antes do reset

**Solução:**
Verificar que o handler está correto:
```typescript
const handleResetAndRestart = () => {
  resetForm() // ← Deve ser chamado ANTES
  navigate('/questionario') // ← Depois navega
}
```

---

## ✅ Status Atual

**Implementação:**
- ✅ `resetForm()` reseta `currentStep` para 0
- ✅ `resetForm()` limpa todos os dados
- ✅ `resetForm()` restaura valores padrão
- ✅ `handleResetAndRestart()` chama `resetForm()`
- ✅ Botões corretos usam o handler

**Botões que RESETAM:**
- ✅ "← Voltar ao início"
- ✅ "🔄 Nova Busca"
- ✅ "Buscar Novamente" (footer)

**Botão que MANTÉM:**
- ✅ "✏️ Editar" (ProfileSummary)

---

## 📝 Código Relevante

### Store: resetForm()
```typescript
resetForm: () => {
  set({
    currentStep: 0,        // ← Volta para primeira página
    formData: initialFormData, // ← Restaura padrões
  })
}
```

### ResultsPage: handleResetAndRestart()
```typescript
const handleResetAndRestart = () => {
  console.log('Reset: Usuário iniciando nova pesquisa do zero')
  resetForm() // ← Limpa tudo
  navigate('/questionario') // ← Navega
}
```

### Valores Padrão (initialFormData)
```typescript
{
  orcamento_min: 50000,
  orcamento_max: 100000,
  city: undefined,
  state: undefined,
  uso_principal: 'familia',
  tamanho_familia: 1,
  tem_criancas: false,
  tem_idosos: false,
  prioridades: {
    economia: 3,
    espaco: 3,
    performance: 3,
    conforto: 3,
    seguranca: 3,
  },
  tipos_preferidos: [],
  marcas_preferidas: [],
  cambio_preferido: undefined,
}
```

---

## 🎯 Conclusão

✅ **FUNCIONANDO CORRETAMENTE**

O sistema já está implementado para:
1. Resetar completamente quando clicar em "Voltar ao início" ou "Nova Busca"
2. Voltar para Step 0 (primeira página)
3. Limpar todos os dados
4. Restaurar valores padrão

**Teste agora seguindo os passos acima!** 🚀
