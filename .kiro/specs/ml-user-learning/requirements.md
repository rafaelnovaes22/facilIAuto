# Requirements Document - Sistema de ML para Aprendizado com Usuários

## Introduction

O FacilIAuto atualmente utiliza um sistema de recomendação baseado em regras que calcula scores de compatibilidade entre preferências do usuário e características dos veículos. Embora funcional, este sistema não aprende com as escolhas reais dos usuários ao longo do tempo.

Esta feature implementará um sistema de Machine Learning que coleta dados de interações dos usuários (cliques, visualizações, contatos) e utiliza esses dados para melhorar progressivamente as recomendações. O sistema será híbrido, combinando o algoritmo de regras atual (para cold start) com modelos de ML (para usuários com histórico), garantindo que o MVP seja viável tecnicamente e agregue valor imediato.

O foco do MVP é criar a infraestrutura de coleta de dados e um modelo simples de aprendizado que possa ser evoluído posteriormente, sem comprometer a experiência atual dos usuários.

## Requirements

### Requirement 1: Coleta de Dados de Interações

**User Story:** Como desenvolvedor do sistema, quero coletar dados de interações dos usuários com os veículos recomendados, para que o modelo de ML possa aprender com comportamentos reais.

#### Acceptance Criteria

1. WHEN um usuário clica em um card de veículo para ver detalhes THEN o sistema SHALL registrar o evento com timestamp, user_session_id, car_id, e contexto da busca (preferências informadas)
2. WHEN um usuário clica no botão de WhatsApp para contatar sobre um veículo THEN o sistema SHALL registrar o evento como interação de alto interesse
3. WHEN um usuário permanece visualizando os detalhes de um veículo por mais de 10 segundos THEN o sistema SHALL registrar o tempo de visualização
4. IF o usuário não estiver autenticado THEN o sistema SHALL utilizar um session_id único armazenado no localStorage para rastrear interações da sessão
5. WHEN eventos são coletados THEN o sistema SHALL enviar os dados para uma API backend de forma assíncrona sem bloquear a UI

### Requirement 2: Armazenamento de Dados de Treinamento

**User Story:** Como cientista de dados, quero que os dados de interações sejam armazenados de forma estruturada, para que eu possa treinar modelos de ML posteriormente.

#### Acceptance Criteria

1. WHEN o backend recebe eventos de interação THEN o sistema SHALL armazenar os dados em uma tabela `user_interactions` com campos: id, session_id, car_id, interaction_type, timestamp, user_preferences_snapshot, duration_seconds
2. WHEN dados são armazenados THEN o sistema SHALL incluir um snapshot das preferências do usuário no momento da busca (budget, usage, priorities)
3. WHEN a tabela de interações atingir 1000+ registros THEN o sistema SHALL estar pronta para extração de features para treinamento
4. IF houver erro no armazenamento THEN o sistema SHALL logar o erro mas não interromper a experiência do usuário

### Requirement 3: Feature Engineering para ML

**User Story:** Como desenvolvedor de ML, quero extrair features relevantes dos dados brutos de interações, para que o modelo possa aprender padrões significativos.

#### Acceptance Criteria

1. WHEN preparando dados para treinamento THEN o sistema SHALL criar features numéricas a partir das preferências do usuário (budget normalizado, usage codificado, priorities como vetores)
2. WHEN preparando dados para treinamento THEN o sistema SHALL criar features dos veículos (price, year, mileage, fuel_type, transmission, todas normalizadas)
3. WHEN preparando dados para treinamento THEN o sistema SHALL criar a variável target baseada no tipo de interação (click=1, view_details=2, whatsapp_contact=3)
4. WHEN features são criadas THEN o sistema SHALL normalizar valores numéricos usando StandardScaler ou MinMaxScaler
5. WHEN features categóricas são processadas THEN o sistema SHALL usar one-hot encoding ou label encoding conforme apropriado

### Requirement 4: Modelo de ML Simples (MVP)

**User Story:** Como usuário do sistema, quero que as recomendações melhorem com base em padrões de comportamento de outros usuários, para que eu receba sugestões mais relevantes.

#### Acceptance Criteria

