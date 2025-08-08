# 🧪 **Guia do Smoke Test E2E - FacilIAuto**

## 🎯 **Objetivo**

O **Smoke Test E2E** é um teste crítico e minimalista que valida o fluxo principal do sistema:

```
Usuário acessa → Preenche questionário → Submete busca → Recebe resultados
```

Este teste **DEVE sempre passar** para garantir que a funcionalidade core está funcionando.

---

## 🚀 **Execução Rápida**

### **Método 1: Script Automatizado (Recomendado)**
```bash
# 1. Iniciar servidor em um terminal
python main.py

# 2. Em outro terminal, executar smoke test
python run_smoke_test.py

# Ou especificar browser
python run_smoke_test.py firefox
```

### **Método 2: Pytest Direto**
```bash
# Servidor deve estar rodando em localhost:8000
python -m pytest tests/e2e/test_smoke.py --browser chromium -v
```

### **Método 3: Docker**
```bash
# Stack completa com teste
docker-compose up -d
python run_smoke_test.py
```

---

## 📋 **Pré-requisitos**

### **Dependências Instaladas**
```bash
pip install playwright==1.40.0 pytest-playwright==0.4.3
playwright install chromium --with-deps
```

### **Servidor Rodando**
```bash
# O servidor DEVE estar acessível em http://localhost:8000
python main.py

# Verificar saúde
curl http://localhost:8000/health
```

---

## 🎭 **Detalhes do Teste**

### **Fluxo Testado**
1. **Acesso**: Carrega página principal
2. **Questionário**: Preenche 8 steps com dados válidos
3. **Busca**: Submete formulário
4. **Resultados**: Valida que modal aparece com conteúdo

### **Dados de Teste Usados**
```yaml
Urgência: "30_dias"
Região: "SP" 
Uso Principal: "urbano"
Pessoas: "2"
Espaço Carga: "medio"
Potência: "media"
Prioridade: "economia"
Orçamento: "30000-80000"
```

### **Validações Realizadas**
- ✅ Página carrega (título correto)
- ✅ Todos os 8 steps são navegáveis
- ✅ Formulário é submetido com sucesso
- ✅ Modal de resultados aparece
- ✅ Modal contém conteúdo válido

---

## 🔧 **Configuração**

### **Timeouts Generosos**
```javascript
timeout: 60000ms        // Timeout total do teste
actionTimeout: 30000ms  // Timeout para cliques/preenchimentos
expectTimeout: 30000ms  // Timeout para validações
```

### **Retry Automático**
- **Desenvolvimento**: 1 retry
- **CI/CD**: 2 retries

### **Debugging Automático**
- **Screenshot** em falhas
- **Video** em falhas
- **Trace** no primeiro retry

---

## 📊 **Interpretando Resultados**

### **✅ Teste Passou**
```
🎉 [SMOKE] TESTE SMOKE PASSOU COM SUCESSO!
✅ [SMOKE] Fluxo crítico funcionando perfeitamente
```
**Significado**: Sistema core está funcionando, pode fazer deploy com confiança.

### **❌ Teste Falhou**
```
❌ [SMOKE] FALHA CRÍTICA: [detalhes do erro]
📸 [SMOKE] Screenshot salvo: smoke_test_failure.png
```
**Ação**: Investigar erro, verificar logs, não fazer deploy.

---

## 🚨 **Troubleshooting**

### **Problema: "Servidor não disponível"**
```bash
# Verificar se servidor está rodando
curl http://localhost:8000/health

# Se não, iniciar servidor
python main.py

# Aguardar alguns segundos e tentar novamente
```

### **Problema: "Elemento não encontrado"**
- **Causa comum**: UI mudou mas teste não foi atualizado
- **Solução**: Verificar seletores em `tests/e2e/test_smoke.py`
- **Debug**: Ver screenshot gerado em falhas

### **Problema: "Timeout"**
- **Causa comum**: Sistema lento ou dependência indisponível
- **Solução**: Verificar health check detalhado
```bash
curl http://localhost:8000/health/detailed | jq
```

### **Problema: "Modal vazio"**
- **Causa comum**: API de busca retornando dados vazios
- **Solução**: Verificar logs do servidor e banco de dados

---

## 🎯 **Boas Práticas**

### **Quando Executar**
- ✅ **Antes de commits** importantes
- ✅ **Antes de deploy** para produção
- ✅ **Após mudanças** na UI principal
- ✅ **No pipeline** CI/CD

### **Quando NÃO Executar**
- ❌ Para mudanças pequenas (unit tests são suficientes)
- ❌ Quando servidor não está disponível
- ❌ Para debug de funcionalidades específicas

### **Manutenção**
- 🔄 **Atualizar seletores** quando UI muda
- 🔄 **Revisar dados** de teste periodicamente
- 🔄 **Ajustar timeouts** conforme performance

---

## 📈 **Métricas**

### **Alvos de Performance**
- **Tempo total**: < 60s
- **Taxa de sucesso**: > 95%
- **Falsos positivos**: < 5%

### **Monitoramento**
```bash
# Ver histórico de execuções
ls -la smoke-test-results/

# Ver último relatório HTML
open smoke-test-results/index.html
```

---

## 🔮 **Evolução Futura**

### **Possíveis Melhorias**
1. **Testes A/B**: Diferentes combinações de dados
2. **Performance**: Medir tempo de resposta
3. **Mobile**: Testar em dispositivos móveis
4. **Acessibilidade**: Validar conformidade WCAG

### **Integração CI/CD**
```yaml
# GitHub Actions
- name: Smoke Test E2E
  run: |
    python main.py &
    sleep 10
    python run_smoke_test.py
    pkill -f "python main.py"
```

---

**🎯 O Smoke Test é a garantia de que o coração do sistema bate forte!**
