# WhatsApp Business API - Checklist de Configuração

Use este checklist para garantir que todos os passos de configuração foram completados corretamente.

## 📋 Checklist Completo

### Fase 1: Conta e App no Meta

- [ ] **1.1** Criar conta no Meta Business Suite
  - URL: https://business.facebook.com/
  - Email corporativo configurado
  - Perfil da empresa completo

- [ ] **1.2** Criar app no Meta for Developers
  - URL: https://developers.facebook.com/
  - Tipo: "Empresa"
  - Nome: "FacilIAuto Chatbot"

- [ ] **1.3** Adicionar produto WhatsApp ao app
  - Dashboard → Adicionar Produto → WhatsApp
  - Termos de serviço aceitos

- [ ] **1.4** Vincular conta comercial do WhatsApp
  - Conta comercial selecionada
  - Permissões configuradas

---

### Fase 2: Número de Telefone

**Opção A: Número de Teste (Desenvolvimento)**

- [ ] **2.1** Usar número de teste fornecido pelo Meta
  - Número copiado do painel
  - Válido por tempo limitado

- [ ] **2.2** Adicionar números para teste (máximo 5)
  - Seu número adicionado
  - Código de verificação recebido via WhatsApp
  - Número verificado com sucesso

**Opção B: Número Próprio (Produção)**

- [ ] **2.3** Adicionar número próprio
  - Número não está registrado no WhatsApp pessoal
  - Formato correto: +55 11 99999-9999
  - Método de verificação escolhido (SMS ou voz)

- [ ] **2.4** Verificar número
  - Código de 6 dígitos recebido
  - Código inserido corretamente
  - Verificação concluída em até 14 dias

- [ ] **2.5** Configurar perfil do negócio
  - Nome do negócio: "FacilIAuto"
  - Descrição adicionada
  - Foto de perfil configurada
  - Categoria selecionada: "Automotivo"

---

### Fase 3: Tokens e Credenciais

- [ ] **3.1** Obter token temporário (desenvolvimento)
  - WhatsApp → Introdução → Copiar token
  - Validade: 24 horas
  - Salvo em local seguro

- [ ] **3.2** Criar usuário do sistema (produção)
  - Configurações → Usuários do sistema → Adicionar
  - Nome: "FacilIAuto Chatbot System User"
  - Função: Administrador

- [ ] **3.3** Gerar token permanente
  - Usuário do sistema → Gerar novo token
  - Permissões selecionadas:
    - ☑️ whatsapp_business_messaging
    - ☑️ whatsapp_business_management
  - Token copiado e salvo (não será mostrado novamente!)

- [ ] **3.4** Obter IDs necessários
  - Phone Number ID copiado
  - Business Account ID copiado
  - App ID copiado
  - App Secret copiado

- [ ] **3.5** Configurar arquivo .env
  - Arquivo .env criado (copiar de .env.example)
  - WHATSAPP_ACCESS_TOKEN configurado
  - WHATSAPP_PHONE_NUMBER_ID configurado
  - WHATSAPP_BUSINESS_ACCOUNT_ID configurado
  - WHATSAPP_APP_SECRET configurado
  - WEBHOOK_VERIFY_TOKEN definido (você escolhe)

---

### Fase 4: Webhook

- [ ] **4.1** Preparar endpoint público
  - **Desenvolvimento:** ngrok instalado e configurado
  - **Produção:** Domínio com HTTPS configurado
  - URL pública acessível

- [ ] **4.2** Implementar endpoint de verificação
  - GET /webhook/whatsapp implementado
  - Retorna hub.challenge quando token correto
  - Testado localmente

- [ ] **4.3** Implementar endpoint de recebimento
  - POST /webhook/whatsapp implementado
  - Valida signature do Meta
  - Processa payload corretamente
  - Retorna 200 OK

- [ ] **4.4** Configurar webhook no Meta
  - WhatsApp → Configuração → Webhooks
  - URL configurada: https://your-domain.com/webhook/whatsapp
  - Token de verificação configurado
  - Verificação bem-sucedida ✅

- [ ] **4.5** Assinar eventos
  - ☑️ messages (mensagens recebidas)
  - ☑️ message_status (status de entrega)
  - Eventos salvos

- [ ] **4.6** Validar assinatura de webhook
  - Código de validação implementado
  - X-Hub-Signature-256 verificado
  - Testes passando

---

### Fase 5: Testes

- [ ] **5.1** Validar configuração
  ```bash
  python scripts/validate_whatsapp_config.py
  ```
  - Todas as verificações passaram ✅

- [ ] **5.2** Testar envio de mensagem de texto
  ```bash
  python scripts/test_whatsapp_send.py --to 5511999999999 --message "Teste"
  ```
  - Mensagem enviada com sucesso
  - Mensagem recebida no WhatsApp
  - Status code 200

- [ ] **5.3** Testar envio de template
  ```bash
  python scripts/test_whatsapp_send.py --to 5511999999999 --template hello_world
  ```
  - Template enviado com sucesso
  - Template recebido no WhatsApp

- [ ] **5.4** Testar envio de imagem
  ```bash
  python scripts/test_whatsapp_send.py --to 5511999999999 --image "URL" --caption "Teste"
  ```
  - Imagem enviada com sucesso
  - Imagem recebida no WhatsApp

