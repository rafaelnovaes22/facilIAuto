# US002 - Gestão de Fornecedores

## História Principal
**Como** vendedor da feira  
**Quero** controlar meus fornecedores e pedidos  
**Para** não perder prazos de pagamento e conseguir melhores preços  

## Contexto
Os vendedores da feira trabalham com múltiplos fornecedores (média de 3-7), cada um com diferentes:
- Prazos de pagamento (7, 14, 21, 30 dias)
- Condições de compra (à vista com desconto, parcelado)
- Dias de entrega específicos
- Produtos diferentes (um fornece camisetas, outro calças, etc.)

## Critérios de Aceitação

### Funcionalidades Essenciais
- [ ] Cadastro rápido de fornecedor (nome + WhatsApp)
- [ ] Registro de pedido com produtos e valores
- [ ] Alertas de pagamento 1 dia antes do vencimento
- [ ] Histórico de compras por fornecedor
- [ ] Cálculo automático de margem (preço venda - preço compra)
- [ ] Funciona 100% offline

### Regras de Negócio
- Nome fornecedor: mínimo 3 caracteres
- WhatsApp: formato brasileiro (11 dígitos)
- Pedido mínimo: R$ 50,00
- Prazo pagamento: 1-90 dias
- Alertas: às 8h da manhã
- Histórico: últimos 6 meses

## Cenários de Teste (Gherkin)

```gherkin
Feature: Gestão de Fornecedores

  Background:
    Given que estou logado como vendedor
    And estou na tela de fornecedores

  Scenario: Cadastro rápido de fornecedor
    When clico em "Novo Fornecedor"
    And preencho nome "João Atacado"
    And preencho WhatsApp "11987654321"
    And seleciono categoria "Camisetas"
    And marco prazo padrão "14 dias"
    And clico em "Salvar"
    Then fornecedor é cadastrado
    And posso ver na lista de fornecedores

  Scenario: Registro de pedido
    Given tenho fornecedor "João Atacado" cadastrado
    When clico em "Novo Pedido"
    And seleciono fornecedor "João Atacado"
    And adiciono produtos:
      | Produto          | Qtd | Preço Unit |
      | Camiseta Branca  | 20  | 15.00      |
      | Camiseta Preta   | 15  | 15.00      |
    And seleciono prazo "14 dias"
    And seleciono forma pagamento "PIX com 5% desconto"
    Then pedido é registrado com total R$ 498.75
    And alerta é agendado para 13 dias

  Scenario: Alerta de pagamento
    Given tenho pedido vencendo amanhã
    When abro o aplicativo às 8h
    Then vejo notificação "Pagamento pendente: João Atacado - R$ 498.75"
    And posso marcar como pago
    Or posso adiar por 1 dia

  Scenario: Análise de margem
    Given tenho produto "Camiseta Branca"
    And comprei por R$ 15.00 do fornecedor
    And vendo por R$ 35.00
    When acesso relatório de margem
    Then vejo margem de 133%
    And lucro de R$ 20.00 por peça

  Scenario: Sugestão de reposição
    Given produto "Camiseta Branca" tem 2 unidades
    And vendi 50 unidades nos últimos 30 dias
    When acesso sugestões de compra
    Then sistema sugere comprar 60 unidades
    And mostra melhor fornecedor por preço
    And calcula investimento necessário

  Scenario: Comparação de fornecedores
    Given tenho 3 fornecedores de camisetas
    When acesso comparação de preços
    Then vejo tabela comparativa:
      | Fornecedor | Preço | Prazo | Qualidade |
      | João       | 15.00 | 14d   | ★★★★★     |
      | Maria      | 13.50 | 7d    | ★★★★      |
      | Pedro      | 16.00 | 30d   | ★★★★★     |
```

## Mockups/Wireframes

### Tela Principal - Fornecedores
```
┌─────────────────────────┐
│  ← Fornecedores     +   │
├─────────────────────────┤
│ 📊 Resumo do Mês        │
│ ┌─────────────────────┐ │
│ │ A Pagar: R$ 2.450   │ │
│ │ Vence Hoje: R$ 450  │ │
│ │ Atrasado: R$ 0      │ │
│ └─────────────────────┘ │
│                         │
│ 🔔 Próximos Pagamentos  │
│ ┌─────────────────────┐ │
│ │ Amanhã              │ │
│ │ João - R$ 498.75    │ │
│ │ [Pagar] [Adiar]     │ │
│ └─────────────────────┘ │
│                         │
│ 👥 Meus Fornecedores    │
│ ┌─────────────────────┐ │
│ │ João Atacado        │ │
│ │ Camisetas • 14 dias │ │
│ │ Último: 01/12       │ │
│ ├─────────────────────┤ │
│ │ Maria Modas         │ │
│ │ Vestidos • 21 dias  │ │
│ │ Último: 28/11       │ │
│ └─────────────────────┘ │
│                         │
│ [📦 Novo Pedido]        │
└─────────────────────────┘
```

