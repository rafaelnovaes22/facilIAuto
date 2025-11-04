# Princípios de Extração de Dados

**Data**: 30/10/2025  
**Versão**: 1.0  
**Prioridade**: CRÍTICA

---

## 🎯 Princípio Fundamental

### ⚠️ NUNCA INVENTE DADOS

**Regra de Ouro**: Se o dado não está no site da concessionária, retorne `None`. **NUNCA** assuma ou crie valores padrão.

---

## ❌ O Que NÃO Fazer

### 1. Não Assumir Valores Padrão

```python
# ❌ ERRADO - Assumindo "Manual" quando não encontra
def extract_cambio(self, text: str) -> str:
    if not text:
        return "Manual"  # ❌ ERRADO!
    
    # ... lógica de extração ...
    
    return "Manual"  # ❌ ERRADO! Não sabemos se é manual

# ✅ CORRETO - Retorna None quando não encontra
def extract_cambio(self, text: str) -> Optional[str]:
    if not text:
        return None  # ✅ CORRETO!
    
    # ... lógica de extração ...
    
    return None  # ✅ CORRETO! Não sabemos o valor
```

### 2. Não Preencher Campos Obrigatórios com Valores Fictícios

```python
# ❌ ERRADO - Criando dados que não existem
car_data = {
    'nome': title.text if title else 'Veículo sem nome',  # ❌ ERRADO!
    'preco': price or 0,  # ❌ ERRADO!
    'ano': year or 2020,  # ❌ ERRADO!
    'cambio': cambio or 'Manual',  # ❌ ERRADO!
}

# ✅ CORRETO - Apenas incluir se existir
car_data = {}
if title:
    car_data['nome'] = title.text
if price:
    car_data['preco'] = price
if year:
    car_data['ano'] = year
if cambio:
    car_data['cambio'] = cambio
```

### 3. Não Inferir Dados de Outros Campos

```python
# ❌ ERRADO - Inferindo categoria do nome
def extract_categoria(self, nome: str) -> str:
    if 'SUV' in nome:
        return 'SUV'  # ❌ ERRADO! Pode estar no nome mas não ser a categoria
    return 'Sedan'  # ❌ ERRADO! Não sabemos

# ✅ CORRETO - Apenas extrair se houver campo específico
def extract_categoria(self, html: str) -> Optional[str]:
    categoria_element = soup.find('span', class_='categoria')
    if categoria_element:
        return self.normalize_categoria(categoria_element.text)
    return None  # ✅ CORRETO! Não sabemos a categoria
```

### 4. Não Usar Valores "Razoáveis"

```python
# ❌ ERRADO - Usando valores "razoáveis"
def extract_portas(self, text: str) -> int:
    if not text:
        return 4  # ❌ ERRADO! "A maioria tem 4 portas"
    # ...

# ✅ CORRETO - Retornar None
def extract_portas(self, text: str) -> Optional[int]:
    if not text:
        return None  # ✅ CORRETO!
    # ...
```

---

## ✅ O Que Fazer

### 1. Retornar None Quando Não Encontrar

```python
# ✅ CORRETO
def extract_field(self, text: str) -> Optional[str]:
    if not text:
        return None
    
    # Tentar extrair
    result = self._try_extract(text)
    
    if result:
        return result
    
    return None  # Não encontrou, retorna None
```

### 2. Validar e Rejeitar Dados Incompletos

```python
# ✅ CORRETO - Validação rigorosa
def validate_car_data(self, car: Dict) -> List[str]:
    """Validar dados extraídos"""
    errors = []
    
    # Campos obrigatórios
    required_fields = ['nome', 'preco', 'ano', 'quilometragem']
    for field in required_fields:
        if field not in car or car[field] is None:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    # Se tem erros, NÃO salvar o veículo
    return errors
```

### 3. Logar Quando Não Encontrar Dados

```python
# ✅ CORRETO - Logging para debug
def extract_cambio(self, text: str) -> Optional[str]:
    if not text:
        logger.warning("Câmbio não encontrado no HTML")
        return None
    
    result = self._normalize_cambio(text)
    
    if result is None:
        logger.warning(f"Não foi possível normalizar câmbio: '{text}'")
    
    return result
```

