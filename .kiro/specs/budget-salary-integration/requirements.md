# Requirements Document

## Introduction

Este documento especifica os requisitos para corrigir a integração entre a faixa de salário selecionada pelo usuário no questionário e o cálculo de TCO (Total Cost of Ownership) no sistema de recomendações. Atualmente, quando o usuário seleciona uma faixa de salário, o valor médio exibido não está sendo considerado no resultado, retornando sempre carros acima do orçamento. As tags de "acima/abaixo do orçamento" só devem aparecer quando o cliente informar o salário.

## Glossary

- **TCO (Total Cost of Ownership)**: Custo total de propriedade mensal do veículo, incluindo financiamento, combustível, manutenção, seguro e IPVA
- **Faixa Salarial**: Intervalo de renda mensal do usuário (ex: "3000-5000", "5000-8000")
- **Financial Capacity**: Objeto que contém a faixa de renda, TCO máximo recomendado (30% da renda média) e flag indicando se foi informado
- **Questionnaire Store**: Gerenciador de estado do questionário no frontend (Zustand)
- **User Profile**: Perfil do usuário enviado ao backend para gerar recomendações
- **Recommendation Engine**: Motor de recomendação no backend que filtra e pontua carros

## Requirements

### Requirement 1: Coleta de Faixa Salarial no Frontend

**User Story:** Como usuário, eu quero informar minha faixa de renda mensal no questionário, para que o sistema possa recomendar carros que cabem no meu orçamento mensal

#### Acceptance Criteria

1. WHEN o usuário acessa o Step 1 do questionário, THE Sistema SHALL exibir um seletor de faixa salarial com as opções: "0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"
2. WHEN o usuário seleciona uma faixa salarial, THE Sistema SHALL calcular a renda média da faixa (média entre mínimo e máximo)
3. WHEN o usuário seleciona uma faixa salarial, THE Sistema SHALL calcular o TCO máximo recomendado como 30% da renda média
4. WHEN o usuário opta por não informar a faixa salarial (pular), THE Sistema SHALL permitir continuar sem essa informação
5. WHEN o usuário não informa a faixa salarial, THE Sistema SHALL definir `is_disclosed` como `false` no objeto `financial_capacity`

### Requirement 2: Transformação de Dados no Frontend

**User Story:** Como desenvolvedor, eu quero que o questionário transforme corretamente a faixa salarial em um objeto `financial_capacity`, para que o backend receba os dados no formato esperado

#### Acceptance Criteria

1. WHEN o método `toUserProfile()` é chamado no Questionnaire Store, THE Sistema SHALL criar um objeto `financial_capacity` se `faixa_salarial` foi informada
2. WHEN `faixa_salarial` é "3000-5000", THE Sistema SHALL calcular `max_monthly_tco` como (3000 + 5000) / 2 * 0.30 = 1200
3. WHEN `faixa_salarial` é "5000-8000", THE Sistema SHALL calcular `max_monthly_tco` como (5000 + 8000) / 2 * 0.30 = 1950
4. WHEN `faixa_salarial` é "8000-12000", THE Sistema SHALL calcular `max_monthly_tco` como (8000 + 12000) / 2 * 0.30 = 3000
5. WHEN `faixa_salarial` é "12000+", THE Sistema SHALL calcular `max_monthly_tco` como (12000 + 16000) / 2 * 0.30 = 4200
6. WHEN `faixa_salarial` não foi informada, THE Sistema SHALL definir `financial_capacity` como `null` ou omitir o campo

### Requirement 3: Validação de Orçamento no Backend

**User Story:** Como sistema, eu quero validar se o TCO mensal do veículo cabe no orçamento do usuário, para que apenas carros adequados sejam recomendados

#### Acceptance Criteria

1. WHEN `financial_capacity.is_disclosed` é `true`, THE Recommendation Engine SHALL filtrar carros cujo `tco.total_monthly` seja menor ou igual a `financial_capacity.max_monthly_tco * 1.10` (tolerância de 10%)
2. WHEN `financial_capacity.is_disclosed` é `false`, THE Recommendation Engine SHALL NOT aplicar filtro de TCO
3. WHEN um carro tem `tco.total_monthly` <= `financial_capacity.max_monthly_tco`, THE Sistema SHALL definir `fits_budget` como `true`
4. WHEN um carro tem `tco.total_monthly` > `financial_capacity.max_monthly_tco`, THE Sistema SHALL definir `fits_budget` como `false`
5. WHEN `financial_capacity.is_disclosed` é `false`, THE Sistema SHALL definir `fits_budget` como `null`

