# Requirements Document - Chatbot WhatsApp FacilIAuto

## Introduction

O chatbot WhatsApp do FacilIAuto é uma solução de atendimento automatizado que permite aos clientes interagirem com a plataforma através do WhatsApp, obtendo recomendações personalizadas de veículos, esclarecendo dúvidas sobre carros disponíveis e sendo qualificados como leads antes de serem direcionados às concessionárias. O sistema integra-se com os agentes de IA existentes do projeto, aproveitando a expertise em recomendação de veículos, análise de dados e IA responsável, seguindo a metodologia XP com testes E2E completos.

O chatbot atua como primeiro ponto de contato digital, qualificando 100% dos leads através de conversação natural, aumentando a taxa de conversão de 5-15% (padrão do mercado) para 60%+ através de recomendações inteligentes e contextualizadas.

---

## Requirements

### Requirement 1: Integração com WhatsApp Business API

**User Story:** Como cliente interessado em comprar um carro, quero conversar com o FacilIAuto pelo WhatsApp, para que eu possa obter recomendações de forma conveniente e familiar.

#### Acceptance Criteria

1. WHEN um cliente envia uma mensagem para o número WhatsApp do FacilIAuto THEN o sistema SHALL responder em até 3 segundos com uma mensagem de boas-vindas
2. WHEN o cliente está interagindo com o chatbot THEN o sistema SHALL manter o contexto da conversa por até 24 horas
3. IF o cliente não responder por mais de 24 horas THEN o sistema SHALL encerrar a sessão e enviar mensagem de reengajamento após 48 horas
4. WHEN múltiplos clientes enviam mensagens simultaneamente THEN o sistema SHALL processar cada conversa de forma independente sem interferência
5. WHEN o sistema recebe mensagens de texto, áudio, imagem ou documento THEN o sistema SHALL processar adequadamente cada tipo de mídia
6. WHEN ocorre erro na API do WhatsApp THEN o sistema SHALL implementar retry com backoff exponencial (3 tentativas) e notificar equipe técnica

### Requirement 2: Qualificação Inteligente de Leads

**User Story:** Como concessionária parceira, quero receber apenas leads qualificados pelo chatbot, para que eu possa focar meu tempo em clientes com alta probabilidade de conversão.

#### Acceptance Criteria

1. WHEN o chatbot inicia uma conversa THEN o sistema SHALL coletar informações essenciais (orçamento, uso pretendido, preferências) através de perguntas conversacionais
2. WHEN o cliente fornece informações incompletas THEN o sistema SHALL fazer perguntas de esclarecimento de forma natural e não intrusiva
3. IF o cliente demonstra interesse genuíno (responde 3+ perguntas) THEN o sistema SHALL classificá-lo como lead qualificado
4. WHEN o perfil do cliente está completo THEN o sistema SHALL calcular score de qualificação (0-100) baseado em: orçamento definido (30%), urgência de compra (25%), preferências claras (25%), engajamento (20%)
5. IF o score de qualificação >= 60 THEN o sistema SHALL encaminhar lead para concessionária com prioridade alta
6. IF o score de qualificação < 60 THEN o sistema SHALL nutrir o lead com conteúdo educativo e reengajar após 7 dias
7. WHEN o lead é encaminhado THEN o sistema SHALL incluir: perfil completo, score, histórico de conversa, recomendações geradas

### Requirement 3: Recomendação Personalizada de Veículos

**User Story:** Como cliente, quero receber recomendações de carros que realmente atendam minhas necessidades, para que eu possa tomar uma decisão de compra informada.

#### Acceptance Criteria

1. WHEN o cliente completa o perfil básico THEN o sistema SHALL gerar até 5 recomendações usando o UnifiedRecommendationEngine existente
2. WHEN as recomendações são geradas THEN o sistema SHALL apresentar cada carro com: foto, marca/modelo, ano, preço, score de compatibilidade (%), justificativa personalizada
3. IF o cliente solicita mais detalhes sobre um carro THEN o sistema SHALL fornecer: especificações técnicas, itens de série, histórico (se usado), localização da concessionária, link para fotos adicionais
4. WHEN o cliente rejeita uma recomendação THEN o sistema SHALL perguntar o motivo e ajustar os pesos do algoritmo para próximas recomendações
5. IF o cliente demonstra interesse em um carro específico THEN o sistema SHALL oferecer: agendar test-drive, falar com vendedor, simular financiamento, comparar com similares
6. WHEN o cliente solicita comparação THEN o sistema SHALL apresentar tabela comparativa de até 3 carros com critérios relevantes ao perfil
7. WHEN nenhuma recomendação atende o perfil THEN o sistema SHALL sugerir ajustes no orçamento ou preferências e explicar o motivo

