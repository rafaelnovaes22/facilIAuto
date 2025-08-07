"""
Processador de Uso Principal - Versão Refatorada
Avalia compatibilidade de veículos com diferentes perfis de uso
"""

from typing import Any, Dict, List, Optional, Tuple

from app.models import CarroRecomendacao, QuestionarioBusca

# Peso do score de uso principal na pontuação final
PESO_USO_PRINCIPAL = 25.0


class UsoMatcherRefactored:
    """Matcher para avaliar compatibilidade com uso principal - REFATORADO"""

    # Critérios e pesos para cada tipo de uso
    CRITERIOS_USO = {
        "urbano": {
            "economia_combustivel_urbana": {"peso": 20},
            "facilidade_manobra": {"peso": 15},
            "tecnologia_conectividade": {"peso": 15},
            "seguranca_urbana": {"peso": 12},
            "custo_manutencao_urbana": {"peso": 10},
            "praticidade_urbana": {"peso": 10},
            "conforto_urbano": {"peso": 10},
            "sustentabilidade_urbana": {"peso": 8},
        },
        "viagem": {
            "conforto_viagens_longas": {"peso": 25},
            "desempenho_seguranca_estrada": {"peso": 20},
            "espaco_capacidade_carga": {"peso": 15},
            "economia_combustivel_estrada": {"peso": 12},
            "tecnologia_entretenimento": {"peso": 10},
            "confiabilidade_viagem": {"peso": 8},
            "facilidade_dirigibilidade": {"peso": 7},
            "sustentabilidade_viagem": {"peso": 3},
        },
        "trabalho": {
            "economia_combustivel": {"peso": 25},
            "confiabilidade": {"peso": 20},
            "baixo_custo_manutencao": {"peso": 15},
            "espaco_capacidade": {"peso": 10},
            "conforto_tecnologia": {"peso": 8},
            "aceitacao_plataformas": {"peso": 7},
            "garantia_procedencia": {"peso": 6},
            "financiamento_facilidade": {"peso": 5},
            "sustentabilidade": {"peso": 4},
        },
        "familia": {
            "seguranca_avancada_familia": {"peso": 25},
            "espaco_passageiros_conforto": {"peso": 20},
            "praticidade_uso_familiar": {"peso": 15},
            "custo_beneficio_familia": {"peso": 12},
            "confiabilidade_transporte": {"peso": 10},
            "tecnologia_seguranca_infantil": {"peso": 8},
            "eficiencia_combustivel_familia": {"peso": 5},
            "versatilidade_configuracao": {"peso": 5},
        },
    }

    def __init__(self):
        """Inicializa o matcher com mapeamento de handlers"""
        self._criterio_handlers = self._build_criterio_handlers()

    def _build_criterio_handlers(self) -> Dict[str, callable]:
        """Constrói o mapeamento de critério para função handler"""
        return {
            "economia_combustivel_urbana": self._avaliar_economia_urbana,
            "facilidade_manobra": self._avaliar_facilidade_manobra,
            "tecnologia_conectividade": self._avaliar_tecnologia_conectividade,
            "seguranca_urbana": self._avaliar_seguranca_urbana,
            "custo_manutencao_urbana": self._avaliar_custo_manutencao_urbana,
            "praticidade_urbana": self._avaliar_praticidade_urbana,
            "conforto_urbano": self._avaliar_conforto_urbano,
            "sustentabilidade_urbana": self._avaliar_sustentabilidade_urbana,
            "conforto_viagens_longas": self._avaliar_conforto_viagens,
            "desempenho_seguranca_estrada": self._avaliar_desempenho_estrada,
            "espaco_capacidade_carga": self._avaliar_espaco_carga,
            "economia_combustivel_estrada": self._avaliar_economia_estrada,
            "tecnologia_entretenimento": self._avaliar_entretenimento,
            "confiabilidade_viagem": self._avaliar_confiabilidade_viagem,
            "facilidade_dirigibilidade": self._avaliar_dirigibilidade,
            "sustentabilidade_viagem": self._avaliar_sustentabilidade_viagem,
            "economia_combustivel": self._avaliar_economia_geral,
            "confiabilidade": self._avaliar_confiabilidade_geral,
            "baixo_custo_manutencao": self._avaliar_baixo_custo,
            "espaco_capacidade": self._avaliar_espaco_geral,
            "conforto_tecnologia": self._avaliar_conforto_tech,
            "aceitacao_plataformas": self._avaliar_aceitacao_plataformas,
            "garantia_procedencia": self._avaliar_garantia,
            "financiamento_facilidade": self._avaliar_financiamento,
            "sustentabilidade": self._avaliar_sustentabilidade_geral,
            "seguranca_avancada_familia": self._avaliar_seguranca_familia,
            "espaco_passageiros_conforto": self._avaliar_espaco_passageiros,
            "praticidade_uso_familiar": self._avaliar_praticidade_familiar,
            "custo_beneficio_familia": self._avaliar_custo_beneficio_familia,
            "confiabilidade_transporte": self._avaliar_confiabilidade_transporte,
            "tecnologia_seguranca_infantil": self._avaliar_seguranca_infantil,
            "eficiencia_combustivel_familia": self._avaliar_eficiencia_familia,
            "versatilidade_configuracao": self._avaliar_versatilidade,
        }

    def _avaliar_criterio(
        self,
        criterio: str,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """
        Avalia um critério específico - VERSÃO REFATORADA

        Complexidade reduzida através de dispatch para handlers específicos
        """
        # Busca o handler para o critério
        handler = self._criterio_handlers.get(criterio)

        if handler:
            return handler(configs, carro, questionario)

        # Fallback para critério não reconhecido
        return 0.0, "", ""

    # ================== HANDLERS URBANO ==================

    def _avaliar_economia_urbana(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia economia de combustível urbana"""
        score_parcial = 0.0
        fatores = []

        # Avalia consumo na cidade
        consumo = carro.get("consumo_cidade", carro.get("consumo", 0))
        if consumo >= configs.get("consumo_cidade_minimo", 0):
            score_parcial += 0.5
            fatores.append(f"consumo cidade {consumo} km/l")

        # Avalia cilindrada ideal
        cilindrada = carro.get("cilindrada", 0)
        if cilindrada in configs.get("cilindradas_ideais", []):
            score_parcial += 0.3
            fatores.append(f"motor {cilindrada} econômico")

        # Verifica marca econômica
        marca = carro.get("marca", "")
        if marca in configs.get("marcas_economicas", []):
            score_parcial += 0.2
            fatores.append(f"marca {marca} econômica")

        if fatores:
            return (
                score_parcial,
                f"Economia urbana: {' e '.join(fatores)}",
                "Baixo custo operacional na cidade",
            )
        return 0.0, "", ""

    def _avaliar_facilidade_manobra(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia facilidade de manobra"""
        score_parcial = 0.0
        fatores = []

        # Verifica categoria ideal
        categoria = carro.get("categoria", "")
        if categoria in configs.get("categorias_ideais", []):
            score_parcial += 0.6
            fatores.append(f"{categoria} compacto")

        # Verifica comprimento (se disponível)
        comprimento = carro.get("comprimento", 0)
        if comprimento > 0 and comprimento <= configs.get("comprimento_max", 4.5):
            score_parcial += 0.2
            fatores.append("dimensões adequadas")

        # Verifica sistemas de assistência
        opcionais = carro.get("opcionais", [])
        sistemas = configs.get("sistemas_assistencia", [])
        tem_sistemas = sum(
            1
            for sistema in sistemas
            if any(sistema in opcional.lower() for opcional in opcionais)
        )
        if tem_sistemas > 0:
            score_parcial += 0.2
            fatores.append("sistemas de auxílio")

        if fatores:
            return (
                score_parcial,
                f"Manobra: {' e '.join(fatores)}",
                "Fácil de manobrar e estacionar",
            )
        return 0.0, "", ""

    def _avaliar_tecnologia_conectividade(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia tecnologia e conectividade"""
        opcionais = carro.get("opcionais", [])
        essenciais = configs.get("essenciais", [])
        desejados = configs.get("desejados", [])

        # Conta itens essenciais
        tem_essenciais = sum(
            1
            for item in essenciais
            if any(item in opcional.lower() for opcional in opcionais)
        )
        # Conta itens desejados
        tem_desejados = sum(
            1
            for item in desejados
            if any(item in opcional.lower() for opcional in opcionais)
        )

        if tem_essenciais >= len(essenciais) * 0.7:  # 70% dos essenciais
            score_base = 0.7
            score_bonus = min((tem_desejados / len(desejados)) * 0.3, 0.3)
            score = score_base + score_bonus
            return (
                score,
                f"Tecnologia: {tem_essenciais} essenciais + {tem_desejados} desejados",
                "Conectividade moderna",
            )
        return 0.0, "", ""

    def _avaliar_seguranca_urbana(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia segurança urbana"""
        score_parcial = 0.0
        fatores = []

        # Verifica básicos obrigatórios
        opcionais = carro.get("opcionais", [])
        basicos = configs.get("basicos_obrigatorios", [])
        tem_basicos = sum(
            1
            for item in basicos
            if any(item in opcional.lower() for opcional in opcionais)
        )

        if tem_basicos >= len(basicos) * 0.8:  # 80% dos básicos
            score_parcial += 0.6
            fatores.append("sistemas básicos")

        # Verifica segurança geral
        seguranca = carro.get("seguranca", 0)
        if seguranca >= 4:
            score_parcial += 0.4
            fatores.append(f"{seguranca} estrelas")

        if fatores:
            return (
                score_parcial,
                f"Segurança urbana: {' e '.join(fatores)}",
                "Proteção adequada no trânsito",
            )
        return 0.0, "", ""

    def _avaliar_custo_manutencao_urbana(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia custo de manutenção urbana"""
        score_parcial = 0.0
        fatores = []

        # Verifica marca com manutenção econômica
        marca = carro.get("marca", "")
        if marca in configs.get("marcas_economicas", []):
            score_parcial += 0.7
            fatores.append(f"marca {marca} com peças acessíveis")

        # Boost para carros populares
        if carro.get("categoria") in ["Hatch", "Sedan Compacto"]:
            score_parcial += 0.3
            fatores.append("modelo popular")

        if fatores:
            return (
                score_parcial,
                f"Manutenção: {' e '.join(fatores)}",
                "Baixo custo de manutenção",
            )
        return 0.0, "", ""

    def _avaliar_praticidade_urbana(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia praticidade urbana"""
        score_parcial = 0.0
        fatores = []

        # Verifica porta-malas adequado
        porta_malas = carro.get("porta_malas_litros", 0)
        minimo = configs.get("porta_malas_litros", {}).get("minimo", 0)
        if porta_malas >= minimo:
            score_parcial += 0.4
            fatores.append(f"porta-malas {porta_malas}L")

        # Verifica número de portas
        portas = carro.get("portas", 0)
        if portas >= configs.get("portas", {}).get("minimo", 4):
            score_parcial += 0.3
            fatores.append(f"{portas} portas")

        # Verifica facilidades
        opcionais = carro.get("opcionais", [])
        facilidades = configs.get("facilidades", [])
        tem_facilidades = sum(
            1
            for item in facilidades
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_facilidades > 0:
            score_parcial += 0.3
            fatores.append("facilidades")

        if fatores:
            return (
                score_parcial,
                f"Praticidade: {' e '.join(fatores)}",
                "Prático para uso diário",
            )
        return 0.0, "", ""

    def _avaliar_conforto_urbano(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia conforto urbano"""
        opcionais = carro.get("opcionais", [])
        clima = configs.get("clima", [])
        ergonomia = configs.get("ergonomia", [])

        tem_clima = sum(
            1
            for item in clima
            if any(item in opcional.lower() for opcional in opcionais)
        )
        tem_ergonomia = sum(
            1
            for item in ergonomia
            if any(item in opcional.lower() for opcional in opcionais)
        )

        if tem_clima > 0 or tem_ergonomia > 0:
            score = 0.7 + min((tem_clima + tem_ergonomia) * 0.1, 0.3)
            return (
                score,
                f"Conforto: {tem_clima + tem_ergonomia} itens",
                "Confortável para cidade",
            )
        return 0.0, "", ""

    def _avaliar_sustentabilidade_urbana(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia sustentabilidade urbana"""
        tipo_motor = carro.get("combustivel", "")
        if tipo_motor in configs.get("tipos_motor", []):
            return (
                1.0,
                f"Motor {tipo_motor} sustentável",
                "Opção ecológica para cidade",
            )
        return 0.0, "", ""

    # ================== HANDLERS VIAGEM ==================

    def _avaliar_conforto_viagens(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia conforto para viagens longas"""
        score_parcial = 0.0
        fatores = []

        # Verifica bancos de qualidade
        opcionais = carro.get("opcionais", [])
        bancos_essenciais = configs.get("bancos_essenciais", [])
        tem_bancos = sum(
            1
            for item in bancos_essenciais
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_bancos > 0:
            score_parcial += 0.4
            fatores.append("bancos de qualidade")

        # Verifica climatização
        climatizacao = configs.get("climatizacao", [])
        tem_clima = sum(
            1
            for item in climatizacao
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_clima > 0:
            score_parcial += 0.4
            fatores.append("climatização adequada")

        # Verifica ergonomia
        ergonomia = configs.get("ergonomia", [])
        tem_ergonomia = sum(
            1
            for item in ergonomia
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_ergonomia > 0:
            score_parcial += 0.2
            fatores.append("ergonomia")

        if fatores:
            return (
                score_parcial,
                f"Conforto viagem: {' e '.join(fatores)}",
                "Confortável para viagens longas",
            )
        return 0.0, "", ""

    def _avaliar_desempenho_estrada(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia desempenho e segurança na estrada"""
        score_parcial = 0.0
        fatores = []

        # Verifica potência por cilindrada
        cilindrada = carro.get("cilindrada", 0)
        if cilindrada >= configs.get("potencia_minima", {}).get("cilindrada_min", 1.4):
            score_parcial += 0.4
            fatores.append(f"motor {cilindrada} potente")

        # Verifica estabilidade e freios
        opcionais = carro.get("opcionais", [])
        estabilidade = configs.get("estabilidade", [])
        tem_estabilidade = sum(
            1
            for item in estabilidade
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_estabilidade > 0:
            score_parcial += 0.3
            fatores.append("sistemas estabilidade")

        # Verifica segurança geral
        seguranca = carro.get("seguranca", 0)
        if seguranca >= 4:
            score_parcial += 0.3
            fatores.append(f"{seguranca} estrelas")

        if fatores:
            return (
                score_parcial,
                f"Desempenho estrada: {' e '.join(fatores)}",
                "Segurança e potência para estradas",
            )
        return 0.0, "", ""

    # ... Adicionar os outros handlers de viagem ...

    # ================== HANDLERS TRABALHO ==================

    def _avaliar_economia_geral(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia economia de combustível geral"""
        score_parcial = 0.0
        fatores = []

        # Avalia consumo médio
        consumo = carro.get("consumo", 0)
        if consumo >= configs.get("consumo_minimo", 0):
            score_parcial += 0.5
            fatores.append(f"consumo {consumo} km/l")

        # Verifica tipo de combustível econômico
        combustivel = carro.get("combustivel", "")
        if combustivel in configs.get("combustiveis_economicos", []):
            score_parcial += 0.3
            fatores.append(f"{combustivel} econômico")

        # Bonus para híbridos/elétricos
        if combustivel in ["Híbrido", "Elétrico"]:
            score_parcial += 0.2
            fatores.append("tecnologia eficiente")

        if fatores:
            return (
                score_parcial,
                f"Economia: {' e '.join(fatores)}",
                "Baixo custo de combustível",
            )
        return 0.0, "", ""

    def _avaliar_confiabilidade_geral(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia confiabilidade geral"""
        score_parcial = 0.0
        fatores = []

        # Verifica marca confiável
        marca = carro.get("marca", "")
        if marca in configs.get("marcas_confiaveis", []):
            score_parcial += 0.6
            fatores.append(f"marca {marca} confiável")

        # Verifica idade/quilometragem
        km = carro.get("km", 0)
        if km <= configs.get("km_maximo", 100000):
            score_parcial += 0.2
            fatores.append(f"{km:,} km")

        # Verifica garantia
        if "garantia" in str(carro.get("opcionais", [])).lower():
            score_parcial += 0.2
            fatores.append("com garantia")

        if fatores:
            return (
                score_parcial,
                f"Confiabilidade: {' e '.join(fatores)}",
                "Veículo confiável para trabalho",
            )
        return 0.0, "", ""

    # ... Adicionar os outros handlers de trabalho ...

    # ================== HANDLERS FAMÍLIA ==================

    def _avaliar_seguranca_familia(
        self,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia segurança avançada para família"""
        score_parcial = 0.0
        fatores = []

        opcionais = carro.get("opcionais", [])

        # Verifica airbags múltiplos
        airbags_essenciais = configs.get("airbags_essenciais", [])
        tem_airbags = sum(
            1
            for item in airbags_essenciais
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_airbags >= len(airbags_essenciais) * 0.8:
            score_parcial += 0.4
            fatores.append(f"{tem_airbags} airbags")

        # Verifica sistemas ativos
        sistemas_ativos = configs.get("sistemas_ativos", [])
        tem_sistemas = sum(
            1
            for item in sistemas_ativos
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_sistemas > 0:
            score_parcial += 0.3
            fatores.append("sistemas ativos")

        # Verifica proteção infantil
        protecao_infantil = configs.get("protecao_infantil", [])
        tem_protecao = sum(
            1
            for item in protecao_infantil
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if tem_protecao > 0:
            score_parcial += 0.3
            fatores.append("proteção infantil")

        if fatores:
            return (
                score_parcial,
                f"Segurança família: {' e '.join(fatores)}",
                "Máxima proteção para família",
            )
        return 0.0, "", ""

    # ... Adicionar os outros handlers de família ...

    # Implementações stub para handlers não detalhados
    def _avaliar_espaco_carga(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_economia_estrada(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_entretenimento(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_confiabilidade_viagem(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_dirigibilidade(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_sustentabilidade_viagem(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_baixo_custo(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_espaco_geral(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_conforto_tech(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_aceitacao_plataformas(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_garantia(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_financiamento(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_sustentabilidade_geral(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_espaco_passageiros(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_praticidade_familiar(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_custo_beneficio_familia(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_confiabilidade_transporte(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_seguranca_infantil(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_eficiencia_familia(self, configs, carro, questionario):
        return 0.0, "", ""

    def _avaliar_versatilidade(self, configs, carro, questionario):
        return 0.0, "", ""
