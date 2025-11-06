# ⛽ Serviço de Preço de Combustível

**Autor**: Kiro AI  
**Data**: 06/11/2024  
**Versão**: 1.0

---

## 📋 Visão Geral

Sistema automático para manter o preço do combustível sempre atualizado no cálculo de TCO.

**Fontes de preço (em ordem de prioridade):**
1. ✅ Variável de ambiente `FUEL_PRICE`
2. ✅ Cache local (válido por 7 dias)
3. 🔄 API externa (futuro)
4. ✅ Valor padrão (R$ 5,89)

---

## 🚀 Como Usar

### 1. Atualização via Variável de Ambiente (Recomendado para Produção)

```bash
# Linux/Mac
export FUEL_PRICE=6.09

# Windows CMD
set FUEL_PRICE=6.09

# Windows PowerShell
$env:FUEL_PRICE = "6.09"

# Docker
docker run -e FUEL_PRICE=6.09 faciliauto-backend

# Railway/Heroku
# Adicionar variável de ambiente no painel de controle
```

### 2. Atualização via API

```bash
# Atualizar preço manualmente
curl -X POST "http://localhost:8000/fuel-price/update?new_price=6.09"

# Consultar preço atual
curl "http://localhost:8000/fuel-price"
```

**Resposta:**
```json
{
  "price": 6.09,
  "source": "cache",
  "last_updated": "2024-11-06T10:30:00",
  "default_price": 5.89
}
```

### 3. Atualização via Python

```python
from services.fuel_price_service import fuel_price_service

# Atualizar preço
fuel_price_service.update_default_price(6.09)

# Obter preço atual
price = fuel_price_service.get_current_price(state="SP")
print(f"Preço atual: R$ {price:.2f}/L")
```

---

## 📊 Fontes de Dados

### ANP (Agência Nacional do Petróleo)

**URL**: https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos

**Atualização**: Semanal (toda segunda-feira)

**Como consultar:**
1. Acessar site da ANP
2. Ir em "Preços e Defesa da Concorrência" → "Preços"
3. Selecionar "Gasolina Comum"
4. Ver "Preço Médio Nacional"

### Alternativas

- **Petrobras**: https://petrobras.com.br/fatos-e-dados/precos-de-venda-de-combustiveis.htm
- **Ticket Log**: https://www.ticketlog.com.br/combustivel/preco-medio
- **Mercado Livre**: Média de postos próximos

---

## 🔄 Cache Local

**Localização**: `platform/backend/data/cache/fuel_price_cache.json`

**Estrutura:**
```json
{
  "price": 6.09,
  "timestamp": "2024-11-06T10:30:00",
  "source": "api"
}
```

**Validade**: 7 dias

**Limpeza automática**: Sim (ao buscar preço expirado)

---

## 🛠️ Configuração

### Alterar Duração do Cache

```python
# Em fuel_price_service.py
CACHE_DURATION_DAYS = 7  # Alterar para 3, 14, 30, etc
```

### Alterar Preço Padrão

```python
# Em fuel_price_service.py
DEFAULT_PRICE = 5.89  # Atualizar quando necessário
```

### Adicionar API Externa

```python
def _fetch_from_api(self, state: str) -> Optional[float]:
    """Implementar integração com API da ANP ou similar"""
    try:
        response = requests.get(
            f"https://api.anp.gov.br/precos/gasolina/{state}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('preco_medio')
    except Exception as e:
        print(f"[FUEL] Erro ao buscar da API: {e}")
    
    return None
```

---

## 📈 Monitoramento

### Logs

```
[FUEL] Usando preço da variável de ambiente: R$ 6.09/L
[FUEL] Usando preço do cache: R$ 6.09/L
[FUEL] Cache expirado (8 dias)
[FUEL] Preço obtido da API: R$ 6.09/L
[FUEL] Usando preço padrão: R$ 5.89/L
[FUEL] Preço salvo no cache: R$ 6.09/L
```

### Endpoint de Status

```bash
GET /fuel-price
```

**Resposta:**
```json
{
  "price": 6.09,
  "source": "environment|cache|api|default",
  "last_updated": "2024-11-06T10:30:00",
  "default_price": 5.89
}
```

---

## 🔒 Segurança

### Produção

⚠️ **IMPORTANTE**: Em produção, proteger o endpoint de atualização:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/fuel-price/update")
def update_fuel_price(
    new_price: float,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Validar token
    if credentials.credentials != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    # Atualizar preço
    fuel_price_service.update_default_price(new_price)
    return {"success": True}
```

---

## 🧪 Testes

```python
# test_fuel_price_service.py
def test_get_current_price():
    service = FuelPriceService()
    price = service.get_current_price()
    assert 3.0 <= price <= 10.0

def test_cache_expiration():
    service = FuelPriceService()
    service.update_default_price(6.09)
    
    # Deve usar cache
    price1 = service.get_current_price()
    assert price1 == 6.09
    
    # Simular expiração
    # ... (modificar timestamp do cache)
    
    # Deve buscar novo preço
    price2 = service.get_current_price()
    assert price2 is not None
```

---

## 📝 Checklist de Atualização

- [ ] Consultar preço na ANP
- [ ] Atualizar via variável de ambiente (produção)
- [ ] Ou atualizar via API POST
- [ ] Verificar logs para confirmar
- [ ] Testar cálculo de TCO
- [ ] Documentar data da atualização

---

## 🔮 Roadmap

### Fase 1 (Atual) ✅
- [x] Sistema de cache local
- [x] Variável de ambiente
- [x] Endpoint de consulta
- [x] Endpoint de atualização

### Fase 2 (Futuro)
- [ ] Integração com API da ANP
- [ ] Preços regionais por estado
- [ ] Atualização automática semanal
- [ ] Histórico de preços
- [ ] Notificações de variação

### Fase 3 (Futuro)
- [ ] Machine Learning para previsão
- [ ] Comparação com múltiplas fontes
- [ ] Dashboard de monitoramento
- [ ] Alertas de preço

---

## 📞 Suporte

**Dúvidas?**
- Documentação: `docs/FUEL-PRICE-SERVICE.md`
- Issues: GitHub Issues
- Email: tech@faciliauto.com

---

**Status**: ✅ Production Ready  
**Última Atualização**: 06/11/2024
