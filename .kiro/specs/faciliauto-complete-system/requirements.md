# Requirements Document - FacilIAuto Complete System

## Introduction

O FacilIAuto é uma plataforma SaaS B2B multi-tenant de recomendação automotiva que visa revolucionar a experiência de compra de veículos no Brasil. O sistema combina inteligência artificial responsável, arquitetura escalável e experiência mobile-first para atender pequenas e médias concessionárias negligenciadas pelos concorrentes.

**Contexto Atual:**
- Backend: 97/100 - Production-ready com 60+ testes e 87% coverage
- Frontend: 40/100 - Estrutura básica implementada, necessita completar funcionalidades
- Projeto Geral: 84/100 - Sistema funcional com gaps específicos
- Tempo estimado para 100%: 2-3 semanas

**Objetivo desta Spec:**
Completar os 16% restantes do projeto, focando em:
1. Finalizar frontend funcional completo
2. Validar e corrigir integração frontend-backend
3. Implementar testes E2E completos
4. Garantir sistema executável com um comando
5. Alinhar documentação com realidade

## Requirements

### Requirement 1: Frontend Completo e Funcional

**User Story:** Como usuário final (comprador de veículo), eu quero navegar por uma interface mobile-first intuitiva e responsiva, para que eu possa encontrar o carro ideal de forma rápida e agradável.

#### Acceptance Criteria

1. WHEN o usuário acessa a HomePage THEN o sistema SHALL exibir hero section, features grid, social proof, pricing preview e footer com navegação funcional
2. WHEN o usuário clica em "Começar" na HomePage THEN o sistema SHALL redirecionar para o QuestionnairePage no Step 0
3. WHEN o usuário preenche o Step 0 (orçamento) THEN o sistema SHALL validar que orcamento_min < orcamento_max E permitir avançar para Step 1
4. WHEN o usuário preenche os 4 steps do questionário THEN o sistema SHALL armazenar os dados no Zustand store E permitir navegação entre steps
5. WHEN o usuário submete o questionário completo THEN o sistema SHALL fazer POST para /recommend E redirecionar para ResultsPage
6. WHEN o usuário visualiza ResultsPage THEN o sistema SHALL exibir lista de carros recomendados com foto, nome, preço, score e botão WhatsApp
7. WHEN o usuário acessa qualquer página em dispositivo mobile THEN o sistema SHALL exibir layout responsivo otimizado para telas pequenas
8. IF ocorrer erro na API THEN o sistema SHALL exibir mensagem de erro amigável com opção de retry
9. WHEN o sistema está carregando dados THEN o sistema SHALL exibir loading states apropriados (spinners, skeletons)

### Requirement 2: Integração Frontend-Backend Validada

**User Story:** Como desenvolvedor, eu quero garantir que o frontend se comunica corretamente com o backend, para que os usuários tenham uma experiência sem erros e com dados reais.

#### Acceptance Criteria

1. WHEN o frontend faz requisição para qualquer endpoint do backend THEN o sistema SHALL configurar CORS corretamente para permitir localhost:3000
2. WHEN o frontend chama GET /health THEN o backend SHALL responder com status 200 E dados de health check
3. WHEN o frontend chama GET /stats THEN o backend SHALL responder com estatísticas das concessionárias E carros disponíveis
4. WHEN o frontend chama POST /recommend com dados válidos THEN o backend SHALL retornar lista de carros recomendados com scores
5. IF o frontend envia dados inválidos para /recommend THEN o backend SHALL retornar erro 422 com detalhes de validação
6. WHEN ocorre timeout na requisição THEN o frontend SHALL implementar retry logic com backoff exponencial
7. WHEN o usuário está offline THEN o sistema SHALL detectar E exibir mensagem apropriada
8. WHEN múltiplas requisições são feitas simultaneamente THEN o sistema SHALL implementar cache com React Query para evitar duplicação

### Requirement 3: Testes E2E Completos

**User Story:** Como QA engineer, eu quero ter uma suite completa de testes E2E, para que possamos garantir que o fluxo completo do usuário funciona corretamente em todos os cenários.

#### Acceptance Criteria

1. WHEN os testes E2E são executados THEN o sistema SHALL validar jornada completa: HomePage → Questionário (4 steps) → ResultsPage
2. WHEN o teste preenche orçamento inválido (min > max) THEN o sistema SHALL exibir mensagem de erro E não permitir avançar
3. WHEN o teste deixa campos obrigatórios vazios THEN o sistema SHALL exibir validação E não permitir submit
4. WHEN o backend está offline durante teste THEN o sistema SHALL exibir mensagem de erro apropriada
5. WHEN o teste simula "sem resultados encontrados" THEN o sistema SHALL exibir mensagem amigável E botão "Nova busca"
6. WHEN os testes E2E são executados THEN o sistema SHALL ter pelo menos 15 testes passando cobrindo user journeys E edge cases
7. WHEN ocorre timeout em requisição durante teste THEN o sistema SHALL implementar retry E eventual fallback

