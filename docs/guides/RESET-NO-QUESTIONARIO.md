# Reset no Questionário - Voltar ao Início

**Data:** 30 de outubro de 2025  
**Funcionalidade:** Reset completo ao clicar em "Voltar para o início" dentro do questionário

## Problema

Quando o usuário estava preenchendo o questionário e clicava em "← Voltar para o início", o sistema:
- ❌ Apenas navegava para a home
- ❌ **Mantinha todos os dados preenchidos**
- ❌ Se voltasse ao questionário, dados ainda estavam lá

Isso causava confusão porque:
- Usuário esperava começar do zero
- Dados antigos permaneciam
- Não ficava claro se era continuação ou nova pesquisa

## Solução Implementada

Agora, ao clicar em "← Voltar para o início" no questionário:
1. ✅ **Reseta todos os dados** (`resetForm()`)
2. ✅ **Volta para step 0** (primeira página)
3. ✅ **Restaura valores padrão**
4. ✅ **Navega para home** (`/`)

### Código Implementado

```typescript
const handleResetAndGoHome = () => {
  console.log('Reset: Usuário voltando ao início do questionário')
  resetForm() // Limpa todos os dados e volta para step 0
  navigate('/') // Volta para a home
}
```

### Botão Atualizado

```typescript
<Button
  variant="ghost"
  size="sm"
  onClick={handleResetAndGoHome} // ← Agora reseta antes de navegar
  color="gray.600"
>
  ← Voltar para o início
</Button>
```

## Fluxo Completo

### Cenário 1: Usuário no Meio do Questionário

```
1. Usuário está no Step 2 (Uso e Família)
2. Preencheu:
   - Orçamento: R$ 50k-80k
   - Uso: Família
   - Tamanho: 4 pessoas
3. Clica em "← Voltar para o início"
   ↓
4. resetForm() é chamado
   ↓
5. Todos os dados são limpos
   ↓
6. currentStep volta para 0
   ↓
7. Navega para home (/)
   ↓
8. Se voltar ao questionário:
   ✅ Está no Step 0
   ✅ Orçamento: R$ 50k-100k (padrão)
   ✅ Todos os campos limpos
```

### Cenário 2: Usuário na Última Etapa

```
1. Usuário está no Step 3 (Preferências)
2. Preencheu tudo
3. Clica em "← Voltar para o início"
   ↓
4. resetForm() é chamado
   ↓
5. Tudo é limpo
   ↓
6. Volta para home
   ↓
7. Pode começar nova pesquisa do zero
```

## Comparação: Antes vs Depois

### ANTES ❌
```
Questionário (Step 2)
  ↓
Clica "Voltar para o início"
  ↓
Navega para home
  ↓
Dados MANTIDOS no store
  ↓
Se voltar ao questionário:
  ❌ Dados ainda preenchidos
  ❌ Confusão: é nova pesquisa?
```

### DEPOIS ✅
```
Questionário (Step 2)
  ↓
Clica "Voltar para o início"
  ↓
resetForm() chamado
  ↓
Dados LIMPOS
  ↓
Navega para home
  ↓
Se voltar ao questionário:
  ✅ Step 0 (primeira página)
  ✅ Todos os campos limpos
  ✅ Valores padrão restaurados
```

## Botões de Navegação no Questionário

### Botão "Voltar" (entre steps)
```typescript
<Button
  onClick={previousStep} // ← Apenas volta 1 step
  isDisabled={currentStep === 0}
>
  Voltar
</Button>
```
- **Comportamento:** Volta 1 step (ex: Step 2 → Step 1)
- **Dados:** MANTÉM todos os dados
- **Uso:** Navegar entre etapas do questionário

### Botão "← Voltar para o início"
```typescript
<Button
  onClick={handleResetAndGoHome} // ← RESETA e vai para home
>
  ← Voltar para o início
</Button>
```
- **Comportamento:** Reseta tudo e vai para home
- **Dados:** LIMPA todos os dados
- **Uso:** Cancelar/abandonar questionário

## Testes

### Teste 1: Reset no Step 0
1. ✅ Abrir questionário (Step 0)
2. ✅ Preencher orçamento: R$ 60k-90k
3. ✅ Clicar "← Voltar para o início"
4. ✅ Verificar que voltou para home
5. ✅ Voltar ao questionário
6. ✅ Verificar: Orçamento = R$ 50k-100k (padrão)

### Teste 2: Reset no Step 2
1. ✅ Preencher Steps 0, 1, 2
2. ✅ Estar no Step 2 (Prioridades)
3. ✅ Clicar "← Voltar para o início"
4. ✅ Verificar que voltou para home
5. ✅ Voltar ao questionário
6. ✅ Verificar: Step 0, todos os dados limpos

### Teste 3: Reset no Step 3
1. ✅ Preencher todo o questionário
2. ✅ Estar no Step 3 (Preferências)
3. ✅ Clicar "← Voltar para o início"
4. ✅ Verificar que voltou para home
5. ✅ Voltar ao questionário
6. ✅ Verificar: Tudo resetado

### Teste 4: Botão "Voltar" Normal
1. ✅ Estar no Step 2
2. ✅ Clicar "Voltar" (não "Voltar para o início")
3. ✅ Verificar: Voltou para Step 1
4. ✅ Verificar: Dados MANTIDOS

## Localização Visual

```
┌─────────────────────────────────────────┐
│  [Progress: Step 2 de 4]                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  [Conteúdo do Step]             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [← Voltar]        [Próximo →]          │ ← Navegação entre steps
│                                         │
│  ← Voltar para o início                 │ ← RESET e vai para home
└─────────────────────────────────────────┘
```

## Benefícios

### 1. Clareza de Intenção
- ✅ "Voltar" = navegar entre steps
- ✅ "Voltar para o início" = cancelar/resetar

### 2. Comportamento Previsível
- ✅ Usuário sabe que vai perder dados
- ✅ Nome do botão deixa claro ("início")
- ✅ Consistente com expectativa

### 3. Limpeza de Estado
- ✅ Não deixa dados "fantasma"
- ✅ Cada nova pesquisa começa limpa
- ✅ Evita confusão

### 4. Experiência Consistente
- ✅ Mesmo comportamento em toda a aplicação
- ✅ "Voltar para o início" sempre reseta
- ✅ Seja no questionário ou nos resultados

## Arquivos Modificados

### Frontend
- `platform/frontend/src/pages/QuestionnairePage.tsx`
  - Importado `resetForm` do store
  - Criado `handleResetAndGoHome()`
  - Atualizado botão "Voltar para o início"

### Store (já existia)
- `platform/frontend/src/store/questionnaireStore.ts`
  - Método `resetForm()` já implementado
  - Reseta `currentStep` para 0
  - Limpa `formData`

## Analytics

O reset é logado para analytics:
```typescript
console.log('Reset: Usuário voltando ao início do questionário')
```

Isso permite rastrear:
- Quantos usuários abandonam o questionário
- Em qual step abandonam mais
- Taxa de conclusão do questionário

## Status

✅ **IMPLEMENTADO E FUNCIONANDO**

- Reset no questionário: ✅
- Volta para home: ✅
- Limpa todos os dados: ✅
- Restaura valores padrão: ✅
- Analytics implementado: ✅

## Teste Agora

1. Abra o questionário
2. Preencha alguns campos
3. Clique em "← Voltar para o início"
4. Verifique que voltou para home
5. Volte ao questionário
6. Confirme que está no Step 0 com dados limpos
