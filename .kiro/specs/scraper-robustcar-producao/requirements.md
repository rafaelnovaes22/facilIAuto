# Requirements Document - Scraper RobustCar Produção

## Introduction

Este documento especifica os requisitos para um scraper de produção que extrairá dados de veículos do site RobustCar de forma eficiente, confiável e escalável. O scraper deve garantir qualidade de dados, performance otimizada e manutenibilidade.

## Glossary

- **Scraper**: Sistema automatizado que extrai dados estruturados de websites
- **RobustCar**: Concessionária parceira fonte dos dados de veículos
- **ETL**: Extract, Transform, Load - processo de extração, transformação e carga de dados
- **Rate Limiting**: Controle de taxa de requisições para não sobrecarregar o servidor
- **Data Quality**: Qualidade dos dados medida por completude, precisão e consistência
- **Idempotência**: Capacidade de executar múltiplas vezes sem duplicar dados
- **Incremental Load**: Carga apenas de dados novos ou modificados
- **Retry Logic**: Lógica de retentativa em caso de falhas temporárias

## Requirements

### Requirement 1: Extração Completa de Dados

**User Story:** Como engenheiro de dados, quero extrair todos os campos relevantes de cada veículo, para que o sistema de recomendação tenha informações completas.

#### Acceptance Criteria

1. WHEN o scraper processa um veículo, THE Scraper SHALL extrair nome, marca, modelo, ano, preço, quilometragem, combustível, câmbio, cor, portas, categoria, imagens e descrição
2. WHEN um campo obrigatório está ausente, THE Scraper SHALL registrar um warning e aplicar valor padrão documentado
3. WHEN a extração é concluída, THE Scraper SHALL validar que pelo menos 95% dos veículos têm todos os campos obrigatórios preenchidos
4. WHEN dados são extraídos, THE Scraper SHALL normalizar formatos (preços, quilometragem, datas) para padrão definido
5. THE Scraper SHALL extrair metadados incluindo URL original, timestamp de scraping e hash de conteúdo

### Requirement 2: Performance e Eficiência

**User Story:** Como engenheiro de dados, quero que o scraper seja eficiente e rápido, para minimizar tempo de execução e custo de infraestrutura.

#### Acceptance Criteria

1. THE Scraper SHALL processar no mínimo 10 veículos por minuto em condições normais
2. WHEN múltiplas páginas são processadas, THE Scraper SHALL usar paralelização com no máximo 3 workers concorrentes
3. THE Scraper SHALL implementar cache de páginas já visitadas com TTL de 24 horas
4. WHEN uma requisição falha, THE Scraper SHALL implementar exponential backoff com máximo de 3 tentativas
5. THE Scraper SHALL consumir no máximo 500MB de memória RAM durante execução

### Requirement 3: Rate Limiting e Respeito ao Servidor

**User Story:** Como engenheiro de dados, quero respeitar os limites do servidor de origem, para manter boa relação com o parceiro e evitar bloqueios.

#### Acceptance Criteria

1. THE Scraper SHALL aguardar no mínimo 1 segundo entre requisições sequenciais
2. WHEN detectado erro 429 (Too Many Requests), THE Scraper SHALL aguardar 60 segundos antes de retomar
3. THE Scraper SHALL respeitar robots.txt do site de origem
4. THE Scraper SHALL usar User-Agent identificável e contato de suporte
5. WHEN executado em horário comercial (8h-18h), THE Scraper SHALL reduzir taxa para 50% da capacidade

### Requirement 4: Qualidade e Validação de Dados

**User Story:** Como engenheiro de dados, quero garantir qualidade dos dados extraídos, para que o sistema de recomendação funcione corretamente.

#### Acceptance Criteria

1. WHEN câmbio é extraído, THE Scraper SHALL validar que valor está em lista permitida: Manual, Automático, Automático CVT, Automatizada
2. WHEN quilometragem é extraída, THE Scraper SHALL validar que valor é numérico e menor que 500.000 km
3. WHEN preço é extraído, THE Scraper SHALL validar que valor está entre R$ 10.000 e R$ 500.000
4. WHEN ano é extraído, THE Scraper SHALL validar que está entre 2010 e ano atual + 1
5. THE Scraper SHALL gerar relatório de qualidade com percentual de completude por campo

### Requirement 5: Detecção de Mudanças e Carga Incremental

**User Story:** Como engenheiro de dados, quero detectar apenas veículos novos ou modificados, para otimizar tempo de processamento e recursos.

#### Acceptance Criteria

1. THE Scraper SHALL calcular hash MD5 do conteúdo de cada veículo
2. WHEN hash de veículo é igual ao anterior, THE Scraper SHALL pular processamento detalhado
3. THE Scraper SHALL manter histórico de hashes em arquivo SQLite local
4. WHEN veículo não existe mais no site, THE Scraper SHALL marcar como indisponível no banco
5. THE Scraper SHALL processar apenas veículos modificados nas últimas 24 horas em modo incremental