### Requirement 4: Exibição de Status de Orçamento no Frontend

**User Story:** Como usuário, eu quero ver claramente se um carro recomendado cabe no meu orçamento mensal, para que eu possa tomar decisões informadas

#### Acceptance Criteria

1. WHEN `fits_budget` é `true`, THE Sistema SHALL exibir uma tag verde com texto "Dentro do orçamento"
2. WHEN `fits_budget` é `false`, THE Sistema SHALL exibir uma tag amarela com texto "Acima do orçamento"
3. WHEN `fits_budget` é `null`, THE Sistema SHALL NOT exibir nenhuma tag de status de orçamento
4. WHEN o usuário passa o mouse sobre a tag de orçamento, THE Sistema SHALL exibir um tooltip com o TCO mensal detalhado
5. WHEN `financial_health.status` é "healthy", THE Sistema SHALL exibir um ícone verde de saúde financeira

### Requirement 5: Cálculo Correto de Renda Média

**User Story:** Como sistema, eu quero calcular corretamente a renda média de cada faixa salarial, para que o TCO máximo recomendado seja preciso

#### Acceptance Criteria

1. WHEN a faixa é "0-3000", THE Sistema SHALL usar renda média de (0 + 3000) / 2 = 1500
2. WHEN a faixa é "3000-5000", THE Sistema SHALL usar renda média de (3000 + 5000) / 2 = 4000
3. WHEN a faixa é "5000-8000", THE Sistema SHALL usar renda média de (5000 + 8000) / 2 = 6500
4. WHEN a faixa é "8000-12000", THE Sistema SHALL usar renda média de (8000 + 12000) / 2 = 10000
5. WHEN a faixa é "12000+", THE Sistema SHALL usar renda média de (12000 + 16000) / 2 = 14000 (assumindo limite superior de 16000)

### Requirement 6: Consistência de Dados Entre Frontend e Backend

**User Story:** Como desenvolvedor, eu quero garantir que os dados de capacidade financeira sejam consistentes entre frontend e backend, para evitar erros de validação

#### Acceptance Criteria

1. WHEN o frontend envia `financial_capacity`, THE Backend SHALL validar que o objeto contém os campos `monthly_income_range`, `max_monthly_tco` e `is_disclosed`
2. WHEN `monthly_income_range` não está nas opções válidas, THE Backend SHALL retornar erro 400 com mensagem descritiva
3. WHEN `max_monthly_tco` é negativo, THE Backend SHALL retornar erro 400 com mensagem descritiva
4. WHEN `is_disclosed` é `true` mas `monthly_income_range` é `null`, THE Backend SHALL retornar erro 400 com mensagem descritiva
5. WHEN todos os campos são válidos, THE Backend SHALL processar a recomendação normalmente

### Requirement 7: Testes de Integração

**User Story:** Como desenvolvedor, eu quero testes automatizados que validem a integração completa da faixa salarial, para garantir que o sistema funciona corretamente

#### Acceptance Criteria

1. WHEN um teste envia perfil com `financial_capacity.is_disclosed = true`, THE Sistema SHALL retornar apenas carros com TCO dentro do orçamento (com 10% de tolerância)
2. WHEN um teste envia perfil com `financial_capacity.is_disclosed = false`, THE Sistema SHALL retornar carros sem filtro de TCO
3. WHEN um teste envia perfil com faixa "5000-8000", THE Sistema SHALL calcular `max_monthly_tco` como 1950
4. WHEN um teste envia perfil com faixa "5000-8000", THE Sistema SHALL retornar carros com `fits_budget = true` se TCO <= 1950
5. WHEN um teste envia perfil com faixa "5000-8000", THE Sistema SHALL retornar carros com `fits_budget = false` se TCO > 1950
