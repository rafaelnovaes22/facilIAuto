# Implementation Plan - Chatbot WhatsApp FacilIAuto

Este plano de implementação segue a metodologia XP (Extreme Programming) com desenvolvimento incremental, TDD (Test-Driven Development) e entregas contínuas. Cada tarefa é projetada para ser executada de forma independente, com testes automatizados e integração com o sistema existente.

**Princípios XP Aplicados**:
- Simple Design: Implementar a solução mais simples que funciona
- Test-First: Escrever testes antes do código
- Refactoring: Melhorar código continuamente
- Continuous Integration: Integrar e testar frequentemente
- Small Releases: Entregas incrementais de valor

**Legenda**:
- `*` = Tarefa opcional (pode ser pulada para MVP)
- Sem `*` = Tarefa obrigatória para funcionalidade core

---

## Phase 1: Infraestrutura e Setup Inicial

- [x] 1. Configurar ambiente de desenvolvimento e dependências





  - Criar estrutura de diretórios do projeto (src/, tests/, config/, docs/)
  - Configurar pyproject.toml com dependências (FastAPI, PydanticAI, LangGraph, Redis, DuckDB, Celery, pytest)
  - Configurar Docker Compose para serviços locais (Redis, PostgreSQL, DuckDB)
  - Criar .env.example com variáveis de ambiente necessárias
  - Configurar pre-commit hooks (black, flake8, mypy)
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 2. Configurar WhatsApp Business API





  - Criar conta no Meta Business Suite
  - Configurar WhatsApp Business API (Cloud API)
  - Obter tokens de acesso e configurar webhooks
  - Testar envio e recebimento de mensagens via API
  - Documentar processo de configuração
  - _Requirements: 1.1, 1.2_

- [x] 3. Implementar database schemas e migrations





  - Criar schema PostgreSQL (users, sessions, messages, qualified_leads, car_interactions, human_handoffs, metrics_daily)
  - Criar schema DuckDB (conversation_context, message_history, message_embeddings)
  - Implementar migrations usando Alembic
  - Criar seeds para dados de teste
  - _Requirements: Data Models_

- [ ]* 3.1 Escrever testes de schema e migrations
  - Testar criação de tabelas
  - Testar constraints e índices
  - Testar rollback de migrations
  - _Requirements: 11.1_

---

## Phase 2: Core Services - Session Management

- [x] 4. Implementar Session Manager com PydanticAI





  - [x] 4.1 Criar modelos Pydantic (SessionData, ConversationMemory, UserProfileData, SessionState)


    - Definir tipos e validações
    - Implementar serialização/deserialização
    - Adicionar métodos de cálculo (completeness, qualification_score)
    - _Requirements: 6.1, 6.2_
  
  - [x] 4.2 Implementar SessionManager com Redis


    - Método get_or_create_session() com locks distribuídos (SET NX)
    - Método update_session() com idempotência (session_id:turn_id)
    - Método expire_session() com TTL de 24h
    - Integração com DuckDB para persistência assíncrona
    - _Requirements: 6.3, 6.4, 6.9_
  
  - [ ]* 4.3 Escrever testes unitários do SessionManager
    - Testar criação de nova sessão
    - Testar recuperação de sessão existente
    - Testar locks distribuídos (race conditions)
    - Testar idempotência de updates
    - Testar expiração de sessões
    - _Requirements: 11.1, 11.2_

---

## Phase 3: NLP Service com LangGraph

- [x] 5. Implementar NLP Service





  - [x] 5.1 Criar classificador de intenções



    - Definir enum Intent com todas as intenções
    - Implementar modelo de classificação (spaCy ou Transformers)
    - Fine-tuning em dataset português automotivo
    - Atingir precisão >= 85%
    - _Requirements: 4.2, 4.7, 11.4_
  
  - [x] 5.2 Implementar extrator de entidades (NER)


    - Extrair orçamento (valores monetários)
    - Extrair marcas e modelos de carros
    - Extrair localização (cidade, estado)
    - Extrair preferências (economia, espaço, performance, etc)
    - _Requirements: 4.2, 4.7_
  
  - [x] 5.3 Implementar análise de sentimento


    - Classificar sentimento (positive, neutral, negative)
    - Adaptar tom de resposta baseado em sentimento
    - _Requirements: 4.4_
  
  - [ ]* 5.4 Escrever testes unitários do NLP Service
    - Testar classificação de intenções (dataset de 100+ exemplos)
    - Testar extração de entidades
    - Testar análise de sentimento
    - Validar precisão >= 85%
    - _Requirements: 11.1, 11.4_

