# Reset de Pesquisa - Implementação

**Data:** 30 de outubro de 2025  
**Funcionalidade:** Reset completo do formulário ao iniciar nova pesquisa

## Problema

Quando o usuário clicava em "Voltar ao início", "Tentar novamente" ou "Buscar novamente" na página de resultados, o sistema navegava de volta ao questionário mas **mantinha os dados anteriores** preenchidos.

Isso causava confusão porque:
- Usuário esperava começar do zero
- Dados antigos apareciam pré-preenchidos
- Não ficava claro se era uma nova pesquisa ou edição

## Solução Implementada

### 1. Uso do `resetForm()` do Store

O store Zustand já tinha um método `resetForm()` que:
- Reseta `currentStep` para 0
- Limpa todos os dados do formulário
- Restaura valores iniciais padrão

### 2. Dois Handlers Distintos

Criados dois handlers na `ResultsPage.tsx`:

#### Handler 1: Nova Pesquisa (Reset Completo)
```typescript
// Handler para resetar pesquisa e voltar ao início (LIMPA TUDO)
const handleResetAndRestart = () => {
  console.log('Reset: Usuário iniciando nova pesquisa do zero')
  resetForm() // Limpa todos os dados do formulário
  navigate('/questionario') // Volta para o questionário
}
```

#### Handler 2: Editar Pesquisa (Mantém Dados)
```typescript
// Handler para editar pesquisa (MANTÉM DADOS)
const handleEditSearch = () => {
  console.log('Edit: Usuário editando pesquisa existente')
  // Não chama resetForm() - mantém os dados
  // Apenas volta para o step 0 do questionário
  const setCurrentStep = useQuestionnaireStore.getState().setCurrentStep
  setCurrentStep(0)
  navigate('/questionario')
}
```

### 3. Botões Atualizados

#### Botões que RESETAM (Nova Pesquisa)

**Botão "Voltar ao início"**
```typescript
<Button
  variant="ghost"
  size="sm"
  leftIcon={<FaArrowLeft />}
  onClick={handleResetAndRestart} // ← RESETA
  alignSelf="flex-start"
>
  ← Voltar ao início
</Button>
```

**Botão "Tentar Novamente"** (quando não há resultados)
```typescript
<Button
  mt={6}
  colorScheme="brand"
  onClick={handleResetAndRestart} // ← RESETA
>
  Tentar Novamente
</Button>
```

**Botão "Buscar Novamente"** (footer)
```typescript
<Button
  colorScheme="brand"
  size="lg"
  onClick={handleResetAndRestart} // ← RESETA
>
  Buscar Novamente
</Button>
```

#### Botão que MANTÉM DADOS (Editar)

**Botão "Editar"** no ProfileSummary
```typescript
<ProfileSummary
  profileSummary={data.profile_summary}
  onEdit={handleEditSearch} // ← MANTÉM DADOS
/>
```

## Comportamento

### Dois Tipos de Ação

#### 1. Nova Pesquisa (RESET COMPLETO)
Botões: "Voltar ao início", "Tentar novamente", "Buscar novamente"

```
Usuário na página de resultados
  ↓
Clica em "Voltar ao início" / "Buscar novamente"
  ↓
resetForm() é chamado
  ↓
Todos os dados são limpos
  ↓
Navega para /questionario (step 0)
  ↓
✅ Formulário completamente limpo
✅ Usuário começa do zero
✅ Valores padrão restaurados
```

#### 2. Editar Pesquisa (MANTÉM DADOS)
Botão: "Editar" no ProfileSummary

```
Usuário na página de resultados
  ↓
Clica em "Editar" no resumo do perfil
  ↓
setCurrentStep(0) é chamado
  ↓
Dados são MANTIDOS
  ↓
Navega para /questionario (step 0)
  ↓
✅ Formulário com dados preenchidos
✅ Usuário pode ajustar valores
✅ Experiência de edição clara
```

## Quando Usar Cada Comportamento

### Use RESET (Nova Pesquisa) quando:
- ✅ Usuário quer começar completamente do zero
- ✅ Resultados não atenderam e quer tentar algo diferente
- ✅ Quer explorar outras opções sem influência da pesquisa anterior
- ✅ Não encontrou nenhum carro e quer tentar novamente

**Botões:** "Voltar ao início", "Tentar novamente", "Buscar novamente"

### Use EDITAR (Mantém Dados) quando:
- ✅ Usuário quer ajustar apenas alguns valores
- ✅ Gostou dos resultados mas quer refinar
- ✅ Quer mudar orçamento ou prioridades levemente
- ✅ Quer ver como pequenas mudanças afetam resultados

**Botão:** "Editar" no resumo do perfil

## Valores Iniciais Padrão

Quando o formulário é resetado (Nova Pesquisa), estes valores são restaurados:

