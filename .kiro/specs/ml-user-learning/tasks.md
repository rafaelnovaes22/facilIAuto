# Implementation Plan - Sistema de ML para Aprendizado com Usuários

## Fase 1: Infraestrutura de Coleta de Dados

- [x] 1. Criar estrutura de dados para interações no backend


  - Criar diretório `platform/backend/data/interactions/`
  - Criar arquivo inicial `user_interactions.json` com estrutura vazia
  - Criar modelo Pydantic `InteractionEvent` em `platform/backend/models/interaction.py`
  - Definir tipos de interação: 'click', 'view_details', 'whatsapp_contact'
  - _Requirements: 1.1, 1.2, 1.3, 2.1_

- [x] 2. Implementar InteractionService no backend

  - [x] 2.1 Criar `platform/backend/services/interaction_service.py`


    - Implementar método `save_interaction()` que persiste eventos em JSON
    - Implementar método `get_all_interactions()` para retornar dados de treinamento
    - Implementar método `get_stats()` para estatísticas básicas
    - Implementar método `get_interactions_count()` para total de interações
    - Adicionar tratamento de erros e logging
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ]* 2.2 Escrever testes unitários para InteractionService
    - Criar `platform/backend/tests/test_interaction_service.py`
    - Testar salvamento de interação
    - Testar recuperação de interações
    - Testar cálculo de estatísticas
    - Testar comportamento com arquivo inexistente
    - _Requirements: 2.1, 2.4_

- [x] 3. Adicionar endpoints de API para coleta de interações

  - [x] 3.1 Implementar endpoints em `platform/backend/api/main.py`


    - Adicionar `POST /api/interactions/track` para receber eventos
    - Adicionar `GET /api/ml/stats` para retornar estatísticas
    - Integrar com InteractionService
    - Adicionar validação de entrada com Pydantic
    - Implementar tratamento de erros sem bloquear resposta
    - _Requirements: 1.5, 2.4, 7.2_
  
  - [ ]* 3.2 Escrever testes de integração para API
    - Criar testes em `platform/backend/tests/test_api_interactions.py`
    - Testar POST /api/interactions/track com dados válidos
    - Testar GET /api/ml/stats retorna estatísticas corretas
    - Testar comportamento com dados inválidos
    - _Requirements: 1.5, 2.4_

- [x] 4. Implementar InteractionTracker no frontend


  - [x] 4.1 Criar serviço de tracking


    - Criar `platform/frontend/src/services/InteractionTracker.ts`
    - Implementar classe InteractionTracker com métodos trackCarClick, trackWhatsAppClick, trackViewDuration
    - Implementar gerenciamento de session_id no localStorage
    - Implementar envio assíncrono de eventos para API
    - Adicionar tratamento de erros sem bloquear UI
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.3_
  
  - [x] 4.2 Integrar tracking nos componentes existentes


    - Integrar em `platform/frontend/src/components/results/CarCard.tsx` para capturar cliques
    - Integrar em `platform/frontend/src/components/results/CarDetailsModal.tsx` para capturar visualizações e WhatsApp
    - Usar useEffect para medir tempo de visualização (threshold 10 segundos)
    - Passar contexto de preferências do usuário em cada evento
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ]* 4.3 Escrever testes para InteractionTracker
    - Criar `platform/frontend/src/services/InteractionTracker.test.ts`
    - Testar criação e persistência de session_id
    - Testar envio de eventos com estrutura correta
    - Testar comportamento em caso de falha de rede
    - _Requirements: 1.4, 1.5_

## Fase 2: Feature Engineering e Modelo ML

