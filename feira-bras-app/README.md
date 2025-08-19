# FeiraBrás - Sistema de Gestão para Vendedores da Feira da Madrugada

## 📋 Visão Geral

Sistema de gestão desenvolvido especificamente para empreendedores informais que vendem roupas na Feira da Madrugada do Brás, São Paulo. O aplicativo visa simplificar a gestão de vendas, estoque, fornecedores e finanças para pequenos comerciantes.

## 🎯 Objetivos do MVP

- **Simplificar a gestão diária** dos vendedores ambulantes
- **Digitalizar controles** atualmente feitos em papel
- **Fornecer insights** sobre vendas e lucratividade
- **Facilitar o relacionamento** com clientes e fornecedores
- **Reduzir perdas** por falta de controle
- **Otimizar compras** com fornecedores

## 🚀 Funcionalidades Principais

### 📦 Gestão de Produtos
- Cadastro rápido com foto
- Controle de estoque em tempo real
- Categorização por tamanho (P/M/G/GG)
- Busca rápida e filtros

### 💰 Registro de Vendas
- Venda em 3 cliques
- PIX, Dinheiro e Cartão
- Descontos flexíveis
- Comprovante via WhatsApp

### 📊 Controle Financeiro
- Abertura/fechamento de caixa
- Resumo diário de vendas
- Cálculo automático de lucro
- Gráficos e relatórios

### 👥 Gestão de Clientes
- Cadastro simplificado
- Histórico de compras
- Controle de fiado
- Comunicação via WhatsApp

### 🏭 Gestão de Fornecedores (NOVO!)
- **Cadastro de fornecedores** com contato WhatsApp
- **Controle de pedidos** com prazos de pagamento
- **Alertas automáticos** de vencimento
- **Análise de margem** por produto/fornecedor
- **Sugestão inteligente** de reposição baseada em vendas
- **Comparação de preços** entre fornecedores
- **Histórico de compras** e avaliação de qualidade

## 🏗️ Metodologia: Extreme Programming (XP)

### Práticas XP Implementadas
- ✅ **TDD** - Test-Driven Development
- ✅ **Pair Programming** - Todo código crítico em dupla
- ✅ **Continuous Integration** - GitHub Actions
- ✅ **Small Releases** - Deploy semanal
- ✅ **Simple Design** - YAGNI (You Aren't Gonna Need It)
- ✅ **Refactoring** - Melhoria contínua
- ✅ **On-site Customer** - Vendedor parceiro no time

## 🧪 Estratégia de Testes E2E

### Ferramentas
- **Mobile:** Detox para React Native
- **Backend:** Cypress para APIs
- **Cobertura:** > 80% do código

### Cenários Críticos Testados
- Fluxo completo de venda
- Fechamento de caixa
- Gestão de produtos
- Pedidos com fornecedores
- Funcionamento offline

## 💻 Stack Tecnológica

### Frontend Mobile
- React Native + Expo
- TypeScript
- Zustand (estado)
- React Query (cache)

### Backend
- Node.js + Express
- PostgreSQL + Prisma
- Redis (cache)
- JWT (auth)

### Infraestrutura
- Docker
- GitHub Actions
- AWS/Heroku
- Cloudinary (imagens)

## 🚀 Quick Start

```bash
# Clone o repositório
git clone <seu-repositorio>

# Entre no diretório
cd feira-bras-app

# Instale as dependências
npm install

# Configure o ambiente
cp .env.example .env

# Rode com Docker
docker-compose up -d

# Rode os testes
npm test

# Inicie o desenvolvimento
npm run dev
```

## 📱 Características Especiais

### Offline First
- Funciona 100% sem internet
- Sincronização automática quando conectado
- Dados seguros no dispositivo

### Performance
- Abertura < 2 segundos
- Operações < 1 segundo
- App size < 30MB

### Acessibilidade
- Fontes grandes
- Alto contraste
- Interface simples
- Suporte a leitores de tela

## 📊 Métricas de Sucesso

### KPIs Técnicos
- Cobertura de testes > 80%
- Uptime > 99.5%
- Crash rate < 1%

### KPIs de Negócio
- 100 usuários em 3 meses
- NPS > 8
- 5+ vendas/dia por usuário
- Redução de 50% em atrasos com fornecedores

## 📚 Documentação Completa

- [📋 Plano Detalhado](./docs/PLANO_DETALHADO.md) - Análise completa do mercado e estratégia
- [📝 User Stories](./docs/user-stories/) - Histórias de usuário e critérios
- [🏗️ Arquitetura](./docs/technical/) - Decisões técnicas e diagramas
- [🧪 Estratégia E2E](./docs/E2E_STRATEGY.md) - Plano completo de testes
- [👥 Gestão de Fornecedores](./docs/user-stories/US002-gestao-fornecedores.md) - Detalhes do módulo

## 🗓️ Roadmap

### ✅ Fase 1 - MVP (3 meses)
- [x] Setup e arquitetura
- [x] Gestão de produtos
- [x] Fluxo de vendas
- [x] Controle financeiro
- [x] Gestão de fornecedores
- [ ] Beta testing

### 📅 Fase 2 - Expansão (6 meses)
- [ ] E-commerce integrado
- [ ] Emissão de NF-e
- [ ] Múltiplas lojas
- [ ] Dashboard web

### 🚀 Fase 3 - Escala (12 meses)
- [ ] Marketplace entre vendedores
- [ ] Integração bancária
- [ ] IA para previsão de vendas
- [ ] Expansão para outras feiras

## 🤝 Time de Desenvolvimento

- **Product Owner:** Vendedor parceiro da feira
- **Scrum Master:** Rotativo entre devs
- **Desenvolvedores:** 2 full-stack (pair programming)
- **UX Designer:** Part-time
- **QA:** Todos (whole team testing)

## 📞 Contato e Suporte

- WhatsApp: (11) 9XXXX-XXXX
- Email: suporte@feirabras.app
- Instagram: @feirabrasapp

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

*Desenvolvido com ❤️ para os empreendedores da Feira da Madrugada*
*Última atualização: Dezembro 2024*