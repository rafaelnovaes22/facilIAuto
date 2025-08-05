"""
Processador Avançado de Critérios de Uso Principal do Veículo

Este módulo implementa os critérios detalhados do relatório de uso principal,
transformando perfis de uso em scores técnicos específicos baseados nas
características dos veículos.

Perfis suportados:
- Urbano: compacto, econômico, tecnológico
- Viagem: espaçoso, potente, confortável, seguro
- Trabalho/Negócios: versátil, durável, custo-benefício
- Família: espaçoso, seguro, confortável, prático
"""

from typing import Dict, List, Any, Tuple
from app.models import QuestionarioBusca

class UsoMatcher:
    """Classe responsável por calcular scores de compatibilidade baseados no uso principal"""
    
    # Pesos para cada tipo de uso (soma deve ser <= 25% do score total)
    PESO_USO_PRINCIPAL = 25.0
    
    # Critérios técnicos por tipo de uso
    CRITERIOS_USO = {
        "urbano": {
            "dimensoes_compactas": {"peso": 8, "categorias_ideais": ["Hatch", "Sedan Compacto"]},
            "baixo_consumo": {"peso": 7, "cilindrada_max": 1.4},
            "tecnologia": {"peso": 5, "tecnologias_valorizadas": ["conectividade", "sensores", "camera"]},
            "sustentabilidade": {"peso": 3, "tipos_motor": ["híbrido", "elétrico", "flex"]},
            "facilidade_estacionamento": {"peso": 2, "categoria_boost": "Hatch"}
        },
        
        "viagem": {
            "espaco_interno": {"peso": 8, "categorias_ideais": ["SUV", "Sedan Médio", "SUV Médio"]},
            "porta_malas": {"peso": 6, "espaco_minimo": "medio"},
            "desempenho_seguranca": {"peso": 6, "potencia_minima": "media", "seguranca_minima": 4},
            "conforto": {"peso": 3, "opcionais_valorizados": ["ar_condicionado", "direcao_assistida"]},
            "suspensao_robusta": {"peso": 2, "categorias_ideais": ["SUV"]}
        },
        
        "trabalho": {
            "versatilidade": {"peso": 7, "categorias_ideais": ["SUV", "Pickup", "Van"]},
            "capacidade_carga": {"peso": 8, "espaco_minimo": "muito"},
            "durabilidade": {"peso": 5, "km_maximo": 80000, "idade_maxima": 8},
            "custo_beneficio": {"peso": 3, "prioriza_economia": True},
            "robustez": {"peso": 2, "categorias_boost": ["Pickup", "SUV"]}
        },
        
        "familia": {
            "espaco_passageiros": {"peso": 9, "pessoas_minimas": 5},
            "seguranca_avancada": {"peso": 8, "seguranca_minima": 4},
            "conforto_entretenimento": {"peso": 4, "opcionais_familia": ["ar_condicionado", "vidros_eletricos"]},
            "facilidade_acesso": {"peso": 2, "categorias_ideais": ["SUV", "Minivan"]},
            "praticidade": {"peso": 2, "porta_malas_minimo": "medio"}
        }
    }
    
    @classmethod
    def calcular_score_uso_principal(cls, questionario: QuestionarioBusca, carro: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
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
    def _avaliar_uso_especifico(cls, uso: str, carro: Dict[str, Any], peso_uso: float, questionario: QuestionarioBusca) -> Tuple[float, List[str], List[str]]:
        """Avalia um tipo de uso específico"""
        criterios = cls.CRITERIOS_USO[uso]
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
    def _avaliar_criterio(cls, criterio: str, configs: Dict[str, Any], carro: Dict[str, Any], questionario: QuestionarioBusca) -> Tuple[float, str, str]:
        """Avalia um critério específico"""
        score = 0.0
        razao = ""
        ponto_forte = ""
        
        if criterio == "dimensoes_compactas":
            if carro.get("categoria") in configs.get("categorias_ideais", []):
                score = 1.0
                razao = f"Categoria {carro['categoria']} ideal para uso urbano"
                ponto_forte = "Fácil de manobrar e estacionar"
        
        elif criterio == "baixo_consumo":
            # Simula verificação de cilindrada (seria ideal ter essa info no banco)
            if carro.get("potencia_desejada") == "economica":
                score = 1.0
                razao = "Motor econômico reduz custos urbanos"
                ponto_forte = "Baixo consumo de combustível"
        
        elif criterio == "tecnologia":
            opcionais = carro.get("opcionais", [])
            tech_count = sum(1 for tech in configs.get("tecnologias_valorizadas", []) 
                           if any(tech in opcional.lower() for opcional in opcionais))
            if tech_count > 0:
                score = min(tech_count / len(configs.get("tecnologias_valorizadas", [])), 1.0)
                razao = f"Tecnologias presentes: {tech_count} itens"
                ponto_forte = "Conectividade e assistência"
        
        elif criterio == "espaco_interno":
            if carro.get("categoria") in configs.get("categorias_ideais", []):
                score = 1.0
                razao = f"{carro['categoria']} oferece bom espaço interno"
                ponto_forte = "Conforto em viagens longas"
        
        elif criterio == "porta_malas":
            if carro.get("espaco_carga") == configs.get("espaco_minimo") or carro.get("espaco_carga") == "muito":
                score = 1.0
                razao = "Porta-malas adequado para bagagens de viagem"
                ponto_forte = "Espaço suficiente para bagagens"
        
        elif criterio == "desempenho_seguranca":
            score_parcial = 0.0
            fatores = []
            
            # Verifica potência
            if carro.get("potencia_desejada") in ["media", "alta"]:
                score_parcial += 0.5
                fatores.append("boa potência")
            
            # Verifica segurança
            if carro.get("seguranca", 0) >= configs.get("seguranca_minima", 0):
                score_parcial += 0.5
                fatores.append("segurança avançada")
            
            if fatores:
                score = score_parcial
                razao = f"Oferece {' e '.join(fatores)}"
                ponto_forte = "Seguro e potente para rodovia"
        
        elif criterio == "versatilidade":
            if carro.get("categoria") in configs.get("categorias_ideais", []):
                score = 1.0
                razao = f"{carro['categoria']} versátil para trabalho"
                ponto_forte = "Adaptável a diferentes necessidades"
        
        elif criterio == "capacidade_carga":
            if carro.get("espaco_carga") == configs.get("espaco_minimo"):
                score = 1.0
                razao = "Grande capacidade de carga"
                ponto_forte = "Ideal para transportar equipamentos"
        
        elif criterio == "durabilidade":
            score_parcial = 0.0
            fatores = []
            
            # Verifica quilometragem
            km = carro.get("km", 0)
            if km <= configs.get("km_maximo", 100000):
                score_parcial += 0.5
                fatores.append("baixa quilometragem")
            
            # Verifica idade (ano atual - ano do carro)
            from datetime import datetime
            idade = datetime.now().year - carro.get("ano", 2020)
            if idade <= configs.get("idade_maxima", 10):
                score_parcial += 0.5
                fatores.append("veículo relativamente novo")
            
            if fatores:
                score = score_parcial
                razao = f"Durabilidade: {' e '.join(fatores)}"
                ponto_forte = "Veículo confiável para uso profissional"
        
        elif criterio == "espaco_passageiros":
            # Verifica se comporta o número de pessoas desejado
            if questionario.pessoas_transportar <= 5:  # Carros normais
                score = 1.0
                razao = f"Comporta {questionario.pessoas_transportar} pessoas confortavelmente"
                ponto_forte = "Espaço adequado para toda família"
        
        elif criterio == "seguranca_avancada":
            seguranca = carro.get("seguranca", 0)
            if seguranca >= configs.get("seguranca_minima", 0):
                score = 1.0
                razao = f"Segurança {seguranca}/5 estrelas"
                ponto_forte = "Protege bem a família"
        
        elif criterio == "conforto_entretenimento":
            opcionais = carro.get("opcionais", [])
            conforto_count = sum(1 for item in configs.get("opcionais_familia", []) 
                               if any(item in opcional.lower() for opcional in opcionais))
            if conforto_count > 0:
                score = min(conforto_count / len(configs.get("opcionais_familia", [])), 1.0)
                razao = f"Itens de conforto: {conforto_count}"
                ponto_forte = "Viagem confortável para família"
        
        # Critérios adicionais podem ser implementados aqui
        
        return score, razao, ponto_forte
    
    @classmethod
    def gerar_sugestoes_uso(cls, questionario: QuestionarioBusca) -> List[str]:
        """Gera sugestões personalizadas baseadas no uso principal"""
        sugestoes = []
        
        for uso in questionario.uso_principal:
            if uso == "urbano":
                sugestoes.extend([
                    "💡 Para uso urbano, considere carros compactos com boa economia",
                    "🅿️ Veículos menores facilitam estacionamento em centros urbanos",
                    "🔋 Modelos híbridos são ideais para trânsito stop-and-go"
                ])
            
            elif uso == "viagem":
                sugestoes.extend([
                    "🧳 Para viagens, priorize espaço do porta-malas e conforto",
                    "🛡️ Segurança é fundamental em rodovias - verifique airbags e controles",
                    "⚡ Potência adequada garante segurança em ultrapassagens"
                ])
            
            elif uso == "trabalho":
                sugestoes.extend([
                    "🔧 Para trabalho, considere durabilidade e custo de manutenção",
                    "📦 Verifique capacidade de carga se transporta equipamentos",
                    "💰 SUVs e pickups oferecem boa versatilidade profissional"
                ])
            
            elif uso == "familia":
                sugestoes.extend([
                    "👨‍👩‍👧‍👦 Para família, segurança e espaço são prioridades",
                    "🚗 SUVs facilitam acesso de crianças e idosos",
                    "❄️ Ar-condicionado é essencial para conforto familiar"
                ])
        
        # Remove duplicatas mantendo ordem
        return list(dict.fromkeys(sugestoes))

    @classmethod
    def get_criterios_por_uso(cls, uso: str) -> Dict[str, Any]:
        """Retorna os critérios técnicos para um tipo de uso específico"""
        return cls.CRITERIOS_USO.get(uso, {})
    
    @classmethod
    def get_descricao_uso(cls, uso: str) -> str:
        """Retorna descrição detalhada de um tipo de uso"""
        descricoes = {
            "urbano": "Uso em cidade: trânsito, estacionamento, economia de combustível",
            "viagem": "Viagens longas: conforto, segurança, espaço para bagagens",
            "trabalho": "Uso profissional: durabilidade, capacidade de carga, custo-benefício",
            "familia": "Uso familiar: segurança, espaço, conforto para todos os ocupantes"
        }
        return descricoes.get(uso, uso)