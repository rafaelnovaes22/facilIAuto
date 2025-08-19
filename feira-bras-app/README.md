# FeiraBrás - Sistema de Gestão para Vendedores da Feira da Madrugada

## 📋 Visão Geral

Sistema de gestão desenvolvido especificamente para empreendedores informais que vendem roupas na Feira da Madrugada do Brás, São Paulo. O aplicativo visa simplificar a gestão de vendas, estoque e finanças para pequenos comerciantes.

## 🎯 Objetivos do MVP

- **Simplificar a gestão diária** dos vendedores ambulantes
- **Digitalizar controles** atualmente feitos em papel
- **Fornecer insights** sobre vendas e lucratividade
- **Facilitar o relacionamento** com clientes
- **Reduzir perdas** por falta de controle de estoque

## 👥 Público-Alvo

### Persona Principal: Maria Silva
- **Idade:** 35 anos
- **Escolaridade:** Ensino médio completo
- **Experiência:** 8 anos vendendo roupas na feira
- **Desafios:**
  - Controla tudo em cadernos
  - Perde vendas por não saber o que tem em estoque
  - Dificuldade em calcular lucro real
  - Não consegue manter contato com clientes
- **Familiaridade com tecnologia:** Usa WhatsApp e redes sociais básicas

## 🏗️ Metodologia de Desenvolvimento: Extreme Programming (XP)

### Valores XP Aplicados
1. **Comunicação** - Feedback constante com vendedores reais
2. **Simplicidade** - Interface minimalista e intuitiva
3. **Feedback** - Ciclos curtos de 1 semana
4. **Coragem** - Refatoração contínua
5. **Respeito** - Pair programming e code reviews

### Práticas XP Implementadas
- ✅ **Planning Game** - Sprints semanais
- ✅ **Small Releases** - Deploy contínuo
- ✅ **Customer Tests** - Validação com usuários reais
- ✅ **Simple Design** - YAGNI (You Aren't Gonna Need It)
- ✅ **Test-Driven Development** - Testes primeiro, código depois
- ✅ **Pair Programming** - Todo código crítico em dupla
- ✅ **Collective Code Ownership** - Todos responsáveis pelo código
- ✅ **Continuous Integration** - GitHub Actions
- ✅ **40-hour Week** - Desenvolvimento sustentável
- ✅ **On-site Customer** - Vendedor parceiro no time
- ✅ **Coding Standards** - ESLint + Prettier
- ✅ **Refactoring** - Melhoria contínua

## 🧪 Estratégia de Testes

### Pirâmide de Testes
```
         /\
        /E2E\       (10%) - Cypress/Detox
       /------\
      /Integr. \    (30%) - Jest + Supertest
     /----------\
    /   Unit     \  (60%) - Jest + React Testing Library
   /--------------\
```

### Testes E2E (End-to-End)
- **Web Admin:** Cypress
- **Mobile App:** Detox
- **Cenários críticos:** Fluxo completo de venda, cadastro de produtos, fechamento de caixa

## 🚀 Funcionalidades do MVP (Fase 1)

### 1. Gestão de Produtos
- Cadastro rápido com foto
- Controle de estoque simples
- Categorização básica (P/M/G/GG)
- Código de barras opcional

### 2. Registro de Vendas
- Venda rápida sem cadastro
- Múltiplas formas de pagamento (Dinheiro, PIX, Cartão)
- Desconto simples
- Comprovante via WhatsApp

### 3. Controle Financeiro
- Resumo diário de vendas
- Despesas básicas
- Lucro do dia/semana/mês
- Gráficos simples

### 4. Gestão de Clientes
- Cadastro opcional
- Histórico de compras
- WhatsApp integrado
- Fiado controlado

## 💻 Stack Tecnológica

### Frontend Mobile
- **React Native** com Expo
- **TypeScript** para type safety
- **React Navigation** para navegação
- **React Hook Form** para formulários
- **Zustand** para estado global
- **React Query** para cache e sync

### Backend
- **Node.js** com Express
- **TypeScript**
- **PostgreSQL** com Prisma ORM
- **Redis** para cache
- **JWT** para autenticação
- **Multer** para upload de imagens

### Infraestrutura
- **Docker** para containerização
- **GitHub Actions** para CI/CD
- **AWS/Heroku** para deploy
- **Cloudinary** para imagens
- **Sentry** para monitoramento

### Testes
- **Jest** para unit tests
- **Supertest** para integration tests
- **Detox** para E2E mobile
- **Cypress** para E2E web admin
- **React Testing Library**

## 📱 Características Específicas do App

### Offline First
- Funciona sem internet
- Sincronização quando disponível
- Cache local com AsyncStorage

### Performance
- Lazy loading de imagens
- Virtualização de listas
- Otimização de re-renders

### Acessibilidade
- Fontes grandes
- Alto contraste
- Navegação simples
- Suporte a leitores de tela

## 📊 Métricas de Sucesso

### KPIs Técnicos
- Cobertura de testes > 80%
- Tempo de resposta < 2s
- Crash rate < 1%
- App size < 30MB

### KPIs de Negócio
- 100 usuários ativos em 3 meses
- NPS > 8
- Retenção D7 > 40%
- 5 vendas/dia por usuário

## 🗓️ Cronograma de Desenvolvimento

### Sprint 0 (Semana 1) - Setup
- Configuração do ambiente
- Setup de CI/CD
- Arquitetura base

### Sprint 1-2 (Semanas 2-3) - Produtos
- CRUD de produtos
- Upload de fotos
- Testes E2E

### Sprint 3-4 (Semanas 4-5) - Vendas
- Fluxo de venda
- Formas de pagamento
- Comprovantes

### Sprint 5-6 (Semanas 6-7) - Finanças
- Dashboard
- Relatórios
- Gráficos

### Sprint 7-8 (Semanas 8-9) - Clientes
- Gestão de clientes
- Integração WhatsApp
- Fiado

### Sprint 9-10 (Semanas 10-11) - Polish
- Melhorias de UX
- Performance
- Bug fixes

### Sprint 11-12 (Semanas 12-13) - Launch
- Beta testing
- Deploy
- Monitoramento

## 🔒 Segurança e Compliance

- LGPD compliance
- Criptografia de dados sensíveis
- Backup automático
- Autenticação 2FA opcional
- Logs de auditoria

## 🚀 Quick Start

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/feira-bras-app.git

# Entre no diretório
cd feira-bras-app

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env

# Rode os testes
npm test

# Inicie o desenvolvimento
npm run dev
```

## 📚 Documentação Adicional

- [User Stories](./docs/user-stories/)
- [Arquitetura Técnica](./docs/technical/)
- [Plano de Testes](./docs/planning/test-plan.md)
- [Manual do Usuário](./docs/user-manual.md)

## 🤝 Time de Desenvolvimento

- **Product Owner:** Vendedor parceiro da feira
- **Scrum Master:** Rotativo entre devs
- **Desenvolvedores:** 2 full-stack (pair programming)
- **UX Designer:** Part-time
- **QA:** Todos (whole team testing)

## 📞 Contato e Suporte

- WhatsApp Business: (11) 9XXXX-XXXX
- Email: suporte@feirabras.app
- Instagram: @feirabrasapp

---

*Desenvolvido com ❤️ para os empreendedores da Feira da Madrugada*