# Reset vs Editar - Guia Rápido

## 🔄 Dois Comportamentos Diferentes

### 1. Nova Pesquisa (RESET) 🆕

**O que faz:** Limpa TODOS os dados e começa do zero

**Quando usar:**
- Quer começar completamente do zero
- Não gostou dos resultados
- Quer explorar algo totalmente diferente

**Botões:**
- ← Voltar ao início
- Tentar Novamente
- Buscar Novamente

**Código:**
```typescript
const handleResetAndRestart = () => {
  resetForm() // Limpa tudo
  navigate('/questionario')
}
```

**Resultado:**
```
Antes: Orçamento R$ 50k-80k, Família, [5,4,3,4,5]
Depois: Orçamento R$ 50k-100k, Família, [3,3,3,3,3] (padrões)
```

---

### 2. Editar Pesquisa (EDIT) ✏️

**O que faz:** MANTÉM todos os dados, permite ajustes

**Quando usar:**
- Quer ajustar apenas alguns valores
- Gostou dos resultados mas quer refinar
- Quer ver como pequenas mudanças afetam

**Botão:**
- Editar (no resumo do perfil)

**Código:**
```typescript
const handleEditSearch = () => {
  setCurrentStep(0) // Volta para início, mas mantém dados
  navigate('/questionario')
}
```

**Resultado:**
```
Antes: Orçamento R$ 50k-80k, Família, [5,4,3,4,5]
Depois: Orçamento R$ 50k-80k, Família, [5,4,3,4,5] (mantém tudo)
```

---

## 📊 Comparação Rápida

| Aspecto | Nova Pesquisa 🆕 | Editar ✏️ |
|---------|------------------|-----------|
| **Dados** | ❌ Limpa tudo | ✅ Mantém tudo |
| **Valores** | Padrões | Preenchidos |
| **Uso** | Começar do zero | Ajustar valores |
| **Botões** | 3 botões | 1 botão |
| **Função** | `resetForm()` | `setCurrentStep(0)` |

---

## 🎯 Exemplos de Uso

### Exemplo 1: Usuário Não Encontrou Nada

**Situação:** Buscou R$ 10k-15k, não encontrou carros

**Ação:** Clica em "Tentar Novamente"

**Comportamento:** RESET 🆕
- Limpa tudo
- Pode tentar faixa diferente
- Começa do zero

---

### Exemplo 2: Usuário Quer Ajustar Orçamento

**Situação:** Buscou R$ 50k-80k, quer ver até R$ 100k

**Ação:** Clica em "Editar"

**Comportamento:** EDIT ✏️
- Mantém uso: Família
- Mantém prioridades: [5,4,3,4,5]
- Ajusta apenas orçamento: R$ 50k-100k
- Refaz pesquisa

---

### Exemplo 3: Usuário Quer Explorar Outro Perfil

**Situação:** Buscou para família, quer ver para trabalho

**Ação:** Clica em "Buscar Novamente"

**Comportamento:** RESET 🆕
- Limpa tudo
- Pode escolher "Trabalho"
- Novas prioridades
- Pesquisa completamente diferente

---

## 💡 Dicas de UX

### Para o Usuário:

**Use "Editar" quando:**
- ✅ Gostou dos resultados mas quer ver mais opções
- ✅ Quer aumentar/diminuir orçamento
- ✅ Quer ajustar uma prioridade
- ✅ Quer manter a maioria das escolhas

**Use "Buscar Novamente" quando:**
- ✅ Não gostou dos resultados
- ✅ Quer tentar algo completamente diferente
- ✅ Quer começar do zero
- ✅ Quer explorar outro perfil de uso

---

## 🔍 Como Identificar

### Visual no Frontend:

**Botão "Editar":**
```
┌─────────────────────────────────┐
│ 📋 Resumo do Perfil             │
│                                 │
│ Orçamento: R$ 50k - 80k         │
│ Uso: Família                    │
│ Prioridades: Economia, Espaço   │
│                                 │
│         [✏️ Editar]              │ ← Mantém dados
└─────────────────────────────────┘
```

**Botões de Reset:**
```
[← Voltar ao início]              ← Limpa tudo

[Tentar Novamente]                ← Limpa tudo

[Buscar Novamente]                ← Limpa tudo
```

---

## 🧪 Como Testar

### Teste 1: Editar Mantém Dados
1. Faça pesquisa: R$ 50k-80k, Família, Economia=5
2. Clique em "Editar"
3. ✅ Verifique: Orçamento ainda é R$ 50k-80k
4. ✅ Verifique: Uso ainda é Família
5. ✅ Verifique: Economia ainda é 5
6. Ajuste orçamento para R$ 50k-100k
7. Faça nova pesquisa
8. ✅ Verifique: Outros valores foram mantidos

### Teste 2: Reset Limpa Tudo
1. Faça pesquisa: R$ 50k-80k, Família, Economia=5
2. Clique em "Buscar Novamente"
3. ✅ Verifique: Orçamento voltou para R$ 50k-100k (padrão)
4. ✅ Verifique: Uso voltou para Família (padrão)
5. ✅ Verifique: Economia voltou para 3 (padrão)

---

## ✅ Checklist de Implementação

- [x] Handler `handleResetAndRestart()` criado
- [x] Handler `handleEditSearch()` criado
- [x] Botão "Voltar ao início" usa reset
- [x] Botão "Tentar Novamente" usa reset
- [x] Botão "Buscar Novamente" usa reset
- [x] Botão "Editar" usa edit
- [x] Analytics implementado
- [x] Documentação completa
- [x] Testes manuais realizados

---

## 🎉 Resultado

Agora o usuário tem **controle total** sobre sua experiência:

- **Quer começar do zero?** → Use botões de reset
- **Quer ajustar valores?** → Use botão editar

**Experiência clara, previsível e intuitiva!** ✨
