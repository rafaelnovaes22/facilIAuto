# Requirements Document - API Routing Fix

## Introduction

O sistema FacilIAuto está apresentando erro 405 (Method Not Allowed) em produção quando usuários selecionam estados sem concessionárias. O problema raiz é uma inconsistência no roteamento de API entre ambiente de desenvolvimento (com proxy Vite) e produção (Railway sem proxy).

## Glossary

- **Frontend**: Aplicação React/TypeScript que roda no navegador do usuário
- **Backend**: API FastAPI que processa recomendações de carros
- **Proxy Vite**: Servidor de desenvolvimento que redireciona requisições `/api/*` para `http://localhost:8000/*`
- **Railway**: Plataforma de deploy em produção onde frontend e backend rodam separadamente
- **CORS**: Cross-Origin Resource Sharing - mecanismo de segurança para requisições entre domínios
- **API Route**: Caminho da URL usado para acessar endpoints da API

## Requirements

### Requirement 1: Roteamento Consistente

**User Story:** Como desenvolvedor, eu quero que as rotas da API funcionem consistentemente em desenvolvimento e produção, para que não haja erros 405 em produção.

#### Acceptance Criteria

1. WHEN o Frontend faz requisição para `/recommend`, THE Backend SHALL processar a requisição com sucesso em desenvolvimento
2. WHEN o Frontend faz requisição para `/recommend`, THE Backend SHALL processar a requisição com sucesso em produção
3. WHEN o usuário seleciona estado sem concessionárias, THE Sistema SHALL retornar resposta 200 com lista vazia ao invés de erro 405
4. WHEN o Frontend está em desenvolvimento, THE Proxy Vite SHALL redirecionar `/api/*` para `http://localhost:8000/*`
5. WHEN o Frontend está em produção, THE Frontend SHALL fazer requisições diretas para a URL do Backend sem prefixo `/api`

### Requirement 2: Tratamento de Estados Sem Concessionárias

**User Story:** Como usuário, eu quero receber uma mensagem clara quando não há concessionárias no meu estado, para que eu entenda por que não há resultados.

#### Acceptance Criteria

1. WHEN o usuário seleciona estado sem concessionárias, THE Backend SHALL retornar status 200 com `recommendations: []`
2. WHEN o Backend retorna lista vazia, THE Frontend SHALL exibir mensagem amigável explicando a situação
3. WHEN não há concessionárias no estado, THE Frontend SHALL sugerir estados próximos com concessionárias disponíveis
4. WHEN o usuário vê mensagem de estado sem concessionárias, THE Frontend SHALL oferecer botão para editar localização
5. THE Sistema SHALL logar informação sobre estados consultados sem concessionárias para análise futura

### Requirement 3: Configuração de Ambiente

**User Story:** Como desenvolvedor, eu quero que a URL da API seja configurada automaticamente baseada no ambiente, para que não seja necessário alterar código ao fazer deploy.

#### Acceptance Criteria

1. WHEN o Frontend está em desenvolvimento, THE Sistema SHALL usar `http://localhost:8000` como base URL
2. WHEN o Frontend está em produção, THE Sistema SHALL usar variável de ambiente `VITE_API_URL` como base URL
3. IF variável `VITE_API_URL` não está definida em produção, THEN THE Sistema SHALL usar URL relativa `/`
4. THE Sistema SHALL validar que a URL da API está acessível antes de fazer requisições
5. WHEN a URL da API muda, THE Sistema SHALL atualizar automaticamente sem necessidade de rebuild

### Requirement 4: Tratamento de Erros de Rede

**User Story:** Como usuário, eu quero receber mensagens claras quando há problemas de conexão, para que eu saiba o que fazer.

#### Acceptance Criteria

1. WHEN há erro de rede (timeout, DNS, etc), THE Frontend SHALL exibir mensagem "Erro de conexão com servidor"
2. WHEN há erro 405, THE Frontend SHALL logar detalhes técnicos e exibir mensagem genérica ao usuário
3. WHEN há erro 500, THE Frontend SHALL exibir mensagem "Erro no servidor, tente novamente"
4. WHEN há erro 400, THE Frontend SHALL exibir mensagem específica do erro de validação
5. THE Sistema SHALL oferecer botão "Tentar Novamente" para todos os tipos de erro

### Requirement 5: Logging e Debugging

**User Story:** Como desenvolvedor, eu quero logs detalhados de requisições API, para que eu possa diagnosticar problemas rapidamente.

#### Acceptance Criteria

1. WHEN requisição API é iniciada, THE Sistema SHALL logar URL completa, método e payload
2. WHEN requisição API retorna, THE Sistema SHALL logar status code e tempo de resposta
3. WHEN há erro na requisição, THE Sistema SHALL logar stack trace completo
4. THE Sistema SHALL incluir session_id em todos os logs para rastreamento
5. WHILE em produção, THE Sistema SHALL enviar logs de erro para serviço de monitoramento
