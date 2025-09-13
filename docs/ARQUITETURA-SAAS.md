# 🏗️ **Arquitetura SaaS - CarMatch Platform**

## 🎯 **Visão Geral da Arquitetura**

Sistema multi-tenant que permite múltiplas concessionárias utilizarem nossa plataforma de recomendação de carros com isolamento completo de dados e customização por cliente.

---

## 📋 **Estrutura Multi-Tenant**

### **🏢 Modelo de Tenancy**
```yaml
Estratégia: Schema-per-Tenant + Shared Application

Tenant Isolation:
  ├── Database: Schema separado por concessionária
  ├── Storage: Bucket S3 por tenant  
  ├── Cache: Redis namespace por tenant
  ├── Domain: Subdomain por concessionária
  └── Config: Configuração isolada por tenant

Shared Resources:
  ├── Application Layer (APIs)
  ├── AI/ML Models
  ├── Monitoring & Logging
  └── Authentication Service
```

### **🗃️ Database Design**
```sql
-- Schema central para gestão
CREATE SCHEMA carmatch_admin;

-- Tabelas de gestão de tenants
carmatch_admin.tenants (
    id UUID PRIMARY KEY,
    slug VARCHAR(50) UNIQUE,        -- robustcar, autocenter
    name VARCHAR(100),              -- "RobustCar São Paulo"
    domain VARCHAR(100),            -- robustcar.carmatch.com.br
    plan VARCHAR(20),               -- basic, professional, enterprise
    status VARCHAR(20),             -- active, suspended, trial
    created_at TIMESTAMP,
    config JSONB                    -- configurações específicas
);

carmatch_admin.subscriptions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    plan VARCHAR(20),
    price_monthly DECIMAL(10,2),
    status VARCHAR(20),
    current_period_start DATE,
    current_period_end DATE
);

-- Schema por concessionária (exemplo)
CREATE SCHEMA robustcar;
CREATE SCHEMA autocenter;

-- Estrutura replicada para cada tenant
robustcar.cars (
    id UUID PRIMARY KEY,
    nome VARCHAR(200),
    marca VARCHAR(50),
    modelo VARCHAR(100),
    ano INTEGER,
    preco DECIMAL(10,2),
    data_scraping TIMESTAMP,
    disponivel BOOLEAN DEFAULT true
);

robustcar.user_sessions (
    id UUID PRIMARY KEY,
    session_data JSONB,
    recommendations JSONB,
    created_at TIMESTAMP
);

robustcar.analytics (
    id UUID PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB,
    created_at TIMESTAMP
);
```

---

## 🔧 **Backend Architecture**

### **🚀 FastAPI Multi-Tenant**
```python
# core/tenant.py
from contextvars import ContextVar
from typing import Optional

current_tenant: ContextVar[Optional[str]] = ContextVar('current_tenant', default=None)

class TenantMiddleware:
    """Middleware para identificar tenant por subdomain"""
    
    async def __call__(self, request: Request, call_next):
        host = request.headers.get('host', '')
        
        # Extrair subdomain: robustcar.carmatch.com.br → robustcar
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain != 'www':
                current_tenant.set(subdomain)
        
        response = await call_next(request)
        return response

# services/tenant_service.py
class TenantService:
    """Serviço para gestão de tenants"""
    
    @staticmethod
    async def get_tenant_config(tenant_slug: str) -> TenantConfig:
        """Buscar configuração do tenant"""
        async with get_db() as db:
            result = await db.execute(
                "SELECT * FROM carmatch_admin.tenants WHERE slug = $1",
                tenant_slug
            )
            return TenantConfig(**result.fetchone())
    
    @staticmethod
    async def get_tenant_db_schema(tenant_slug: str) -> str:
        """Obter schema do banco para o tenant"""
        return f"tenant_{tenant_slug}"

# database/connection.py
class TenantDatabase:
    """Manager de conexão com isolamento por tenant"""
    
    def __init__(self):
        self.pools = {}  # Pool por tenant
    
    async def get_connection(self, tenant_slug: str):
        if tenant_slug not in self.pools:
            # Criar pool para novo tenant
            self.pools[tenant_slug] = await create_pool(
                schema=f"tenant_{tenant_slug}"
            )
        return self.pools[tenant_slug]

# api/dependencies.py
async def get_current_tenant() -> TenantConfig:
    """Dependency para obter tenant atual"""
    tenant_slug = current_tenant.get()
    if not tenant_slug:
        raise HTTPException(404, "Tenant não identificado")
    
    return await TenantService.get_tenant_config(tenant_slug)

async def get_tenant_db(tenant: TenantConfig = Depends(get_current_tenant)):
    """Dependency para obter DB do tenant"""
    return await TenantDatabase().get_connection(tenant.slug)
```