### Requirement 4: Sistema Executável com Um Comando

**User Story:** Como desenvolvedor ou stakeholder, eu quero iniciar todo o sistema com um único comando, para que eu possa fazer demos e validações rapidamente sem configuração complexa.

#### Acceptance Criteria

1. WHEN o usuário executa `start-faciliauto.bat` no Windows THEN o sistema SHALL verificar Python E Node.js instalados
2. IF Python ou Node.js não estão instalados THEN o script SHALL exibir mensagem de erro clara E instruções de instalação
3. WHEN o script inicia o backend THEN o sistema SHALL executar `python api/main.py` em terminal separado E aguardar 5 segundos
4. WHEN o script inicia o frontend THEN o sistema SHALL executar `npm run dev` em terminal separado
5. WHEN ambos os serviços estão rodando THEN o script SHALL exibir URLs de acesso (Backend: localhost:8000, Frontend: localhost:3000)
6. WHEN o usuário executa `start-faciliauto.sh` no Linux/Mac THEN o sistema SHALL executar mesma lógica com comandos Unix
7. WHEN o usuário pressiona Ctrl+C THEN o script SHALL encerrar ambos os processos gracefully
8. IF a porta 8000 ou 3000 está em uso THEN o script SHALL detectar E exibir mensagem de erro com instruções

### Requirement 5: Componentes de UI Completos e Reutilizáveis

**User Story:** Como desenvolvedor frontend, eu quero ter componentes de UI completos e bem testados, para que eu possa construir páginas consistentes e manuteníveis.

#### Acceptance Criteria

1. WHEN o componente QuestionnaireStep é renderizado THEN o sistema SHALL exibir título, descrição, campos de input E botões de navegação
2. WHEN o usuário interage com sliders de prioridades THEN o sistema SHALL atualizar valores em tempo real E validar range 1-5
3. WHEN o componente CarCard é renderizado THEN o sistema SHALL exibir foto, nome, preço formatado, score visual E botão de ação
4. WHEN o componente LoadingSpinner é exibido THEN o sistema SHALL mostrar animação suave E mensagem de loading
5. WHEN o componente ErrorMessage é exibido THEN o sistema SHALL mostrar ícone de erro, mensagem clara E botão de retry
6. WHEN componentes são testados THEN o sistema SHALL ter pelo menos 50 testes unitários cobrindo renderização, interação E edge cases
7. WHEN componentes são usados em mobile THEN o sistema SHALL adaptar layout E tamanhos para telas pequenas

### Requirement 6: Performance e Otimização

**User Story:** Como usuário final, eu quero que o sistema carregue rapidamente e responda instantaneamente, para que eu tenha uma experiência fluida e profissional.

#### Acceptance Criteria

1. WHEN o usuário acessa qualquer página THEN o sistema SHALL carregar em menos de 2 segundos
2. WHEN o backend processa requisição /recommend THEN o sistema SHALL responder em menos de 100ms
3. WHEN o frontend carrega assets THEN o sistema SHALL implementar lazy loading para imagens E code splitting para rotas
4. WHEN o usuário navega entre páginas THEN o sistema SHALL usar React Router com transições suaves
5. WHEN dados são buscados da API THEN o sistema SHALL implementar cache com React Query para evitar requisições duplicadas
6. WHEN imagens são carregadas THEN o sistema SHALL otimizar tamanho E formato (WebP quando possível)
7. WHEN o bundle é gerado THEN o sistema SHALL ter tamanho total < 500KB (gzipped)

### Requirement 7: Documentação Alinhada e Atualizada

**User Story:** Como stakeholder ou novo desenvolvedor, eu quero ter documentação precisa e atualizada, para que eu possa entender o estado real do projeto e contribuir efetivamente.

#### Acceptance Criteria

1. WHEN o README.md é lido THEN o documento SHALL refletir status real: Backend 97/100, Frontend 40/100, Projeto 84/100
2. WHEN a documentação menciona funcionalidades THEN o sistema SHALL garantir que apenas features implementadas são descritas como "completas"
3. WHEN novos desenvolvedores leem COMO-EXECUTAR.md THEN o documento SHALL ter instruções passo-a-passo testadas E funcionais
4. WHEN stakeholders leem STATUS-REAL-ATUAL.md THEN o documento SHALL apresentar gaps honestos E plano de ação claro
5. WHEN o projeto atinge 100% THEN o sistema SHALL atualizar todos os documentos para refletir completude
6. WHEN documentação técnica é criada THEN o sistema SHALL incluir exemplos de código, diagramas E troubleshooting
7. WHEN CHANGELOG.md é atualizado THEN o documento SHALL seguir formato semântico com versões E datas

### Requirement 8: Testes Unitários Frontend Completos

**User Story:** Como desenvolvedor frontend, eu quero ter cobertura completa de testes unitários, para que eu possa refatorar código com confiança e prevenir regressões.

#### Acceptance Criteria

