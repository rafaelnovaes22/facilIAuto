# Estratégia de Testes E2E - FeiraBrás App

## 1. VISÃO GERAL

### Objetivo
Garantir que os fluxos críticos do aplicativo funcionem corretamente de ponta a ponta, simulando o comportamento real dos usuários vendedores da Feira da Madrugada.

### Princípios
- **Realismo:** Simular cenários reais da feira
- **Cobertura:** Focar nos fluxos de maior valor
- **Velocidade:** Testes rápidos para CI/CD
- **Confiabilidade:** Evitar flaky tests
- **Manutenibilidade:** Código limpo e reutilizável

## 2. FERRAMENTAS E TECNOLOGIAS

### Mobile (React Native)
```javascript
// Detox - Framework principal para E2E mobile
{
  "detox": "^20.13.0",
  "jest": "^29.5.0",
  "jest-circus": "^29.5.0"
}
```

### Backend API
```javascript
// Cypress - Para testes de API e admin web
{
  "cypress": "^13.0.0",
  "@cypress/request": "^3.0.0"
}
```

### Ferramentas Auxiliares
```javascript
{
  "faker": "^6.0.0",        // Dados fake
  "dayjs": "^1.11.0",       // Manipulação de datas
  "dotenv": "^16.0.0",      // Variáveis ambiente
  "allure-commandline": "^2.0.0" // Relatórios
}
```

## 3. ARQUITETURA DE TESTES

### Estrutura de Pastas
```
e2e/
├── config/
│   ├── detox.config.js
│   ├── jest.config.js
│   └── test-data.js
├── fixtures/
│   ├── products.json
│   ├── customers.json
│   └── sales.json
├── helpers/
│   ├── auth.helper.js
│   ├── api.helper.js
│   └── ui.helper.js
├── page-objects/
│   ├── LoginPage.js
│   ├── ProductPage.js
│   ├── SalePage.js
│   └── ReportsPage.js
├── specs/
│   ├── critical/
│   │   ├── sale-flow.spec.js
│   │   ├── cash-closing.spec.js
│   │   └── product-management.spec.js
│   ├── regression/
│   │   ├── customer.spec.js
│   │   ├── reports.spec.js
│   │   └── offline.spec.js
│   └── smoke/
│       └── basic-flow.spec.js
└── reports/
```

### Page Object Pattern
```javascript
// e2e/page-objects/SalePage.js
class SalePage {
  constructor() {
    this.searchInput = element(by.id('search-product'));
    this.productList = element(by.id('product-list'));
    this.cartButton = element(by.id('cart-button'));
    this.totalAmount = element(by.id('total-amount'));
    this.paymentMethodPix = element(by.id('payment-pix'));
    this.confirmButton = element(by.id('confirm-sale'));
  }

  async searchProduct(name) {
    await this.searchInput.typeText(name);
    await this.searchInput.tapReturnKey();
  }

  async selectProduct(index = 0) {
    await this.productList.atIndex(index).tap();
  }

  async goToCart() {
    await this.cartButton.tap();
  }

  async selectPaymentMethod(method = 'pix') {
    await element(by.id(`payment-${method}`)).tap();
  }

  async confirmSale() {
    await this.confirmButton.tap();
  }

  async completeSaleFlow(products, paymentMethod) {
    for (const product of products) {
      await this.searchProduct(product);
      await this.selectProduct();
    }
    await this.goToCart();
    await this.selectPaymentMethod(paymentMethod);
    await this.confirmSale();
  }
}

module.exports = new SalePage();
```

## 4. CENÁRIOS DE TESTE CRÍTICOS