### **🤖 AI Engine Multi-Tenant**
```python
# ai/multi_tenant_engine.py
class MultiTenantRecommendationEngine:
    """Engine de IA com cache por tenant"""
    
    def __init__(self):
        self.engines = {}  # Cache de engines por tenant
        self.redis_client = Redis()
    
    async def get_engine(self, tenant_slug: str) -> RecommendationEngine:
        """Obter engine específico do tenant"""
        
        # Cache em memória
        if tenant_slug in self.engines:
            return self.engines[tenant_slug]
        
        # Cache Redis
        cache_key = f"engine:{tenant_slug}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            # Reconstruir engine do cache
            engine_data = json.loads(cached_data)
            engine = RecommendationEngine.from_dict(engine_data)
        else:
            # Carregar dados do banco
            async with get_tenant_db(tenant_slug) as db:
                cars = await db.fetch("SELECT * FROM cars WHERE disponivel = true")
                engine = RecommendationEngine(cars)
                
                # Salvar no cache
                await self.redis_client.setex(
                    cache_key, 3600, engine.to_json()
                )
        
        self.engines[tenant_slug] = engine
        return engine
    
    async def recommend(self, tenant_slug: str, profile: UserProfile):
        """Gerar recomendações para tenant específico"""
        engine = await self.get_engine(tenant_slug)
        return engine.recommend(profile)
```

---

## 🎨 **Frontend Multi-Tenant**

### **⚛️ React Architecture**
```typescript
// hooks/useTenant.ts
export const useTenant = () => {
  const [config, setConfig] = useState<TenantConfig | null>(null)
  
  useEffect(() => {
    const loadTenantConfig = async () => {
      const hostname = window.location.hostname
      const subdomain = hostname.split('.')[0]
      
      try {
        const response = await api.get(`/tenant/${subdomain}/config`)
        setConfig(response.data)
        
        // Aplicar tema dinamicamente
        applyTenantTheme(response.data.branding)
      } catch (error) {
        console.error('Tenant não encontrado:', error)
      }
    }
    
    loadTenantConfig()
  }, [])
  
  return { config, isLoading: !config }
}

// components/TenantProvider.tsx
export const TenantProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { config, isLoading } = useTenant()
  
  if (isLoading) {
    return <LoadingSpinner />
  }
  
  if (!config) {
    return <TenantNotFound />
  }
  
  // Aplicar tema do tenant
  const theme = createTenantTheme(config.branding)
  
  return (
    <TenantContext.Provider value={config}>
      <ChakraProvider theme={theme}>
        {children}
      </ChakraProvider>
    </TenantContext.Provider>
  )
}

// utils/theming.ts
export const createTenantTheme = (branding: BrandingConfig) => {
  return extendTheme({
    colors: {
      brand: {
        50: branding.colors.light,
        500: branding.colors.primary,
        600: branding.colors.dark,
      }
    },
    fonts: {
      heading: branding.fonts.heading,
      body: branding.fonts.body,
    },
    components: {
      Button: {
        defaultProps: {
          colorScheme: 'brand',
        }
      }
    }
  })
}

// components/TenantHeader.tsx
export const TenantHeader = () => {
  const tenant = useTenantContext()
  
  return (
    <Header>
      <Logo src={tenant.branding.logo} alt={tenant.name} />
      <ContactInfo 
        phone={tenant.contact.phone}
        whatsapp={tenant.contact.whatsapp}
      />
    </Header>
  )
}
```

### **🎨 Customização por Tenant**
```typescript
// types/tenant.ts
interface TenantConfig {
  slug: string
  name: string
  domain: string
  branding: {
    logo: string
    colors: {
      primary: string
      secondary: string
      accent: string
    }
    fonts: {
      heading: string
      body: string
    }
  }
  contact: {
    phone: string
    whatsapp: string
    email: string
    address: string
  }
  features: {
    advanced_analytics: boolean
    custom_questionnaire: boolean
    crm_integration: boolean
    white_label: boolean
  }
  limits: {
    cars_max: number
    recommendations_monthly: number
    storage_gb: number
  }
}

// Exemplo de configurações
const TENANT_CONFIGS = {
  robustcar: {
    slug: 'robustcar',
    name: 'RobustCar São Paulo',
    branding: {
      logo: '/logos/robustcar.png',
      colors: {
        primary: '#0ea5e9',
        secondary: '#64748b',
        accent: '#f59e0b'
      }
    },
    features: {
      advanced_analytics: true,
      white_label: false
    },
    limits: {
      cars_max: 200,
      recommendations_monthly: 2000
    }
  },
  autocenter: {
    slug: 'autocenter',
    name: 'AutoCenter Rio de Janeiro',
    branding: {
      logo: '/logos/autocenter.png',
      colors: {
        primary: '#dc2626',
        secondary: '#374151',
        accent: '#059669'
      }
    },
    features: {
      advanced_analytics: false,
      white_label: false
    },
    limits: {
      cars_max: 50,
      recommendations_monthly: 500
    }
  }
}
```