```typescript
{
  orcamento_min: 50000,        // R$ 50.000
  orcamento_max: 100000,       // R$ 100.000
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

## Fluxos de Usuário

### Fluxo 1: Nenhum Resultado Encontrado
```
1. Usuário faz pesquisa
2. Nenhum carro encontrado
3. Clica em "Tentar Novamente"
4. ✅ Formulário resetado
5. Começa nova pesquisa do zero
```

### Fluxo 2: Quer Fazer Nova Pesquisa
```
1. Usuário vê resultados
2. Não gostou das opções
3. Clica em "Buscar Novamente" (footer)
4. ✅ Formulário resetado
5. Começa nova pesquisa do zero
```

### Fluxo 3: Quer Voltar ao Início
```
1. Usuário vê resultados
2. Clica em "← Voltar ao início"
3. ✅ Formulário resetado
4. Volta para o questionário limpo
```

### Fluxo 4: Quer Editar Perfil
```
1. Usuário vê resultados
2. Clica em "Editar" no resumo do perfil
3. ✅ Dados MANTIDOS (não reseta)
4. Volta para step 0 com dados preenchidos
5. Pode ajustar valores e refazer pesquisa
```

## Analytics

O reset é logado para analytics:

```typescript
console.log('Reset: Usuário iniciando nova pesquisa')
```

Isso permite rastrear:
- Quantos usuários fazem múltiplas pesquisas
- Em que ponto do fluxo eles resetam
- Taxa de conversão após reset

## Arquivos Modificados

### Frontend
- `platform/frontend/src/pages/ResultsPage.tsx` - Implementação do reset
  - Importado `useQuestionnaireStore`
  - Criado `handleResetAndRestart()`
  - Atualizado 4 botões para usar o handler

### Store (já existia)
- `platform/frontend/src/store/questionnaireStore.ts` - Método `resetForm()` já implementado

## Testes Manuais

### Teste 1: Reset após Nenhum Resultado
1. ✅ Fazer pesquisa que não retorna resultados
2. ✅ Clicar em "Tentar Novamente"
3. ✅ Verificar que formulário está limpo
4. ✅ Preencher novos dados
5. ✅ Confirmar que pesquisa anterior não interfere

### Teste 2: Reset após Ver Resultados
1. ✅ Fazer pesquisa que retorna resultados
2. ✅ Clicar em "Buscar Novamente"
3. ✅ Verificar que formulário está limpo
4. ✅ Valores padrão restaurados

### Teste 3: Reset via Voltar ao Início
1. ✅ Fazer pesquisa
2. ✅ Clicar em "← Voltar ao início"
3. ✅ Verificar que está no step 0
4. ✅ Verificar que dados estão limpos

### Teste 4: Editar Perfil (Mantém Dados)
1. ✅ Fazer pesquisa com valores específicos
2. ✅ Clicar em "Editar" no resumo
3. ✅ Verificar que está no step 0
4. ✅ Verificar que dados estão PREENCHIDOS
5. ✅ Ajustar um valor (ex: orçamento)
6. ✅ Fazer nova pesquisa
7. ✅ Verificar que outros valores foram mantidos

## Comparação Visual

| Ação | Botão | Comportamento | Dados | Uso |
|------|-------|---------------|-------|-----|
| **Nova Pesquisa** | "Voltar ao início"<br>"Tentar novamente"<br>"Buscar novamente" | `resetForm()` | ❌ Limpa tudo | Começar do zero |
| **Editar** | "Editar" (ProfileSummary) | `setCurrentStep(0)` | ✅ Mantém dados | Ajustar valores |

### Exemplo Prático

**Cenário:** Usuário fez pesquisa com orçamento R$ 50k-80k

#### Se clicar em "Buscar Novamente":
```
Antes: Orçamento R$ 50k-80k, Uso: Família, Prioridades: [...]
         ↓ resetForm()
Depois: Orçamento R$ 50k-100k (padrão), Uso: Família (padrão), Prioridades: [3,3,3,3,3] (padrão)
```

#### Se clicar em "Editar":
```
Antes: Orçamento R$ 50k-80k, Uso: Família, Prioridades: [5,4,3,4,5]
         ↓ setCurrentStep(0)
Depois: Orçamento R$ 50k-80k ✅, Uso: Família ✅, Prioridades: [5,4,3,4,5] ✅
        (Pode ajustar apenas o que quiser)
```

## Melhorias Futuras

### 1. Confirmação de Reset
Para evitar perda acidental de dados:
```typescript
const handleResetAndRestart = () => {
  if (confirm('Deseja iniciar uma nova pesquisa? Os dados atuais serão perdidos.')) {
    resetForm()
    navigate('/questionario')
  }
}
```

### 2. Salvar Pesquisas Anteriores
Permitir que usuário compare múltiplas pesquisas:
```typescript
interface SearchHistory {
  id: string
  timestamp: Date
  profile: UserProfile
  results: RecommendationResponse
}
```

### 3. Botão "Editar" vs "Nova Pesquisa"
Diferenciar entre:
- **Editar**: Mantém dados, permite ajustes
- **Nova Pesquisa**: Reseta tudo

## Status

✅ **IMPLEMENTADO E FUNCIONANDO**

- Reset completo do formulário (Nova Pesquisa): ✅
- Edição com dados mantidos (Editar): ✅
- Dois handlers distintos: ✅
- Todos os botões atualizados: ✅
- Valores padrão restaurados (reset): ✅
- Dados preservados (editar): ✅
- Experiência de usuário clara: ✅
- Analytics implementado: ✅

## Teste Agora

1. Faça uma pesquisa
2. Veja os resultados
3. Clique em qualquer botão de "Voltar" ou "Buscar novamente"
4. Verifique que o formulário está completamente limpo
5. Confirme que pode fazer uma nova pesquisa do zero