- [ ] **5.5** Testar recebimento de webhook
  ```bash
  python scripts/test_whatsapp_webhook.py
  ```
  - Servidor iniciado
  - Mensagem enviada do WhatsApp
  - Webhook recebido
  - Payload processado corretamente

- [ ] **5.6** Testar rate limits
  ```bash
  python scripts/test_rate_limits.py --to 5511999999999 --count 10
  ```
  - Teste executado
  - Taxa dentro dos limites
  - Sem erros de rate limiting

---

### Fase 6: Segurança

- [ ] **6.1** Proteger credenciais
  - .env adicionado ao .gitignore
  - Credenciais não commitadas no git
  - Variáveis de ambiente configuradas no servidor

- [ ] **6.2** Configurar HTTPS
  - Certificado SSL válido
  - TLS 1.3 configurado
  - Redirecionamento HTTP → HTTPS

- [ ] **6.3** Implementar validação de signature
  - Código de validação implementado
  - Requisições sem signature rejeitadas
  - Testes de segurança passando

- [ ] **6.4** Configurar rate limiting
  - Rate limiting implementado
  - Limites configurados:
    - 80 mensagens/segundo
    - 1000 mensagens/minuto
  - Backoff exponencial implementado

- [ ] **6.5** Implementar retry logic
  - Retry com backoff exponencial
  - Máximo de 3 tentativas
  - Timeout de 30 segundos

---

### Fase 7: Monitoramento

- [ ] **7.1** Configurar logging
  - Logs estruturados implementados
  - Nível de log configurado (INFO)
  - Rotação de logs configurada

- [ ] **7.2** Configurar métricas
  - Prometheus configurado
  - Métricas de mensagens coletadas
  - Métricas de latência coletadas

- [ ] **7.3** Configurar alertas
  - Alertas de erro configurados
  - Alertas de rate limit configurados
  - Notificações configuradas (Slack/PagerDuty)

- [ ] **7.4** Configurar dashboards
  - Grafana configurado
  - Dashboard de mensagens criado
  - Dashboard de performance criado

---

### Fase 8: Documentação

- [ ] **8.1** Documentar processo de setup
  - Guia de configuração completo
  - Quick start guide criado
  - Troubleshooting documentado

- [ ] **8.2** Documentar APIs
  - Endpoints documentados
  - Payloads de exemplo incluídos
  - Códigos de erro documentados

- [ ] **8.3** Criar runbook
  - Procedimentos operacionais documentados
  - Procedimentos de incident response
  - Contatos de suporte listados

---

### Fase 9: Produção

- [ ] **9.1** Migrar para token permanente
  - Token temporário substituído
  - Token permanente testado
  - Token antigo revogado

- [ ] **9.2** Configurar número próprio
  - Número de teste substituído
  - Número próprio verificado
  - Perfil do negócio completo

- [ ] **9.3** Configurar domínio de produção
  - Domínio configurado
  - DNS configurado
  - SSL configurado

- [ ] **9.4** Atualizar webhook
  - URL de produção configurada
  - Webhook verificado
  - Eventos testados

- [ ] **9.5** Configurar backup
  - Backup de credenciais
  - Backup de configurações
  - Procedimento de recovery documentado

- [ ] **9.6** Realizar testes E2E
  - Fluxo completo testado
  - Todos os cenários validados
  - Performance validada

- [ ] **9.7** Configurar CI/CD
  - Pipeline configurado
  - Deploy automatizado
  - Rollback configurado

---

## 📊 Status Geral

**Total de itens:** 60

**Completados:** _____ / 60

**Progresso:** _____ %

---

## ✅ Critérios de Aceitação

Para considerar a configuração completa, você deve ter:

### Mínimo (Desenvolvimento)
- ✅ Token temporário funcionando
- ✅ Número de teste configurado
- ✅ Envio de mensagens funcionando
- ✅ Webhook recebendo mensagens
- ✅ Testes básicos passando

### Recomendado (Staging)
- ✅ Token permanente configurado
- ✅ Webhook com HTTPS
- ✅ Validação de signature
- ✅ Rate limiting implementado
- ✅ Logging configurado

### Obrigatório (Produção)
- ✅ Número próprio verificado
- ✅ Domínio de produção
- ✅ Segurança completa
- ✅ Monitoramento configurado
- ✅ Backup configurado
- ✅ Documentação completa
- ✅ Testes E2E passando

---

## 🎯 Próximos Passos

Após completar este checklist:

1. ✅ Implementar webhook handler (Task 8)
2. ✅ Integrar com NLP Service (Task 5)
3. ✅ Implementar Session Manager (Task 4)
4. ✅ Implementar Conversation Engine (Task 6)
5. ✅ Testar fluxo completo E2E (Task 14)

---

## 📞 Suporte

**Problemas com configuração?**
- Consulte: [WHATSAPP_SETUP_GUIDE.md](WHATSAPP_SETUP_GUIDE.md)
- Troubleshooting: [WHATSAPP_SETUP_GUIDE.md#troubleshooting](WHATSAPP_SETUP_GUIDE.md#troubleshooting)

**Problemas com a API?**
- Meta Business Help: https://www.facebook.com/business/help
- Developer Community: https://developers.facebook.com/community/

---

**Última atualização:** 2024-10-15
**Versão:** 1.0.0
