# Sistema de Classificação de Carros

## Visão Geral

O FacilIAuto utiliza um classificador inteligente que categoriza veículos automaticamente baseado em nome, modelo e ano. Este documento descreve o funcionamento, manutenção e casos especiais do sistema.

## Problema Identificado

Alguns veículos estavam sendo classificados incorretamente:
- **Ford Focus 2009-2013**: Classificado como Hatch, mas era Sedan no Brasil
- **Motos**: Sendo classificadas como carros (Hatch por padrão)

## Solução Implementada

### 1. Classificador Atualizado (`car_classifier.py`)

**Localização:** `platform/backend/services/car_classifier.py`

**Melhorias:**
- ✅ Adicionado parâmetro `ano` ao método `classify()`
- ✅ Detecção automática de motos (categoria especial)
- ✅ Regra específica para Ford Focus 2009-2013 → Sedan
- ✅ Focus 2014+ continua como Hatch (nova geração)
- ✅ Proteção contra falsos positivos (ex: Onix MT ≠ Moto)

### 2. Scripts Disponíveis

**Localização:** `platform/backend/scripts/`

#### `test_classifier.py` - Testar Classificador
```bash
cd platform/backend/scripts
python test_classifier.py
```
Testa o classificador com 13 casos conhecidos para validar a lógica.

#### `validate_classification.py` - Validação Rápida
```bash
python validate_classification.py
```
Valida 8 casos críticos rapidamente (ideal para CI/CD).

#### `find_misclassified.py` - Encontrar Problemas
```bash
python find_misclassified.py
```
Varre todos os estoques e identifica:
- Motos classificadas como carros
- Sedans classificados como Hatch
- Focus 2009-2013 incorretos

#### `fix_classifications.py` - Corrigir Automaticamente
```bash
python fix_classifications.py
```
Aplica as correções automaticamente:
- Reclassifica carros usando a lógica atualizada
- Marca motos como `disponivel: false`
- Atualiza os arquivos JSON

#### `reclassify_cars.py` - Reclassificação Completa
```bash
python reclassify_cars.py
```
Reclassifica TODOS os carros em todos os estoques.

## Workflow Recomendado

### Após Adicionar Novos Carros

1. **Testar o classificador:**
   ```bash
   cd platform/backend/scripts
   python test_classifier.py
   ```

2. **Verificar problemas:**
   ```bash
   python find_misclassified.py
   ```

3. **Corrigir se necessário:**
   ```bash
   python fix_classifications.py
   ```

4. **Reiniciar o backend:**
   ```bash
   cd ..
   python api/main.py
   ```

### Adicionar Nova Regra de Classificação

1. Editar `services/car_classifier.py`
2. Adicionar padrão em `MODEL_PATTERNS` ou lógica especial
3. Testar com `test_classifier.py`
4. Aplicar com `fix_classifications.py`
5. Commit das mudanças

## Categorias Suportadas

- **SUV**: Tracker, Creta, Kicks, T-Cross, Compass, etc.
- **Sedan**: Corolla, Civic, Virtus, Focus 2009-2013, etc.
- **Pickup**: Hilux, Ranger, S10, Amarok, Toro, etc.
- **Hatch**: Onix, Gol, Polo, Focus 2014+, HB20, etc.
- **Compacto**: Kwid, Mobi, Up, Picanto, etc.
- **Van**: Doblo, Kangoo, Spin, Zafira, etc.
- **Moto**: Detectada e marcada como indisponível

## Casos Especiais

### Ford Focus
- **2009-2013**: Sedan (geração anterior no Brasil)
- **2014+**: Hatch (nova geração)
- **Com "Sedan" no nome**: Sempre Sedan

**Lógica:**
```python
if 'focus' in search_text and ano and 2009 <= ano <= 2013:
    return 'Sedan'
```

### Motos

**Detecção por palavras-chave:**
- moto, motorcycle, bike, scooter, motocicleta