- [ ] 5. Implementar feature engineering
  - [ ] 5.1 Criar MLService com preparação de features
    - Criar `platform/backend/services/ml_service.py`
    - Implementar método `prepare_features()` que transforma dados brutos em matriz numérica
    - Implementar normalização de features numéricas (budget, price, year, mileage)
    - Implementar encoding de features categóricas (usage, fuel_type, transmission)
    - Implementar encoding de priorities como vetores binários
    - Criar variável target baseada em interaction_type (click=1, view_details=2, whatsapp_contact=3)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 5.2 Escrever testes para feature engineering
    - Criar testes em `platform/backend/tests/test_ml_service.py`
    - Testar transformação de dados brutos em features
    - Testar normalização de valores numéricos
    - Testar encoding de valores categóricos
    - Testar criação de variável target
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6. Implementar treinamento do modelo ML
  - [ ] 6.1 Adicionar lógica de treinamento no MLService
    - Implementar método `train_model()` que treina Random Forest Regressor
    - Adicionar validação de mínimo de interações (500)
    - Implementar split de dados (80% treino, 20% teste)
    - Configurar hiperparâmetros do Random Forest (n_estimators=100, max_depth=10)
    - Implementar método `evaluate_model()` para calcular métricas (RMSE, MAE, R²)
    - Implementar métodos `save_model()` e `load_model()` usando joblib
    - Salvar metadata do modelo (versão, data, métricas, features)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ] 6.2 Criar script de treinamento standalone
    - Criar `platform/backend/scripts/train_ml_model.py`
    - Script deve carregar interações, treinar modelo, avaliar e salvar
    - Adicionar logging detalhado do processo
    - Adicionar validação de performance mínima antes de salvar
    - Script deve ser executável via linha de comando
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 6.1, 6.2_
  
  - [ ]* 6.3 Escrever testes para treinamento
    - Adicionar testes em `platform/backend/tests/test_ml_service.py`
    - Testar treinamento com dados sintéticos
    - Testar que não treina com dados insuficientes
    - Testar salvamento e carregamento de modelo
    - Testar cálculo de métricas
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 7. Implementar predição com modelo ML
  - [ ] 7.1 Adicionar método de predição no MLService
    - Implementar método `predict_score()` que recebe preferências e carro
    - Transformar inputs em features usando mesmo pipeline de treinamento
    - Fazer predição com modelo carregado
    - Normalizar score de saída para range [0, 1]
    - Retornar 0.0 se modelo não estiver disponível
    - _Requirements: 4.1, 5.1, 7.2_
  
  - [ ]* 7.2 Escrever testes para predição
    - Adicionar testes em `platform/backend/tests/test_ml_service.py`
    - Testar predição com modelo treinado
    - Testar comportamento sem modelo disponível
    - Testar que score está no range [0, 1]
    - _Requirements: 4.1, 5.1_

## Fase 3: Sistema Híbrido de Recomendação

- [ ] 8. Implementar HybridRecommendationEngine
  - [ ] 8.1 Criar engine híbrido
    - Criar `platform/backend/services/hybrid_recommendation_engine.py`
    - Inicializar UnifiedRecommendationEngine (regras) e MLService
    - Implementar método `get_recommendations()` que combina scores
    - Calcular score de regras para cada carro (usando engine atual)
    - Se ML disponível, calcular score ML para cada carro
    - Combinar scores usando pesos configuráveis (70% regras + 30% ML)
    - Reordenar carros por score híbrido
    - Implementar fallback gracioso se ML falhar
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 7.2_
  
  - [ ] 8.2 Adicionar método get_stats() no HybridEngine
    - Retornar se ML está disponível
    - Retornar pesos atuais (regras vs ML)
    - Retornar versão do modelo ML
    - Retornar estatísticas de uso
    - _Requirements: 7.1, 7.4_
  
  - [ ]* 8.3 Escrever testes para HybridEngine
    - Criar `platform/backend/tests/test_hybrid_engine.py`
    - Testar combinação de scores com ML disponível
    - Testar fallback quando ML não disponível
    - Testar reordenação de resultados
    - Testar cálculo de estatísticas
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 9. Integrar sistema híbrido na API
  - [ ] 9.1 Atualizar endpoints de recomendação
    - Modificar `platform/backend/api/main.py`
    - Substituir UnifiedRecommendationEngine por HybridRecommendationEngine no endpoint principal
    - Manter endpoint antigo como fallback/comparação
    - Adicionar campo `ml_score` nos carros retornados (para debug)
    - Adicionar logging de uso de ML vs regras
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 7.1_
  
  - [ ] 9.2 Atualizar endpoint de estatísticas
    - Modificar GET /api/ml/stats para incluir estatísticas do HybridEngine
    - Adicionar informações sobre modelo ML (versão, métricas, data de treinamento)
    - Adicionar contadores de uso (quantas recomendações usaram ML)
    - _Requirements: 7.1, 7.4_
  
  - [ ]* 9.3 Escrever testes de integração
    - Criar `platform/backend/tests/test_api_hybrid.py`
    - Testar endpoint de recomendação híbrida
    - Testar que scores são combinados corretamente
    - Testar endpoint de estatísticas
    - _Requirements: 5.1, 7.1_