1. WHEN há dados suficientes (mínimo 500 interações) THEN o sistema SHALL treinar um modelo de classificação ou regressão para prever score de interesse
2. WHEN escolhendo algoritmo THEN o sistema SHALL usar um modelo simples e interpretável (Random Forest ou Gradient Boosting) adequado para MVP
3. WHEN o modelo é treinado THEN o sistema SHALL avaliar performance usando métricas apropriadas (RMSE para regressão ou F1-score para classificação)
4. WHEN o modelo atinge performance mínima aceitável (a ser definida em design) THEN o sistema SHALL salvar o modelo treinado em formato pickle ou joblib
5. IF não houver dados suficientes THEN o sistema SHALL continuar usando apenas o algoritmo de regras atual

### Requirement 5: Sistema Híbrido de Recomendação

**User Story:** Como usuário, quero receber recomendações que combinem regras de negócio com aprendizado de máquina, para que as sugestões sejam tanto precisas quanto personalizadas.

#### Acceptance Criteria

1. WHEN um usuário faz uma busca THEN o sistema SHALL calcular score usando o algoritmo de regras atual (baseline)
2. IF existe modelo ML treinado e disponível THEN o sistema SHALL também calcular score ML para cada veículo
3. WHEN ambos scores estão disponíveis THEN o sistema SHALL combinar os scores usando uma estratégia de ensemble (ex: média ponderada 70% regras + 30% ML para MVP)
4. WHEN não há modelo ML disponível THEN o sistema SHALL usar apenas o score de regras sem degradação de experiência
5. WHEN scores são combinados THEN o sistema SHALL reordenar os resultados baseado no score híbrido final

### Requirement 6: Pipeline de Retreinamento

**User Story:** Como administrador do sistema, quero que o modelo de ML seja retreinado periodicamente com novos dados, para que as recomendações continuem melhorando ao longo do tempo.

#### Acceptance Criteria

1. WHEN o sistema acumula novos dados de interações THEN o sistema SHALL disponibilizar um script de retreinamento que pode ser executado manualmente ou via cron job
2. WHEN o retreinamento é executado THEN o sistema SHALL carregar dados novos desde o último treinamento
3. WHEN novo modelo é treinado THEN o sistema SHALL comparar performance com modelo anterior antes de substituir
4. IF novo modelo tem performance melhor THEN o sistema SHALL substituir o modelo em produção automaticamente
5. WHEN modelo é atualizado THEN o sistema SHALL logar métricas de performance e timestamp da atualização

### Requirement 7: Monitoramento e Observabilidade

**User Story:** Como desenvolvedor, quero monitorar a performance do sistema ML em produção, para que eu possa identificar problemas e oportunidades de melhoria.

#### Acceptance Criteria

1. WHEN o sistema está em produção THEN o sistema SHALL logar quantas recomendações usam apenas regras vs híbrido (regras + ML)
2. WHEN erros ocorrem no modelo ML THEN o sistema SHALL fazer fallback gracioso para o sistema de regras e logar o erro
3. WHEN o modelo ML é usado THEN o sistema SHALL logar tempo de inferência para monitorar performance
4. WHEN dados são coletados THEN o sistema SHALL disponibilizar endpoint para consultar estatísticas básicas (total de interações, distribuição por tipo)
5. IF o modelo ML falhar THEN o sistema SHALL garantir que a experiência do usuário não seja impactada negativamente

### Requirement 8: Privacidade e Conformidade

**User Story:** Como usuário, quero que meus dados de interação sejam tratados de forma responsável e anônima, para que minha privacidade seja respeitada.

#### Acceptance Criteria

1. WHEN dados são coletados THEN o sistema SHALL usar identificadores anônimos (session_id) ao invés de dados pessoais
2. WHEN dados são armazenados THEN o sistema SHALL não incluir informações pessoalmente identificáveis (PII) nas tabelas de interação
3. WHEN usuário limpa cookies/localStorage THEN o sistema SHALL tratar como nova sessão sem vincular ao histórico anterior
4. WHEN dados são usados para treinamento THEN o sistema SHALL agregar e anonimizar dados para proteger privacidade individual