### Requirement 6: Tratamento de Erros e Resiliência

**User Story:** Como engenheiro de dados, quero que o scraper seja resiliente a falhas, para garantir execução confiável mesmo com problemas temporários.

#### Acceptance Criteria

1. WHEN ocorre timeout de rede, THE Scraper SHALL retentar com timeout incrementado até 30 segundos
2. WHEN página retorna erro 5xx, THE Scraper SHALL retentar após 10 segundos
3. WHEN parsing HTML falha, THE Scraper SHALL registrar erro detalhado e continuar com próximo veículo
4. WHEN 10% das extrações falham, THE Scraper SHALL enviar alerta e pausar execução
5. THE Scraper SHALL salvar checkpoint a cada 50 veículos processados para permitir retomada

### Requirement 7: Logging e Monitoramento

**User Story:** Como engenheiro de dados, quero logs detalhados e métricas, para monitorar saúde do scraper e diagnosticar problemas.

#### Acceptance Criteria

1. THE Scraper SHALL registrar logs em formato JSON estruturado com níveis DEBUG, INFO, WARNING, ERROR
2. WHEN scraping inicia, THE Scraper SHALL registrar timestamp, versão e configuração
3. THE Scraper SHALL registrar métricas: total processado, sucessos, falhas, tempo médio por veículo
4. WHEN scraping termina, THE Scraper SHALL gerar relatório com estatísticas completas
5. THE Scraper SHALL exportar métricas em formato Prometheus para monitoramento

### Requirement 8: Configuração e Parametrização

**User Story:** Como engenheiro de dados, quero configurar o scraper facilmente, para ajustar comportamento sem modificar código.

#### Acceptance Criteria

1. THE Scraper SHALL ler configurações de arquivo YAML ou variáveis de ambiente
2. WHERE configuração de rate limit é fornecida, THE Scraper SHALL usar valor configurado
3. WHERE modo de execução é especificado, THE Scraper SHALL executar em modo full ou incremental
4. THE Scraper SHALL validar configurações na inicialização e falhar rápido se inválidas
5. THE Scraper SHALL documentar todas as configurações disponíveis com valores padrão

### Requirement 9: Extração de Seletores Dinâmicos

**User Story:** Como engenheiro de dados, quero que o scraper se adapte a mudanças no HTML, para reduzir manutenção quando site muda.

#### Acceptance Criteria

1. THE Scraper SHALL usar múltiplos seletores CSS alternativos para cada campo
2. WHEN primeiro seletor falha, THE Scraper SHALL tentar seletores alternativos em ordem de prioridade
3. THE Scraper SHALL registrar qual seletor foi usado com sucesso para análise
4. WHEN todos os seletores falham, THE Scraper SHALL registrar HTML da página para debug
5. THE Scraper SHALL permitir atualização de seletores via arquivo de configuração sem redeployment

### Requirement 10: Saída de Dados Estruturada

**User Story:** Como engenheiro de dados, quero dados em formato estruturado e versionado, para facilitar integração com outros sistemas.

#### Acceptance Criteria

1. THE Scraper SHALL exportar dados em formato JSON com schema versionado
2. THE Scraper SHALL incluir metadados: versão do schema, timestamp, total de registros
3. WHEN exportação é concluída, THE Scraper SHALL validar JSON contra schema definido
4. THE Scraper SHALL gerar arquivo separado com dados rejeitados e motivo da rejeição
5. THE Scraper SHALL comprimir saída com gzip para otimizar armazenamento

### Requirement 11: Testes e Validação

**User Story:** Como engenheiro de dados, quero testes automatizados, para garantir qualidade e prevenir regressões.

#### Acceptance Criteria

1. THE Scraper SHALL ter cobertura de testes unitários de no mínimo 80%
2. THE Scraper SHALL ter testes de integração com páginas HTML mockadas
3. THE Scraper SHALL ter smoke test que valida extração de 5 veículos reais
4. WHEN código é modificado, THE Scraper SHALL executar suite de testes automaticamente
5. THE Scraper SHALL ter testes de performance que validam tempo de execução

### Requirement 12: Documentação e Manutenibilidade

**User Story:** Como engenheiro de dados, quero documentação completa, para facilitar manutenção e onboarding de novos desenvolvedores.

#### Acceptance Criteria

1. THE Scraper SHALL ter README com instruções de instalação, configuração e execução
2. THE Scraper SHALL documentar arquitetura com diagramas de fluxo e componentes
3. THE Scraper SHALL documentar todos os seletores CSS com screenshots do HTML
4. THE Scraper SHALL ter guia de troubleshooting com problemas comuns e soluções
5. THE Scraper SHALL ter changelog versionado seguindo Semantic Versioning

---

**Data**: 30/10/2025  
**Versão**: 1.0  
**Status**: Aprovação Pendente