### 4.1 Fluxo de Venda Completo
```javascript
// e2e/specs/critical/sale-flow.spec.js
describe('Fluxo de Venda Completo', () => {
  beforeAll(async () => {
    await device.launchApp();
    await loginHelper.loginAsVendor();
  });

  it('deve realizar venda com múltiplos produtos e PIX', async () => {
    // Arrange
    const products = ['Camiseta Branca M', 'Calça Jeans 40'];
    const expectedTotal = 89.90;

    // Act
    await salePage.completeSaleFlow(products, 'pix');

    // Assert
    await expect(element(by.text('Venda realizada com sucesso!'))).toBeVisible();
    await expect(element(by.text(`R$ ${expectedTotal}`))).toBeVisible();
    
    // Verificar estoque atualizado
    await element(by.id('menu-products')).tap();
    await expect(element(by.text('Camiseta Branca M (4)'))).toBeVisible();
  });

  it('deve aplicar desconto e calcular corretamente', async () => {
    // Arrange
    await salePage.searchProduct('Vestido Floral');
    await salePage.selectProduct();
    
    // Act
    await salePage.goToCart();
    await element(by.id('discount-input')).typeText('10');
    
    // Assert
    const originalPrice = 120.00;
    const expectedPrice = 108.00;
    await expect(element(by.text(`R$ ${expectedPrice}`))).toBeVisible();
  });

  it('deve gerar comprovante e enviar por WhatsApp', async () => {
    // Complete sale
    await salePage.completeSaleFlow(['Blusa Rosa P'], 'dinheiro');
    
    // Generate receipt
    await element(by.id('generate-receipt')).tap();
    await element(by.id('customer-phone')).typeText('11999999999');
    await element(by.id('send-whatsapp')).tap();
    
    // Verify WhatsApp intent
    await expect(element(by.text('Abrir WhatsApp'))).toBeVisible();
  });
});
```

### 4.2 Fechamento de Caixa
```javascript
// e2e/specs/critical/cash-closing.spec.js
describe('Fechamento de Caixa', () => {
  beforeAll(async () => {
    await device.launchApp();
    await loginHelper.loginAsVendor();
    await testDataHelper.createSalesForToday(10);
  });

  it('deve fechar caixa com conferência', async () => {
    // Navigate to cash closing
    await element(by.id('menu-cash')).tap();
    await element(by.id('close-cash')).tap();

    // Verify summary
    await expect(element(by.text('Resumo do Dia'))).toBeVisible();
    await expect(element(by.text('Total Vendas: R$ 1.250,00'))).toBeVisible();
    await expect(element(by.text('Dinheiro: R$ 450,00'))).toBeVisible();
    await expect(element(by.text('PIX: R$ 650,00'))).toBeVisible();
    await expect(element(by.text('Cartão: R$ 150,00'))).toBeVisible();

    // Confirm closing
    await element(by.id('confirm-closing')).tap();
    await expect(element(by.text('Caixa fechado com sucesso'))).toBeVisible();
  });

  it('deve registrar sangria corretamente', async () => {
    await element(by.id('menu-cash')).tap();
    await element(by.id('cash-withdrawal')).tap();
    await element(by.id('amount-input')).typeText('200');
    await element(by.id('reason-input')).typeText('Pagamento fornecedor');
    await element(by.id('confirm-withdrawal')).tap();

    await expect(element(by.text('Sangria registrada'))).toBeVisible();
    await expect(element(by.text('Saldo: R$ 250,00'))).toBeVisible();
  });
});
```

### 4.3 Gestão de Produtos
```javascript
// e2e/specs/critical/product-management.spec.js
describe('Gestão de Produtos', () => {
  it('deve cadastrar produto com foto', async () => {
    await element(by.id('menu-products')).tap();
    await element(by.id('add-product')).tap();

    // Fill form
    await element(by.id('product-name')).typeText('Jaqueta Jeans');
    await element(by.id('product-price')).typeText('89.90');
    await element(by.id('product-quantity')).typeText('5');
    
    // Add photo
    await element(by.id('add-photo')).tap();
    await element(by.text('Escolher da Galeria')).tap();
    // Detox will use a mock photo

    // Select sizes
    await element(by.id('size-M')).tap();
    await element(by.id('size-G')).tap();

    // Save
    await element(by.id('save-product')).tap();
    await expect(element(by.text('Produto cadastrado'))).toBeVisible();
  });

  it('deve atualizar estoque após venda', async () => {
    const initialStock = 10;
    const soldQuantity = 3;

    // Create product with stock
    await productHelper.createProduct('Camisa Polo', initialStock);

    // Make sale
    await salePage.completeSaleFlow(['Camisa Polo'], 'pix', soldQuantity);

    // Verify stock
    await element(by.id('menu-products')).tap();
    await element(by.text('Camisa Polo')).tap();
    
    const expectedStock = initialStock - soldQuantity;
    await expect(element(by.text(`Estoque: ${expectedStock}`))).toBeVisible();
  });
});
```