### 4. Documentar Campos Opcionais vs Obrigatórios

```python
# ✅ CORRETO - Documentação clara
class Vehicle(BaseModel):
    """
    Modelo de veículo
    
    Campos OBRIGATÓRIOS (devem estar no site):
    - nome, marca, modelo, ano, preco, quilometragem
    
    Campos OPCIONAIS (podem não estar no site):
    - cambio, cor, portas, categoria, descricao
    """
    # Obrigatórios
    nome: str
    marca: str
    modelo: str
    ano: int
    preco: float
    quilometragem: int
    
    # Opcionais (podem ser None)
    cambio: Optional[str] = None
    cor: Optional[str] = None
    portas: Optional[int] = None
    categoria: Optional[str] = None
```

---

## 🔍 Checklist de Revisão

Antes de fazer commit, verifique:

- [ ] ✅ Todos os métodos `extract_*` retornam `Optional[T]`?
- [ ] ✅ Nenhum método retorna valor padrão quando não encontra dado?
- [ ] ✅ Validação rejeita veículos com campos obrigatórios faltando?
- [ ] ✅ Logs indicam quando dados não são encontrados?
- [ ] ✅ Documentação clara sobre campos obrigatórios vs opcionais?

---

## 📊 Exemplos Práticos

### Exemplo 1: Extração de Câmbio

```python
# Site da concessionária:
<div class="specs">
    <span class="label">Câmbio:</span>
    <span class="value">Automático CVT</span>
</div>

# ✅ CORRETO - Extrair o que está lá
cambio = soup.find('span', class_='value').text  # "Automático CVT"
car_data['cambio'] = self.normalize_cambio(cambio)  # "Automático CVT"
```

```python
# Site da concessionária:
<div class="specs">
    <!-- Câmbio não está listado -->
</div>

# ✅ CORRETO - Não inventar
cambio_element = soup.find('span', class_='cambio-value')
if cambio_element:
    car_data['cambio'] = self.normalize_cambio(cambio_element.text)
else:
    # NÃO adicionar 'cambio' ao dict
    # OU adicionar como None
    car_data['cambio'] = None
    logger.warning(f"Câmbio não encontrado para {car_data['nome']}")
```

### Exemplo 2: Extração de Quilometragem

```python
# Site da concessionária:
<div class="mileage">50.000 km</div>

# ✅ CORRETO - Extrair e normalizar
km_text = soup.find('div', class_='mileage').text  # "50.000 km"
car_data['quilometragem'] = self.extract_km(km_text)  # 50000
```

```python
# Site da concessionária:
<!-- Quilometragem não está listada -->

# ✅ CORRETO - Não inventar
km_element = soup.find('div', class_='mileage')
if km_element:
    car_data['quilometragem'] = self.extract_km(km_element.text)
else:
    # Campo obrigatório faltando - veículo será rejeitado na validação
    logger.error(f"Quilometragem não encontrada para {car_data['nome']}")
    # Não adicionar ao dict ou adicionar como None
```

### Exemplo 3: Extração de Categoria

```python
# Site da concessionária:
<div class="category">SUV</div>

# ✅ CORRETO - Extrair o que está lá
categoria_text = soup.find('div', class_='category').text  # "SUV"
car_data['categoria'] = self.normalize_categoria(categoria_text)  # "SUV"
```

```python
# Site da concessionária:
<!-- Categoria não está listada -->

# ❌ ERRADO - Inferir do nome
nome = "Toyota RAV4 SUV 2023"
if 'SUV' in nome:
    car_data['categoria'] = 'SUV'  # ❌ ERRADO!

# ✅ CORRETO - Não inventar
categoria_element = soup.find('div', class_='category')
if categoria_element:
    car_data['categoria'] = self.normalize_categoria(categoria_element.text)
else:
    car_data['categoria'] = None
    logger.warning(f"Categoria não encontrada para {nome}")
```

---

## 🚨 Consequências de Inventar Dados

