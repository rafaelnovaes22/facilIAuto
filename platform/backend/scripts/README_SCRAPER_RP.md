# Scraper RP Multimarcas

Scraper para extrair dados de veículos do site da RP Multimarcas (rpmultimarcas.com.br).

## Características

- ✅ Extração via API (rápido e confiável)
- ✅ Fallback para HTML parsing se API falhar
- ✅ Normalização automática de dados
- ✅ Formato compatível com FacilIAuto
- ✅ Logging detalhado
- ✅ Tratamento de erros robusto

## Uso

### Executar scraping

```bash
python platform/backend/scripts/scraper_rp_multimarcas.py
```

### Adicionar ao dealerships.json

```bash
python platform/backend/scripts/add_rp_multimarcas_to_dealerships.py
```

## Arquivos Gerados

- `rp_multimarcas_raw.json` - Dados brutos extraídos
- `platform/backend/data/rpmultimarcas_estoque.json` - Formato FacilIAuto
- `platform/backend/data/dealerships.json` - Atualizado com RP Multimarcas

## Dados Extraídos

- Marca
- Modelo
- Versão
- Ano de fabricação/modelo
- Preço
- Quilometragem
- Câmbio
- Combustível
- Cor
- Imagens
- URL original

## Performance

- **Tempo médio**: ~1-2 segundos
- **Veículos extraídos**: 32+ (depende do estoque)
- **Taxa de sucesso**: 100% (com fallback)

## Informações da Concessionária

- **Nome**: RP Multimarcas
- **Endereço**: Av. Marechal Tito, 5385 - São Paulo - SP
- **Telefone**: (11) 5050-8288
- **WhatsApp**: (11) 94036-0465
- **Site**: https://rpmultimarcas.com.br

## Tecnologias

- Python 3.10+
- requests - HTTP client
- BeautifulSoup4 - HTML parsing
- json - Data serialization

## Estrutura do Código

```python
class RPMultimarcasScraper:
    - fetch_vehicles_from_api()      # Busca da API
    - parse_api_vehicle()            # Processa dados da API
    - scrape_listing_page()          # Fallback HTML
    - parse_vehicle_card()           # Processa cards HTML
    - convert_to_faciliauto_format() # Converte formato
    - save_to_json()                 # Salva arquivos
    - run()                          # Orquestra tudo
```

## Manutenção

Se o site mudar:

1. **API mudou**: Atualizar `fetch_vehicles_from_api()` com novo endpoint
2. **HTML mudou**: Atualizar seletores em `scrape_listing_page()`
3. **Campos novos**: Adicionar em `parse_api_vehicle()` e `convert_to_faciliauto_format()`

## Logs

O scraper gera logs detalhados:

```
INFO - === Iniciando scraping RP Multimarcas ===
INFO - Buscando veículos da API: https://rpmultimarcas.com.br/Home/ListaEstoque
INFO - API retornou 32 veículos
INFO - Processados 32 veículos da API
INFO - Dados salvos em: rp_multimarcas_raw.json
INFO - Dados salvos em: platform/backend/data/rpmultimarcas_estoque.json
INFO - === Scraping concluído em 1.15s ===
INFO - Total de veículos: 32
```

## Próximos Passos

- [ ] Adicionar scraping de detalhes individuais (mais campos)
- [ ] Implementar agendamento automático (cron)
- [ ] Adicionar detecção de mudanças (diff)
- [ ] Implementar notificações de novos veículos
- [ ] Adicionar cache com TTL
- [ ] Implementar rate limiting mais sofisticado
