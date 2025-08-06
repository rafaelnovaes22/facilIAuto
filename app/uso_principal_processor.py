"""
Processador Avançado de Critérios de Uso Principal do Veículo

Este módulo implementa os critérios detalhados do relatório de uso principal,
transformando perfis de uso em scores técnicos específicos baseados nas
características dos veículos.

Perfis suportados:
- Urbano: compacto, econômico, tecnológico
- Viagem: espaçoso, potente, confortável, seguro
- Trabalho/Negócios: economia combustível (20%), confiabilidade (20%), baixo custo manutenção (15%),
  espaço/capacidade (15%), conforto/tecnologia (10%), aceitação plataformas (10%)
  Subsegmentos: motoristas app, MEIs, pequenos negócios, entregas
- Família: espaçoso, seguro, confortável, prático
"""

from typing import Any, Dict, List, Tuple, cast

from app.models import QuestionarioBusca


class UsoMatcher:
    """Classe responsável por calcular scores de compatibilidade baseados no uso principal"""

    # Pesos para cada tipo de uso (soma deve ser <= 25% do score total)
    PESO_USO_PRINCIPAL = 25.0

    # Critérios técnicos por tipo de uso
    CRITERIOS_USO = {
        "urbano": {
            "economia_combustivel_urbana": {
                "peso": 20,
                "consumo_cidade_minimo": 12,  # km/l
                "cilindradas_ideais": [1.0, 1.4],
                "marcas_economicas": ["Honda", "Toyota", "Chevrolet", "Nissan"],
                "tecnologias_eco": ["flex", "start_stop", "híbrido"],
            },
            "facilidade_manobra": {
                "peso": 20,
                "categorias_ideais": ["Hatch", "Sedan Compacto"],
                "comprimento_max": 4.2,  # metros
                "raio_giro_max": 5.0,  # metros
                "sistemas_assistencia": ["sensores", "camera_re", "park_assist"],
            },
            "tecnologia_conectividade": {
                "peso": 15,
                "essenciais": ["central_multimidia", "bluetooth", "usb"],
                "desejados": ["android_auto", "apple_carplay", "wifi"],
                "navegacao": ["gps_integrado", "waze_nativo"],
                "subsegmento_boost": {"executivo": 1.5},
            },
            "seguranca_urbana": {
                "peso": 15,
                "basicos_obrigatorios": ["abs", "airbag_duplo", "cintos_3pontos"],
                "avancados": ["controle_estabilidade", "assistente_frenagem"],
                "visibilidade": ["faróis_led", "retrovisores_eletricos"],
                "subsegmento_boost": {"primeiro_carro": 1.3},
            },
            "custo_manutencao_urbana": {
                "peso": 10,
                "marcas_economicas": ["Chevrolet", "Fiat", "Volkswagen", "Renault"],
                "pecas_disponiveis": True,
                "rede_autorizada": ["ampla", "acessivel"],
                "intervalos_revisao": {"ideal_km": 10000, "max_km": 15000},
            },
            "praticidade_urbana": {
                "peso": 8,
                "porta_malas_litros": {"minimo": 250, "ideal": 350},
                "altura_solo": {"minimo": 14, "maximo": 18},  # cm
                "portas": {"minimo": 4, "ideal": 5},
                "facilidades": ["vidros_eletricos", "travamento_central"],
            },
            "conforto_urbano": {
                "peso": 7,
                "clima": ["ar_condicionado", "ventilacao_eficiente"],
                "ergonomia": ["direcao_assistida", "bancos_regulaveis"],
                "ruido": ["isolamento_acustico", "motor_silencioso"],
            },
            "sustentabilidade_urbana": {
                "peso": 5,
                "tipos_motor": ["flex", "híbrido", "elétrico"],
                "emissoes": ["euro_5", "proconve_l6"],
                "eficiencia": ["baixa_pegada_carbono"],
            },
        },
        "viagem": {
            "conforto_viagens_longas": {
                "peso": 20,
                "bancos_essenciais": [
                    "regulagem_altura",
                    "apoio_lombar",
                    "couro_tecido_premium",
                ],
                "climatizacao": [
                    "ar_condicionado",
                    "climatizador_automatico",
                    "saidas_traseiras",
                ],
                "ergonomia": ["volante_regulavel", "apoio_braco", "espaco_pernas"],
                "subsegmento_boost": {"turismo_lazer": 1.3, "road_trip": 1.5},
            },
            "desempenho_seguranca_estrada": {
                "peso": 20,
                "potencia_minima": {"cilindrada_min": 1.4, "hp_estimado": 100},
                "estabilidade": [
                    "controle_estabilidade",
                    "controle_tracao",
                    "abs_avancado",
                ],
                "freios": [
                    "freios_disco",
                    "assistencia_frenagem",
                    "distribuicao_eletronica",
                ],
                "seguranca_ativa": ["airbags_multiplos", "estrutura_reforçada"],
                "subsegmento_boost": {"road_trip": 1.4, "viagem_trabalho": 1.2},
            },
            "espaco_capacidade_carga": {
                "peso": 15,
                "categorias_ideais": [
                    "SUV",
                    "Sedan Médio",
                    "SUV Médio",
                    "Wagon",
                    "Minivan",
                ],
                "porta_malas_litros": {"minimo": 400, "ideal": 500},
                "passageiros": {"minimo": 5, "ideal": 7},
                "versatilidade": [
                    "bancos_rebatraveis",
                    "porta_malas_amplo",
                    "compartimentos",
                ],
                "subsegmento_boost": {"viagem_familia": 1.4},
            },
            "economia_combustivel_estrada": {
                "peso": 15,
                "consumo_estrada_minimo": 10,  # km/l
                "autonomia_minima": 500,  # km
                "tecnologias_economia": [
                    "injecão_eletronica",
                    "start_stop",
                    "eco_mode",
                ],
                "marcas_eficientes": ["Honda", "Toyota", "Volkswagen", "Hyundai"],
                "subsegmento_boost": {"viagem_trabalho": 1.3},
            },
            "tecnologia_entretenimento": {
                "peso": 10,
                "navegacao": ["gps_integrado", "mapas_atualizados", "comando_voz"],
                "conectividade": [
                    "android_auto",
                    "apple_carplay",
                    "wifi",
                    "usb_multiplas",
                ],
                "entretenimento": ["som_premium", "tela_grande", "dvd_traseiro"],
                "subsegmento_boost": {"turismo_lazer": 1.2, "viagem_familia": 1.3},
            },
            "confiabilidade_viagem": {
                "peso": 8,
                "marcas_confiaveis": [
                    "Toyota",
                    "Honda",
                    "Volkswagen",
                    "Hyundai",
                    "Chevrolet",
                ],
                "km_maximo": 100000,
                "historico_revisoes": ["concessionaria", "revisado", "garantia"],
                "reputacao_estrada": [
                    "baixa_quebra",
                    "pecas_disponiveis",
                    "rede_autorizada",
                ],
            },
            "facilidade_dirigibilidade": {
                "peso": 7,
                "transmissao": ["automatico", "cvt", "manual_suave"],
                "direcao": ["assistida_eletrica", "hidraulica_leve", "responsiva"],
                "assistencias": [
                    "piloto_automatico",
                    "controle_velocidade",
                    "alerta_faixa",
                ],
                "visibilidade": ["farois_led", "retrovisores_grandes", "campo_visao"],
            },
            "sustentabilidade_viagem": {
                "peso": 5,
                "tipos_motor": ["flex", "híbrido", "turbo_eficiente"],
                "emissoes": ["euro_5", "proconve_l6", "baixa_pegada"],
                "eficiencia_energetica": ["recuperacao_energia", "gestao_inteligente"],
            },
        },
        "trabalho": {
            "economia_combustivel": {
                "peso": 20,
                "consumo_minimo": 10,
                "cilindrada_ideal": [1.0, 1.4, 1.6],
            },
            "confiabilidade": {
                "peso": 20,
                "marcas_confiaveis": ["Toyota", "Honda", "Chevrolet", "Volkswagen"],
                "km_maximo": 80000,
            },
            "baixo_custo_manutencao": {
                "peso": 15,
                "marcas_economicas": ["Chevrolet", "Fiat", "Volkswagen"],
                "pecas_acessiveis": True,
            },
            "espaco_capacidade": {
                "peso": 15,
                "categorias_versateis": [
                    "Hatch",
                    "Sedan",
                    "SUV Compacto",
                    "Pickup",
                    "Van",
                ],
            },
            "conforto_tecnologia": {
                "peso": 10,
                "opcionais_essenciais": [
                    "ar_condicionado",
                    "direcao_assistida",
                    "conectividade",
                ],
            },
            "aceitacao_plataformas": {
                "peso": 10,
                "ano_minimo": 2012,
                "portas_minimas": 4,
                "ar_obrigatorio": True,
            },
            "garantia_procedencia": {
                "peso": 5,
                "concessionaria_boost": True,
                "revisado": True,
            },
            "financiamento_facilidade": {
                "peso": 3,
                "aceita_cnpj": True,
                "aceita_mei": True,
            },
            "sustentabilidade": {
                "peso": 2,
                "tipos_motor": ["flex", "híbrido", "elétrico"],
            },
        },
        "familia": {
            "seguranca_avancada_familia": {
                "peso": 20,
                "airbags_essenciais": ["frontais", "laterais", "cortina", "joelho"],
                "isofix_pontos": {"minimo": 2, "ideal": 3},
                "estrutura_seguranca": [
                    "zona_deformacao",
                    "celula_rigida",
                    "absorvedor_impacto",
                ],
                "sistemas_ativos": [
                    "abs",
                    "controle_estabilidade",
                    "assistencia_frenagem",
                ],
                "subsegmento_boost": {"criancas_pequenas": 1.4, "familia_grande": 1.2},
            },
            "espaco_passageiros_conforto": {
                "peso": 20,
                "categorias_ideais": [
                    "SUV",
                    "Minivan",
                    "SUV Médio",
                    "Sedan Médio",
                    "Wagon",
                ],
                "pessoas_capacidade": {"minimo": 5, "ideal": 7},
                "espaco_interno": ["pernas_traseiras", "altura_teto", "largura_bancos"],
                "conforto_ocupantes": [
                    "ar_condicionado",
                    "saidas_traseiras",
                    "apoio_braco",
                ],
                "subsegmento_boost": {"familia_grande": 1.5, "viagem_familia": 1.3},
            },
            "praticidade_uso_familiar": {
                "peso": 15,
                "acesso_facilidade": ["4_portas", "abertura_ampla", "altura_entrada"],
                "configuracao_flexivel": [
                    "bancos_rebatraveis",
                    "divisoria_removivel",
                    "compartimentos",
                ],
                "porta_malas_familia": {"minimo_litros": 350, "ideal_litros": 500},
                "conveniencias": [
                    "vidros_eletricos",
                    "travas_eletricas",
                    "espelhos_eletricos",
                ],
                "subsegmento_boost": {"atividades_esportivas": 1.3},
            },
            "custo_beneficio_familia": {
                "peso": 15,
                "preco_justo": {
                    "faixa_ideal": [30000, 80000],
                    "depreciacao_baixa": True,
                },
                "custo_manutencao": [
                    "pecas_acessiveis",
                    "rede_autorizada",
                    "revisoes_programadas",
                ],
                "seguro_acessivel": [
                    "categoria_baixa",
                    "perfil_familia",
                    "dispositivos_seguranca",
                ],
                "economia_operacional": ["combustivel_eficiente", "durabilidade_alta"],
            },
            "confiabilidade_transporte": {
                "peso": 10,
                "marcas_familia": [
                    "Toyota",
                    "Honda",
                    "Volkswagen",
                    "Hyundai",
                    "Chevrolet",
                    "Ford",
                ],
                "historico_confiavel": [
                    "baixo_recall",
                    "satisfacao_proprietarios",
                    "durabilidade",
                ],
                "garantia_suporte": [
                    "garantia_estendida",
                    "rede_concessionarias",
                    "suporte_tecnico",
                ],
                "km_adequada": {"maximo": 80000, "ideal": 50000},
            },
            "tecnologia_seguranca_infantil": {
                "peso": 8,
                "isofix_completo": [
                    "pontos_ancoragem",
                    "top_tether",
                    "guias_instalacao",
                ],
                "travas_seguranca": [
                    "portas_traseiras",
                    "vidros_traseiros",
                    "cinto_bloqueio",
                ],
                "monitoramento": ["sensor_ocupacao", "alerta_cinto", "camera_re"],
                "visibilidade": ["farois_automaticos", "sensores_estacionamento"],
            },
            "eficiencia_combustivel_familia": {
                "peso": 7,
                "consumo_familia": {"cidade_minimo": 8, "estrada_minimo": 10},
                "autonomia_adequada": 400,  # km
                "tecnologias_economia": [
                    "injecao_eletronica",
                    "start_stop",
                    "eco_mode",
                ],
                "motores_eficientes": [1.0, 1.4, 1.6, 1.8],  # cilindradas ideais
            },
            "versatilidade_configuracao": {
                "peso": 5,
                "flexibilidade_interior": [
                    "bancos_60_40",
                    "encosto_rebativel",
                    "altura_ajustavel",
                ],
                "espacos_uteis": ["porta_objetos", "console_central", "porta_copos"],
                "facilidades_familia": [
                    "ganchos_sacolas",
                    "iluminacao_interna",
                    "tomadas_12v",
                ],
            },
        },
    }

    @classmethod
    def calcular_score_uso_principal(
        cls, questionario: QuestionarioBusca, carro: Dict[str, Any]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calcula score baseado no uso principal do veículo

        Returns:
            Tuple[float, List[str], List[str]]: (score, razões, pontos_fortes)
        """
        if not questionario.uso_principal:
            return 0.0, [], []

        score_total = 0.0
        razoes = []
        pontos_fortes = []

        # Calcula peso por uso (divide igualmente entre os usos selecionados)
        peso_por_uso = cls.PESO_USO_PRINCIPAL / len(questionario.uso_principal)

        for uso in questionario.uso_principal:
            if uso not in cls.CRITERIOS_USO:
                continue

            score_uso, razoes_uso, pontos_uso = cls._avaliar_uso_especifico(uso, carro, peso_por_uso, questionario)
            score_total += score_uso
            razoes.extend(razoes_uso)
            pontos_fortes.extend(pontos_uso)

        return score_total, razoes, pontos_fortes

    @classmethod
    def _avaliar_uso_especifico(
        cls,
        uso: str,
        carro: Dict[str, Any],
        peso_uso: float,
        questionario: QuestionarioBusca,
    ) -> Tuple[float, List[str], List[str]]:
        """Avalia um tipo de uso específico"""
        criterios = cast(Dict[str, Any], cls.CRITERIOS_USO[uso])
        score = 0.0
        razoes = []
        pontos_fortes = []

        for criterio, configs in criterios.items():
            score_criterio, razao, ponto_forte = cls._avaliar_criterio(criterio, configs, carro, questionario)

            # Aplica peso do critério dentro do uso
            peso_criterio = configs["peso"] / 100.0  # Converte percentual para decimal
            score += score_criterio * peso_criterio * peso_uso

            if razao:
                razoes.append(f"{uso.capitalize()}: {razao}")
            if ponto_forte:
                pontos_fortes.append(f"{uso.capitalize()}: {ponto_forte}")

        return score, razoes, pontos_fortes

    @classmethod
    def _avaliar_criterio(
        cls,
        criterio: str,
        configs: Dict[str, Any],
        carro: Dict[str, Any],
        questionario: QuestionarioBusca,
    ) -> Tuple[float, str, str]:
        """Avalia um critério específico"""
        score = 0.0
        razao = ""
        ponto_forte = ""

        if criterio == "economia_combustivel_urbana":
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
                score = score_parcial
                razao = f"Economia urbana: {' e '.join(fatores)}"
                ponto_forte = "Baixo custo operacional na cidade"

        elif criterio == "facilidade_manobra":
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
            tem_sistemas = sum(1 for sistema in sistemas if any(sistema in opcional.lower() for opcional in opcionais))
            if tem_sistemas > 0:
                score_parcial += 0.2
                fatores.append("sistemas de auxílio")

            if fatores:
                score = score_parcial
                razao = f"Manobra: {' e '.join(fatores)}"
                ponto_forte = "Fácil de manobrar e estacionar"

        elif criterio == "tecnologia_conectividade":
            opcionais = carro.get("opcionais", [])
            essenciais = configs.get("essenciais", [])
            desejados = configs.get("desejados", [])

            # Conta itens essenciais
            tem_essenciais = sum(1 for item in essenciais if any(item in opcional.lower() for opcional in opcionais))
            # Conta itens desejados
            tem_desejados = sum(1 for item in desejados if any(item in opcional.lower() for opcional in opcionais))

            if tem_essenciais >= len(essenciais) * 0.7:  # 70% dos essenciais
                score_base = 0.7
                score_bonus = min((tem_desejados / len(desejados)) * 0.3, 0.3)
                score = score_base + score_bonus
                razao = f"Tecnologia: {tem_essenciais} essenciais + {tem_desejados} desejados"
                ponto_forte = "Conectividade moderna"

        elif criterio == "seguranca_urbana":
            score_parcial = 0.0
            fatores = []

            # Verifica básicos obrigatórios
            opcionais = carro.get("opcionais", [])
            basicos = configs.get("basicos_obrigatorios", [])
            tem_basicos = sum(1 for item in basicos if any(item in opcional.lower() for opcional in opcionais))

            if tem_basicos >= len(basicos) * 0.8:  # 80% dos básicos
                score_parcial += 0.6
                fatores.append("sistemas básicos")

            # Verifica segurança geral
            seguranca = carro.get("seguranca", 0)
            if seguranca >= 4:
                score_parcial += 0.4
                fatores.append(f"{seguranca} estrelas")

            if fatores:
                score = score_parcial
                razao = f"Segurança urbana: {' e '.join(fatores)}"
                ponto_forte = "Proteção adequada no trânsito"

        elif criterio == "custo_manutencao_urbana":
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
                score = score_parcial
                razao = f"Manutenção: {' e '.join(fatores)}"
                ponto_forte = "Baixo custo de manutenção"

        elif criterio == "praticidade_urbana":
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
            tem_facilidades = sum(1 for item in facilidades if any(item in opcional.lower() for opcional in opcionais))
            if tem_facilidades > 0:
                score_parcial += 0.3
                fatores.append("facilidades")

            if fatores:
                score = score_parcial
                razao = f"Praticidade: {' e '.join(fatores)}"
                ponto_forte = "Prático para uso diário"

        elif criterio == "conforto_urbano":
            opcionais = carro.get("opcionais", [])
            clima = configs.get("clima", [])
            ergonomia = configs.get("ergonomia", [])

            tem_clima = sum(1 for item in clima if any(item in opcional.lower() for opcional in opcionais))
            tem_ergonomia = sum(1 for item in ergonomia if any(item in opcional.lower() for opcional in opcionais))

            if tem_clima > 0 or tem_ergonomia > 0:
                score = 0.7 + min((tem_clima + tem_ergonomia) * 0.1, 0.3)
                razao = f"Conforto: {tem_clima + tem_ergonomia} itens"
                ponto_forte = "Confortável para cidade"

        elif criterio == "sustentabilidade_urbana":
            tipo_motor = carro.get("combustivel", "")
            if tipo_motor in configs.get("tipos_motor", []):
                score = 1.0
                razao = f"Motor {tipo_motor} sustentável"
                ponto_forte = "Opção ecológica para cidade"

        elif criterio == "conforto_viagens_longas":
            score_parcial = 0.0
            fatores = []

            # Verifica bancos de qualidade
            opcionais = carro.get("opcionais", [])
            bancos_essenciais = configs.get("bancos_essenciais", [])
            tem_bancos = sum(1 for item in bancos_essenciais if any(item in opcional.lower() for opcional in opcionais))
            if tem_bancos > 0:
                score_parcial += 0.4
                fatores.append("bancos de qualidade")

            # Verifica climatização
            climatizacao = configs.get("climatizacao", [])
            tem_clima = sum(1 for item in climatizacao if any(item in opcional.lower() for opcional in opcionais))
            if tem_clima > 0:
                score_parcial += 0.4
                fatores.append("climatização adequada")

            # Verifica ergonomia
            ergonomia = configs.get("ergonomia", [])
            tem_ergonomia = sum(1 for item in ergonomia if any(item in opcional.lower() for opcional in opcionais))
            if tem_ergonomia > 0:
                score_parcial += 0.2
                fatores.append("ergonomia")

            if fatores:
                score = score_parcial
                razao = f"Conforto viagem: {' e '.join(fatores)}"
                ponto_forte = "Confortável para viagens longas"

        elif criterio == "desempenho_seguranca_estrada":
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
            tem_estabilidade = sum(1 for item in estabilidade if any(item in opcional.lower() for opcional in opcionais))
            if tem_estabilidade > 0:
                score_parcial += 0.3
                fatores.append("sistemas estabilidade")

            # Verifica segurança geral
            seguranca = carro.get("seguranca", 0)
            if seguranca >= 4:
                score_parcial += 0.3
                fatores.append(f"{seguranca} estrelas")

            if fatores:
                score = score_parcial
                razao = f"Desempenho estrada: {' e '.join(fatores)}"
                ponto_forte = "Segurança e potência para estradas"

        elif criterio == "espaco_capacidade_carga":
            score_parcial = 0.0
            fatores = []

            # Verifica categoria ideal
            categoria = carro.get("categoria", "")
            if categoria in configs.get("categorias_ideais", []):
                score_parcial += 0.5
                fatores.append(f"{categoria} espaçoso")

            # Verifica porta-malas
            porta_malas = carro.get("porta_malas_litros", 0)
            minimo = configs.get("porta_malas_litros", {}).get("minimo", 0)
            if porta_malas >= minimo:
                score_parcial += 0.3
                fatores.append(f"porta-malas {porta_malas}L")

            # Verifica capacidade passageiros
            pessoas = carro.get("pessoas_transportar", 0)
            if pessoas >= configs.get("passageiros", {}).get("minimo", 5):
                score_parcial += 0.2
                fatores.append(f"{pessoas} pessoas")

            if fatores:
                score = score_parcial
                razao = f"Capacidade: {' e '.join(fatores)}"
                ponto_forte = "Espaço adequado para viagens"

        elif criterio == "economia_combustivel_estrada":
            score_parcial = 0.0
            fatores = []

            # Verifica consumo na estrada
            consumo = carro.get("consumo_estrada", carro.get("consumo", 0))
            if consumo >= configs.get("consumo_estrada_minimo", 0):
                score_parcial += 0.6
                fatores.append(f"consumo estrada {consumo} km/l")

            # Verifica marca eficiente
            marca = carro.get("marca", "")
            if marca in configs.get("marcas_eficientes", []):
                score_parcial += 0.4
                fatores.append(f"marca {marca} eficiente")

            if fatores:
                score = score_parcial
                razao = f"Economia estrada: {' e '.join(fatores)}"
                ponto_forte = "Econômico em viagens longas"

        elif criterio == "tecnologia_entretenimento":
            score_parcial = 0.0
            fatores = []

            # Verifica navegação
            opcionais = carro.get("opcionais", [])
            navegacao = configs.get("navegacao", [])
            tem_navegacao = sum(1 for item in navegacao if any(item in opcional.lower() for opcional in opcionais))
            if tem_navegacao > 0:
                score_parcial += 0.4
                fatores.append("navegação")

            # Verifica conectividade
            conectividade = configs.get("conectividade", [])
            tem_conectividade = sum(1 for item in conectividade if any(item in opcional.lower() for opcional in opcionais))
            if tem_conectividade > 0:
                score_parcial += 0.4
                fatores.append("conectividade")

            # Verifica entretenimento
            entretenimento = configs.get("entretenimento", [])
            tem_entretenimento = sum(1 for item in entretenimento if any(item in opcional.lower() for opcional in opcionais))
            if tem_entretenimento > 0:
                score_parcial += 0.2
                fatores.append("entretenimento")

            if fatores:
                score = score_parcial
                razao = f"Tecnologia viagem: {' e '.join(fatores)}"
                ponto_forte = "Tecnologia para viagens"

        elif criterio == "confiabilidade_viagem":
            score_parcial = 0.0
            fatores = []

            # Verifica marca confiável
            marca = carro.get("marca", "")
            if marca in configs.get("marcas_confiaveis", []):
                score_parcial += 0.5
                fatores.append(f"marca {marca} confiável")

            # Verifica quilometragem
            km = carro.get("km", 0)
            if km <= configs.get("km_maximo", 100000):
                score_parcial += 0.3
                fatores.append("baixa quilometragem")

            # Verifica histórico
            if carro.get("revisado") or carro.get("concessionaria"):
                score_parcial += 0.2
                fatores.append("histórico confiável")

            if fatores:
                score = score_parcial
                razao = f"Confiabilidade: {' e '.join(fatores)}"
                ponto_forte = "Confiável para viagens"

        elif criterio == "facilidade_dirigibilidade":
            opcionais = carro.get("opcionais", [])
            direcao = configs.get("direcao", [])
            assistencias = configs.get("assistencias", [])

            tem_direcao = sum(1 for item in direcao if any(item in opcional.lower() for opcional in opcionais))
            tem_assistencias = sum(1 for item in assistencias if any(item in opcional.lower() for opcional in opcionais))

            if tem_direcao > 0 or tem_assistencias > 0:
                score = 0.7 + min((tem_direcao + tem_assistencias) * 0.15, 0.3)
                razao = f"Dirigibilidade: {tem_direcao + tem_assistencias} facilidades"
                ponto_forte = "Fácil de dirigir em viagens"

        elif criterio == "sustentabilidade_viagem":
            tipo_motor = carro.get("combustivel", "")
            if tipo_motor in configs.get("tipos_motor", []):
                score = 1.0
                razao = f"Motor {tipo_motor} eficiente"
                ponto_forte = "Opção sustentável para viagens"

        elif criterio == "economia_combustivel":
            score_parcial = 0.0
            fatores = []

            # Avalia consumo de combustível
            consumo = carro.get("consumo_cidade", carro.get("consumo", 0))
            if consumo >= configs.get("consumo_minimo", 0):
                score_parcial += 0.6
                fatores.append(f"consumo {consumo} km/l")

            # Avalia cilindrada ideal
            cilindrada = carro.get("cilindrada", 0)
            if cilindrada in configs.get("cilindrada_ideal", []):
                score_parcial += 0.4
                fatores.append(f"motor {cilindrada} econômico")

            if fatores:
                score = score_parcial
                razao = f"Economia: {' e '.join(fatores)}"
                ponto_forte = "Baixo custo operacional"

        elif criterio == "confiabilidade":
            score_parcial = 0.0
            fatores = []

            # Verifica marca confiável
            marca = carro.get("marca", "")
            if marca in configs.get("marcas_confiaveis", []):
                score_parcial += 0.5
                fatores.append(f"marca {marca} confiável")

            # Verifica quilometragem
            km = carro.get("km", 0)
            if km <= configs.get("km_maximo", 100000):
                score_parcial += 0.5
                fatores.append("baixa quilometragem")

            if fatores:
                score = score_parcial
                razao = f"Confiabilidade: {' e '.join(fatores)}"
                ponto_forte = "Veículo confiável para uso intenso"

        elif criterio == "baixo_custo_manutencao":
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
                score = score_parcial
                razao = f"Manutenção: {' e '.join(fatores)}"
                ponto_forte = "Baixo custo de manutenção"

        elif criterio == "espaco_capacidade":
            categoria = carro.get("categoria", "")
            if categoria in configs.get("categorias_versateis", []):
                score = 1.0
                razao = f"{categoria} oferece bom espaço para trabalho"
                ponto_forte = "Espaço adequado para equipamentos/passageiros"

        elif criterio == "conforto_tecnologia":
            opcionais = carro.get("opcionais", [])
            essenciais = configs.get("opcionais_essenciais", [])
            tem_essenciais = sum(1 for item in essenciais if item in opcionais)

            if tem_essenciais >= len(essenciais) * 0.7:  # 70% dos essenciais
                score = 1.0
                razao = f"Tem {tem_essenciais}/{len(essenciais)} itens essenciais"
                ponto_forte = "Conforto adequado para uso profissional"

        elif criterio == "aceitacao_plataformas":
            score_parcial = 0.0
            fatores = []

            # Verifica ano mínimo para apps
            ano = carro.get("ano", 0)
            if ano >= configs.get("ano_minimo", 2012):
                score_parcial += 0.4
                fatores.append(f"ano {ano} aceito em apps")

            # Verifica 4 portas
            if carro.get("portas", 0) >= configs.get("portas_minimas", 4):
                score_parcial += 0.3
                fatores.append("4 portas")

            # Verifica ar-condicionado obrigatório
            if "ar_condicionado" in carro.get("opcionais", []):
                score_parcial += 0.3
                fatores.append("ar-condicionado")

            if fatores:
                score = score_parcial
                razao = f"Plataformas: {' e '.join(fatores)}"
                ponto_forte = "Aceito em Uber/99/InDrive"

        elif criterio == "garantia_procedencia":
            score_parcial = 0.0
            fatores = []

            # Boost para concessionária
            if carro.get("concessionaria", False):
                score_parcial += 0.6
                fatores.append("concessionária")

            # Boost para revisado
            if carro.get("revisado", False):
                score_parcial += 0.4
                fatores.append("revisado")

            if fatores:
                score = score_parcial
                razao = f"Procedência: {' e '.join(fatores)}"
                ponto_forte = "Garantia e histórico transparente"

        elif criterio == "financiamento_facilidade":
            # Critério mais conceitual, sempre dá boost
            score = 0.5
            razao = "Facilidades de financiamento para MEI/CNPJ"
            ponto_forte = "Opções de crédito empresarial"

        elif criterio == "sustentabilidade":
            tipo_motor = carro.get("combustivel", "")
            if tipo_motor in configs.get("tipos_motor", []):
                score = 1.0
                razao = f"Motor {tipo_motor} sustentável"
                ponto_forte = "Opção ecológica para empresa"

        elif criterio == "seguranca_avancada_familia":
            score_parcial = 0.0
            fatores = []

            # Verifica airbags essenciais
            opcionais = carro.get("opcionais", [])
            airbags_essenciais = configs.get("airbags_essenciais", [])
            tem_airbags = sum(1 for item in airbags_essenciais if any(item in opcional.lower() for opcional in opcionais))
            if tem_airbags > 0:
                score_parcial += 0.4
                fatores.append(f"{tem_airbags} tipos airbags")

            # Verifica segurança geral
            seguranca = carro.get("seguranca", 0)
            if seguranca >= 4:
                score_parcial += 0.4
                fatores.append(f"{seguranca} estrelas")

            # Verifica sistemas ativos
            sistemas_ativos = configs.get("sistemas_ativos", [])
            tem_sistemas = sum(1 for item in sistemas_ativos if any(item in opcional.lower() for opcional in opcionais))
            if tem_sistemas > 0:
                score_parcial += 0.2
                fatores.append("sistemas ativos")

            if fatores:
                score = score_parcial
                razao = f"Segurança família: {' + '.join(fatores)}"
                ponto_forte = "Máxima proteção para a família"

        elif criterio == "espaco_passageiros_conforto":
            score_parcial = 0.0
            fatores = []

            # Verifica categoria ideal
            categoria = carro.get("categoria", "")
            if categoria in configs.get("categorias_ideais", []):
                score_parcial += 0.5
                fatores.append(f"{categoria} espaçoso")

            # Verifica capacidade de pessoas
            pessoas = carro.get("pessoas_transportar", questionario.pessoas_transportar or 5)
            minimo = configs.get("pessoas_capacidade", {}).get("minimo", 5)
            if pessoas >= minimo:
                score_parcial += 0.3
                fatores.append(f"{pessoas} pessoas")

            # Verifica conforto específico
            opcionais = carro.get("opcionais", [])
            conforto_ocupantes = configs.get("conforto_ocupantes", [])
            tem_conforto = sum(1 for item in conforto_ocupantes if any(item in opcional.lower() for opcional in opcionais))
            if tem_conforto > 0:
                score_parcial += 0.2
                fatores.append("conforto ocupantes")

            if fatores:
                score = score_parcial
                razao = f"Espaço família: {' + '.join(fatores)}"
                ponto_forte = "Conforto para toda a família"

        elif criterio == "praticidade_uso_familiar":
            score_parcial = 0.0
            fatores = []

            # Verifica facilidade de acesso
            opcionais = carro.get("opcionais", [])
            facilidades = configs.get("conveniencias", [])
            tem_facilidades = sum(1 for item in facilidades if any(item in opcional.lower() for opcional in opcionais))
            if tem_facilidades > 0:
                score_parcial += 0.4
                fatores.append(f"{tem_facilidades} facilidades")

            # Verifica porta-malas
            porta_malas = carro.get("porta_malas_litros", 0)
            minimo = configs.get("porta_malas_familia", {}).get("minimo_litros", 0)
            if porta_malas >= minimo:
                score_parcial += 0.4
                fatores.append(f"porta-malas {porta_malas}L")

            # Verifica flexibilidade
            config_flexivel = configs.get("configuracao_flexivel", [])
            tem_flex = sum(1 for item in config_flexivel if any(item in opcional.lower() for opcional in opcionais))
            if tem_flex > 0:
                score_parcial += 0.2
                fatores.append("configuração flexível")

            if fatores:
                score = score_parcial
                razao = f"Praticidade: {' + '.join(fatores)}"
                ponto_forte = "Prático para uso diário familiar"

        elif criterio == "custo_beneficio_familia":
            score_parcial = 0.0
            fatores = []

            # Verifica preço justo
            preco = carro.get("preco", 0)
            faixa_ideal = configs.get("preco_justo", {}).get("faixa_ideal", [0, 999999])
            if faixa_ideal[0] <= preco <= faixa_ideal[1]:
                score_parcial += 0.5
                fatores.append(f"preço R$ {preco:,.0f}")

            # Verifica economia operacional
            consumo = carro.get("consumo", 0)
            if consumo >= 8:
                score_parcial += 0.3
                fatores.append(f"consumo {consumo} km/l")

            # Verifica marca confiável
            marca = carro.get("marca", "")
            marcas_familia = configs.get("marcas_familia", [])
            if marca in marcas_familia:
                score_parcial += 0.2
                fatores.append(f"marca {marca}")

            if fatores:
                score = score_parcial
                razao = f"Custo-benefício: {' + '.join(fatores)}"
                ponto_forte = "Bom investimento para família"

        elif criterio == "confiabilidade_transporte":
            score_parcial = 0.0
            fatores = []

            # Verifica marca confiável
            marca = carro.get("marca", "")
            marcas_familia = configs.get("marcas_familia", [])
            if marca in marcas_familia:
                score_parcial += 0.5
                fatores.append(f"marca {marca} confiável")

            # Verifica quilometragem
            km = carro.get("km", 0)
            km_adequada = configs.get("km_adequada", {}).get("maximo", 80000)
            if km <= km_adequada:
                score_parcial += 0.3
                fatores.append("baixa quilometragem")

            # Verifica histórico
            if carro.get("revisado") or carro.get("concessionaria"):
                score_parcial += 0.2
                fatores.append("histórico confiável")

            if fatores:
                score = score_parcial
                razao = f"Confiabilidade: {' + '.join(fatores)}"
                ponto_forte = "Transporte seguro e confiável"

        elif criterio == "tecnologia_seguranca_infantil":
            opcionais = carro.get("opcionais", [])
            travas_seguranca = configs.get("travas_seguranca", [])
            monitoramento = configs.get("monitoramento", [])

            tem_travas = sum(1 for item in travas_seguranca if any(item in opcional.lower() for opcional in opcionais))
            tem_monitoramento = sum(1 for item in monitoramento if any(item in opcional.lower() for opcional in opcionais))

            if tem_travas > 0 or tem_monitoramento > 0:
                score = 0.6 + min((tem_travas + tem_monitoramento) * 0.2, 0.4)
                razao = f"Segurança infantil: {tem_travas + tem_monitoramento} recursos"
                ponto_forte = "Proteção especial para crianças"

        elif criterio == "eficiencia_combustivel_familia":
            score_parcial = 0.0
            fatores = []

            # Verifica consumo adequado
            consumo = carro.get("consumo", 0)
            consumo_minimo = configs.get("consumo_familia", {}).get("cidade_minimo", 8)
            if consumo >= consumo_minimo:
                score_parcial += 0.7
                fatores.append(f"consumo {consumo} km/l")

            # Verifica motor eficiente
            cilindrada = carro.get("cilindrada", 0)
            motores_eficientes = configs.get("motores_eficientes", [])
            if cilindrada in motores_eficientes:
                score_parcial += 0.3
                fatores.append(f"motor {cilindrada} eficiente")

            if fatores:
                score = score_parcial
                razao = f"Eficiência: {' + '.join(fatores)}"
                ponto_forte = "Econômico no uso familiar"

        elif criterio == "versatilidade_configuracao":
            opcionais = carro.get("opcionais", [])
            flexibilidade = configs.get("flexibilidade_interior", [])
            facilidades = configs.get("facilidades_familia", [])

            tem_flexibilidade = sum(1 for item in flexibilidade if any(item in opcional.lower() for opcional in opcionais))
            tem_facilidades = sum(1 for item in facilidades if any(item in opcional.lower() for opcional in opcionais))

            if tem_flexibilidade > 0 or tem_facilidades > 0:
                score = 0.5 + min((tem_flexibilidade + tem_facilidades) * 0.25, 0.5)
                razao = f"Versatilidade: {tem_flexibilidade + tem_facilidades} recursos"
                ponto_forte = "Adaptável às necessidades da família"

        # Critérios adicionais podem ser implementados aqui

        return score, razao, ponto_forte

    @classmethod
    def gerar_sugestoes_uso(cls, questionario: QuestionarioBusca) -> List[str]:
        """Gera sugestões personalizadas baseadas no uso principal"""
        sugestoes = []

        for uso in questionario.uso_principal:
            if uso == "urbano":
                sugestoes.extend(
                    [
                        "🚗 Para cidade: priorize carros compactos (Hatch/Sedan pequeno)",
                        "⛽ Economia urbana: busque consumo ≥12 km/l na cidade",
                        "🅿️ Facilidade estacionamento: carros ≤4,2m são ideais",
                        "📱 Conectividade: central multimídia + Bluetooth são essenciais",
                        "🛡️ Segurança urbana: ABS + airbag duplo + controle estabilidade",
                        "🔧 Manutenção: Chevrolet, Fiat, VW têm peças acessíveis",
                        "💡 Primeiro carro: foque em economia + segurança básica",
                        "💼 Executivo: tecnologia + conforto valorizam o veículo",
                        "👴 Aposentado: simplicidade + confiabilidade são prioridade",
                    ]
                )

            elif uso == "viagem":
                sugestoes.extend(
                    [
                        "🚗 Viagens longas: SUV/Sedan Médio com conforto + espaço",
                        "🛋️ Conforto essencial: bancos ajustáveis + climatização dupla",
                        "⚡ Desempenho estrada: motor ≥1.4L + controle estabilidade",
                        "🧡 Capacidade: porta-malas ≥400L + 5-7 passageiros",
                        "⛽ Economia estrada: busque ≥10 km/l na rodovia",
                        "📱 Tecnologia viagem: GPS + Android Auto + USB múltiplas",
                        "🔍 Turismo lazer: conforto + entretenimento são prioridade",
                        "💼 Viagem trabalho: confiabilidade + economia operacional",
                        "🏔️ Road trip: potência + segurança ativa + autonomia",
                        "👨‍👩‍👧‍👦 Viagem família: espaço + segurança + praticidade",
                    ]
                )

            elif uso == "trabalho":
                sugestoes.extend(
                    [
                        "💰 Foque em custo-benefício: veículos usados têm menor depreciação",
                        "⛽ Economia de combustível é fundamental - busque motores 1.0 a 1.6",
                        "🔧 Priorize marcas com baixo custo de manutenção (Chevrolet, Fiat, VW)",
                        "📱 Para apps: ano 2012+, 4 portas, ar-condicionado obrigatório",
                        "📦 Autônomos: considere espaço para ferramentas/equipamentos",
                        "🚚 Entregas: vans/pickups para maior capacidade de carga",
                        "📈 Concessionárias oferecem garantia e histórico transparente",
                        "🏦 Facilidades de financiamento para MEI/CNPJ disponíveis",
                        "🌱 Considere híbridos/elétricos para metas de sustentabilidade",
                    ]
                )

            elif uso == "familia":
                sugestoes.extend(
                    [
                        "👨‍👩‍👧‍👦 Família: SUV/Minivan com segurança + espaço + praticidade",
                        "🛡️ Segurança máxima: airbags múltiplos + ISOFIX + 4+ estrelas",
                        "🚗 Espaço ideal: 5-7 lugares + porta-malas ≥350L + fácil acesso",
                        "💰 Custo-benefício: R$ 30-80k + baixa manutenção + consumo ≥8 km/l",
                        "🔍 Praticidade: 4 portas + vidros elétricos + configuração flexível",
                        "🎆 Tecnologia infantil: travas segurança + ISOFIX + sensores",
                        "👶 Crianças pequenas: priorizar airbags + ISOFIX + acesso fácil",
                        "👨‍👩‍👧‍👦 Família grande: 7 lugares + espaço amplo + baixo custo",
                        "🏃 Atividades esportivas: versatilidade + porta-malas grande",
                        "🚗 Confiabilidade: Toyota/Honda/VW + baixa km + histórico",
                    ]
                )

        # Remove duplicatas mantendo ordem
        return list(dict.fromkeys(sugestoes))

    @classmethod
    def get_criterios_por_uso(cls, uso: str) -> Dict[str, Any]:
        """Retorna os critérios técnicos para um tipo de uso específico"""
        return cast(Dict[str, Any], cls.CRITERIOS_USO.get(uso, {}))

    @classmethod
    def get_descricao_uso(cls, uso: str) -> str:
        """Retorna descrição detalhada de um tipo de uso"""
        descricoes = {
            "urbano": "Uso urbano: economia combustível (≥12 km/l), facilidade manobra (≤4,2m), tecnologia (conectividade), segurança (ABS+airbag). Subsegmentos: primeiro carro, executivo, aposentado, família urbana",
            "viagem": "Viagens longas: conforto (bancos+clima), desempenho estrada (≥1.4L), espaço (400L+), economia (≥10 km/l), tecnologia (GPS+conectividade). Subsegmentos: turismo, trabalho, road trip, família",
            "trabalho": "Uso profissional: economia combustível, confiabilidade, baixo custo manutenção, espaço adequado",
            "familia": "Uso familiar: segurança máxima (airbags+ISOFIX), espaço (5-7 lugares+350L), praticidade (4 portas+flex), custo-benefício (R$ 30-80k+≥8 km/l). Subsegmentos: crianças pequenas, família grande, atividades esportivas",
        }
        return descricoes.get(uso, uso)
