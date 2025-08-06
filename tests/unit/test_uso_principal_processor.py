"""
Testes unitários para o processador de uso principal do veículo
"""

import pytest

from app.models import QuestionarioBusca
from app.uso_principal_processor import UsoMatcher


class TestUsoMatcher:
    """Testes para a classe UsoMatcher"""

    def test_calcular_score_uso_urbano(self):
        """Testa o cálculo de score para urbano com novos critérios"""
        questionario = QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="Fit",
            urgencia="sem_pressa",
            regiao="São Paulo",
            uso_principal=["urbano"],
            pessoas_transportar=2,
            espaco_carga="pequeno",
            potencia_desejada="economica",
            prioridade="economia",
        )

        # Carro ideal para urbano com novos critérios
        carro = {
            "id": "1",
            "marca": "Honda",
            "modelo": "Fit",
            "categoria": "Hatch",
            "cilindrada": 1.0,
            "consumo_cidade": 15,
            "comprimento": 3.9,
            "portas": 4,
            "porta_malas_litros": 320,
            "opcionais": [
                "central_multimidia",
                "bluetooth",
                "usb",
                "abs",
                "airbag_duplo",
                "ar_condicionado",
            ],
            "combustivel": "flex",
            "seguranca": 4,
            "ano": 2020,
            "preco": 45000,
        }

        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(
            questionario, carro
        )

        # Score deve ser significativamente melhor que antes (>50%)
        assert score > 12.5  # Mais de 50% do total (25)
        assert len(razoes) >= 6  # Múltiplos critérios
        assert len(pontos_fortes) >= 6
        assert any("economia" in razao.lower() for razao in razoes)
        assert any(
            "manobra" in razao.lower() or "compacto" in razao.lower()
            for razao in razoes
        )
        assert any("tecnologia" in razao.lower() for razao in razoes)

    def test_calcular_score_uso_viagem(self):
        """Testa o cálculo de score para viagem com novos critérios"""
        questionario = QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="CR-V",
            urgencia="sem_pressa",
            regiao="Rio de Janeiro",
            uso_principal=["viagem"],
            pessoas_transportar=5,
            espaco_carga="muito",
            potencia_desejada="media",
            prioridade="conforto",
        )

        # Carro ideal para viagem com novos critérios
        carro = {
            "id": "2",
            "marca": "Honda",
            "modelo": "CR-V",
            "categoria": "SUV",
            "cilindrada": 1.8,
            "consumo_estrada": 12,
            "porta_malas_litros": 480,
            "pessoas_transportar": 5,
            "opcionais": [
                "ar_condicionado",
                "climatizador_automatico",
                "bancos_couro",
                "gps_integrado",
                "android_auto",
                "controle_estabilidade",
                "abs",
                "airbag_multiplos",
                "direcao_assistida",
            ],
            "combustivel": "flex",
            "seguranca": 5,
            "revisado": True,
            "km": 45000,
            "ano": 2021,
            "preco": 80000,
        }

        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(
            questionario, carro
        )

        # Score deve ser significativamente melhor que antes (>75%)
        assert score > 18.75  # Mais de 75% do total (25)
        assert len(razoes) >= 6  # Múltiplos critérios
        assert len(pontos_fortes) >= 6
        assert any("conforto" in razao.lower() for razao in razoes)
        assert any(
            "desempenho" in razao.lower() or "estrada" in razao.lower()
            for razao in razoes
        )
        assert any(
            "tecnologia" in razao.lower() or "entretenimento" in razao.lower()
            for razao in razoes
        )

    def test_calcular_score_uso_trabalho(self):
        """Testa o cálculo de score para trabalho/negócios"""
        questionario = QuestionarioBusca(
            marca_preferida="Chevrolet",
            modelo_especifico="Onix",
            urgencia="esta_semana",
            regiao="São Paulo",
            uso_principal=["trabalho"],
            pessoas_transportar=4,
            espaco_carga="medio",
            potencia_desejada="economica",
            prioridade="economia",
        )

        # Carro ideal para motorista de app
        carro = {
            "id": "3",
            "marca": "Chevrolet",
            "modelo": "Onix",
            "categoria": "Hatch",
            "consumo_cidade": 13,
            "cilindrada": 1.4,
            "km": 45000,
            "ano": 2018,
            "portas": 4,
            "opcionais": ["ar_condicionado", "direcao_assistida", "conectividade"],
            "combustivel": "flex",
            "concessionaria": True,
            "revisado": True,
            "preco": 45000,
        }

        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(
            questionario, carro
        )

        # Veículo deve ter score alto para trabalho
        assert score > 0
        assert any("trabalho" in razao.lower() for razao in razoes)
        assert any(
            "economia" in ponto.lower()
            or "profissional" in ponto.lower()
            or "plataformas" in ponto.lower()
            for ponto in pontos_fortes
        )

    def test_calcular_score_uso_familia(self):
        """Testa o cálculo de score para família com novos critérios"""
        questionario = QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="CR-V",
            urgencia="ate_15_dias",
            regiao="Salvador",
            uso_principal=["familia"],
            pessoas_transportar=5,
            criancas=True,
            espaco_carga="muito",
            potencia_desejada="media",
            prioridade="seguranca",
        )

        # Carro ideal para família com novos critérios
        carro = {
            "id": "4",
            "marca": "Honda",
            "modelo": "CR-V",
            "categoria": "SUV",
            "cilindrada": 1.8,
            "consumo": 10,
            "porta_malas_litros": 480,
            "pessoas_transportar": 5,
            "preco": 65000,
            "opcionais": [
                "ar_condicionado",
                "airbag_multiplos",
                "abs",
                "controle_estabilidade",
                "vidros_eletricos",
                "travas_eletricas",
                "isofix",
                "camera_re",
                "bancos_rebatraveis",
            ],
            "combustivel": "flex",
            "seguranca": 5,
            "revisado": True,
            "km": 35000,
            "ano": 2020,
        }

        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(
            questionario, carro
        )

        # Score deve ser significativamente melhor que antes (>75%)
        assert score > 18.75  # Mais de 75% do total (25)
        assert len(razoes) >= 6  # Múltiplos critérios
        assert len(pontos_fortes) >= 6
        assert any("segurança" in razao.lower() for razao in razoes)
        assert any(
            "espaço" in razao.lower() or "família" in razao.lower() for razao in razoes
        )
        assert any(
            "praticidade" in razao.lower() or "custo" in razao.lower()
            for razao in razoes
        )

    def test_uso_multiplo(self):
        """Testa o cálculo de score para múltiplos usos"""
        questionario = QuestionarioBusca(
            marca_preferida="Volkswagen",
            modelo_especifico="Tiguan",
            urgencia="sem_pressa",
            regiao="Porto Alegre",
            uso_principal=["urbano", "familia", "viagem"],
            pessoas_transportar=5,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="equilibrio",
        )

        carro = {
            "id": "5",
            "marca": "Volkswagen",
            "modelo": "Tiguan",
            "categoria": "SUV Médio",
            "capacidade_pessoas": 5,
            "seguranca": 5,
            "espaco_carga": "medio",
            "potencia_desejada": "media",
            "opcionais": ["Conectividade", "Ar condicionado", "Sensores"],
            "ano": 2021,
            "preco": 90000,
        }

        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(
            questionario, carro
        )

        # Deve ter score dividido entre os usos
        assert score > 0
        assert len(razoes) >= 3  # Pelo menos uma razão por uso

        # Deve mencionar diferentes tipos de uso
        razoes_texto = " ".join(razoes).lower()
        assert (
            "urbano" in razoes_texto
            or "família" in razoes_texto
            or "viagem" in razoes_texto
        )

    def test_gerar_sugestoes_uso(self):
        """Testa a geração de sugestões baseadas no uso"""
        questionario = QuestionarioBusca(
            marca_preferida="Nissan",
            modelo_especifico="March",
            urgencia="hoje_amanha",
            regiao="Recife",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            espaco_carga="pouco",
            potencia_desejada="economica",
            prioridade="economia",
        )

        sugestoes = UsoMatcher.gerar_sugestoes_uso(questionario)

        assert len(sugestoes) > 0
        assert any(
            any(
                word in sugestao.lower()
                for word in ["cidade", "compacto", "economia", "estacion"]
            )
            for sugestao in sugestoes
        )
        # Não deve ter duplicatas
        assert len(sugestoes) == len(set(sugestoes))

    def test_get_criterios_por_uso(self):
        """Testa a obtenção de critérios por tipo de uso"""
        criterios_urbano = UsoMatcher.get_criterios_por_uso("urbano")
        criterios_viagem = UsoMatcher.get_criterios_por_uso("trabalho")
        criterios_invalido = UsoMatcher.get_criterios_por_uso("invalido")

        assert len(criterios_urbano) > 0
        assert len(criterios_viagem) > 0
        assert len(criterios_invalido) == 0

        # Verificar estrutura dos novos critérios urbanos
        assert "economia_combustivel_urbana" in criterios_urbano
        assert "peso" in criterios_urbano["economia_combustivel_urbana"]

        # Verificar novos critérios de trabalho/negócios
        criterios_trabalho = UsoMatcher.get_criterios_por_uso("trabalho")
        assert "economia_combustivel" in criterios_trabalho
        assert "confiabilidade" in criterios_trabalho
        assert "aceitacao_plataformas" in criterios_trabalho
        assert criterios_trabalho["economia_combustivel"]["peso"] == 20

        # Verificar novos critérios urbanos
        criterios_urbano_novo = UsoMatcher.get_criterios_por_uso("urbano")
        assert "economia_combustivel_urbana" in criterios_urbano_novo
        assert "facilidade_manobra" in criterios_urbano_novo
        assert "tecnologia_conectividade" in criterios_urbano_novo
        assert "seguranca_urbana" in criterios_urbano_novo
        assert criterios_urbano_novo["economia_combustivel_urbana"]["peso"] == 20
        assert criterios_urbano_novo["facilidade_manobra"]["peso"] == 20

        # Verificar que peso total urbano é 100%
        total_peso_urbano = sum(c["peso"] for c in criterios_urbano_novo.values())
        assert total_peso_urbano == 100

        # Verificar novos critérios de viagem
        criterios_viagem_novo = UsoMatcher.get_criterios_por_uso("viagem")
        assert "conforto_viagens_longas" in criterios_viagem_novo
        assert "desempenho_seguranca_estrada" in criterios_viagem_novo
        assert "espaco_capacidade_carga" in criterios_viagem_novo
        assert "economia_combustivel_estrada" in criterios_viagem_novo
        assert "tecnologia_entretenimento" in criterios_viagem_novo
        assert criterios_viagem_novo["conforto_viagens_longas"]["peso"] == 20
        assert criterios_viagem_novo["desempenho_seguranca_estrada"]["peso"] == 20

        # Verificar que peso total viagem é 100%
        total_peso_viagem = sum(c["peso"] for c in criterios_viagem_novo.values())
        assert total_peso_viagem == 100

        # Verificar novos critérios de família
        criterios_familia_novo = UsoMatcher.get_criterios_por_uso("familia")
        assert "seguranca_avancada_familia" in criterios_familia_novo
        assert "espaco_passageiros_conforto" in criterios_familia_novo
        assert "praticidade_uso_familiar" in criterios_familia_novo
        assert "custo_beneficio_familia" in criterios_familia_novo
        assert "tecnologia_seguranca_infantil" in criterios_familia_novo
        assert criterios_familia_novo["seguranca_avancada_familia"]["peso"] == 20
        assert criterios_familia_novo["espaco_passageiros_conforto"]["peso"] == 20

        # Verificar que peso total família é 100%
        total_peso_familia = sum(c["peso"] for c in criterios_familia_novo.values())
        assert total_peso_familia == 100

    def test_get_descricao_uso(self):
        """Testa a obtenção de descrições de uso"""
        desc_urbano = UsoMatcher.get_descricao_uso("urbano")
        desc_familia = UsoMatcher.get_descricao_uso("familia")
        desc_invalido = UsoMatcher.get_descricao_uso("invalido")

        assert "urbano" in desc_urbano.lower()
        assert "família" in desc_familia.lower() or "familiar" in desc_familia.lower()
        assert desc_invalido == "invalido"  # Fallback para o próprio termo

    def test_peso_uso_principal_limite(self):
        """Testa se o peso total do uso principal respeita o limite"""
        questionario = QuestionarioBusca(
            marca_preferida="BMW",
            modelo_especifico="X1",
            urgencia="sem_pressa",
            regiao="Curitiba",
            uso_principal=["urbano", "viagem", "trabalho", "familia"],  # Todos os usos
            pessoas_transportar=5,
            espaco_carga="medio",
            potencia_desejada="alta",
            prioridade="performance",
        )

        carro = {
            "id": "6",
            "marca": "BMW",
            "modelo": "X1",
            "categoria": "SUV",
            "capacidade_pessoas": 5,
            "seguranca": 5,
            "espaco_carga": "medio",
            "potencia_desejada": "alta",
            "opcionais": ["Conectividade premium", "Ar condicionado", "Couro"],
            "ano": 2022,
            "preco": 150000,
        }

        score, _, _ = UsoMatcher.calcular_score_uso_principal(questionario, carro)

        # Score não deve exceder o peso máximo configurado
        assert score <= UsoMatcher.PESO_USO_PRINCIPAL
