# Roadmap: Gestão de Estoque Self-Service

**Objetivo**: Permitir que concessionárias gerenciem seu próprio estoque de veículos no FacilIAuto

**Status**: Planejamento  
**Prioridade**: Fase 2 (Pós-MVP)  
**Estimativa**: 3-4 semanas

---

## 📊 Contexto

### Situação Atual (MVP)
- Scraping manual/semi-automático para popular banco
- Dados extraídos de sites das concessionárias
- Atualização manual quando necessário
- **Problema**: Não escala, dados podem ficar desatualizados

### Situação Desejada (Produção)
- Concessionárias gerenciam próprio estoque
- Atualização em tempo real
- Integração com sistemas existentes (opcional)
- **Benefício**: Escala, dados sempre atualizados, menos trabalho manual

---

## 🎯 Objetivos

### Objetivos de Negócio
1. **Reduzir custo operacional**: Eliminar scraping manual
2. **Melhorar qualidade dos dados**: Concessionária conhece melhor seu estoque
3. **Aumentar satisfação do cliente**: Dados sempre atualizados
4. **Facilitar onboarding**: Concessionária controla quando ativar

### Objetivos Técnicos
1. **Portal de administração**: Interface web para gestão de estoque
2. **API REST**: Integração com sistemas existentes
3. **Importação em lote**: Upload de planilhas/CSV
4. **Sincronização automática**: Integração com sistemas de gestão

---

## 🏗️ Arquitetura Proposta

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    FacilIAuto Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Portal de Administração (React)              │  │
│  │  - Login/Autenticação                                │  │
│  │  - Dashboard de estoque                              │  │
│  │  - CRUD de veículos                                  │  │
│  │  - Upload em lote (CSV/Excel)                        │  │
│  │  - Relatórios e métricas                             │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │         API Backend (FastAPI)                        │  │
│  │  - Autenticação JWT                                  │  │
│  │  - CRUD endpoints                                    │  │
│  │  - Validação de dados                                │  │
│  │  - Upload/Import service                             │  │
│  │  - Webhook para integrações                          │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │         Database (PostgreSQL)                        │  │
│  │  - Tabela: dealerships                               │  │
│  │  - Tabela: vehicles                                  │  │
│  │  - Tabela: users (admin concessionária)             │  │
│  │  - Tabela: audit_log                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Integrações Externas:
┌──────────────────────┐
│ Sistema de Gestão    │ ──► Webhook/API ──► FacilIAuto
│ (DMS da concessionária)│
└──────────────────────┘

┌──────────────────────┐
│ Planilha Excel/CSV   │ ──► Upload ──► FacilIAuto
└──────────────────────┘
```

---

## 📋 Features Detalhadas

### 1. Portal de Administração

#### 1.1 Autenticação e Autorização
```
User Stories:
- Como gerente da concessionária, quero fazer login no portal
- Como gerente, quero que apenas usuários autorizados acessem meu estoque
- Como admin FacilIAuto, quero gerenciar acessos das concessionárias

Features:
✓ Login com email/senha
✓ Autenticação JWT
✓ Roles: admin_faciliauto, admin_dealership, operator_dealership
✓ Multi-tenant: cada concessionária vê apenas seu estoque
✓ 2FA opcional (SMS/Email)
```

#### 1.2 Dashboard de Estoque
```
User Stories:
- Como gerente, quero ver visão geral do meu estoque
- Como gerente, quero ver quais carros estão gerando mais interesse
- Como gerente, quero ver carros que precisam atualização

Features:
✓ Total de veículos ativos/inativos
✓ Carros mais visualizados
✓ Carros sem foto/descrição
✓ Alertas de dados incompletos
✓ Gráficos de estoque por categoria/marca
```

#### 1.3 CRUD de Veículos
```
User Stories:
- Como operador, quero adicionar novo veículo
- Como operador, quero editar informações de veículo
- Como operador, quero marcar veículo como vendido
- Como operador, quero duplicar veículo similar

Features:
✓ Formulário de cadastro com validação
✓ Upload de múltiplas fotos (drag & drop)
✓ Auto-complete de marca/modelo
✓ Sugestão de categoria baseada em modelo
✓ Preview antes de salvar
✓ Histórico de alterações
✓ Ações em lote (ativar/desativar múltiplos)
```

#### 1.4 Importação em Lote
```
User Stories:
- Como gerente, quero importar estoque de planilha Excel
- Como gerente, quero ver erros de validação antes de importar
- Como gerente, quero atualizar preços em lote