## 5. TESTES DE CENÁRIOS ESPECIAIS

### 5.1 Modo Offline
```javascript
// e2e/specs/regression/offline.spec.js
describe('Funcionamento Offline', () => {
  it('deve funcionar sem internet', async () => {
    // Disable network
    await device.setURLBlacklist(['.*']);

    // Perform offline operations
    await salePage.completeSaleFlow(['Produto Teste'], 'dinheiro');
    await expect(element(by.text('Venda salva localmente'))).toBeVisible();

    // Enable network
    await device.clearURLBlacklist();
    
    // Verify sync
    await device.sendToHome();
    await device.launchApp();
    await expect(element(by.text('Sincronizando...'))).toBeVisible();
    await waitFor(element(by.text('Sincronizado'))).toBeVisible().withTimeout(5000);
  });
});
```

### 5.2 Performance
```javascript
// e2e/specs/regression/performance.spec.js
describe('Performance', () => {
  it('deve carregar lista de 100 produtos em menos de 2s', async () => {
    // Create many products
    await testDataHelper.createProducts(100);

    // Measure load time
    const startTime = Date.now();
    await element(by.id('menu-products')).tap();
    await waitFor(element(by.id('product-list'))).toBeVisible();
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(2000);
  });

  it('deve realizar venda em menos de 10s', async () => {
    const startTime = Date.now();
    
    await salePage.searchProduct('Produto Rápido');
    await salePage.selectProduct();
    await salePage.goToCart();
    await salePage.selectPaymentMethod('pix');
    await salePage.confirmSale();
    
    const saleTime = Date.now() - startTime;
    expect(saleTime).toBeLessThan(10000);
  });
});
```

## 6. CONFIGURAÇÃO DO AMBIENTE

### 6.1 Detox Config
```javascript
// .detoxrc.js
module.exports = {
  testRunner: {
    args: {
      $0: 'jest',
      config: 'e2e/config/jest.config.js'
    },
    jest: {
      setupTimeout: 120000
    }
  },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/FeiraBras.app',
      build: 'xcodebuild -workspace ios/FeiraBras.xcworkspace -scheme FeiraBras -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build'
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
      reversePorts: [8081]
    }
  },
  devices: {
    'simulator': {
      type: 'ios.simulator',
      device: {
        type: 'iPhone 14'
      }
    },
    'emulator': {
      type: 'android.emulator',
      device: {
        avdName: 'Pixel_4_API_30'
      }
    }
  },
  configurations: {
    'ios.sim.debug': {
      device: 'simulator',
      app: 'ios.debug'
    },
    'android.emu.debug': {
      device: 'emulator',
      app: 'android.debug'
    }
  }
};
```

### 6.2 Jest Config
```javascript
// e2e/config/jest.config.js
module.exports = {
  maxWorkers: 1,
  testEnvironment: './environment',
  testRunner: 'jest-circus/runner',
  testTimeout: 120000,
  testRegex: '\\.spec\\.js$',
  reporters: [
    'default',
    ['jest-allure', {
      outputDir: 'e2e/reports/allure-results'
    }]
  ],
  verbose: true,
  bail: 0,
  setupFilesAfterEnv: ['./init.js']
};
```

## 7. CI/CD PIPELINE

### 7.1 GitHub Actions
```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-android:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
          npm run postinstall
      
      - name: Setup Android
        uses: android-actions/setup-android@v2
      
      - name: Create AVD
        run: |
          echo "y" | $ANDROID_HOME/tools/bin/sdkmanager --install "system-images;android-30;google_apis;x86_64"
          echo "no" | $ANDROID_HOME/tools/bin/avdmanager create avd -n Pixel_4_API_30 -k "system-images;android-30;google_apis;x86_64"
      
      - name: Start Emulator
        run: |
          $ANDROID_HOME/emulator/emulator -avd Pixel_4_API_30 -no-window -no-audio &
          adb wait-for-device
      
      - name: Build App
        run: |
          npm run build:android:debug
      
      - name: Run E2E Tests
        run: |
          npm run e2e:android:ci
      
      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-results
          path: e2e/reports/

  test-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          npm ci
          cd ios && pod install
      
      - name: Build App
        run: |
          npm run build:ios:debug
      
      - name: Run E2E Tests
        run: |
          npm run e2e:ios:ci
      
      - name: Generate Report
        if: always()
        run: |
          npm run report:generate
      
      - name: Deploy Report
        if: always()
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./e2e/reports/html
```

