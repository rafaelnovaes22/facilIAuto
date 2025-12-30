"""
Maintenance Agent - Agente especializado em cálculo de score de manutenção

Calcula score de manutenção baseado em:
- Custo real de manutenção por marca/modelo
- Idade do veículo (penalização progressiva)
- Quilometragem (desgaste acumulado)
- Índice de confiabilidade da marca
- Recalls conhecidos (penalização)
- Problemas típicos do modelo
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile
from services.agents.base_agent import BaseAgent
from services.car_metrics import CarMetricsCalculator


logger = logging.getLogger(__name__)


class MaintenanceAgent(BaseAgent):
    """
    Agente especializado em calcular score de manutenção

    Usa dados reais de custos por marca e ajusta por idade, quilometragem
    e confiabilidade para calcular score mais preciso.
    """

    # Custos de manutenção por marca (R$/ano) - Referência
    # Reutiliza dados do CarMetricsCalculator
    MAINTENANCE_COST_BY_BRAND = {
        # Econômicas (< R$ 2.500/ano)
        "Toyota": 2200,
        "Honda": 2400,
        "Hyundai": 2000,
        "Kia": 1900,

        # Médias (R$ 2.500-3.500/ano)
        "Volkswagen": 2800,
        "Ford": 2700,
        "Chevrolet": 2600,
        "Nissan": 2900,
        "Fiat": 2500,
        "Renault": 3200,

        # Caras (R$ 3.500-5.000/ano)
        "Peugeot": 3500,
        "Jeep": 4000,
        "Citroën": 3300,
        "Mitsubishi": 3400,

        # Premium (> R$ 5.000/ano)
        "BMW": 6500,
        "Mercedes": 7000,
        "Audi": 6800,
        "Volvo": 6200,
        "Land Rover": 8000,

        # Default
        "DEFAULT": 2800
    }

    # Índice de confiabilidade por marca (0-1)
    # Maior = mais confiável = menos problemas
    BRAND_RELIABILITY = {
        "Toyota": 0.95,
        "Honda": 0.92,
        "Hyundai": 0.88,
        "Kia": 0.85,
        "Nissan": 0.83,
        "Mazda": 0.90,

        "Volkswagen": 0.78,
        "Ford": 0.75,
        "Chevrolet": 0.72,
        "Fiat": 0.70,
        "Renault": 0.68,
        "Peugeot": 0.65,

        "BMW": 0.70,
        "Mercedes": 0.68,
        "Audi": 0.72,

        "Jeep": 0.60,
        "Land Rover": 0.55,

        "DEFAULT": 0.75
    }

    # Problemas conhecidos por marca (reduz score)
    # Lista de problemas típicos que aumentam custo de manutenção
    KNOWN_ISSUES = {
        "Volkswagen": ["Caixa DSG (dupla embreagem)", "Módulo eletrônico"],
        "Ford": ["Transmissão PowerShift", "Sistema elétrico"],
        "Jeep": ["Problemas eletrônicos", "Transmissão automática"],
        "Fiat": ["Embreagem", "Sistema elétrico"],
        "Renault": ["Caixa de câmbio", "Sensor ABS"],
        "Peugeot": ["Caixa automática", "Sistema eletrônico"],
    }

    def __init__(self, cache_manager=None):
        """
        Inicializa o MaintenanceAgent

        Args:
            cache_manager: Gerenciador de cache (opcional)
        """
        super().__init__(cache_manager, name="MaintenanceAgent")
        self.car_metrics = CarMetricsCalculator()
        self.current_year = datetime.now().year

    async def calculate_score(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula score de manutenção (0-1)

        Fórmula:
        - 40% custo anual normalizado (R$ 1.500-8.000)
        - 30% confiabilidade da marca
        - 20% penalização por idade/quilometragem
        - 10% problemas conhecidos

        Args:
            car: Veículo a ser avaliado
            profile: Perfil do usuário

        Returns:
            float: Score normalizado entre 0.0 e 1.0
                  (maior score = menor custo de manutenção)
        """
        try:
            # 1. Calcular custo anual de manutenção
            annual_cost = self._calculate_annual_cost(
                car.marca,
                car.ano,
                car.quilometragem
            )

            # 2. Obter confiabilidade da marca
            reliability = self._get_brand_reliability(car.marca)

            # 3. Calcular penalização por desgaste
            wear_penalty = self._calculate_wear_penalty(
                car.ano,
                car.quilometragem
            )

            # 4. Calcular penalização por problemas conhecidos
            issues_penalty = self._get_known_issues_penalty(car.marca)

            # 5. Normalizar componentes
            cost_score = self._normalize_cost(annual_cost)
            reliability_score = reliability
            wear_score = 1.0 - wear_penalty
            issues_score = 1.0 - issues_penalty

            # 6. Calcular score final (ponderado)
            final_score = (
                0.40 * cost_score +
                0.30 * reliability_score +
                0.20 * wear_score +
                0.10 * issues_score
            )

            logger.debug(
                f"[MaintenanceAgent] {car.marca} {car.modelo}: "
                f"cost=R${annual_cost:.0f}/ano, "
                f"reliability={reliability:.2f}, "
                f"wear_penalty={wear_penalty:.2f}, "
                f"final={final_score:.2f}"
            )

            return max(0.0, min(1.0, final_score))

        except Exception as e:
            logger.error(f"[MaintenanceAgent] Erro para {car.nome}: {e}")
            return self._get_fallback_score(car)

    def _calculate_annual_cost(
        self,
        marca: str,
        ano: int,
        quilometragem: int
    ) -> float:
        """
        Calcula custo anual de manutenção

        Considera:
        - Custo base da marca
        - Aumento por idade (10% ao ano)
        - Aumento por quilometragem

        Args:
            marca: Marca do veículo
            ano: Ano do veículo
            quilometragem: Km rodados

        Returns:
            float: Custo estimado em R$/ano
        """
        # 1. Custo base da marca
        base_cost = self.MAINTENANCE_COST_BY_BRAND.get(
            marca,
            self.MAINTENANCE_COST_BY_BRAND["DEFAULT"]
        )

        # 2. Ajuste por idade (10% ao ano)
        age = self.current_year - ano
        age_multiplier = 1.0 + (age * 0.10)

        # 3. Ajuste por quilometragem
        km_multiplier = self._get_mileage_multiplier(quilometragem)

        # 4. Custo final
        annual_cost = base_cost * age_multiplier * km_multiplier

        return annual_cost

    def _get_mileage_multiplier(self, quilometragem: int) -> float:
        """
        Multiplicador por quilometragem

        Alto km = mais desgaste = maior custo

        Args:
            quilometragem: Km rodados

        Returns:
            float: Multiplicador (1.0 = sem ajuste)
        """
        if quilometragem < 30000:
            return 1.0  # Novo, sem desgaste
        elif quilometragem < 60000:
            return 1.1  # Baixo desgaste (+10%)
        elif quilometragem < 100000:
            return 1.2  # Médio desgaste (+20%)
        elif quilometragem < 150000:
            return 1.4  # Alto desgaste (+40%)
        else:
            return 1.7  # Muito alto desgaste (+70%)

    def _get_brand_reliability(self, marca: str) -> float:
        """
        Obtém índice de confiabilidade da marca

        Args:
            marca: Marca do veículo

        Returns:
            float: Índice 0-1 (1 = muito confiável)
        """
        return self.BRAND_RELIABILITY.get(
            marca,
            self.BRAND_RELIABILITY["DEFAULT"]
        )

    def _calculate_wear_penalty(
        self,
        ano: int,
        quilometragem: int
    ) -> float:
        """
        Calcula penalização por desgaste (idade + km)

        Args:
            ano: Ano do veículo
            quilometragem: Km rodados

        Returns:
            float: Penalização 0-1 (0 = sem penalização, 1 = máxima)
        """
        age = self.current_year - ano

        # Penalização por idade (até 0.4)
        if age <= 2:
            age_penalty = 0.0
        elif age <= 5:
            age_penalty = 0.1
        elif age <= 10:
            age_penalty = 0.2
        elif age <= 15:
            age_penalty = 0.3
        else:
            age_penalty = 0.4

        # Penalização por quilometragem (até 0.4)
        if quilometragem < 50000:
            km_penalty = 0.0
        elif quilometragem < 100000:
            km_penalty = 0.1
        elif quilometragem < 150000:
            km_penalty = 0.2
        elif quilometragem < 200000:
            km_penalty = 0.3
        else:
            km_penalty = 0.4

        # Combinar penalizações (média)
        total_penalty = (age_penalty + km_penalty) / 2

        return min(1.0, total_penalty)

    def _get_known_issues_penalty(self, marca: str) -> float:
        """
        Penalização por problemas conhecidos da marca

        Marcas com histórico de problemas recebem penalização

        Args:
            marca: Marca do veículo

        Returns:
            float: Penalização 0-0.3 (0 = sem problemas, 0.3 = muitos problemas)
        """
        if marca not in self.KNOWN_ISSUES:
            return 0.0

        # Penalização baseada no número de problemas conhecidos
        num_issues = len(self.KNOWN_ISSUES[marca])

        if num_issues == 0:
            return 0.0
        elif num_issues == 1:
            return 0.1
        elif num_issues == 2:
            return 0.2
        else:
            return 0.3

    def _normalize_cost(self, annual_cost: float) -> float:
        """
        Normaliza custo anual para score 0-1

        Invertido: menor custo = maior score

        Args:
            annual_cost: Custo anual em R$

        Returns:
            float: Score 0-1
        """
        MIN_COST = 1500   # R$ 1.500/ano (muito econômico)
        MAX_COST = 8000   # R$ 8.000/ano (muito caro)

        if annual_cost <= MIN_COST:
            return 1.0
        elif annual_cost >= MAX_COST:
            return 0.0
        else:
            # Inverter: custo baixo = score alto
            normalized = 1.0 - (
                (annual_cost - MIN_COST) / (MAX_COST - MIN_COST)
            )
            return max(0.0, min(1.0, normalized))

    def _get_fallback_score(self, car: Car) -> float:
        """
        Score de fallback quando cálculo falha

        Tenta usar índice de confiabilidade ou retorna 0.5

        Args:
            car: Veículo

        Returns:
            float: Score de fallback
        """
        # Tentar usar confiabilidade da marca
        reliability = self._get_brand_reliability(car.marca)
        if reliability:
            return reliability

        return 0.5

    def _get_cache_ttl(self) -> int:
        """
        TTL do cache: 30 dias (custos de manutenção são estáveis)

        Returns:
            int: TTL em segundos
        """
        return 30 * 24 * 3600  # 30 dias

    def get_maintenance_breakdown(self, car: Car) -> Dict:
        """
        Retorna detalhamento do cálculo de manutenção (para debug/UI)

        Args:
            car: Veículo

        Returns:
            dict: Detalhamento com custos e scores
        """
        annual_cost = self._calculate_annual_cost(
            car.marca,
            car.ano,
            car.quilometragem
        )

        reliability = self._get_brand_reliability(car.marca)
        wear_penalty = self._calculate_wear_penalty(car.ano, car.quilometragem)
        issues_penalty = self._get_known_issues_penalty(car.marca)

        return {
            "custo_anual_estimado": annual_cost,
            "custo_mensal_estimado": annual_cost / 12,
            "confiabilidade_marca": reliability,
            "penalizacao_desgaste": wear_penalty,
            "penalizacao_problemas": issues_penalty,
            "problemas_conhecidos": self.KNOWN_ISSUES.get(car.marca, []),
            "idade_anos": self.current_year - car.ano,
            "quilometragem": car.quilometragem,
            "custo_base_marca": self.MAINTENANCE_COST_BY_BRAND.get(
                car.marca,
                self.MAINTENANCE_COST_BY_BRAND["DEFAULT"]
            )
        }
