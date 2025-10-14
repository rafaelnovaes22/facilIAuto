# 🧪 Como Testar a Galeria de Fotos

## 🚀 Passo a Passo para Testar

### 1️⃣ **Certifique-se que Backend e Frontend estão rodando**

```bash
# Se não estiverem rodando, execute:
start-faciliauto.bat
```

Aguarde até ver:
- ✅ Backend: `http://localhost:8000`
- ✅ Frontend: `http://localhost:3000`

---

### 2️⃣ **Acesse o Frontend**

Abra no navegador: **http://localhost:3000**

---

### 3️⃣ **Complete o Questionário**

1. **Passo 1 - Orçamento:**
   - Orçamento mín: `30000`
   - Orçamento máx: `60000`
   - Estado: `SP`
   - Cidade: `São Paulo`

2. **Passo 2 - Uso:**
   - Uso principal: Qualquer opção
   - Tamanho da família: `1`

3. **Passo 3 - Prioridades:**
   - Ajuste os sliders como preferir

4. **Passo 4 - Preferências:**
   - Tipos: Marque alguns (Hatch, Sedan, SUV)
   - Clique em "Ver Recomendações"

---

### 4️⃣ **Teste as Funcionalidades da Galeria**

Na **Página de Resultados**, você verá:

#### ✅ **Foto Principal no Card:**
- [x] Cada carro mostra uma foto (200px largura)
- [x] Se tiver mais fotos, aparece badge com número (ex: "🖼️ 5")
- [x] Foto é clicável (cursor vira "pointer")

#### ✅ **Botão "Ver Detalhes e Fotos":**
- [x] Aparece abaixo do botão WhatsApp
- [x] Mostra quantidade de fotos (ex: "Ver Detalhes e Fotos (5)")

---

### 5️⃣ **Abrir Modal de Detalhes**

**Duas formas de abrir:**
1. Clicar na **foto do carro**
2. Clicar no botão **"Ver Detalhes e Fotos"**

---

### 6️⃣ **Testar Galeria no Modal**

Quando o modal abrir, teste:

#### **A) Navegação com Setas:**
- [x] Clique na seta **→** (próxima foto)
- [x] Clique na seta **←** (foto anterior)
- [x] Navegação circular (última → primeira)

#### **B) Miniaturas:**
- [x] Miniaturas aparecem abaixo da foto principal
- [x] Clique em qualquer miniatura
- [x] Foto principal muda
- [x] Miniatura selecionada tem borda azul

#### **C) Indicador de Posição:**
- [x] Badge mostra "1 / 5" (foto atual / total)
- [x] Atualiza ao navegar

#### **D) Informações do Carro:**
- [x] Preço em destaque
- [x] Características (ano, km, combustível, câmbio, cor, portas)
- [x] Dados da concessionária
- [x] Botão WhatsApp funcional

#### **E) Fechar Modal:**
- [x] Clique no X no canto superior direito
- [x] Ou clique fora do modal (overlay)
- [x] Ao reabrir, deve começar na primeira foto

---

### 7️⃣ **Testar Casos Especiais**

#### **Carro com UMA foto apenas:**
- [ ] Não aparece badge de quantidade
- [ ] Não aparecem setas de navegação
- [ ] Não aparecem miniaturas
- [ ] Indicador mostra "1 / 1"

#### **Carro SEM foto:**
- [ ] Aparece placeholder "Sem Imagem"
- [ ] Card funciona normalmente
- [ ] Modal abre com placeholder

---

## 🎯 Checklist Completo

### **Página de Resultados:**
- [ ] Fotos carregam corretamente
- [ ] Badge de quantidade aparece (quando >1 foto)
- [ ] Imagem clicável
- [ ] Botão "Ver Detalhes" visível
- [ ] Layout responsivo

### **Modal de Detalhes:**
- [ ] Abre ao clicar na foto
- [ ] Abre ao clicar no botão
- [ ] Foto principal em destaque
- [ ] Navegação com setas funciona
- [ ] Miniaturas funcionam
- [ ] Indicador de posição correto
- [ ] Todas as informações visíveis
- [ ] WhatsApp funciona
- [ ] Fecha corretamente
- [ ] Reset da foto ao reabrir

### **Responsividade:**
- [ ] Desktop (>1024px): Layout padrão
- [ ] Tablet (768-1024px): Ajustado
- [ ] Mobile (<768px): Empilhado

---

## 🐛 Problemas Conhecidos?

Se encontrar algum problema:

1. **Fotos não carregam:**
   - Verifique console do navegador (F12)
   - Verifique se URLs das imagens estão corretas

2. **Modal não abre:**
   - Verifique console (F12)
   - Recarregue a página (Ctrl+F5)

3. **Navegação não funciona:**
   - Verifique se carro tem múltiplas fotos
   - Teste com diferentes carros

---

## 📸 Exemplos de Carros para Testar

**Carros da RobustCar (São Paulo):**
- Geralmente têm múltiplas fotos
- Testam navegação completa

**Carros da AutoCenter (Rio de Janeiro):**
- Podem ter 1 foto ou placeholder
- Testam casos especiais

---

## ✅ Resultado Esperado

Após os testes, você deve ter:
- ✅ Galeria de fotos totalmente funcional
- ✅ Navegação intuitiva
- ✅ Modal responsivo
- ✅ Experiência de usuário fluida

---

## 🎉 Pronto para Testar!

Execute: `start-faciliauto.bat` e acesse: **http://localhost:3000**

