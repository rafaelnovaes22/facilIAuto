# US001 - Cadastro de Produto

## História
**Como** vendedor da feira  
**Quero** cadastrar produtos rapidamente  
**Para** ter controle do meu estoque  

## Critérios de Aceitação

### Funcionalidades
- [ ] Deve permitir cadastro com foto do celular
- [ ] Deve ter campos: nome, preço, quantidade, tamanhos
- [ ] Deve salvar mesmo sem internet
- [ ] Deve permitir cadastro em menos de 30 segundos
- [ ] Deve sugerir preços baseado em produtos similares

### Regras de Negócio
- Nome: mínimo 3 caracteres
- Preço: maior que R$ 0,01
- Quantidade: número inteiro positivo
- Tamanhos: PP, P, M, G, GG, XG ou único
- Foto: opcional, máximo 5MB

## Cenários de Teste (Gherkin)

```gherkin
Feature: Cadastro de Produto

  Background:
    Given que estou logado como vendedor
    And estou na tela de produtos

  Scenario: Cadastro rápido com sucesso
    When clico em "Adicionar Produto"
    And tiro uma foto do produto
    And preencho nome "Camiseta Branca"
    And preencho preço "29.90"
    And seleciono tamanhos "P,M,G"
    And preencho quantidade "10"
    And clico em "Salvar"
    Then produto é salvo com sucesso
    And retorno para lista de produtos
    And vejo "Camiseta Branca" na lista

  Scenario: Cadastro offline
    Given que estou sem conexão com internet
    When cadastro um novo produto
    Then produto é salvo localmente
    And vejo ícone de "sincronização pendente"
    When conexão é restaurada
    Then produto é sincronizado automaticamente

  Scenario: Validação de campos obrigatórios
    When clico em "Adicionar Produto"
    And clico em "Salvar" sem preencher campos
    Then vejo erro "Nome é obrigatório"
    And vejo erro "Preço é obrigatório"
    And vejo erro "Quantidade é obrigatória"
```

## Mockups/Wireframes

```
┌─────────────────────────┐
│  ← Novo Produto     ✓   │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │                     │ │
│ │    📷 Adicionar     │ │
│ │       Foto          │ │
│ │                     │ │
│ └─────────────────────┘ │
│                         │
│ Nome do Produto*        │
│ ┌─────────────────────┐ │
│ │                     │ │
│ └─────────────────────┘ │
│                         │
│ Preço (R$)*            │
│ ┌─────────────────────┐ │
│ │ 0,00                │ │
│ └─────────────────────┘ │
│                         │
│ Tamanhos Disponíveis    │
│ [PP][P][M][G][GG][XG]  │
│                         │
│ Quantidade*             │
│ ┌─────────────────────┐ │
│ │ 0                   │ │
│ └─────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │      SALVAR         │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

## Definition of Done
- [ ] Código implementado e revisado
- [ ] Testes unitários (>80% cobertura)
- [ ] Testes E2E implementados
- [ ] Code review aprovado
- [ ] Documentação atualizada
- [ ] Funciona offline
- [ ] Performance < 2s para salvar
- [ ] Acessibilidade validada

## Estimativa
**Story Points:** 5  
**Prioridade:** Alta (Must Have)  
**Sprint:** 1  

## Notas Técnicas
- Usar React Native Image Picker para fotos
- Comprimir imagem antes de salvar (max 1MB)
- Salvar em AsyncStorage quando offline
- Usar Formik + Yup para validação
- Implementar debounce na busca de produtos similares

## Dependências
- Nenhuma

## Riscos
- Performance com muitas fotos
- Espaço de armazenamento do dispositivo

---
*Criado em: [Data]*  
*Última atualização: [Data]*  
*Responsável: Time de Desenvolvimento*