---

## Phase 4: Conversation Engine com LangGraph

- [x] 6. Implementar Conversation Engine





  - [x] 6.1 Criar grafo de estados conversacionais (LangGraph)


    - Definir ConversationState (TypedDict)
    - Criar nós: process_nlp, handle_greeting, collect_profile, generate_recommendations, show_car_details, compare_cars, human_handoff, apply_guardrails
    - Definir edges condicionais baseados em intenção
    - Implementar checkpoints para recuperação
    - _Requirements: 6.2, 6.6_
  
  - [x] 6.2 Implementar handlers de cada estado

    - handle_greeting(): Mensagem de boas-vindas
    - collect_profile(): Coletar informações do usuário
    - generate_recommendations(): Chamar backend para recomendações
    - show_car_details(): Mostrar detalhes de carro específico
    - compare_cars(): Comparar múltiplos carros
    - human_handoff(): Transferir para atendimento humano
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 7.1, 7.2_
  
  - [x] 6.3 Implementar Guardrails para evitar duplicações



    - Deduplicação por hash de conteúdo
    - Filtros de repetição (últimas 5 mensagens)
    - Reformulação automática de respostas duplicadas
    - Políticas de estilo (tom, formatação)
    - _Requirements: 6.9, 6.10_
  
  - [ ]* 6.4 Escrever testes de integração do Conversation Engine
    - Testar fluxo completo de qualificação
    - Testar transições de estado
    - Testar handoff para humano
    - Testar guardrails anti-duplicação
    - _Requirements: 11.2, 11.5_

---

## Phase 5: Integração com Backend Existente

- [x] 7. Implementar Backend Client






  - [x] 7.1 Criar cliente HTTP para API do FacilIAuto

    - Método get_recommendations(user_profile) → /api/recommend
    - Método get_car_details(car_id) → /api/cars/{car_id}
    - Método submit_feedback(feedback) → /api/feedback
    - Método refine_recommendations(request) → /api/refine-recommendations
    - Implementar retry com backoff exponencial
    - Implementar circuit breaker
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  

  - [x] 7.2 Implementar cache de recomendações


    - Cache em Redis com TTL de 1 hora
    - Fallback para cache quando backend indisponível
    - Invalidação de cache quando perfil muda
    - _Requirements: 5.3, 12.4_
  
  - [ ]* 7.3 Escrever testes de integração com backend
    - Testar chamadas à API de recomendação
    - Testar retry e circuit breaker
    - Testar fallback para cache
    - Mock do backend para testes
    - _Requirements: 11.2, 11.5_

---

## Phase 6: Webhook Handler e WhatsApp Integration

- [x] 8. Implementar Webhook Handler (FastAPI)







  - [x] 8.1 Criar endpoints de webhook






    - POST /webhook/whatsapp: Receber mensagens
    - GET /webhook/whatsapp: Verificação inicial do Meta
    - Validar signature do Meta (X-Hub-Signature-256)
    - Implementar deduplicação de mensagens


    - _Requirements: 1.1, 1.6_
  
  - [x] 8.2 Implementar processamento assíncrono de mensagens



    - Extrair mensagens do payload do webhook


    - Enfileirar processamento via Celery
    - Retornar 200 OK imediatamente
    - _Requirements: 1.1, 12.8_
  
  - [x] 8.3 Implementar envio de mensagens para WhatsApp






    - Método send_text_message()
    - Método send_image_message()
    - Método send_template_message()
    - Implementar retry com backoff
    - _Requirements: 1.1, 1.6_
  
  - [ ]* 8.4 Escrever testes unitários do Webhook Handler
    - Testar validação de signature
    - Testar deduplicação
    - Testar processamento assíncrono
    - Testar envio de mensagens
    - _Requirements: 11.1_

---

## Phase 7: Celery Workers para Tarefas Assíncronas

- [x] 9. Implementar Celery Workers





  - [x] 9.1 Configurar Celery com Redis como broker

    - Configurar Celery app
    - Definir queues (default, high_priority, low_priority)
    - Configurar retry policies
    - Configurar rate limiting
    - _Requirements: 13.6, 12.8_
  
  - [x] 9.2 Implementar tasks assíncronas

    - process_message_task(): Processar mensagem do WhatsApp
    - save_session_to_duckdb_task(): Persistir sessão no DuckDB
    - generate_embeddings_task(): Gerar embeddings de mensagens
    - notify_human_handoff_task(): Notificar equipe de handoff
    - send_reengagement_task(): Enviar mensagens de reengajamento
    - collect_metrics_task(): Coletar e agregar métricas
    - _Requirements: 6.10, 8.1, 8.2, 8.3, 8.4_
  
  - [x] 9.3 Implementar idempotência e debounce



    - Idempotência por chave de turno (session_id:turn_id)
    - Debounce de eventos rápidos (consolidar edições)
    - Deduplicação de jobs
    - _Requirements: 6.4, 12.9_
  
  - [ ]* 9.4 Escrever testes de tasks Celery
    - Testar execução de tasks
    - Testar retry policies
    - Testar idempotência
    - Testar debounce
    - _Requirements: 11.1_