### Tela de Novo Pedido
```
┌─────────────────────────┐
│  ← Novo Pedido      ✓   │
├─────────────────────────┤
│ Fornecedor*             │
│ ┌─────────────────────┐ │
│ │ ▼ João Atacado      │ │
│ └─────────────────────┘ │
│                         │
│ Produtos                │
│ ┌─────────────────────┐ │
│ │ + Adicionar Produto │ │
│ ├─────────────────────┤ │
│ │ Camiseta Branca     │ │
│ │ 20un x R$ 15 = 300  │ │
│ │ [Editar] [Remover]  │ │
│ └─────────────────────┘ │
│                         │
│ Pagamento               │
│ ○ À vista (5% desc)    │
│ ● Prazo 14 dias        │
│ ○ Parcelado 2x         │
│                         │
│ Data Entrega            │
│ ┌─────────────────────┐ │
│ │ 15/12/2024          │ │
│ └─────────────────────┘ │
│                         │
│ Total: R$ 300.00        │
│                         │
│ [Salvar Pedido]         │
└─────────────────────────┘
```

### Tela de Análise
```
┌─────────────────────────┐
│  ← Análise Fornecedor   │
├─────────────────────────┤
│ 📈 Reposição Sugerida   │
│ ┌─────────────────────┐ │
│ │ Camiseta Branca     │ │
│ │ Estoque: 2          │ │
│ │ Venda/mês: 50       │ │
│ │ Sugestão: 60 un     │ │
│ │ Investir: R$ 900    │ │
│ │ [Fazer Pedido]      │ │
│ └─────────────────────┘ │
│                         │
│ 💰 Margem de Lucro      │
│ ┌─────────────────────┐ │
│ │ Produto  | Margem   │ │
│ │ Camiseta | 133% ✅  │ │
│ │ Calça    | 87%  ⚠️  │ │
│ │ Vestido  | 150% ✅  │ │
│ └─────────────────────┘ │
│                         │
│ 🏆 Melhor Fornecedor    │
│ ┌─────────────────────┐ │
│ │ Por Preço: Maria    │ │
│ │ Por Prazo: Pedro    │ │
│ │ Por Mix: João       │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

## Definition of Done
- [ ] Código implementado com TDD
- [ ] Testes unitários (>80% cobertura)
- [ ] Testes E2E para fluxo completo
- [ ] Code review em pair programming
- [ ] Funciona 100% offline
- [ ] Sincronização quando online
- [ ] Performance < 1s para operações
- [ ] Notificações funcionando

## Estimativa
**Story Points:** 8  
**Prioridade:** Alta (Must Have)  
**Sprint:** 2-3  

## Notas Técnicas

### Backend
```typescript
// Modelo de dados
interface Fornecedor {
  id: string;
  nome: string;
  whatsapp: string;
  categorias: string[];
  prazoPadrao: number; // dias
  avaliacaoQualidade: number; // 1-5
  ativo: boolean;
}

interface Pedido {
  id: string;
  fornecedorId: string;
  produtos: ItemPedido[];
  valorTotal: number;
  formaPagamento: 'avista' | 'prazo' | 'parcelado';
  dataCompra: Date;
  dataPagamento: Date;
  dataEntrega: Date;
  status: 'pendente' | 'pago' | 'atrasado';
  observacoes?: string;
}

interface ItemPedido {
  produtoId: string;
  nomeProduto: string;
  quantidade: number;
  precoUnitario: number;
  subtotal: number;
}
```

### Notificações
- Usar React Native Push Notifications
- Agendar com react-native-background-fetch
- Fallback para notificações locais quando offline

### Análise e Sugestões
```typescript
// Algoritmo de sugestão de reposição
function calcularSugestaoReposicao(produto: Produto) {
  const vendasUltimos30Dias = getVendas30Dias(produto.id);
  const velocidadeVenda = vendasUltimos30Dias / 30;
  const diasEstoque = produto.quantidade / velocidadeVenda;
  
  if (diasEstoque < 7) {
    const sugestao = Math.ceil(velocidadeVenda * 45); // 45 dias de estoque
    const melhorFornecedor = getMelhorFornecedor(produto.categoria);
    
    return {
      urgente: diasEstoque < 3,
      quantidade: sugestao,
      fornecedor: melhorFornecedor,
      investimento: sugestao * melhorFornecedor.preco
    };
  }
}
```

## Dependências
- US001 - Cadastro de Produtos (para vincular produtos)
- Sistema de notificações configurado
- Integração WhatsApp

## Riscos
- Resistência dos fornecedores em formalizar
- Complexidade de múltiplas formas de pagamento
- Volume de notificações pode incomodar

## Métricas de Sucesso
- Redução de 50% em atrasos de pagamento
- Aumento de 20% na margem média
- 80% dos pedidos registrados no app
- Tempo médio de registro < 2 minutos

---
*Criado em: [Data]*  
*Última atualização: [Data]*  
*Responsável: Time de Desenvolvimento*