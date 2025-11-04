# Estratégia de Scraping para MVP

**Data**: 30/10/2025  
**Contexto**: Popular banco de dados rapidamente para MVP

---

## 🎯 Objetivo

Obter dados de 2-3 concessionárias para validar produto no MVP.

---

## 📊 Status dos Scrapers

### 1. RobustCar
**Status**: ✅ Funcional (HTML estático)  
**Método**: Scraping automático  
**Tempo**: ~5-10 minutos  
**Veículos**: ~70-90 carros

### 2. RP Multimarcas
**Status**: ⚠️ Site usa JavaScript  
**Problema**: Veículos carregados dinamicamente via JS  
**Soluções**:

#### Opção A: Selenium/Playwright (Automático)
```python
# Pros:
✅ Totalmente automático
✅ Funciona com JavaScript
✅ Pode ser reutilizado

# Contras:
❌ Requer instalação de browser driver
❌ Mais lento (5-10x)
❌ Mais complexo
❌ Pode quebrar facilmente

# Tempo estimado: 3-4 horas de implementação
```

#### Opção B: Extração Manual + CSV (Recomendado para MVP)
```python
# Pros:
✅ Muito rápido (30-60 minutos)
✅ Simples e confiável
✅ Dados 100% precisos
✅ Não quebra

# Contras:
❌ Trabalho manual
❌ Não escalável

# Tempo estimado: 30-60 minutos
```

#### Opção C: API/Feed (Ideal, mas improvável)
```python
# Pros:
✅ Dados estruturados
✅ Sempre atualizado
✅ Oficial

# Contras:
❌ Concessionária precisa fornecer
❌ Improvável para MVP

# Tempo estimado: Depende da concessionária
```

---

## 🚀 Recomendação para MVP

### Use Opção B: Extração Manual + CSV

**Por quê?**
1. **Tempo**: 30-60 minutos vs 3-4 horas
2. **Confiabilidade**: 100% vs ~70% (Selenium pode falhar)
3. **Simplicidade**: Copiar/colar vs código complexo
4. **MVP**: Objetivo é validar produto, não ter scraping perfeito

**Como fazer:**

#### Passo 1: Criar Template CSV
```csv
nome,marca,modelo,ano,preco,quilometragem,combustivel,cambio,cor,portas,categoria,url_original
```

#### Passo 2: Abrir Site e Copiar Dados
1. Abrir https://rpmultimarcas.com.br/
2. Para cada veículo:
   - Copiar nome, preço, ano, km
   - Copiar características (câmbio, combustível, etc.)
   - Colar na planilha

#### Passo 3: Importar CSV
```python
python import_csv_to_json.py rpmultimarcas.csv
```

**Tempo total**: 30-60 minutos para ~30-50 carros

---

## 📋 Plano de Ação Imediato

### Para MVP (Hoje)

1. ✅ **RobustCar**: Executar scraper automático
   ```bash
   python robustcar_scraper.py
   ```

2. ✅ **RP Multimarcas**: Extração manual + CSV
   ```bash
   # Criar planilha manualmente
   # Importar com script
   python import_csv_to_json.py rpmultimarcas.csv
   ```

3. ✅ **Importar no Backend**
   ```bash
   # Copiar JSONs para backend/data/
   cp robustcar_estoque.json ../backend/data/
   cp rpmultimarcas_estoque.json ../backend/data/
   ```

**Tempo total**: 1-2 horas  
**Resultado**: MVP com ~100-150 carros de 2 concessionárias

### Para Produção (Fase 2)

1. 🚀 **Portal Self-Service**: Concessionárias gerenciam próprio estoque
2. 🚀 **Eliminar scraping**: Não será mais necessário
3. 🚀 **Ver**: `docs/implementation/ROADMAP-GESTAO-ESTOQUE.md`

---

## 🛠️ Script de Importação CSV

Vou criar um script para facilitar a importação:

```python
# import_csv_to_json.py
import csv
import json
from datetime import datetime
import hashlib

def import_csv_to_json(csv_file, output_file):
    """Importar CSV para formato JSON do FacilIAuto"""
    
    vehicles = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Converter tipos
            vehicle = {
                'id': f"rpmulti_{len(vehicles) + 1}",
                'nome': row['nome'],
                'marca': row['marca'],
                'modelo': row['modelo'],
                'ano': int(row['ano']),
                'preco': float(row['preco']),
                'quilometragem': int(row['quilometragem']),
                'combustivel': row['combustivel'],
                'cambio': row['cambio'],
                'cor': row.get('cor'),
                'portas': int(row['portas']) if row.get('portas') else None,
                'categoria': row['categoria'],
                'url_original': row['url_original'],
                'data_scraping': datetime.now().isoformat()
            }
            
            # Calcular hash
            hashable = {k: v for k, v in vehicle.items() if k not in ['id', 'data_scraping']}
            vehicle['content_hash'] = hashlib.md5(
                json.dumps(hashable, sort_keys=True).encode()
            ).hexdigest()
            
            vehicles.append(vehicle)
    
    # Salvar JSON
    output = {
        'metadata': {
            'source': 'rpmultimarcas.com.br',
            'method': 'manual_csv_import',
            'timestamp': datetime.now().isoformat(),
            'total_vehicles': len(vehicles)
        },
        'vehicles': vehicles
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Importados {len(vehicles)} veículos")
    print(f"💾 Salvo em: {output_file}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python import_csv_to_json.py <arquivo.csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    output_file = csv_file.replace('.csv', '_estoque.json')
    import_csv_to_json(csv_file, output_file)
```

---

## 📊 Comparação de Métodos

| Método | Tempo | Confiabilidade | Escalabilidade | Recomendado para |
|--------|-------|----------------|----------------|------------------|
| **Scraping HTML** | 10 min | Alta (90%) | Média | Sites estáticos |
| **Selenium/Playwright** | 30-60 min | Média (70%) | Baixa | Sites com JS simples |
| **Manual + CSV** | 30-60 min | Muito Alta (100%) | Muito Baixa | MVP rápido |
| **API/Feed** | 5 min | Muito Alta (100%) | Muito Alta | Produção |
| **Portal Self-Service** | N/A | Muito Alta (100%) | Muito Alta | Produção |

---

## ✅ Decisão para MVP

### RobustCar
- ✅ Usar scraper automático (já funciona)
- ✅ Executar agora

### RP Multimarcas
- ✅ Usar extração manual + CSV
- ✅ Mais rápido e confiável para MVP
- ✅ Executar agora

### Próximas Concessionárias (se necessário)
- ✅ Avaliar caso a caso
- ✅ Priorizar sites com HTML estático
- ✅ Usar manual + CSV se tiver JavaScript

---

## 🎯 Próximos Passos

1. **Agora**: Executar scraper RobustCar
2. **Agora**: Criar CSV RP Multimarcas (30-60 min)
3. **Agora**: Importar ambos no backend
4. **Depois**: Validar no frontend
5. **Futuro**: Implementar portal self-service (Fase 2)

---

**Última Atualização**: 30/10/2025  
**Status**: Estratégia definida, pronta para execução