Features:
✓ Upload de CSV/Excel
✓ Template de planilha para download
✓ Preview de dados antes de importar
✓ Validação com relatório de erros
✓ Opções: criar novos, atualizar existentes, ou ambos
✓ Importação assíncrona com progresso
```

### 2. API REST

#### 2.1 Endpoints de Veículos
```http
# Listar veículos da concessionária
GET /api/v1/dealerships/{dealership_id}/vehicles
Query params: page, limit, status, categoria, marca

# Obter veículo específico
GET /api/v1/dealerships/{dealership_id}/vehicles/{vehicle_id}

# Criar novo veículo
POST /api/v1/dealerships/{dealership_id}/vehicles
Body: VehicleCreate (Pydantic model)

# Atualizar veículo
PUT /api/v1/dealerships/{dealership_id}/vehicles/{vehicle_id}
Body: VehicleUpdate (Pydantic model)

# Deletar veículo (soft delete)
DELETE /api/v1/dealerships/{dealership_id}/vehicles/{vehicle_id}

# Upload de imagens
POST /api/v1/dealerships/{dealership_id}/vehicles/{vehicle_id}/images
Body: multipart/form-data

# Importação em lote
POST /api/v1/dealerships/{dealership_id}/vehicles/import
Body: CSV/Excel file
```

#### 2.2 Autenticação
```http
# Login
POST /api/v1/auth/login
Body: { email, password }
Response: { access_token, refresh_token, user }

# Refresh token
POST /api/v1/auth/refresh
Body: { refresh_token }
Response: { access_token }

# Logout
POST /api/v1/auth/logout
Headers: Authorization: Bearer {token}
```

#### 2.3 Webhooks (Integração)
```http
# Registrar webhook
POST /api/v1/dealerships/{dealership_id}/webhooks
Body: { url, events: ["vehicle.created", "vehicle.updated"] }

# Eventos enviados:
POST {webhook_url}
Body: {
  event: "vehicle.created",
  dealership_id: "robustcar",
  vehicle: { ... },
  timestamp: "2025-10-30T14:30:00Z"
}
```

### 3. Modelos de Dados

#### 3.1 User Model
```python
class User(BaseModel):
    id: str
    email: str
    name: str
    dealership_id: str
    role: str  # admin_faciliauto, admin_dealership, operator_dealership
    active: bool
    created_at: datetime
    last_login: Optional[datetime]
```

#### 3.2 Vehicle Model (Estendido)
```python
class Vehicle(BaseModel):
    # Campos existentes...
    
    # Novos campos para gestão:
    created_by: str  # user_id
    updated_by: str  # user_id
    created_at: datetime
    updated_at: datetime
    status: str  # active, sold, reserved, inactive
    internal_code: Optional[str]  # Código interno da concessionária
    notes: Optional[str]  # Notas internas
```

#### 3.3 AuditLog Model
```python
class AuditLog(BaseModel):
    id: str
    dealership_id: str
    user_id: str
    action: str  # created, updated, deleted, imported
    entity_type: str  # vehicle, user
    entity_id: str
    changes: Dict  # Campos alterados
    timestamp: datetime
```

---

## 🔄 Fluxos de Uso

### Fluxo 1: Cadastro Manual de Veículo
```
1. Operador faz login no portal
2. Clica em "Adicionar Veículo"
3. Preenche formulário:
   - Dados básicos (nome, marca, modelo, ano)
   - Preço e quilometragem
   - Características (câmbio, combustível, cor)
   - Upload de fotos (drag & drop)
   - Descrição
4. Sistema valida dados em tempo real
5. Preview do veículo
6. Confirma e salva
7. Veículo aparece no estoque e nas recomendações
```

### Fluxo 2: Importação em Lote
```
1. Gerente faz login no portal
2. Clica em "Importar Estoque"
3. Baixa template de planilha
4. Preenche planilha com dados dos veículos
5. Upload da planilha
6. Sistema valida e mostra preview:
   - 45 veículos válidos
   - 3 com erros (lista erros)
7. Gerente corrige erros ou ignora
8. Confirma importação
9. Sistema processa em background
10. Notificação quando concluído
```

### Fluxo 3: Integração Automática (Avançado)
```
1. Concessionária tem sistema de gestão (DMS)
2. Admin FacilIAuto configura webhook
3. Quando veículo é adicionado no DMS:
   - DMS envia POST para webhook FacilIAuto
   - FacilIAuto valida e cria veículo
   - Retorna confirmação
