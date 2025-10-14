# 🧪 Como Rodar os Testes

## Problema Encontrado

O comando `executePwsh` está tendo problemas com o caminho do diretório. Isso é um problema conhecido do ambiente.

## ✅ Solução: Rodar Manualmente

### Opção 1: Usar o Script Batch (Recomendado)

```bash
# No terminal do Windows (CMD ou PowerShell)
cd platform\frontend
run-tests.bat
```

### Opção 2: Rodar Diretamente com NPM

```bash
# No terminal do Windows (CMD ou PowerShell)
cd platform\frontend
npm test -- --run
```

### Opção 3: Rodar com Coverage

```bash
# No terminal do Windows (CMD ou PowerShell)
cd platform\frontend
npm run test:coverage -- --run
```

### Opção 4: Rodar em Watch Mode (Desenvolvimento)

```bash
# No terminal do Windows (CMD ou PowerShell)
cd platform\frontend
npm test
```

---

## 📊 O Que Esperar

### Testes Criados

**Total: 152 testes em 11 arquivos**

```
✅ HomePage.test.tsx              - 10 testes
✅ QuestionnairePage.test.tsx     -  8 testes
✅ ResultsPage.test.tsx           - 30 testes
✅ Step1Budget.test.tsx           - 13 testes
✅ Step2Usage.test.tsx            - 14 testes
✅ Step3Priorities.test.tsx       - 17 testes
✅ Step4Preferences.test.tsx      - 20 testes
✅ ProgressIndicator.test.tsx     - 15 testes
✅ CarCard.test.tsx               - 14 testes
✅ ScoreVisual.test.tsx           - 11 testes
✅ CarDetailsModal.test.tsx       - 30 testes
```

### Resultado Esperado

```
 ✓ src/pages/__tests__/HomePage.test.tsx (10)
 ✓ src/pages/__tests__/QuestionnairePage.test.tsx (8)
 ✓ src/pages/__tests__/ResultsPage.test.tsx (30)
 ✓ src/components/questionnaire/__tests__/Step1Budget.test.tsx (13)
 ✓ src/components/questionnaire/__tests__/Step2Usage.test.tsx (14)
 ✓ src/components/questionnaire/__tests__/Step3Priorities.test.tsx (17)
 ✓ src/components/questionnaire/__tests__/Step4Preferences.test.tsx (20)
 ✓ src/components/questionnaire/__tests__/ProgressIndicator.test.tsx (15)
 ✓ src/components/results/__tests__/CarCard.test.tsx (14)
 ✓ src/components/results/__tests__/ScoreVisual.test.tsx (11)
 ✓ src/components/results/__tests__/CarDetailsModal.test.tsx (30)

Test Files  11 passed (11)
     Tests  152 passed (152)
  Start at  XX:XX:XX
  Duration  X.XXs
```

---

## 🔧 Possíveis Problemas e Soluções

### Problema 1: Imports não encontrados

**Erro:**
```
Cannot find module '@/...'
```

**Solução:**
Verificar se o `tsconfig.json` tem o path alias configurado:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Problema 2: Módulos não instalados

**Erro:**
```
Cannot find module 'vitest' or '@testing-library/react'
```

**Solução:**
```bash
cd platform\frontend
npm install
```

### Problema 3: Tipos não encontrados

**Erro:**
```
Cannot find type definitions
```

**Solução:**
Verificar se `@types` estão instalados no `package.json`

### Problema 4: Testes falhando por mocks

**Erro:**
```
TypeError: Cannot read property 'mock' of undefined
```

**Solução:**
Verificar se os mocks estão configurados corretamente no início dos arquivos de teste.

---

## 📈 Próximos Passos Após Rodar os Testes

### Se Todos os Testes Passarem ✅

1. **Gerar Coverage Report**
   ```bash
   npm run test:coverage -- --run
   ```

2. **Ver Coverage no Navegador**
   ```bash
   # Abrir o arquivo gerado
   start coverage/index.html
   ```

3. **Avançar para Fase 2**
   - Validar integração backend-frontend
   - Testar CORS
   - Validar fluxo end-to-end

### Se Alguns Testes Falharem ❌

1. **Ver detalhes dos erros**
   ```bash
   npm test -- --run --reporter=verbose
   ```

2. **Rodar teste específico**
   ```bash
   npm test -- --run src/pages/__tests__/HomePage.test.tsx
   ```

3. **Corrigir os problemas**
   - Verificar imports
   - Verificar mocks
   - Verificar tipos

4. **Rodar novamente**
   ```bash
   npm test -- --run
   ```

---

## 🎯 Comandos Úteis

### Rodar Testes

```bash
# Todos os testes (uma vez)
npm test -- --run

# Todos os testes (watch mode)
npm test

# Teste específico
npm test -- --run HomePage.test.tsx

# Com coverage
npm run test:coverage -- --run

# UI de testes
npm run test:ui
```

### Ver Resultados

```bash
# Coverage HTML
start coverage/index.html

# Coverage no terminal
npm run test:coverage -- --run --reporter=verbose
```

### Debug

```bash
# Modo verbose
npm test -- --run --reporter=verbose

# Com logs
npm test -- --run --reporter=verbose --silent=false
```

---

## ✅ Checklist de Validação

Após rodar os testes, verificar:

- [ ] Todos os 152 testes passaram
- [ ] Coverage está acima de 80%
- [ ] Nenhum erro de import
- [ ] Nenhum erro de tipo
- [ ] Nenhum warning crítico

---

## 📞 Suporte

Se encontrar problemas:

1. Verificar se `node_modules` está instalado
2. Verificar versão do Node.js (deve ser 18+)
3. Verificar versão do npm (deve ser 9+)
4. Limpar cache: `npm cache clean --force`
5. Reinstalar: `rm -rf node_modules && npm install`

---

**Criado em:** 13 de Outubro, 2025  
**Status:** Aguardando execução manual dos testes  
**Próximo:** Validar resultados e avançar para Fase 2