### Requirement 4: Processamento de Linguagem Natural (NLP)

**User Story:** Como cliente, quero conversar naturalmente com o chatbot sem precisar usar comandos específicos, para que a experiência seja fluida e intuitiva.

#### Acceptance Criteria

1. WHEN o cliente envia mensagem em português THEN o sistema SHALL compreender variações regionais (PT-BR) e gírias comuns do contexto automotivo
2. WHEN o cliente faz pergunta sobre características de carros THEN o sistema SHALL identificar a intenção (economia, espaço, performance, segurança, tecnologia) com precisão >= 85%
3. IF o cliente usa termos ambíguos THEN o sistema SHALL solicitar esclarecimento com opções de múltipla escolha
4. WHEN o cliente expressa emoções (frustração, empolgação, dúvida) THEN o sistema SHALL adaptar o tom da resposta apropriadamente
5. WHEN o cliente faz múltiplas perguntas em uma mensagem THEN o sistema SHALL identificar e responder cada pergunta separadamente
6. IF o sistema não compreende a mensagem THEN o sistema SHALL pedir reformulação e oferecer exemplos de perguntas válidas
7. WHEN o cliente usa abreviações comuns (SUV, 4x4, 0km, semi-novo) THEN o sistema SHALL interpretar corretamente

### Requirement 5: Integração com Sistema de Recomendação Existente

**User Story:** Como desenvolvedor, quero que o chatbot utilize o UnifiedRecommendationEngine existente, para que mantenhamos consistência nas recomendações entre web e WhatsApp.

#### Acceptance Criteria

1. WHEN o chatbot precisa gerar recomendações THEN o sistema SHALL utilizar a API do backend existente (FastAPI) em /api/recommendations
2. WHEN o perfil do usuário é construído THEN o sistema SHALL mapear as respostas do chat para o formato UserProfile do engine existente
3. IF o backend está indisponível THEN o sistema SHALL usar cache local das últimas recomendações e notificar o usuário sobre possível desatualização
4. WHEN o usuário interage com recomendações THEN o sistema SHALL enviar feedback para o backend para aprendizado contínuo
5. WHEN o chatbot acessa dados de carros THEN o sistema SHALL usar o mesmo dataset (89 carros RobustCar) do sistema web
6. IF há atualização no catálogo de carros THEN o sistema SHALL sincronizar automaticamente a cada 1 hora
7. WHEN métricas são coletadas THEN o sistema SHALL enviar para o mesmo Prometheus/Grafana do backend

### Requirement 6: Gestão de Conversas e Contexto (Anti-Eco)

**User Story:** Como cliente, quero que o chatbot lembre do que conversamos anteriormente sem repetir informações, para que eu tenha uma conversa natural e fluida.

#### Acceptance Criteria

1. WHEN uma conversa é iniciada THEN o sistema SHALL criar sessão única com ID (session_id:turn_id) e timestamp usando PydanticAI para memória tipada
2. WHEN o cliente fornece informação THEN o sistema SHALL armazenar no contexto usando LangGraph com MemorySaver() e checkpoints, mantendo apenas o essencial
3. IF o cliente retorna após < 24 horas THEN o sistema SHALL recuperar resumo conversacional incremental (não histórico bruto) do Redis
4. WHEN múltiplas escritas concorrentes ocorrem THEN o sistema SHALL usar Redis locks distribuídos (SET NX com TTL) para garantir um único write por turno
5. WHEN o cliente muda de preferência THEN o sistema SHALL atualizar contexto com idempotency key e regenerar recomendações
6. WHEN a sessão expira THEN o sistema SHALL arquivar histórico estruturado no DuckDB para consultas baratas sem reprocessamento
7. IF o cliente solicita "recomeçar" THEN o sistema SHALL limpar contexto e iniciar nova qualificação
8. WHEN há múltiplas sessões do mesmo número THEN o sistema SHALL manter histórico de todas as interações para análise de comportamento
9. WHEN respostas são geradas THEN o sistema SHALL aplicar deduplicação por hash do conteúdo antes de enviar (Guardrails)
10. WHEN tarefas de memória são processadas THEN o sistema SHALL usar Celery para write-behind assíncrono (resumo, embeddings, métricas) fora do request principal