---

## 🛠️ **DevOps & Infrastructure**

### **☁️ Cloud Architecture**
```yaml
AWS Infrastructure:

Load Balancer (ALB):
  - Domain routing: *.carmatch.com.br
  - SSL termination
  - Health checks

ECS Fargate:
  - Multi-container: API + Worker
  - Auto-scaling por tenant
  - Blue/green deployments

RDS PostgreSQL:
  - Multi-schema strategy
  - Read replicas por região
  - Automated backups

ElastiCache Redis:
  - Session storage
  - Engine cache
  - Real-time analytics

S3 Buckets:
  - Static assets por tenant
  - Car images
  - Backup storage

CloudFront CDN:
  - Asset delivery
  - Geographic distribution
  - Tenant-specific caching
```

### **🐳 Docker Multi-Stage**
```dockerfile
# Dockerfile.api
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS development
COPY . .
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0"]

FROM base AS production  
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# docker-compose.yml
version: '3.8'
services:
  api:
    build: 
      context: .
      target: development
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/carmatch
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: carmatch
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## 📊 **Monitoring & Analytics**

### **📈 Métricas por Tenant**
```python
# monitoring/metrics.py
class TenantMetrics:
    """Coletores de métricas isoladas por tenant"""
    
    def __init__(self, tenant_slug: str):
        self.tenant = tenant_slug
        self.redis = Redis()
    
    async def track_recommendation(self, session_id: str, recommendations: List[Dict]):
        """Tracking de recomendações geradas"""
        metric = {
            'tenant': self.tenant,
            'event': 'recommendation_generated',
            'session_id': session_id,
            'count': len(recommendations),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Analytics em tempo real
        await self.redis.lpush(f"analytics:{self.tenant}", json.dumps(metric))
        
        # Aggregate metrics
        await self.redis.incr(f"metrics:{self.tenant}:recommendations:daily:{date.today()}")
    
    async def track_conversion(self, session_id: str, car_id: str):
        """Tracking de conversões (cliques/interesse)"""
        metric = {
            'tenant': self.tenant,
            'event': 'conversion',
            'session_id': session_id,
            'car_id': car_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.redis.lpush(f"conversions:{self.tenant}", json.dumps(metric))
        await self.redis.incr(f"metrics:{self.tenant}:conversions:daily:{date.today()}")

# Endpoint de analytics por tenant
@app.get("/analytics/dashboard")
async def get_tenant_analytics(
    tenant: TenantConfig = Depends(get_current_tenant),
    period: str = "7d"
):
    """Dashboard de analytics para o tenant"""
    metrics = TenantMetrics(tenant.slug)
    
    return {
        'recommendations': await metrics.get_recommendations_stats(period),
        'conversions': await metrics.get_conversion_stats(period),
        'top_cars': await metrics.get_top_recommended_cars(period),
        'user_behavior': await metrics.get_user_behavior_stats(period)
    }
```

---

## 🔐 **Security & Compliance**

### **🛡️ Security Layers**
```python
# security/tenant_isolation.py
class TenantSecurityMiddleware:
    """Garantir isolamento completo entre tenants"""
    
    async def __call__(self, request: Request, call_next):
        tenant_slug = current_tenant.get()
        
        # Validar acesso ao tenant
        if not await self.validate_tenant_access(request, tenant_slug):
            raise HTTPException(403, "Access denied")
        
        # Injetar context de segurança
        security_context.set({
            'tenant': tenant_slug,
            'allowed_schemas': [f"tenant_{tenant_slug}"],
            'rate_limits': await self.get_tenant_limits(tenant_slug)
        })
        
        response = await call_next(request)
        return response
    
    async def validate_tenant_access(self, request: Request, tenant: str) -> bool:
        """Validar se request tem acesso ao tenant"""
        # Verificar domain matching
        expected_domain = f"{tenant}.carmatch.com.br"
        actual_host = request.headers.get('host', '')
        
        return expected_domain == actual_host

# Rate limiting por tenant
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    tenant = current_tenant.get()
    client_ip = request.client.host
    
    # Rate limit baseado no plano do tenant
    tenant_config = await TenantService.get_tenant_config(tenant)
    rate_limit = PLAN_LIMITS[tenant_config.plan]['requests_per_minute']
    
    # Verificar limite no Redis
    key = f"rate_limit:{tenant}:{client_ip}"
    current_requests = await redis.incr(key)
    
    if current_requests == 1:
        await redis.expire(key, 60)  # 1 minuto
    
    if current_requests > rate_limit:
        raise HTTPException(429, "Rate limit exceeded")
    
    return await call_next(request)
```

---

## 🚀 **Deployment Strategy**

### **📦 CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy CarMatch SaaS

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          python -m pytest tests/
          npm run test:e2e
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS
        run: |
          # Blue/green deployment
          aws ecs update-service --service carmatch-api-green
          
          # Smoke tests
          ./scripts/health-check.sh
          
          # Switch traffic
          aws elbv2 modify-rule --rule-arn $RULE_ARN --actions TargetGroupArn=$GREEN_TG
          
          # Cleanup blue environment
          sleep 300  # 5 min grace period
          aws ecs update-service --service carmatch-api-blue --desired-count 0

# scripts/tenant-setup.sh
#!/bin/bash
# Script para onboarding de novo tenant

TENANT_SLUG=$1
TENANT_NAME=$2
TENANT_PLAN=$3

echo "🚀 Setting up tenant: $TENANT_SLUG"

# 1. Criar schema no banco
psql $DATABASE_URL -c "CREATE SCHEMA tenant_$TENANT_SLUG;"
psql $DATABASE_URL -f sql/tenant-schema.sql -v schema=tenant_$TENANT_SLUG

# 2. Configurar DNS
aws route53 change-resource-record-sets --hosted-zone-id $ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "'$TENANT_SLUG'.carmatch.com.br",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "lb.carmatch.com.br"}]
    }
  }]
}'

# 3. Criar configuração inicial
curl -X POST $API_URL/admin/tenants -d '{
  "slug": "'$TENANT_SLUG'",
  "name": "'$TENANT_NAME'",
  "plan": "'$TENANT_PLAN'",
  "status": "trial"
}'

echo "✅ Tenant $TENANT_SLUG configurado com sucesso!"
echo "🌐 Acesso: https://$TENANT_SLUG.carmatch.com.br"
```

---

## 📊 **Performance & Scaling**

### **⚡ Performance Targets**
```markdown
SLA por Tier:

📦 BASIC:
- Response time: <3s (95th percentile)
- Uptime: 99.0%
- Concurrent users: 50

📦 PROFESSIONAL:  
- Response time: <2s (95th percentile)
- Uptime: 99.5%
- Concurrent users: 200

📦 ENTERPRISE:
- Response time: <1s (95th percentile) 
- Uptime: 99.9%
- Concurrent users: 1000+
```

### **📈 Auto-Scaling Strategy**
```python
# Auto-scaling baseado em métricas por tenant
SCALING_POLICIES = {
    'cpu_threshold': 70,  # %
    'memory_threshold': 80,  # %
    'response_time_threshold': 2000,  # ms
    'queue_length_threshold': 100,  # requests
}

async def check_scaling_needs():
    """Verificar necessidade de scaling baseado em tenants ativos"""
    active_tenants = await get_active_tenants()
    
    for tenant in active_tenants:
        metrics = await get_tenant_metrics(tenant.slug)
        
        if should_scale_up(metrics):
            await scale_tenant_resources(tenant.slug, 'up')
        elif should_scale_down(metrics):
            await scale_tenant_resources(tenant.slug, 'down')
```

---

## 🎯 **Conclusão**

Esta arquitetura SaaS multi-tenant nos permite:

✅ **Escalar horizontalmente** para centenas de concessionárias  
✅ **Isolamento completo** de dados entre clientes  
✅ **Customização** por tenant sem código duplicado  
✅ **Performance** otimizada com cache inteligente  
✅ **Billing** automático baseado em uso  
✅ **Onboarding** automatizado em 24h  
✅ **Monitoring** granular por cliente  

**🚀 Pronto para transformar RobustCar (caso de teste) em uma plataforma SaaS escalável para todo mercado automotivo brasileiro!**