### 1. Perda de Confiança do Cliente
```
Cliente: "O site diz que é automático, mas o carro é manual!"
Resultado: Cliente insatisfeito, reclamação, perda de credibilidade
```

### 2. Recomendações Incorretas
```
Sistema recomenda carro "Manual" para quem quer "Automático"
Motivo: Scraper assumiu "Manual" quando dado não existia
Resultado: Recomendação ruim, cliente não encontra o que quer
```

### 3. Problemas Legais
```
Anúncio diz: "4 portas"
Realidade: 2 portas (scraper assumiu 4)
Resultado: Propaganda enganosa, possível processo
```

### 4. Dados Inconsistentes
```
Mesmo carro em sites diferentes:
- Site A: Câmbio não informado → Scraper assume "Manual"
- Site B: Câmbio informado → "Automático"
Resultado: Dados conflitantes no banco
```

---

## ✅ Benefícios de Não Inventar Dados

### 1. Confiança
- Dados correspondem exatamente ao que está no site
- Cliente vê no FacilIAuto o que vê no site da concessionária

### 2. Qualidade
- Fácil identificar sites com dados incompletos
- Possível solicitar à concessionária que complete informações

### 3. Transparência
- Relatórios mostram % de completude por concessionária
- Decisões baseadas em dados reais, não suposições

### 4. Manutenibilidade
- Código mais simples (sem lógica de inferência)
- Menos bugs (sem casos especiais)

---

## 📋 Processo de Validação

### 1. Durante Extração
```python
def extract_vehicle_data(self, url: str) -> Optional[Dict]:
    """Extrair dados de um veículo"""
    car_data = {}
    
    # Extrair cada campo
    car_data['nome'] = self.extract_nome(html)
    car_data['preco'] = self.extract_preco(html)
    car_data['ano'] = self.extract_ano(html)
    car_data['quilometragem'] = self.extract_km(html)
    car_data['cambio'] = self.extract_cambio(html)  # Pode ser None
    
    # Validar campos obrigatórios
    required = ['nome', 'preco', 'ano', 'quilometragem']
    missing = [f for f in required if not car_data.get(f)]
    
    if missing:
        logger.error(f"Campos obrigatórios faltando: {missing}")
        return None  # Rejeitar veículo
    
    return car_data
```

### 2. Após Extração
```python
def validate_and_save(self, cars: List[Dict]) -> Dict:
    """Validar e salvar veículos"""
    valid_cars = []
    rejected_cars = []
    
    for car in cars:
        errors = self.validate_car_data(car)
        
        if errors:
            rejected_cars.append({
                'car': car,
                'errors': errors
            })
        else:
            valid_cars.append(car)
    
    # Salvar apenas veículos válidos
    self.save_to_json(valid_cars, 'valid_cars.json')
    
    # Salvar rejeitados para análise
    self.save_to_json(rejected_cars, 'rejected_cars.json')
    
    return {
        'total': len(cars),
        'valid': len(valid_cars),
        'rejected': len(rejected_cars),
        'completeness': len(valid_cars) / len(cars) if cars else 0
    }
```

### 3. Relatório de Qualidade
```python
def generate_quality_report(self, cars: List[Dict]) -> Dict:
    """Gerar relatório de qualidade dos dados"""
    total = len(cars)
    
    fields = ['nome', 'preco', 'ano', 'quilometragem', 'cambio', 'cor', 'categoria']
    completeness = {}
    
    for field in fields:
        count = sum(1 for car in cars if car.get(field) is not None)
        completeness[field] = {
            'count': count,
            'percentage': (count / total * 100) if total > 0 else 0
        }
    
    return {
        'total_vehicles': total,
        'field_completeness': completeness
    }
```

---

## 🎯 Resumo

### Regras Simples

1. **Se não está no site, retorne `None`**
2. **Nunca assuma valores padrão**
3. **Valide e rejeite dados incompletos**
4. **Logue quando não encontrar dados**
5. **Documente campos obrigatórios vs opcionais**

### Mantra

> **"Prefiro ter 70% dos dados corretos do que 100% dos dados com 30% inventados"**

---

**Última Atualização**: 30/10/2025  
**Revisão Obrigatória**: Antes de cada scraping