### Requirement 7: Handoff para Atendimento Humano

**User Story:** Como cliente, quero falar com um atendente humano quando o chatbot não consegue resolver minha dúvida, para que eu receba suporte adequado.

#### Acceptance Criteria

1. WHEN o cliente solicita atendimento humano (palavras-chave: "atendente", "humano", "pessoa") THEN o sistema SHALL transferir para fila de atendimento em até 30 segundos
2. WHEN o chatbot não consegue responder 3 vezes consecutivas THEN o sistema SHALL oferecer automaticamente transferência para humano
3. IF não há atendentes disponíveis THEN o sistema SHALL informar horário de atendimento e oferecer callback
4. WHEN a transferência ocorre THEN o sistema SHALL enviar para o atendente: histórico completo da conversa, perfil do cliente, recomendações geradas, score de qualificação
5. WHEN o atendimento humano é finalizado THEN o sistema SHALL solicitar avaliação (1-5 estrelas) e feedback opcional
6. IF o cliente não avalia THEN o sistema SHALL enviar lembrete após 2 horas
7. WHEN o atendimento é avaliado THEN o sistema SHALL armazenar métricas para análise de qualidade

### Requirement 8: Notificações e Reengajamento

**User Story:** Como concessionária, quero que o sistema reengaje leads inativos automaticamente, para que possamos maximizar conversões.

#### Acceptance Criteria

1. WHEN um lead qualificado não responde por 48 horas THEN o sistema SHALL enviar mensagem de reengajamento personalizada
2. WHEN novos carros que atendem o perfil chegam THEN o sistema SHALL notificar leads relevantes em até 2 horas
3. IF um carro recomendado tem redução de preço >= 5% THEN o sistema SHALL notificar leads interessados imediatamente
4. WHEN um lead demonstrou interesse mas não agendou test-drive THEN o sistema SHALL enviar lembrete após 24 horas
5. IF o lead não responde a 3 tentativas de reengajamento THEN o sistema SHALL marcar como "inativo" e pausar notificações por 30 dias
6. WHEN há promoções especiais THEN o sistema SHALL segmentar e notificar apenas leads com perfil compatível
7. WHEN notificações são enviadas THEN o sistema SHALL respeitar horário comercial (9h-20h) e limite de 2 mensagens/dia por lead

### Requirement 9: Analytics e Métricas

**User Story:** Como gestor da plataforma, quero visualizar métricas de performance do chatbot, para que eu possa otimizar continuamente a experiência.

#### Acceptance Criteria

1. WHEN uma conversa é iniciada THEN o sistema SHALL registrar: timestamp, origem (QR code, link, anúncio), dispositivo
2. WHEN uma interação ocorre THEN o sistema SHALL medir: tempo de resposta, taxa de compreensão NLP, satisfação inferida
3. WHEN um lead é qualificado THEN o sistema SHALL registrar: score, tempo até qualificação, número de mensagens trocadas
4. WHEN uma conversão ocorre THEN o sistema SHALL rastrear: lead_id, carro escolhido, concessionária, valor da venda
5. WHEN métricas são coletadas THEN o sistema SHALL calcular KPIs: taxa de resposta, taxa de qualificação, taxa de conversão, tempo médio de atendimento, CSAT score
6. IF taxa de compreensão NLP < 80% THEN o sistema SHALL alertar equipe para retreinamento do modelo
7. WHEN dashboards são acessados THEN o sistema SHALL apresentar métricas em tempo real com latência < 5 segundos

### Requirement 10: Segurança e Compliance

**User Story:** Como responsável pela plataforma, quero garantir que dados dos clientes sejam protegidos conforme LGPD, para que evitemos problemas legais e mantenhamos confiança.

#### Acceptance Criteria