4. Sincronização automática e em tempo real
```

---

## 🛠️ Stack Tecnológica

### Backend
```
FastAPI (já em uso)
PostgreSQL (migrar de JSON)
SQLAlchemy (ORM)
Alembic (migrations)
JWT (autenticação)
Celery (tarefas assíncronas)
Redis (cache e queue)
```

### Frontend (Portal Admin)
```
React 18 (já em uso)
TypeScript
Chakra UI (já em uso)
React Query (já em uso)
React Hook Form (formulários)
React Dropzone (upload de fotos)
```

### Infraestrutura
```
Docker (containerização)
Nginx (reverse proxy)
AWS S3 (armazenamento de imagens)
AWS RDS (PostgreSQL)
AWS Lambda (processamento de imagens)
```

---

## 📅 Roadmap de Implementação

### Sprint 1: Fundação (1 semana)
- [ ] Migrar de JSON para PostgreSQL
- [ ] Criar modelos de User e AuditLog
- [ ] Implementar autenticação JWT
- [ ] Criar endpoints básicos de CRUD

### Sprint 2: Portal Admin - Básico (1 semana)
- [ ] Tela de login
- [ ] Dashboard de estoque
- [ ] Listagem de veículos
- [ ] Formulário de cadastro de veículo

### Sprint 3: Portal Admin - Avançado (1 semana)
- [ ] Upload de múltiplas fotos
- [ ] Edição de veículos
- [ ] Ações em lote
- [ ] Histórico de alterações

### Sprint 4: Importação e Integrações (1 semana)
- [ ] Upload de CSV/Excel
- [ ] Validação e preview
- [ ] Processamento assíncrono
- [ ] Webhooks para integrações

---

## 🎯 Critérios de Sucesso

### Métricas de Produto
- **Tempo de cadastro**: < 3 minutos por veículo
- **Taxa de erro**: < 5% em importações
- **Adoção**: 80%+ das concessionárias usando self-service
- **Satisfação**: NPS > 8

### Métricas Técnicas
- **Disponibilidade**: 99.5%+
- **Tempo de resposta**: < 200ms (p95)
- **Upload de fotos**: < 5s por foto
- **Importação**: 100 veículos em < 30s

---

## 💰 Estimativa de Esforço

### Desenvolvimento
- Backend: 80 horas (2 semanas)
- Frontend: 80 horas (2 semanas)
- Testes: 40 horas (1 semana)
- **Total**: 200 horas (5 semanas com 1 dev)

### Infraestrutura
- Setup PostgreSQL: 8 horas
- Setup S3 e CDN: 8 horas
- CI/CD: 16 horas
- **Total**: 32 horas

### Documentação e Treinamento
- Documentação técnica: 16 horas
- Guia do usuário: 16 horas
- Vídeos de treinamento: 16 horas
- **Total**: 48 horas

**Estimativa Total**: 280 horas (7 semanas com 1 dev, ou 3.5 semanas com 2 devs)

---

## 🚨 Riscos e Mitigações

### Risco 1: Resistência das Concessionárias
**Probabilidade**: Média  
**Impacto**: Alto  
**Mitigação**: 
- Onboarding assistido
- Suporte dedicado nas primeiras semanas
- Incentivos (desconto, features premium)

### Risco 2: Qualidade dos Dados
**Probabilidade**: Alta  
**Impacto**: Médio  
**Mitigação**:
- Validação rigorosa
- Sugestões automáticas (categoria, etc.)
- Revisão manual FacilIAuto antes de publicar

### Risco 3: Integração com Sistemas Legados
**Probabilidade**: Média  
**Impacto**: Médio  
**Mitigação**:
- API REST bem documentada
- Webhooks flexíveis
- Suporte para múltiplos formatos (CSV, Excel, JSON)

---

## 📚 Referências

### Inspirações
- **OLX Autos**: Portal de gestão de anúncios
- **Webmotors Pro**: Dashboard para concessionárias
- **Shopify**: Self-service para lojistas

### Documentação Técnica
- FastAPI: https://fastapi.tiangolo.com/
- PostgreSQL: https://www.postgresql.org/docs/
- JWT: https://jwt.io/

---

**Próximos Passos**:
1. Validar roadmap com stakeholders
2. Priorizar features (MVP vs Nice-to-have)
3. Definir equipe e timeline
4. Iniciar Sprint 1

**Última Atualização**: 30/10/2025  
**Responsável**: Equipe de Produto
