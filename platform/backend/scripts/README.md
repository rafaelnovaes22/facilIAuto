# Scripts de Manutenção

Scripts utilitários para manutenção do backend FacilIAuto.

## Classificação de Carros

### Validação Rápida
```bash
python validate_classification.py
```
Valida 8 casos críticos do classificador.

### Testes Completos
```bash
python test_classifier.py
```
Executa 13 casos de teste do classificador.

### Encontrar Problemas
```bash
python find_misclassified.py
```
Varre estoques procurando classificações incorretas.

### Corrigir Automaticamente
```bash
python fix_classifications.py
```
Aplica correções automáticas nos estoques.

### Reclassificar Tudo
```bash
python reclassify_cars.py
```
Reclassifica todos os carros em todos os estoques.

## Análise e Calibração

### Analisar Métricas
```bash
python analyze_metrics.py
```
Analisa distribuição de scores e métricas.

### Calibrar Scores
```bash
python calibrate_scores.py
```
Calibra pesos e thresholds do sistema de recomendação.

### Validar Dados
```bash
python validate_car_data.py
```
Valida integridade dos dados de carros.

## Documentação

Para documentação completa sobre classificação de carros:
- **Técnica:** `docs/technical/CLASSIFICADOR-CARROS.md`
- **Relatório:** `docs/reports/CORRECAO-CLASSIFICACAO-2025-01.md`