## 8. SCRIPTS NPM

```json
// package.json
{
  "scripts": {
    "e2e:build:ios": "detox build -c ios.sim.debug",
    "e2e:build:android": "detox build -c android.emu.debug",
    "e2e:test:ios": "detox test -c ios.sim.debug",
    "e2e:test:android": "detox test -c android.emu.debug",
    "e2e:ios": "npm run e2e:build:ios && npm run e2e:test:ios",
    "e2e:android": "npm run e2e:build:android && npm run e2e:test:android",
    "e2e:ci": "detox test -c android.emu.debug --cleanup --headless --record-logs all",
    "e2e:smoke": "detox test e2e/specs/smoke -c android.emu.debug",
    "e2e:critical": "detox test e2e/specs/critical -c android.emu.debug",
    "e2e:regression": "detox test e2e/specs/regression -c android.emu.debug",
    "report:generate": "allure generate e2e/reports/allure-results -o e2e/reports/html",
    "report:open": "allure open e2e/reports/html"
  }
}
```

## 9. MELHORES PRÁTICAS

### 9.1 Escrita de Testes
```javascript
// ✅ BOM - Teste focado e independente
it('deve calcular desconto corretamente', async () => {
  const product = await productHelper.createProduct({ price: 100 });
  await salePage.addToCart(product);
  await salePage.applyDiscount(10);
  await expect(salePage.total).toHaveText('R$ 90,00');
});

// ❌ RUIM - Teste com múltiplas responsabilidades
it('deve testar toda a aplicação', async () => {
  // Login
  // Criar produto
  // Fazer venda
  // Verificar relatório
  // Fechar caixa
  // ... 100 linhas de código
});
```

### 9.2 Seletores
```javascript
// ✅ BOM - Seletores específicos para teste
<TouchableOpacity testID="confirm-sale-button">

// ❌ RUIM - Seletores frágeis
element(by.text('Confirmar')) // Pode quebrar com mudança de texto
element(by.type('TouchableOpacity')).atIndex(3) // Posição pode mudar
```

### 9.3 Esperas
```javascript
// ✅ BOM - Espera explícita com timeout
await waitFor(element(by.id('loading')))
  .not.toBeVisible()
  .withTimeout(5000);

// ❌ RUIM - Sleep fixo
await new Promise(resolve => setTimeout(resolve, 3000));
```

## 10. TROUBLESHOOTING

### Problemas Comuns

#### 1. Teste intermitente (Flaky)
```javascript
// Problema: Elemento não encontrado ocasionalmente
// Solução: Adicionar espera explícita
await waitFor(element(by.id('product-list')))
  .toBeVisible()
  .withTimeout(10000);
```

#### 2. Emulador lento
```javascript
// Solução: Aumentar timeouts no CI
testTimeout: process.env.CI ? 180000 : 120000
```

#### 3. Estado compartilhado entre testes
```javascript
// Solução: Limpar estado antes de cada teste
beforeEach(async () => {
  await device.clearKeychain();
  await device.launchApp({ delete: true });
});
```

## 11. MÉTRICAS E KPIs

### Métricas de Qualidade
- **Cobertura E2E:** > 80% dos fluxos críticos
- **Tempo de execução:** < 30 min suite completa
- **Taxa de falha:** < 5% (flaky tests)
- **Tempo de feedback:** < 10 min no PR

### Dashboard de Monitoramento
```javascript
// Integração com ferramentas de monitoramento
const metrics = {
  totalTests: 45,
  passed: 43,
  failed: 2,
  duration: '25m 30s',
  coverage: {
    critical: '100%',
    regression: '85%',
    smoke: '100%'
  }
};
```

## 12. ROADMAP

### Fase 1 (MVP) ✅
- Setup inicial Detox
- Testes dos fluxos críticos
- CI/CD básico

### Fase 2 (3 meses)
- Testes de performance
- Testes de acessibilidade
- Visual regression tests

### Fase 3 (6 meses)
- Testes multi-dispositivo
- Testes de stress
- Chaos engineering

---

*Documento mantido pelo time de QA*
*Última atualização: [Data atual]*
*Versão: 1.0*