---

## Phase 8: Qualificação de Leads

- [ ] 10. Implementar sistema de qualificação de leads
  - [ ] 10.1 Criar algoritmo de scoring
    - Calcular score baseado em: orçamento definido (30%), urgência (25%), preferências claras (25%), engajamento (20%)
    - Normalizar score para 0-100
    - Classificar leads: high (>= 60), medium (40-59), low (< 40)
    - _Requirements: 2.4, 2.5_
  
  - [ ] 10.2 Implementar encaminhamento de leads
    - Criar registro em qualified_leads quando score >= 60
    - Notificar concessionária via email/WhatsApp
    - Incluir: perfil completo, score, histórico, recomendações
    - _Requirements: 2.6, 2.7_
  
  - [ ] 10.3 Implementar nutrição de leads de baixo score
    - Enviar conteúdo educativo para leads < 60
    - Agendar reengajamento após 7 dias
    - _Requirements: 2.6, 8.2, 8.5_
  
  - [ ]* 10.4 Escrever testes do sistema de qualificação
    - Testar cálculo de score
    - Testar classificação de leads
    - Testar encaminhamento
    - Testar nutrição
    - _Requirements: 11.1_

---

## Phase 9: Notificações e Reengajamento

- [ ] 11. Implementar sistema de notificações
  - [ ] 11.1 Implementar notificações automáticas
    - Reengajamento após 48h de inatividade
    - Novos carros que atendem perfil
    - Redução de preço >= 5%
    - Lembrete de test-drive não agendado
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 11.2 Implementar regras de frequência
    - Respeitar horário comercial (9h-20h)
    - Limite de 2 mensagens/dia por lead
    - Pausar após 3 tentativas sem resposta (30 dias)
    - _Requirements: 8.5, 8.7_
  
  - [ ] 11.3 Implementar segmentação de notificações
    - Segmentar por perfil de usuário
    - Personalizar mensagens baseado em histórico
    - _Requirements: 8.6_
  
  - [ ]* 11.4 Escrever testes do sistema de notificações
    - Testar disparo de notificações
    - Testar regras de frequência
    - Testar segmentação
    - _Requirements: 11.1_

---

## Phase 10: Analytics e Métricas

- [ ] 12. Implementar coleta de métricas
  - [ ] 12.1 Configurar Prometheus metrics
    - Contadores: messages_received, messages_sent, nlp_predictions, leads_qualified
    - Histogramas: response_latency, nlp_processing_time
    - Gauges: active_sessions, redis_connections
    - _Requirements: 9.1, 9.2_
  
  - [ ] 12.2 Implementar endpoints de métricas
    - GET /metrics: Prometheus metrics
    - GET /health: Health check
    - GET /ready: Readiness probe
    - _Requirements: 9.1_
  
  - [ ] 12.3 Criar dashboards Grafana
    - Dashboard 1: Overview (mensagens, leads, latência, erros)
    - Dashboard 2: NLP Performance (intenções, precisão, tempo)
    - Dashboard 3: Business Metrics (leads, conversão, handoffs)
    - Dashboard 4: Infrastructure (CPU, memória, Redis, DB)
    - _Requirements: 9.5_
  
  - [ ]* 12.4 Escrever testes de métricas
    - Testar coleta de métricas
    - Testar endpoints
    - _Requirements: 11.1_

---

## Phase 11: Segurança e LGPD