1. WHEN testes de store são executados THEN o sistema SHALL validar questionnaireStore com todas as ações E estados
2. WHEN testes de services são executados THEN o sistema SHALL mockar chamadas API E validar error handling
3. WHEN testes de hooks são executados THEN o sistema SHALL validar useApi, useQuestionnaire E outros hooks customizados
4. WHEN testes de componentes são executados THEN o sistema SHALL validar renderização, props E interações de usuário
5. WHEN coverage é calculado THEN o sistema SHALL atingir pelo menos 80% de cobertura no frontend
6. WHEN testes são executados THEN o sistema SHALL ter pelo menos 50 testes unitários passando
7. IF um teste falha THEN o sistema SHALL exibir mensagem clara com stack trace E linha do erro

### Requirement 9: Error Handling e User Feedback

**User Story:** Como usuário final, eu quero receber feedback claro quando algo dá errado, para que eu saiba o que aconteceu e como proceder.

#### Acceptance Criteria

1. WHEN ocorre erro de rede THEN o sistema SHALL exibir toast com mensagem "Erro de conexão. Verifique sua internet." E botão retry
2. WHEN a API retorna erro 422 (validação) THEN o sistema SHALL exibir mensagens de erro específicas em cada campo inválido
3. WHEN a API retorna erro 500 THEN o sistema SHALL exibir mensagem genérica "Erro no servidor. Tente novamente em instantes."
4. WHEN o usuário tenta avançar step sem preencher campos obrigatórios THEN o sistema SHALL destacar campos vazios E exibir mensagem de validação
5. WHEN operação é bem-sucedida THEN o sistema SHALL exibir toast de sucesso com mensagem apropriada
6. WHEN o sistema está processando THEN o sistema SHALL desabilitar botões E exibir loading state
7. WHEN timeout ocorre THEN o sistema SHALL exibir mensagem "A operação está demorando. Deseja continuar aguardando?" com opções

### Requirement 10: Responsividade e Acessibilidade

**User Story:** Como usuário com diferentes dispositivos e necessidades, eu quero acessar o sistema de forma confortável, para que eu possa usar independente do meu contexto.

#### Acceptance Criteria

1. WHEN o sistema é acessado em mobile (< 768px) THEN o layout SHALL adaptar para single column E touch-friendly
2. WHEN o sistema é acessado em tablet (768px - 1024px) THEN o layout SHALL usar grid de 2 colunas quando apropriado
3. WHEN o sistema é acessado em desktop (> 1024px) THEN o layout SHALL usar grid de 3-4 colunas E aproveitar espaço horizontal
4. WHEN o usuário navega por teclado THEN o sistema SHALL ter focus states visíveis E ordem lógica de tab
5. WHEN screen reader é usado THEN o sistema SHALL ter labels apropriados, aria-labels E semantic HTML
6. WHEN contraste é verificado THEN o sistema SHALL ter ratio mínimo de 4.5:1 para texto normal E 3:1 para texto grande
7. WHEN o usuário aumenta zoom para 200% THEN o sistema SHALL manter funcionalidade E legibilidade

### Requirement 11: Deploy e Infraestrutura

**User Story:** Como DevOps engineer, eu quero ter infraestrutura configurada e testada, para que eu possa fazer deploy em produção com confiança.

#### Acceptance Criteria

1. WHEN docker-compose up é executado THEN o sistema SHALL iniciar backend, nginx, prometheus E grafana
2. WHEN containers estão rodando THEN o sistema SHALL ter health checks configurados E funcionais
3. WHEN variáveis de ambiente são necessárias THEN o sistema SHALL ter .env.example com todas as variáveis documentadas
4. WHEN logs são gerados THEN o sistema SHALL usar structured logging com níveis apropriados (INFO, WARNING, ERROR)
5. WHEN CI/CD pipeline é executado THEN o sistema SHALL rodar testes, linting E build antes de deploy
6. WHEN deploy em staging é feito THEN o sistema SHALL validar smoke tests antes de promover para produção
7. WHEN monitoramento é configurado THEN o sistema SHALL ter dashboards no Grafana com métricas de performance E erros

### Requirement 12: Multi-tenant e Escalabilidade

**User Story:** Como administrador da plataforma, eu quero gerenciar múltiplas concessionárias, para que eu possa escalar o negócio sem retrabalho técnico.

#### Acceptance Criteria

1. WHEN nova concessionária é adicionada THEN o sistema SHALL criar tenant isolado com dados próprios
2. WHEN requisição é feita THEN o sistema SHALL identificar tenant por domínio ou header E filtrar dados apropriadamente
3. WHEN concessionária customiza branding THEN o sistema SHALL aplicar logo, cores E textos específicos
4. WHEN dados são armazenados THEN o sistema SHALL garantir isolamento entre tenants (row-level security)
5. WHEN relatórios são gerados THEN o sistema SHALL agregar dados por tenant E permitir visão consolidada para admin
6. WHEN sistema escala THEN a arquitetura SHALL suportar pelo menos 100 tenants simultâneos sem degradação
7. WHEN backup é feito THEN o sistema SHALL permitir restore por tenant individual

