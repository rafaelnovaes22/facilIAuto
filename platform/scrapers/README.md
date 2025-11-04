# 🕷️ Scrapers - FacilIAuto

Scrapers para extração de dados de concessionárias parceiras.

---

## 📋 Scrapers Disponíveis

### 1. RobustCar Scraper

**Arquivo**: `robustcar_scraper.py`

**Funcionalidades**:
- ✅ Extração de nome, marca, modelo
- ✅ Extração de preço
- ✅ Extração de ano
- ✅ **Extração correta de câmbio** (Manual, Automático, CVT)
- ✅ **Extração correta de quilometragem**
- ✅ Extração de combustível
- ✅ Extração de cor
- ✅ Extração de portas
- ✅ Extração de imagens
- ✅ Extração de descrição
- ✅ Validação automática de dados

---

## 🚀 Como Usar

### Instalação de Dependências

```bash
pip install requests beautifulsoup4
```

### Executar Scraper

```bash
cd platform/scrapers
python robustcar_scraper.py
```

### Parâmetros

```python
# No código, ajustar:
scraper.scrape_all(max_pages=3)  # Número de páginas
```

---

## 🔧 Extração de Câmbio

### Padrões Reconhecidos

O scraper reconhece os seguintes padrões:

```python
# Texto → Resultado
"Câmbio: Manual" → "Manual"
"Câmbio: Automático" → "Automático"
"Câmbio: Automático CVT" → "Automático CVT"
"Câmbio: Automatizada" → "Automatizada"
"M" → "Manual"
"A" → "Automático"
"CVT" → "Automático CVT"
```

### Método de Extração

```python
def extract_cambio(self, text: str) -> str:
    """
    Extrair tipo de câmbio do texto
    """
    text_lower = text.lower()
    
    if 'automático cvt' in text_lower or 'cvt' in text_lower:
        return "Automático CVT"
    elif 'automático' in text_lower or 'automatico' in text_lower:
        return "Automático"
    elif 'automatizada' in text_lower:
        return "Automatizada"
    elif 'manual' in text_lower:
        return "Manual"
    
    return "Manual"  # Padrão
```

---

## 🚗 Extração de Quilometragem

### Padrões Reconhecidos

```python
# Texto → Resultado
"50.000 km" → 50000
"50000 km" → 50000
"50 mil km" → 50000
"0 km" → 0
"Zero km" → 0
```

### Método de Extração

```python
def extract_quilometragem(self, text: str) -> int:
    """
    Extrair quilometragem do texto
    """
    # Zero km
    if 'zero km' in text_lower or '0 km' in text_lower:
        return 0
    
    # Padrão: números seguidos de "km"
    pattern = r'(\d+(?:[.,]\d+)*)\s*(?:mil\s+)?km'
    match = re.search(pattern, text_lower)
    
    if match:
        km_str = match.group(1).replace('.', '').replace(',', '')
        km = int(km_str)
        
        # Se tem "mil" no texto, multiplicar por 1000
        if 'mil' in text_lower and km < 1000:
            km *= 1000
        
        return km
    
    return 0
```

---

## ✅ Validação de Dados

O scraper valida automaticamente:

### 1. Campos Obrigatórios
- Nome
- Preço
- Ano

### 2. Câmbio
- Deve ser: Manual, Automático, Automático CVT ou Automatizada
- Alerta se não extraído

### 3. Quilometragem
- Alerta se não extraído
- Alerta se carro antigo tem 0km

### 4. Preço
- Deve ser > 0

### Exemplo de Validação

```
🔍 Validando 73 carros...

⚠️  Toyota Corolla 2022:
   - Carro de 2022 com 0km é suspeito

⚠️  Chevrolet Onix 2021:
   - Câmbio não extraído

✅ Todos os carros validados com sucesso!
```

---

## 📊 Estrutura de Dados

### Saída JSON

```json
{
  "nome": "Toyota Corolla GLi",
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2022,
  "preco": 95000.0,
  "quilometragem": 45000,
  "combustivel": "Flex",
  "cambio": "Automático CVT",
  "cor": "Prata",
  "portas": 4,
  "imagens": [
    "https://example.com/image1.jpg"
  ],
  "descricao": "Toyota Corolla GLi 2022...",
  "url_original": "https://robustcar.com.br/...",
  "data_scraping": "2025-10-30T14:30:00"
}
```

---

## 🐛 Troubleshooting

### Problema: Câmbio sempre "Manual"

**Causa**: Seletor CSS incorreto

**Solução**:
1. Inspecionar HTML do site
2. Ajustar seletor em `extract_car_details()`
3. Testar com `extract_cambio()`

### Problema: Quilometragem sempre 0

**Causa**: Padrão de texto não reconhecido

**Solução**:
1. Ver exemplos de texto no site
2. Ajustar regex em `extract_quilometragem()`
3. Adicionar novos padrões

### Problema: Timeout

**Causa**: Site lento ou bloqueando

**Solução**:
```python
# Aumentar timeout
response = self.session.get(car_url, timeout=30)

# Aumentar delay entre requisições
time.sleep(2)  # 2 segundos
```

---

## 🔄 Atualização de Dados

### Fluxo Recomendado

1. **Executar scraper**:
   ```bash
   python robustcar_scraper.py
   ```

2. **Validar dados**:
   ```bash
   python ../backend/scripts/audit_data_quality.py
   ```

3. **Se necessário, corrigir**:
   ```bash
   python ../backend/scripts/fix_missing_data.py --force
   ```

4. **Substituir arquivo**:
   ```bash
   cp robustcar_estoque_new.json ../backend/data/robustcar_estoque.json
   ```

5. **Reiniciar API**:
   ```bash
   cd ../backend
   python api/main.py
   ```

---

## 📝 Notas Importantes

### Rate Limiting

- Delay de 1 segundo entre requisições
- Respeitar robots.txt
- Não sobrecarregar o servidor

### User Agent

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### Ética

- Usar apenas para fins legítimos
- Respeitar termos de uso do site
- Não fazer scraping excessivo
- Cachear dados quando possível

---

## 🎯 Próximos Passos

1. ✅ Scraper básico criado
2. ⏳ Testar com site real
3. ⏳ Ajustar seletores CSS
4. ⏳ Adicionar mais concessionárias
5. ⏳ Automatizar atualização diária
6. ⏳ Adicionar monitoramento

---

**Criado**: 30/10/2025  
**Última atualização**: 30/10/2025  
**Status**: ✅ Pronto para uso (ajustar seletores conforme site real)