- [ ] 13. Implementar compliance com LGPD
  - [ ] 13.1 Implementar solicitação de consentimento
    - Solicitar consentimento no primeiro contato
    - Armazenar consentimento com timestamp
    - Bloquear processamento sem consentimento
    - _Requirements: 10.1_
  
  - [ ] 13.2 Implementar direito ao esquecimento
    - Endpoint para solicitar exclusão de dados
    - Anonimizar dados em PostgreSQL
    - Remover sessões do Redis
    - Remover contexto do DuckDB
    - Logar auditoria de exclusões
    - _Requirements: 10.3_
  
  - [ ] 13.3 Implementar criptografia
    - Criptografar dados sensíveis (CPF, email) com AES-256
    - TLS 1.3 para todas as comunicações
    - Gerenciar secrets via HashiCorp Vault ou AWS Secrets
    - _Requirements: 10.2, 10.4_
  
  - [ ] 13.4 Implementar auditoria
    - Logar todas as operações sensíveis
    - Registrar acessos a dados pessoais
    - Retenção de logs por 1 ano
    - _Requirements: 10.5, 10.7_
  
  - [ ]* 13.5 Escrever testes de segurança e compliance
    - Testar solicitação de consentimento
    - Testar exclusão de dados
    - Testar criptografia
    - Testar auditoria
    - _Requirements: 11.1_

---

## Phase 12: Testes End-to-End

- [ ] 14. Implementar testes E2E
  - [ ] 14.1 Configurar ambiente de testes E2E
    - Configurar Playwright para automação
    - Criar simulador de WhatsApp para testes
    - Configurar ambiente isolado (Docker)
    - _Requirements: 11.3_
  
  - [ ] 14.2 Implementar testes de jornada completa do usuário
    - Testar fluxo: saudação → qualificação → recomendações → detalhes → contato
    - Validar todas as transições de estado
    - Validar formatação de mensagens
    - _Requirements: 11.1, 11.5_
  
  - [ ] 14.3 Implementar testes de performance
    - Testar 100 conversas simultâneas
    - Validar latência P95 < 3s
    - Validar taxa de erro < 1%
    - _Requirements: 11.3, 12.1_
  
  - [ ] 14.4 Implementar testes de precisão NLP
    - Dataset de 500+ mensagens reais
    - Validar precisão >= 85%
    - Testar edge cases
    - _Requirements: 11.4_

---

## Phase 13: Deployment e DevOps

- [ ] 15. Configurar infraestrutura de produção
  - [ ] 15.1 Criar Dockerfiles
    - Dockerfile para chatbot service
    - Dockerfile para Celery workers
    - Docker Compose para desenvolvimento
    - _Requirements: 12.7_
  
  - [ ] 15.2 Configurar Kubernetes
    - Deployment manifests (chatbot, celery, redis, postgres)
    - Service manifests
    - HorizontalPodAutoscaler (3-20 pods)
    - ConfigMaps e Secrets
    - _Requirements: 12.2, 12.6_
  
  - [ ] 15.3 Implementar CI/CD pipeline
    - GitHub Actions workflow
    - Stages: lint → test → build → deploy
    - Blue-green deployment
    - Smoke tests pós-deploy
    - _Requirements: 12.7_
  
  - [ ] 15.4 Configurar monitoring e alerting
    - Prometheus para coleta de métricas
    - Grafana para visualização
    - Alertmanager para alertas
    - Integração com PagerDuty/Slack
    - _Requirements: 9.6_

---

## Phase 14: Documentação e Handoff

- [ ] 16. Criar documentação completa
  - [ ] 16.1 Documentação técnica
    - README com instruções de setup
    - Guia de desenvolvimento
    - Guia de deployment
    - Troubleshooting guide
    - API documentation (OpenAPI/Swagger)
  
  - [ ] 16.2 Documentação de operação
    - Runbook para operações
    - Guia de monitoramento
    - Procedimentos de incident response
    - Guia de backup e recovery
  
  - [ ] 16.3 Documentação de negócio
    - Guia de uso para equipe de atendimento
    - Fluxos conversacionais
    - Métricas e KPIs
    - Casos de uso e exemplos

---

## Resumo de Entregas

**MVP (Minimum Viable Product)**:
- Phases 1-6: Infraestrutura + Core Services + Integração Backend + Webhook
- Funcionalidades: Receber mensagens, processar NLP, gerar recomendações, enviar respostas
- Tempo estimado: 4-6 semanas

**Versão Completa**:
- Todas as 16 fases
- Funcionalidades: MVP + Qualificação de leads + Notificações + Analytics + LGPD + E2E Tests + Deployment
- Tempo estimado: 8-12 semanas

**Tarefas Opcionais (marcadas com `*`)**:
- Testes unitários e de integração adicionais
- Podem ser implementadas após MVP para aumentar cobertura de testes

**Metodologia XP**:
- Cada fase entrega valor incremental
- Testes escritos antes do código (TDD)
- Integração contínua a cada commit
- Refatoração constante
- Pair programming recomendado para tarefas complexas
