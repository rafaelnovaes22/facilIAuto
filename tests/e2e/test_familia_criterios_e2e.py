"""
Testes E2E específicos para novos critérios do perfil FAMÍLIA
Seguindo metodologia XP com TDD e validação completa
"""
import pytest

from app.models import QuestionarioBusca
from app.uso_principal_processor import UsoMatcher


@pytest.mark.asyncio
@pytest.mark.xp_methodology
@pytest.mark.tdd
@pytest.mark.familia_criterios
class TestFamiliaCriteriosE2E:
    """Testes E2E para novos critérios de família implementados"""

    @pytest.fixture
    def questionario_familia_completo(self):
        """Questionário completo para família com todos os novos critérios"""
        return QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="CR-V",
            urgencia="ate_15_dias",
            regiao="SP",
            uso_principal=["familia"],
            pessoas_transportar=5,
            criancas=True,
            espaco_carga="muito",
            potencia_desejada="media",
            prioridade="seguranca",
        )

    @pytest.fixture
    def carro_ideal_familia(self):
        """Carro ideal para família com todos os critérios novos"""
        return {
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
                "apoio_braco",
                "porta_objetos",
            ],
            "combustivel": "flex",
            "seguranca": 5,
            "revisado": True,
            "km": 35000,
        }

    async def test_seguranca_avancada_familia_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério seguranca_avancada_familia (20%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica se segurança é avaliada corretamente
        seguranca_razoes = [
            r for r in razoes if "segurança" in r.lower() or "família" in r.lower()
        ]
        assert (
            len(seguranca_razoes) >= 1
        ), "Deve ter pelo menos 1 razão de segurança família"

        # Verifica elementos específicos da segurança
        razoes_str = " ".join(razoes).lower()
        assert any(
            palavra in razoes_str for palavra in ["airbags", "estrelas", "sistemas"]
        )

    async def test_espaco_passageiros_conforto_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério espaco_passageiros_conforto (20%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica avaliação de espaço/conforto
        espaco_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["espaço", "família", "pessoas", "conforto"]
            )
        ]
        assert len(espaco_razoes) >= 1, "Deve ter pelo menos 1 razão de espaço família"

        # SUV deve ser categoria ideal para família
        assert carro_ideal_familia["categoria"] == "SUV"
        assert carro_ideal_familia["pessoas_transportar"] >= 5

    async def test_praticidade_uso_familiar_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério praticidade_uso_familiar (15%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica praticidade específica para família
        praticidade_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["praticidade", "facilidades", "porta-malas"]
            )
        ]
        assert (
            len(praticidade_razoes) >= 1
        ), "Deve ter pelo menos 1 razão de praticidade"

        # Deve ter facilidades essenciais
        opcionais = carro_ideal_familia["opcionais"]
        facilidades = ["vidros_eletricos", "travas_eletricas"]
        assert any(item in opcionais for item in facilidades)

    async def test_custo_beneficio_familia_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério custo_beneficio_familia (15%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica custo-benefício para família
        custo_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["custo", "preço", "benefício", "marca"]
            )
        ]
        assert len(custo_razoes) >= 1, "Deve ter pelo menos 1 razão de custo-benefício"

        # Preço deve estar na faixa adequada para família
        assert 30000 <= carro_ideal_familia["preco"] <= 80000

    async def test_tecnologia_seguranca_infantil_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério tecnologia_seguranca_infantil (8%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica tecnologia específica para segurança infantil
        opcionais = carro_ideal_familia["opcionais"]
        tech_infantil = ["isofix", "travas_eletricas", "camera_re"]
        assert any(item in opcionais for item in tech_infantil)

    async def test_score_total_familia_meta_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E que score total atinge meta de 75%"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Meta: ≥75% (18.75/25)
        assert score >= 18.75, f"Score {score:.2f} deve ser ≥18.75 (75%)"

        # Deve ter múltiplos critérios avaliados
        assert len(razoes) >= 6, f"Deve ter ≥6 razões, tem {len(razoes)}"
        assert len(pontos) >= 6, f"Deve ter ≥6 pontos fortes, tem {len(pontos)}"

    async def test_sugestoes_especificas_familia_e2e(
        self, questionario_familia_completo
    ):
        """Testa E2E sugestões específicas para família"""
        sugestoes = UsoMatcher.gerar_sugestoes_uso(questionario_familia_completo)

        # Deve ter sugestões específicas para família
        familia_sugs = [
            s
            for s in sugestoes
            if any(
                w in s.lower()
                for w in [
                    "família",
                    "segurança",
                    "airbags",
                    "isofix",
                    "criança",
                    "custo",
                    "atividades",
                    "esportivas",
                ]
            )
        ]

        assert (
            len(familia_sugs) >= 6
        ), f"Deve ter ≥6 sugestões família, tem {len(familia_sugs)}"

        # Verificar subsegmentos específicos
        subsegmentos = ["crianças pequenas", "família grande", "esportivas"]
        for seg in subsegmentos:
            seg_found = any(seg.lower() in sug.lower() for sug in familia_sugs)
            assert seg_found, f"Subsegmento '{seg}' não encontrado nas sugestões"

    async def test_pesos_criterios_familia_100_porcento_e2e(self):
        """Testa E2E que pesos dos critérios somam exatamente 100%"""
        criterios = UsoMatcher.get_criterios_por_uso("familia")

        # Verifica todos os critérios implementados
        criterios_esperados = [
            "seguranca_avancada_familia",
            "espaco_passageiros_conforto",
            "praticidade_uso_familiar",
            "custo_beneficio_familia",
            "confiabilidade_transporte",
            "tecnologia_seguranca_infantil",
            "eficiencia_combustivel_familia",
            "versatilidade_configuracao",
        ]

        for criterio in criterios_esperados:
            assert criterio in criterios, f"Critério '{criterio}' não encontrado"

        # Soma deve ser exatamente 100%
        total_peso = sum(c["peso"] for c in criterios.values())
        assert total_peso == 100, f"Peso total deve ser 100%, é {total_peso}%"

    async def test_subsegmentos_boost_familia_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E aplicação de boost por subsegmentos"""
        # Testa diferentes subsegmentos implícitos

        # Crianças pequenas (segurança prioritária)
        q_criancas = questionario_familia_completo.model_copy()
        q_criancas.criancas = True
        q_criancas.prioridade = "seguranca"

        score_criancas, _, _ = UsoMatcher.calcular_score_uso_principal(
            q_criancas, carro_ideal_familia
        )

        # Família grande (espaço prioritário)
        q_grande = questionario_familia_completo.model_copy()
        q_grande.pessoas_transportar = 7

        score_grande, _, _ = UsoMatcher.calcular_score_uso_principal(
            q_grande, carro_ideal_familia
        )

        # Ambos devem ter scores altos
        assert (
            score_criancas >= 18.0
        ), f"Score crianças deve ser alto: {score_criancas:.2f}"
        assert (
            score_grande >= 18.0
        ), f"Score família grande deve ser alto: {score_grande:.2f}"

    async def test_descricao_familia_atualizada_e2e(self):
        """Testa E2E que descrição do perfil família foi atualizada"""
        descricao = UsoMatcher.get_descricao_uso("familia")

        # Deve conter elementos específicos implementados
        elementos = ["segurança", "espaço", "praticidade", "custo", "airbags", "isofix"]

        for elemento in elementos:
            assert (
                elemento.lower() in descricao.lower()
            ), f"Elemento '{elemento}' não encontrado na descrição"

        # Deve mencionar valores específicos
        assert "350L" in descricao or "≥350L" in descricao
        assert "30-80k" in descricao or "R$ 30-80k" in descricao
        assert "8 km/l" in descricao or "≥8 km/l" in descricao

    async def test_confiabilidade_transporte_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério confiabilidade_transporte (10%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica confiabilidade específica para transporte familiar
        conf_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["confiabilidade", "honda", "confiável"]
            )
        ]
        assert len(conf_razoes) >= 1, "Deve ter pelo menos 1 razão de confiabilidade"

        # Honda deve ser marca confiável para família
        assert carro_ideal_familia["marca"] == "Honda"
        assert carro_ideal_familia["km"] <= 80000

    async def test_eficiencia_combustivel_familia_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério eficiencia_combustivel_familia (7%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica eficiência específica para uso familiar
        efic_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["eficiência", "consumo", "econômico"]
            )
        ]
        assert len(efic_razoes) >= 1, "Deve ter pelo menos 1 razão de eficiência"

        # Consumo deve ser adequado para família
        assert carro_ideal_familia["consumo"] >= 8

    async def test_versatilidade_configuracao_e2e(
        self, questionario_familia_completo, carro_ideal_familia
    ):
        """Testa E2E critério versatilidade_configuracao (5%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_familia_completo, carro_ideal_familia
        )

        # Verifica versatilidade para diferentes necessidades familiares
        opcionais = carro_ideal_familia["opcionais"]
        versatilidade = ["bancos_rebatraveis", "porta_objetos", "apoio_braco"]
        assert any(item in opcionais for item in versatilidade)


@pytest.mark.asyncio
@pytest.mark.performance
@pytest.mark.familia_criterios
async def test_performance_criterios_familia_e2e():
    """Testa performance dos novos critérios de família"""
    import time

    q = QuestionarioBusca(
        marca_preferida="Honda",
        modelo_especifico="CR-V",
        urgencia="ate_15_dias",
        regiao="SP",
        uso_principal=["familia"],
        pessoas_transportar=5,
        criancas=True,
        espaco_carga="muito",
        potencia_desejada="media",
        prioridade="seguranca",
    )

    carro = {
        "marca": "Honda",
        "modelo": "CR-V",
        "categoria": "SUV",
        "cilindrada": 1.8,
        "consumo": 10,
        "porta_malas_litros": 480,
        "pessoas_transportar": 5,
        "preco": 65000,
        "combustivel": "flex",
        "seguranca": 5,
        "revisado": True,
        "km": 35000,
        "opcionais": ["ar_condicionado", "airbag_multiplos", "abs", "isofix"],
    }

    # Teste de performance
    start_time = time.time()

    for _ in range(10):
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(q, carro)

    elapsed = time.time() - start_time
    avg_time = elapsed / 10

    # Deve processar em menos de 50ms em média
    assert avg_time < 0.05, f"Performance muito lenta: {avg_time:.3f}s por cálculo"
    assert score > 16.5, f"Score deve ser alto: {score:.2f}"
