# 📱 Configuração do WhatsApp

**Número Configurado**: +55 11 94910-5033  
**Formato**: 5511949105033

---

## 🎯 Como Funciona

Quando um usuário clica no botão "Falar no WhatsApp" em qualquer carro recomendado, ele é redirecionado para o seu WhatsApp com uma mensagem pré-formatada.

**Mensagem enviada:**
```
Olá! Vi o [NOME DO CARRO] ([ANO]) por R$ [PREÇO] no FacilIAuto e gostaria de mais informações.
```

**Exemplo:**
```
Olá! Vi o Hyundai Creta 16A (2020) por R$ 81.990,00 no FacilIAuto e gostaria de mais informações.
```

---

## ⚙️ Configuração

### Desenvolvimento Local

Arquivo: `platform/frontend/.env`
```bash
VITE_WHATSAPP_NUMBER=5511949105033
```

### Produção (Railway)

Adicionar variável de ambiente no painel do Railway:
```
VITE_WHATSAPP_NUMBER=5511949105033
```

---

## 🔄 Como Alterar o Número

### Opção 1: Via Variável de Ambiente (Recomendado)

**Local:**
```bash
# Editar platform/frontend/.env
VITE_WHATSAPP_NUMBER=5511999999999
```

**Produção (Railway):**
1. Acessar Railway Dashboard
2. Selecionar serviço `faciliauto-frontend`
3. Ir em **Variables**
4. Editar `VITE_WHATSAPP_NUMBER`
5. Salvar (redeploy automático)

### Opção 2: Via Código (Não Recomendado)

Editar `platform/frontend/src/components/results/CarCard.tsx`:
```typescript
const whatsappNumber = import.meta.env.VITE_WHATSAPP_NUMBER || '5511949105033'
//                                                                ^^^^^^^^^^^^
//                                                                Alterar aqui
```

---

## 🧪 Como Testar

### 1. Testar Localmente

```bash
cd platform/frontend
npm run dev
```

1. Acessar http://localhost:3000
2. Preencher questionário
3. Ver recomendações
4. Clicar em "Falar no WhatsApp"
5. Verificar se abre o WhatsApp com seu número

### 2. Testar em Produção

1. Acessar https://[seu-dominio-frontend]
2. Seguir mesmo fluxo
3. Verificar redirecionamento

---

## 📊 Rastreamento

O sistema rastreia automaticamente:
- ✅ Quantos cliques no WhatsApp
- ✅ Qual carro gerou o contato
- ✅ Perfil do usuário que clicou
- ✅ Score de match do carro

**Ver estatísticas:**
```bash
GET /api/ml/stats
```

---

## 🔒 Segurança

**Número público**: O número do WhatsApp fica visível no código frontend (é esperado e seguro).

**Proteção contra spam**:
- Usuário precisa preencher questionário completo
- Mensagem pré-formatada (não pode ser alterada facilmente)
- Rastreamento de interações

---

## 💡 Dicas

### Mensagem Personalizada

Para alterar a mensagem enviada, editar em `CarCard.tsx`:

```typescript
const message = encodeURIComponent(
  `Olá! Vi o ${car.nome} (${car.ano}) por R$ ${formatCurrency(car.preco)} no FacilIAuto e gostaria de mais informações.`
)
```

### Múltiplos Números

Para ter números diferentes por concessionária (futuro):

```typescript
// Manter estrutura original
const whatsappNumber = car.dealership_whatsapp || import.meta.env.VITE_WHATSAPP_NUMBER || '5511949105033'
```

### WhatsApp Business

Recomendado usar WhatsApp Business para:
- ✅ Respostas automáticas
- ✅ Catálogo de produtos
- ✅ Estatísticas de mensagens
- ✅ Múltiplos atendentes

---

## 🆘 Troubleshooting

### Problema: WhatsApp não abre

**Causa**: Número inválido ou mal formatado

**Solução**: Verificar formato (apenas números, com DDI e DDD)
```
Correto: 5511949105033
Errado: +55 11 94910-5033
Errado: 11949105033
```

### Problema: Mensagem não aparece

**Causa**: Caracteres especiais na mensagem

**Solução**: Usar `encodeURIComponent()` (já implementado)

### Problema: Abre WhatsApp Web em vez do app

**Causa**: Comportamento padrão do navegador

**Solução**: Normal. Usuário pode escolher abrir no app.

---

## 📞 Suporte

**Número Configurado**: +55 11 94910-5033  
**Última Atualização**: 06/11/2024  
**Status**: ✅ Ativo
