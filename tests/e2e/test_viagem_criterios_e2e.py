"""
Testes E2E específicos para novos critérios do perfil VIAGEM
Seguindo metodologia XP com TDD e validação completa
"""
import pytest

from app.models import QuestionarioBusca
from app.uso_principal_processor import UsoMatcher


@pytest.mark.asyncio
@pytest.mark.xp_methodology
@pytest.mark.tdd
@pytest.mark.viagem_criterios
class TestViagemCriteriosE2E:
    """Testes E2E para novos critérios de viagem implementados"""

    @pytest.fixture
    def questionario_viagem_completo(self):
        """Questionário completo para viagem com todos os novos critérios"""
        return QuestionarioBusca(
            marca_preferida="Honda",
            modelo_especifico="CR-V",
            urgencia="ate_15_dias",
            regiao="SP",
            uso_principal=["viagem"],
            pessoas_transportar=5,
            espaco_carga="muito",
            potencia_desejada="media",
            prioridade="conforto",
        )

    @pytest.fixture
    def carro_ideal_viagem(self):
        """Carro ideal para viagem com todos os critérios novos"""
        return {
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
                "piloto_automatico",
            ],
            "combustivel": "flex",
            "seguranca": 5,
            "revisado": True,
            "km": 45000,
        }

    async def test_conforto_viagens_longas_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E critério conforto_viagens_longas (20%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Verifica se conforto é avaliado corretamente
        conforto_razoes = [r for r in razoes if "conforto" in r.lower()]
        assert len(conforto_razoes) >= 1, "Deve ter pelo menos 1 razão de conforto"

        # Verifica elementos específicos do conforto
        razoes_str = " ".join(razoes).lower()
        assert any(
            palavra in razoes_str for palavra in ["bancos", "climatização", "ergonomia"]
        )

    async def test_desempenho_seguranca_estrada_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E critério desempenho_seguranca_estrada (20%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Verifica se desempenho/segurança é avaliado
        desempenho_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["desempenho", "estrada", "motor", "potente"]
            )
        ]
        assert len(desempenho_razoes) >= 1, "Deve ter pelo menos 1 razão de desempenho"

        # Motor 1.8 deve ser considerado adequado
        assert carro_ideal_viagem["cilindrada"] >= 1.4

    async def test_espaco_capacidade_carga_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E critério espaco_capacidade_carga (15%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Verifica avaliação de espaço/capacidade
        espaco_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["capacidade", "espaço", "pessoas", "porta-malas"]
            )
        ]
        assert len(espaco_razoes) >= 1, "Deve ter pelo menos 1 razão de espaço"

        # SUV deve ser categoria ideal
        assert carro_ideal_viagem["categoria"] == "SUV"
        assert carro_ideal_viagem["porta_malas_litros"] >= 400

    async def test_economia_combustivel_estrada_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E critério economia_combustivel_estrada (15%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Verifica economia específica para estrada
        economia_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower() for palavra in ["economia", "consumo", "estrada"]
            )
        ]
        assert len(economia_razoes) >= 1, "Deve ter pelo menos 1 razão de economia"

        # Consumo deve ser adequado para estrada
        assert carro_ideal_viagem["consumo_estrada"] >= 10

    async def test_tecnologia_entretenimento_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E critério tecnologia_entretenimento (10%)"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Verifica tecnologia/entretenimento
        tech_razoes = [
            r
            for r in razoes
            if any(
                palavra in r.lower()
                for palavra in ["tecnologia", "gps", "entretenimento", "navegação"]
            )
        ]
        assert len(tech_razoes) >= 1, "Deve ter pelo menos 1 razão de tecnologia"

        # Deve ter tecnologias específicas para viagem
        opcionais = carro_ideal_viagem["opcionais"]
        tech_items = ["gps_integrado", "android_auto"]
        assert any(item in opcionais for item in tech_items)

    async def test_score_total_viagem_meta_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E que score total atinge meta de 75%"""
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(
            questionario_viagem_completo, carro_ideal_viagem
        )

        # Meta: ≥75% (18.75/25)
        assert score >= 18.75, f"Score {score:.2f} deve ser ≥18.75 (75%)"

        # Deve ter múltiplos critérios avaliados
        assert len(razoes) >= 6, f"Deve ter ≥6 razões, tem {len(razoes)}"
        assert len(pontos) >= 6, f"Deve ter ≥6 pontos fortes, tem {len(pontos)}"

    async def test_sugestoes_especificas_viagem_e2e(self, questionario_viagem_completo):
        """Testa E2E sugestões específicas para viagem"""
        sugestoes = UsoMatcher.gerar_sugestoes_uso(questionario_viagem_completo)

        # Deve ter sugestões específicas para viagem
        viagem_sugs = [
            s
            for s in sugestoes
            if any(
                w in s.lower()
                for w in [
                    "viagem",
                    "estrada",
                    "conforto",
                    "turismo",
                    "road",
                    "gps",
                    "climatiz",
                ]
            )
        ]

        assert (
            len(viagem_sugs) >= 8
        ), f"Deve ter ≥8 sugestões viagem, tem {len(viagem_sugs)}"

        # Verificar subsegmentos específicos
        subsegmentos = ["turismo", "trabalho", "road", "família"]
        for seg in subsegmentos:
            seg_found = any(seg.lower() in sug.lower() for sug in viagem_sugs)
            assert seg_found, f"Subsegmento '{seg}' não encontrado nas sugestões"

    async def test_pesos_criterios_viagem_100_porcento_e2e(self):
        """Testa E2E que pesos dos critérios somam exatamente 100%"""
        criterios = UsoMatcher.get_criterios_por_uso("viagem")

        # Verifica todos os critérios implementados
        criterios_esperados = [
            "conforto_viagens_longas",
            "desempenho_seguranca_estrada",
            "espaco_capacidade_carga",
            "economia_combustivel_estrada",
            "tecnologia_entretenimento",
            "confiabilidade_viagem",
            "facilidade_dirigibilidade",
            "sustentabilidade_viagem",
        ]

        for criterio in criterios_esperados:
            assert criterio in criterios, f"Critério '{criterio}' não encontrado"

        # Soma deve ser exatamente 100%
        total_peso = sum(c["peso"] for c in criterios.values())
        assert total_peso == 100, f"Peso total deve ser 100%, é {total_peso}%"

    async def test_subsegmentos_boost_viagem_e2e(
        self, questionario_viagem_completo, carro_ideal_viagem
    ):
        """Testa E2E aplicação de boost por subsegmentos"""
        # Testa diferentes subsegmentos implícitos

        # Turismo (conforto + entretenimento)
        q_turismo = questionario_viagem_completo.model_copy()
        q_turismo.prioridade = "conforto"

        score_turismo, _, _ = UsoMatcher.calcular_score_uso_principal(
            q_turismo, carro_ideal_viagem
        )

        # Road trip (potência + segurança)
        q_roadtrip = questionario_viagem_completo.model_copy()
        q_roadtrip.potencia_desejada = "alta"

        score_roadtrip, _, _ = UsoMatcher.calcular_score_uso_principal(
            q_roadtrip, carro_ideal_viagem
        )

        # Ambos devem ter scores altos
        assert (
            score_turismo >= 18.0
        ), f"Score turismo deve ser alto: {score_turismo:.2f}"
        assert (
            score_roadtrip >= 18.0
        ), f"Score road trip deve ser alto: {score_roadtrip:.2f}"

    async def test_descricao_viagem_atualizada_e2e(self):
        """Testa E2E que descrição do perfil viagem foi atualizada"""
        descricao = UsoMatcher.get_descricao_uso("viagem")

        # Deve conter elementos específicos implementados
        elementos = [
            "conforto",
            "desempenho",
            "espaço",
            "economia",
            "tecnologia",
            "subsegmentos",
        ]

        for elemento in elementos:
            assert (
                elemento.lower() in descricao.lower()
            ), f"Elemento '{elemento}' não encontrado na descrição"

        # Deve mencionar valores específicos
        assert "1.4L" in descricao or "≥1.4L" in descricao
        assert "400L" in descricao or "≥400L" in descricao
        assert "10 km/l" in descricao or "≥10 km/l" in descricao


@pytest.mark.asyncio
@pytest.mark.performance
@pytest.mark.viagem_criterios
async def test_performance_criterios_viagem_e2e():
    """Testa performance dos novos critérios de viagem"""
    import time

    q = QuestionarioBusca(
        marca_preferida="Honda",
        modelo_especifico="CR-V",
        urgencia="ate_15_dias",
        regiao="SP",
        uso_principal=["viagem"],
        pessoas_transportar=5,
        espaco_carga="muito",
        potencia_desejada="media",
        prioridade="conforto",
    )

    carro = {
        "marca": "Honda",
        "modelo": "CR-V",
        "categoria": "SUV",
        "cilindrada": 1.8,
        "consumo_estrada": 12,
        "porta_malas_litros": 480,
        "pessoas_transportar": 5,
        "combustivel": "flex",
        "seguranca": 5,
        "revisado": True,
        "km": 45000,
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
    }

    # Teste de performance
    start_time = time.time()

    for _ in range(10):
        score, razoes, pontos = UsoMatcher.calcular_score_uso_principal(q, carro)

    elapsed = time.time() - start_time
    avg_time = elapsed / 10

    # Deve processar em menos de 50ms em média
    assert avg_time < 0.05, f"Performance muito lenta: {avg_time:.3f}s por cálculo"
    assert score > 17.5, f"Score deve ser alto: {score:.2f}"