**Detecção por modelos específicos:**
- Honda: CB, CBR, CRF, XRE, Bros
- Yamaha: MT-07, MT-09, XTZ, YBR, Fazer, YZF
- Kawasaki: Ninja, Z650, Z900, ZX
- Suzuki: GSXR, GSX, V-Strom
- BMW: R1200, F800, G310

**Tratamento:**
- Categoria: "Moto"
- Automaticamente marcadas como `disponivel: false`
- Não aparecem nas recomendações

### Falsos Positivos Evitados

**Chevrolet Onix MT:**
- "MT" = Manual Transmission (câmbio manual)
- Não confundir com Yamaha MT (modelo de moto)
- Solução: Padrões específicos (mt-07, mt-09, não apenas "mt")

## Arquitetura

### Fluxo de Classificação

```
Entrada: nome, modelo, ano
    ↓
Normalização (lowercase)
    ↓
Detecção de Motos
    ↓
Busca por Padrões (ordem de especificidade)
    1. Pickup
    2. Van
    3. SUV
    4. Sedan (+ casos especiais)
    5. Compacto
    6. Hatch
    ↓
Retorno: Categoria
```

### Ordem de Especificidade

A ordem importa para evitar classificações incorretas:

1. **Pickup** (mais específico) - Hilux, Ranger, S10
2. **Van** (específico) - Doblo, Kangoo
3. **SUV** (pode confundir com Hatch) - Tracker, Creta
4. **Sedan** (detectar "s" ou palavra sedan)
5. **Compacto** (subconjunto de Hatch)
6. **Hatch** (padrão para carros populares)

## Testes

### Suite Completa
**Arquivo:** `platform/backend/tests/test_car_classification.py`

```bash
cd platform/backend
pytest tests/test_car_classification.py -v
```

**Cobertura:**
- Classificação por categoria
- Casos especiais (Focus, motos)
- Falsos positivos
- Inferência de características
- Detecção de versões premium

### Validação Rápida
```bash
cd platform/backend/scripts
python validate_classification.py
```

**8 testes críticos:**
- ✅ Focus 2009 = Sedan
- ✅ Focus 2014+ = Hatch
- ✅ Honda CB = Moto
- ✅ Yamaha MT = Moto
- ✅ Yamaha XTZ = Moto
- ✅ Onix MT ≠ Moto
- ✅ Tracker = SUV
- ✅ Corolla = Sedan

## Manutenção

### Se Encontrar Problemas

1. **Adicionar caso de teste:**
   ```python
   # Em test_classifier.py
   ("Novo Modelo", "Novo Modelo", 2024, "Categoria Esperada")
   ```

2. **Atualizar lógica:**
   ```python
   # Em car_classifier.py
   MODEL_PATTERNS['Categoria'].append('novo_modelo')
   ```

3. **Executar correção:**
   ```bash
   python scripts/fix_classifications.py
   ```

4. **Commit das mudanças**

### Logs e Debugging

Os scripts mostram:
- ✅ Sucessos
- ⚠️ Avisos (motos detectadas)
- ❌ Erros
- 📝 Exemplos de mudanças aplicadas

## Integração com API

O classificador é usado automaticamente ao:
- Carregar estoques na inicialização
- Adicionar novos carros
- Atualizar dados de veículos

**Não é necessário classificar manualmente** - o sistema faz isso automaticamente.

## Performance

- **Tempo de classificação:** < 1ms por carro
- **Carregamento inicial:** ~100ms para 1000 carros
- **Impacto na API:** Negligível (classificação em memória)

## Referências

- **Código:** `platform/backend/services/car_classifier.py`
- **Testes:** `platform/backend/tests/test_car_classification.py`
- **Scripts:** `platform/backend/scripts/`
- **Correção Aplicada:** `docs/technical/CORRECAO-CLASSIFICACAO.md`