## Fase 4: Retreinamento e Monitoramento

- [ ] 10. Implementar pipeline de retreinamento
  - [ ] 10.1 Criar script de retreinamento periódico
    - Criar `platform/backend/scripts/retrain_ml_model.py`
    - Carregar dados novos desde último treinamento
    - Treinar novo modelo com dados atualizados
    - Comparar performance com modelo anterior
    - Substituir modelo apenas se performance melhorar
    - Salvar logs de retreinamento com timestamp e métricas
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ] 10.2 Documentar processo de retreinamento
    - Criar `platform/backend/docs/ML_RETRAINING.md`
    - Documentar quando retreinar (ex: semanalmente ou a cada 1000 novas interações)
    - Documentar como executar script manualmente
    - Documentar como configurar cron job para automação
    - Documentar métricas de performance esperadas
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 11. Adicionar monitoramento e observabilidade
  - [ ] 11.1 Implementar logging detalhado
    - Adicionar logs em MLService para tempo de inferência
    - Adicionar logs em HybridEngine para uso de ML vs regras
    - Adicionar logs em InteractionService para volume de dados
    - Adicionar logs de erros com fallback gracioso
    - Configurar níveis de log apropriados (INFO, WARNING, ERROR)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 11.2 Criar endpoint de health check para ML
    - Adicionar GET /api/ml/health em `platform/backend/api/main.py`
    - Retornar status do modelo ML (disponível, versão, última atualização)
    - Retornar métricas de performance do modelo
    - Retornar estatísticas de uso (total de predições, tempo médio)
    - Retornar alertas se houver problemas
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 12. Implementar conformidade com privacidade
  - [ ] 12.1 Validar anonimização de dados
    - Revisar InteractionService para garantir que não armazena PII
    - Garantir que session_id é anônimo e não vinculável a usuário real
    - Adicionar documentação sobre privacidade em `platform/backend/docs/PRIVACY.md`
    - Implementar limpeza de session_id ao limpar localStorage
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 12.2 Adicionar política de retenção de dados
    - Documentar por quanto tempo dados de interação são mantidos
    - Implementar script opcional para limpar dados antigos
    - Adicionar configuração para período de retenção
    - _Requirements: 8.1, 8.4_

## Fase 5: Documentação e Finalização

- [ ] 13. Criar documentação completa
  - Criar `platform/backend/docs/ML_SYSTEM.md` com visão geral do sistema
  - Documentar arquitetura e fluxo de dados
  - Documentar como adicionar novas features
  - Documentar como ajustar pesos do sistema híbrido
  - Criar guia de troubleshooting para problemas comuns
  - _Requirements: Todos_

- [ ] 14. Preparar para produção
  - Adicionar variáveis de ambiente para configuração (pesos, thresholds)
  - Criar checklist de deploy
  - Documentar requisitos de infraestrutura
  - Criar plano de rollback caso ML cause problemas
  - Documentar estratégia de A/B testing para validar ML
  - _Requirements: 7.1, 7.2, 7.5_
