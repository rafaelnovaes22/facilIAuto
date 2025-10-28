# Changelog - FacilIAuto

Registro de mudanças significativas no projeto.

## [2025-01-28] - Correção de Classificação de Carros

### Corrigido
- Ford Focus 2009-2013 agora classificado corretamente como Sedan (era Hatch)
- Motos detectadas e marcadas como indisponíveis (Yamaha XTZ 250)
- Falso positivo evitado: Chevrolet Onix MT não é mais confundido com moto

### Adicionado
- Parâmetro `ano` no classificador para classificação contextual
- Detecção inteligente de motos por palavras-chave e modelos específicos
- Scripts de validação: `validate_classification.py`, `test_classifier.py`
- Scripts de correção: `fix_classifications.py`, `find_misclassified.py`
- Suite de testes: `tests/test_car_classification.py` (13 casos)
- Documentação técnica: `docs/technical/CLASSIFICADOR-CARROS.md`
- Relatório de correção: `docs/reports/CORRECAO-CLASSIFICACAO-2025-01.md`

### Melhorado
- Classificador agora considera ano do veículo para casos especiais
- Proteção contra falsos positivos (MT = Manual vs MT-07 = Moto)
- Documentação organizada em `docs/` (raiz limpa e profissional)

### Técnico
- **Arquivos modificados:**
  - `platform/backend/services/car_classifier.py`
  - `platform/backend/scripts/reclassify_cars.py`
  - `platform/backend/data/robustcar_estoque.json` (3 carros)

- **Testes:**
  - 13/13 testes passando (100%)
  - 8/8 validações críticas passando (100%)
  - 0 problemas remanescentes

### Documentação
- Documentação movida para `docs/technical/` e `docs/reports/`
- README criado em `platform/backend/scripts/`
- Índice atualizado em `docs/README.md`
- CHANGELOG criado em `docs/CHANGELOG.md`
- Raiz do projeto limpa e profissional

---

## [2025-01-27] - Correção de Placeholders de Imagens

### Corrigido
- Erro `ERR_NAME_NOT_RESOLVED` ao carregar imagens de `via.placeholder.com`
- Frontend agora usa placeholders SVG locais (data URIs)

### Modificado
- `platform/frontend/src/components/results/CarCard.tsx`
- `platform/frontend/src/components/results/CarDetailsModal.tsx`

### Técnico
- Substituído `via.placeholder.com` por `CAR_PLACEHOLDER` (SVG inline)
- Sem dependência de serviços externos
- Funciona offline

---

## Formato

Este changelog segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

### Categorias
- **Adicionado** - Novas funcionalidades
- **Modificado** - Mudanças em funcionalidades existentes
- **Descontinuado** - Funcionalidades que serão removidas
- **Removido** - Funcionalidades removidas
- **Corrigido** - Correções de bugs
- **Segurança** - Vulnerabilidades corrigidas
