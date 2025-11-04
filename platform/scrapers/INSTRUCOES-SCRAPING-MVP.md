# Instruções: Scraping para MVP

**Objetivo**: Popular banco de dados com veículos de 2 concessionárias  
**Tempo estimado**: 1-2 horas  
**Data**: 30/10/2025

---

## 🎯 Resumo Executivo

### O Que Fazer

1. ✅ **RobustCar**: Scraping automático (10 minutos)
2. ✅ **RP Multimarcas**: Extração manual + CSV (30-60 minutos)
3. ✅ **Importar no backend**: Copiar JSONs (5 minutos)

**Total**: 1-2 horas para ~100-150 carros

---

## 📋 Passo a Passo

### Passo 1: Scraping RobustCar (Automático)

```bash
# Navegar para pasta de scrapers
cd platform/scrapers

# Executar scraper
python robustcar_scraper.py

# Resultado esperado:
# ✅ Scraping concluído: 70-90 carros extraídos
# 💾 Dados salvos em: robustcar_estoque.json
```

**Tempo**: ~10 minutos

---

### Passo 2: RP Multimarcas (Manual + CSV)

#### 2.1 Criar Planilha

1. Abrir `template_veiculos.csv` no Excel/Google Sheets
2. Ou criar nova planilha com colunas:
   ```
   nome,marca,modelo,ano,preco,quilometragem,combustivel,cambio,cor,portas,categoria,descricao,imagens,url_original
   ```

#### 2.2 Extrair Dados do Site

1. Abrir https://rpmultimarcas.com.br/
2. Ir para seção "Nossos veículos"
3. Para cada veículo:
   - Clicar no veículo
   - Copiar informações:
     - **Nome**: Título completo (ex: "Toyota Corolla GLi 1.8")
     - **Marca**: Toyota
     - **Modelo**: Corolla
     - **Ano**: 2022
     - **Preço**: 95990 (sem pontos/vírgulas)
     - **KM**: 45000 (sem pontos/vírgulas)
     - **Combustível**: Flex, Gasolina, Diesel, etc.
     - **Câmbio**: Manual, Automático, Automático CVT
     - **Cor**: Prata, Preto, Branco, etc.
     - **Portas**: 4, 2, 5
     - **Categoria**: Sedan, Hatch, SUV, Pickup, Van
     - **URL**: URL da página do veículo
   - Colar na planilha

4. Salvar como `rpmultimarcas.csv`

**Dicas**:
- Campos obrigatórios: nome, marca, modelo, ano, preco, quilometragem
- Campos opcionais: combustivel, cambio, cor, portas, categoria, descricao, imagens, url_original
- Se não tiver a informação, deixe em branco (não invente!)
- Preço e KM: apenas números (ex: 95990, não R$ 95.990,00)
- Imagens: separar por ponto-e-vírgula (;)

**Tempo**: ~30-60 minutos para 30-50 carros

#### 2.3 Importar CSV para JSON

```bash
# Importar CSV
python import_csv_to_json.py rpmultimarcas.csv rpmultimarcas

# Resultado esperado:
# ✅ Dados salvos com sucesso!
# 💾 Arquivo: rpmultimarcas_estoque.json
# 📊 Veículos: 30-50
```

**Tempo**: ~1 minuto

---

### Passo 3: Validar Dados

```bash
# Verificar arquivos gerados
ls -la *.json

# Deve mostrar:
# robustcar_estoque.json
# rpmultimarcas_estoque.json

# Verificar conteúdo (primeiros veículos)
head -n 50 robustcar_estoque.json
head -n 50 rpmultimarcas_estoque.json
```

**Tempo**: ~2 minutos

---

### Passo 4: Importar no Backend

```bash
# Copiar JSONs para backend
cp robustcar_estoque.json ../backend/data/
cp rpmultimarcas_estoque.json ../backend/data/

# Ou no Windows:
copy robustcar_estoque.json ..\backend\data\
copy rpmultimarcas_estoque.json ..\backend\data\
```

**Tempo**: ~1 minuto

---

### Passo 5: Atualizar dealerships.json

Editar `platform/backend/data/dealerships.json` para incluir RP Multimarcas:

