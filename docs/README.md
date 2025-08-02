# 🚗 FacilIAuto - Sistema de Busca Inteligente de Carros

Um sistema avançado de recomendação de carros que usa **LangGraph** para processar inteligentemente as preferências do usuário através de um questionário de 8 perguntas e recomendar os carros mais adequados ao seu perfil.

## 🎯 Funcionalidades

- **Questionário Inteligente**: 8 perguntas estratégicas para mapear o perfil do usuário
- **Busca com LangGraph**: Processamento inteligente usando fluxos de trabalho com grafos
- **Recomendações Personalizadas**: Score de compatibilidade baseado em múltiplos critérios
- **Interface Web Moderna**: Design responsivo e intuitivo
- **API RESTful**: Endpoints para integração com outros sistemas

## 📋 Questionário

O sistema coleta informações através de 8 perguntas principais:

1. **Marca/Modelo Específico**: Preferências por marca ou modelo
2. **Urgência da Compra**: Imediata, 30 dias, 60 dias ou mais
3. **Localização**: Estado para encontrar opções próximas
4. **Uso Principal**: Urbano, viagem, trabalho, família, esportivo, aventura
5. **Necessidades Familiares**: Número de pessoas, crianças, animais
6. **Espaço e Potência**: Necessidades de carga e performance
7. **Prioridades**: Economia, conforto, segurança, performance ou equilíbrio
8. **Orçamento**: Faixa de investimento desejada

## 🛠 Tecnologias Utilizadas

- **Backend**: Python 3.8+, FastAPI, LangGraph, LangChain
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: PostgreSQL com SQLAlchemy
- **Processamento**: Algoritmos de matching e scoring personalizado
- **Dados**: Base real com 137+ carros do mercado brasileiro

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Docker (para PostgreSQL)
- PostgreSQL rodando na porta 5432

### Passo a passo

1. **Clone ou baixe o projeto**
```bash
cd facilIAuto
```

2. **Configure o PostgreSQL (se necessário)**
```bash
# Caso não tenha o banco rodando, use Docker:
docker run --name carencia_postgres \
  -e POSTGRES_DB=carencia_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:16
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Teste a conexão com o banco**
```bash
python teste_postgresql.py
```

5. **Execute a aplicação**
```bash
python main.py
```

4. **Acesse a aplicação**
- Interface web: http://localhost:8000
- Documentação da API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 🎮 Como Usar

### Interface Web

1. Acesse http://localhost:8000
2. Responda às 8 perguntas do questionário
3. Clique em "Encontrar Carros"
4. Veja suas recomendações personalizadas com:
   - Score de compatibilidade
   - Razões da recomendação
   - Pontos fortes do veículo
   - Considerações importantes

### API REST

#### Buscar Carros
```bash
POST /buscar-carros
Content-Type: application/json

{
  "marca_preferida": "Toyota",
  "modelo_preferido": null,
  "urgencia": "imediata",
  "regiao": "SP",
  "uso_principal": ["urbano", "familia"],
  "pessoas_transportar": 4,
  "criancas": true,
  "animais": false,
  "espaco_carga": "medio",
  "potencia_desejada": "media",
  "prioridade": "seguranca",
  "orcamento_min": 80000,
  "orcamento_max": 150000
}
```

#### Listar Todos os Carros
```bash
GET /carros
```

#### Obter Carro Específico
```bash
GET /carros/{id}
```

## 🧠 Como Funciona o LangGraph

O sistema usa LangGraph para criar um fluxo de processamento em etapas:

```
Entrada (Questionário)
        ↓
    Filtros Básicos (orçamento, região, urgência)
        ↓
    Cálculo de Scores (compatibilidade baseada no perfil)
        ↓
    Geração de Recomendações (top 5 carros)
        ↓
    Resumo do Perfil (análise do usuário)
        ↓
    Sugestões Gerais (dicas personalizadas)
        ↓
    Resposta Final
```

### Critérios de Score

- **Marca/Modelo Preferido**: 20% do score
- **Uso Principal**: 15% do score
- **Capacidade**: 10% do score
- **Espaço de Carga**: 10% do score
- **Potência**: 10% do score
- **Prioridade Principal**: 15% do score
- **Preço no Orçamento**: 10% do score
- **Adequação Familiar**: 10% do score

## 🗄️ Configuração do Banco de Dados

### Conexão PostgreSQL

O sistema está configurado para conectar automaticamente ao PostgreSQL com:

```
Host: localhost
Port: 5432
Database: carencia_db
User: postgres
Password: postgres
```

### Variáveis de Ambiente (Opcional)

Você pode personalizar a conexão através de variáveis de ambiente:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=carencia_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_SCHEMA=public
```

## 📊 Base de Dados

O sistema utiliza **dados reais** do PostgreSQL com **137+ carros** do mercado brasileiro, incluindo:

- **Marcas**: Hyundai, Fiat, Renault, Chevrolet, KIA, Ford, Nissan, Mitsubishi, Volkswagen, Honda, Toyota, Audi
- **Categorias**: Hatches, Sedans, SUVs, Picapes, Crossovers
- **Faixa de preços**: R$ 50.000 a R$ 200.000+
- **Anos**: 2020 a 2024

Cada veículo possui dados completos:
- Preço, quilometragem, combustível
- Fotos, descrição, opcionais
- Informações técnicas detalhadas
- Status de disponibilidade

## 🔧 Customização

### Adicionando Novos Carros

Edite o arquivo `app/data/carros.py` e adicione novos carros ao array `carros_database`:

```python
{
    "id": 11,
    "marca": "Marca",
    "modelo": "Modelo",
    "ano": 2023,
    "preco": 100000,
    "categoria": "hatch",
    "consumo": 12.0,
    "potencia": 120,
    "capacidade_pessoas": 5,
    "porta_malas": 300,
    "combustivel": "flex",
    "cambio": "manual",
    "uso_recomendado": ["urbano"],
    "familia": "pequeno",
    "seguranca": 4,
    "conforto": 3,
    "economia": 5,
    "performance": 3,
    "disponibilidade": "imediata",
    "regiao": ["SP", "RJ"]
}
```

### Modificando Critérios de Score

Edite as funções em `app/busca_inteligente.py` para ajustar os pesos e critérios de recomendação.

## 📝 Estrutura do Projeto

```
facilIAuto/
├── app/
│   ├── __init__.py
│   ├── api.py              # API FastAPI
│   ├── models.py           # Modelos Pydantic
│   ├── busca_inteligente.py # Lógica LangGraph
│   ├── config.py           # Configurações do banco
│   ├── database.py         # Acesso ao PostgreSQL
│   └── data/
│       └── carros.py       # Base de dados simulada (backup)
├── main.py                 # Entrada da aplicação
├── requirements.txt        # Dependências Python
├── teste_postgresql.py     # Teste de integração PostgreSQL
├── teste_conexao.py        # Teste de conexão básica
├── explorar_banco.py       # Explorador de estrutura do banco
└── README.md              # Documentação
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🆘 Suporte

Se encontrar problemas ou tiver dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Confirme que está usando Python 3.8+
3. Tente executar `pip install -r requirements.txt` novamente
4. Verifique se a porta 8000 está disponível

---

Desenvolvido com ❤️ para facilitar a escolha do carro ideal! 