1. WHEN dados pessoais são coletados THEN o sistema SHALL solicitar consentimento explícito conforme LGPD
2. WHEN dados são armazenados THEN o sistema SHALL criptografar informações sensíveis (CPF, telefone, email) usando AES-256
3. IF o cliente solicita exclusão de dados (direito ao esquecimento) THEN o sistema SHALL remover todos os dados em até 48 horas
4. WHEN mensagens são transmitidas THEN o sistema SHALL usar HTTPS/TLS 1.3 para todas as comunicações
5. WHEN há acesso a dados THEN o sistema SHALL registrar logs de auditoria com: usuário, ação, timestamp, IP
6. IF detectada tentativa de acesso não autorizado THEN o sistema SHALL bloquear IP e notificar equipe de segurança
7. WHEN dados são compartilhados com concessionárias THEN o sistema SHALL anonimizar informações não essenciais e obter consentimento do cliente

### Requirement 11: Testes End-to-End (E2E)

**User Story:** Como desenvolvedor, quero garantir que o chatbot funcione corretamente em todos os cenários, para que entreguemos qualidade em produção.

#### Acceptance Criteria

1. WHEN testes E2E são executados THEN o sistema SHALL validar fluxo completo: recepção de mensagem → processamento NLP → geração de recomendação → envio de resposta
2. WHEN testes de integração são executados THEN o sistema SHALL validar comunicação com: WhatsApp API, Backend FastAPI, Redis, PostgreSQL, Prometheus
3. IF testes de carga são executados THEN o sistema SHALL suportar 100 conversas simultâneas com latência < 3s (P95)
4. WHEN testes de NLP são executados THEN o sistema SHALL validar precisão >= 85% em dataset de 500+ mensagens reais
5. WHEN testes de recomendação são executados THEN o sistema SHALL validar consistência com engine web (mesmas entradas = mesmas saídas)
6. IF testes de resiliência são executados THEN o sistema SHALL recuperar gracefully de falhas (API down, timeout, rate limit)
7. WHEN cobertura de testes é medida THEN o sistema SHALL manter >= 80% conforme metodologia XP

### Requirement 12: Escalabilidade e Performance

**User Story:** Como gestor técnico, quero que o chatbot escale conforme crescimento da base de clientes, para que mantenhamos qualidade de serviço.

#### Acceptance Criteria

1. WHEN o sistema está em operação THEN o sistema SHALL processar até 1000 mensagens/minuto com latência média < 2s
2. WHEN há pico de demanda THEN o sistema SHALL escalar horizontalmente adicionando workers Celery automaticamente
3. IF a latência ultrapassa 5s THEN o sistema SHALL ativar circuit breaker e retornar resposta em cache
4. WHEN cache é utilizado THEN o sistema SHALL armazenar respostas frequentes com TTL de 1 hora
5. WHEN banco de dados é acessado THEN o sistema SHALL usar connection pooling com máximo de 50 conexões
6. IF recursos atingem 80% de capacidade THEN o sistema SHALL alertar equipe de infraestrutura
7. WHEN deploy é realizado THEN o sistema SHALL usar blue-green deployment com zero downtime
8. WHEN chamadas a LLMs são feitas THEN o sistema SHALL implementar rate limit e retry com backoff exponencial via Celery
9. WHEN eventos rápidos ocorrem THEN o sistema SHALL aplicar debounce consolidando múltiplas edições do usuário em um único resumo
10. WHEN batch de ferramentas é executado THEN o sistema SHALL usar Celery groups/chords para orquestração paralela e atualização de memória ao final

### Requirement 13: Stack Tecnológica e Arquitetura

**User Story:** Como desenvolvedor, quero usar tecnologias modernas e comprovadas, para que o sistema seja mantível e escalável.

#### Acceptance Criteria

1. WHEN o sistema é desenvolvido THEN o sistema SHALL usar PydanticAI para memória tipada e validada (episódica, resumo conversacional, variáveis de sessão)
2. WHEN fluxos conversacionais são implementados THEN o sistema SHALL usar LangGraph para grafo de estados com checkpoints
3. WHEN sessões são gerenciadas THEN o sistema SHALL usar Redis para armazenamento de sessão, locks distribuídos e cache
4. WHEN contexto estruturado é consultado THEN o sistema SHALL usar DuckDB para consultas baratas sem reprocessar documentos
5. WHEN respostas são validadas THEN o sistema SHALL usar Guardrails para dedupe de saída, filtros de repetição e políticas de estilo
6. WHEN tarefas assíncronas são executadas THEN o sistema SHALL usar Celery como maestro assíncrono com idempotência por chave de turno
7. WHEN persistência é confirmada THEN o sistema SHALL implementar padrão Outbox/Saga (opcional) antes de promover estado do agente