```json
[
  {
    "id": "robustcar",
    "name": "RobustCar São Paulo",
    "city": "São Paulo",
    "state": "SP",
    "phone": "(11) 1234-5678",
    "whatsapp": "5511987654321",
    "active": true,
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  {
    "id": "rpmultimarcas",
    "name": "RP Multimarcas",
    "city": "São Paulo",
    "state": "SP",
    "phone": "(11) 0000-0000",
    "whatsapp": "5511000000000",
    "active": true,
    "latitude": -23.5505,
    "longitude": -46.6333
  }
]
```

**Tempo**: ~2 minutos

---

### Passo 6: Testar no Frontend

```bash
# Iniciar backend (se não estiver rodando)
cd platform/backend
python api/main.py

# Em outro terminal, iniciar frontend
cd platform/frontend
npm run dev

# Abrir navegador
# http://localhost:3000

# Testar:
# 1. Preencher questionário
# 2. Ver recomendações
# 3. Verificar se carros das 2 concessionárias aparecem
```

**Tempo**: ~5 minutos

---

## ✅ Checklist de Validação

Após completar todos os passos, verificar:

- [ ] `robustcar_estoque.json` existe e tem 70-90 veículos
- [ ] `rpmultimarcas_estoque.json` existe e tem 30-50 veículos
- [ ] Ambos os JSONs estão em `platform/backend/data/`
- [ ] `dealerships.json` inclui ambas as concessionárias
- [ ] Backend inicia sem erros
- [ ] Frontend mostra carros das 2 concessionárias
- [ ] Recomendações funcionam corretamente

---

## 🚨 Troubleshooting

### Problema: Scraper RobustCar falha

**Solução**:
1. Verificar se site está acessível: https://robustcar.com.br
2. Verificar logs de erro
3. Se necessário, usar extração manual + CSV também

### Problema: CSV não importa

**Erros comuns**:
- Campos obrigatórios faltando → Preencher nome, marca, modelo, ano, preco, km
- Formato de preço errado → Usar apenas números (95990, não R$ 95.990,00)
- Formato de KM errado → Usar apenas números (45000, não 45.000 km)
- Encoding errado → Salvar CSV como UTF-8

**Solução**:
```bash
# Ver erros detalhados
python import_csv_to_json.py rpmultimarcas.csv rpmultimarcas

# Corrigir erros na planilha
# Tentar novamente
```

### Problema: Backend não carrega veículos

**Solução**:
1. Verificar se JSONs estão em `platform/backend/data/`
2. Verificar formato dos JSONs (deve ter `metadata` e `vehicles`)
3. Reiniciar backend
4. Verificar logs do backend

### Problema: Frontend não mostra veículos

**Solução**:
1. Abrir DevTools (F12)
2. Ver Console para erros
3. Ver Network para verificar chamadas API
4. Verificar se backend está rodando
5. Verificar se endpoint `/api/v1/cars` retorna dados

---

## 📊 Resultado Esperado

### Estatísticas

- **Total de veículos**: 100-150
- **Concessionárias**: 2 (RobustCar + RP Multimarcas)
- **Tempo total**: 1-2 horas
- **Qualidade**: Alta (dados validados)

### Próximos Passos

1. ✅ Validar produto com stakeholders
2. ✅ Coletar feedback de usuários
3. ✅ Decidir se precisa mais concessionárias
4. ✅ Planejar Fase 2: Portal Self-Service

---

## 📚 Documentação Relacionada

- **Princípios de Extração**: `PRINCIPIOS-EXTRACAO-DADOS.md`
- **Estratégia MVP**: `SCRAPING-MVP-ESTRATEGIA.md`
- **Roadmap Produção**: `docs/implementation/ROADMAP-GESTAO-ESTOQUE.md`
- **Validação**: `validate_no_default_values.py`

---

## 🎉 Conclusão

Após completar estes passos, você terá:

✅ MVP funcional com dados reais  
✅ 100-150 veículos de 2 concessionárias  
✅ Sistema de recomendação validado  
✅ Base para demonstrar valor do produto  

**Pronto para validar o MVP!** 🚀

---

**Última Atualização**: 30/10/2025  
**Próxima Revisão**: Após validação do MVP
