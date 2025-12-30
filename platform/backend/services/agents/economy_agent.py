"""
Economy Agent - Agente especializado em cálculo de score de economia

Calcula score de economia baseado em:
- Consumo REAL do veículo (km/L)
- Preços atualizados de combustível por região
- Custo mensal estimado de combustível
- Tipo de combustível (flex, gasolina, etanol, diesel, elétrico)
- Normalização por categoria (comparar Hatch com Hatch, SUV com SUV)
"""

import logging
from typing import Dict, Optional

from models.car import Car
from models.user_profile import UserProfile
from services.agents.base_agent import BaseAgent
from services.fuel_price_service import fuel_price_service


logger = logging.getLogger(__name__)


class EconomyAgent(BaseAgent):
    """
    Agente especializado em calcular score de economia

    Usa consumo REAL do veículo e preços atualizados de combustível
    para calcular score mais preciso que o genérico.
    """

    # Referências de consumo por categoria (km/L)
    # Usadas para normalização: comparar cada carro com a média da categoria
    CATEGORY_FUEL_EFFICIENCY = {
        "Hatch": {"min": 10.0, "avg": 13.5, "max": 18.0},
        "Sedan Compacto": {"min": 9.5, "avg": 13.0, "max": 17.0},
        "Sedan": {"min": 8.5, "avg": 11.5, "max": 15.0},
        "SUV Compacto": {"min": 8.0, "avg": 11.0, "max": 14.0},
        "SUV": {"min": 6.5, "avg": 9.5, "max": 12.5},
        "Pickup": {"min": 6.0, "avg": 9.0, "max": 12.0},
        "Pickup Grande": {"min": 5.5, "avg": 8.0, "max": 11.0},
        "Van": {"min": 5.5, "avg": 8.5, "max": 11.5},
        "Furgão": {"min": 6.0, "avg": 9.0, "max": 12.0},
        "Crossover": {"min": 8.5, "avg": 11.5, "max": 15.0},
        "Minivan": {"min": 7.0, "avg": 10.0, "max": 13.0},
        "Compacto": {"min": 9.5, "avg": 12.5, "max": 17.0},
    }

    # Preços médios por tipo de combustível (fallback)
    # Usados quando não conseguimos obter preço real
    FUEL_TYPE_PRICES = {
        "Gasolina": 6.17,
        "Etanol": 4.50,
        "Diesel": 6.00,
        "Flex": 6.17,  # Assume gasolina para Flex
        "GNV": 4.00,
        "Elétrico": 0.80,  # R$/kWh equivalente
        "Híbrido": 5.00,  # Média ponderada
    }

    # Bonus por tipo de combustível (econômicos ganham mais)
    FUEL_TYPE_BONUS = {
        "Flex": 1.0,      # Flexível = melhor
        "Etanol": 0.9,    # Econômico mas menos potente
        "Gasolina": 0.7,  # Mais caro
        "Diesel": 0.8,    # Econômico para comerciais
        "GNV": 1.0,       # Muito econômico
        "Elétrico": 1.0,  # Mais econômico
        "Híbrido": 1.0    # Muito econômico
    }

    def __init__(self, cache_manager=None):
        """
        Inicializa o EconomyAgent

        Args:
            cache_manager: Gerenciador de cache (opcional)
        """
        super().__init__(cache_manager, name="EconomyAgent")
        self.fuel_price_service = fuel_price_service

    async def calculate_score(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula score de economia (0-1) baseado em consumo real

        Fórmula:
        - 60% consumo de combustível normalizado por categoria
        - 30% custo mensal de combustível
        - 10% bonus por tipo de combustível

        Args:
            car: Veículo a ser avaliado
            profile: Perfil do usuário

        Returns:
            float: Score normalizado entre 0.0 e 1.0
        """
        try:
            # 1. Obter consumo real do veículo
            fuel_efficiency = self._get_fuel_efficiency(car)

            # 2. Obter preço de combustível
            fuel_price = self._get_fuel_price(car, profile)

            # 3. Estimar km mensal do usuário
            monthly_km = self._estimate_monthly_km(profile)

            # 4. Calcular custo mensal de combustível
            monthly_cost = (monthly_km / fuel_efficiency) * fuel_price

            # 5. Normalizar componentes
            consumption_score = self._normalize_fuel_efficiency(
                fuel_efficiency,
                car.categoria
            )

            cost_score = self._normalize_fuel_cost(monthly_cost, profile)

            fuel_type_bonus = self._get_fuel_type_bonus(car.combustivel)

            # 6. Calcular score final (ponderado)
            final_score = (
                0.60 * consumption_score +
                0.30 * cost_score +
                0.10 * fuel_type_bonus
            )

            logger.debug(
                f"[EconomyAgent] {car.marca} {car.modelo}: "
                f"consumption={fuel_efficiency:.1f}km/L, "
                f"monthly_cost=R${monthly_cost:.2f}, "
                f"consumption_score={consumption_score:.2f}, "
                f"cost_score={cost_score:.2f}, "
                f"final={final_score:.2f}"
            )

            return max(0.0, min(1.0, final_score))

        except Exception as e:
            logger.error(f"[EconomyAgent] Erro para {car.nome}: {e}")
            # Retornar fallback
            return self._get_fallback_score(car)

    def _get_fuel_efficiency(self, car: Car) -> float:
        """
        Obtém consumo de combustível (km/L)

        Prioridade:
        1. consumo_cidade (mais representativo para uso urbano)
        2. consumo_estrada
        3. consumo (média ou único valor)
        4. Estimativa por categoria (fallback)

        Args:
            car: Veículo

        Returns:
            float: Consumo em km/L
        """
        # Prioridade 1: Consumo cidade
        if hasattr(car, 'consumo_cidade') and car.consumo_cidade:
            return float(car.consumo_cidade)

        # Prioridade 2: Consumo estrada
        if hasattr(car, 'consumo_estrada') and car.consumo_estrada:
            return float(car.consumo_estrada)

        # Prioridade 3: Consumo genérico
        if hasattr(car, 'consumo') and car.consumo:
            return float(car.consumo)

        # Fallback: Estimativa por categoria
        category_ref = self.CATEGORY_FUEL_EFFICIENCY.get(
            car.categoria,
            {"avg": 11.0}
        )
        return category_ref["avg"]

    def _get_fuel_price(self, car: Car, profile: UserProfile) -> float:
        """
        Obtém preço de combustível por região

        Args:
            car: Veículo
            profile: Perfil do usuário

        Returns:
            float: Preço em R$/L
        """
        # Obter estado do perfil
        state = getattr(profile, 'state', 'SP')

        # Buscar preço atualizado (gasolina sempre, para normalização)
        try:
            price = self.fuel_price_service.get_current_price(state)

            # Ajustar por tipo de combustível
            if car.combustivel in self.FUEL_TYPE_PRICES:
                # Para Etanol, usar proporção típica (70% do preço da gasolina)
                if car.combustivel == "Etanol":
                    price = price * 0.70
                # Para Diesel, usar preço específico
                elif car.combustivel == "Diesel":
                    price = self.FUEL_TYPE_PRICES["Diesel"]
                # Para GNV, usar preço específico
                elif car.combustivel == "GNV":
                    price = self.FUEL_TYPE_PRICES["GNV"]
                # Para Elétrico, converter kWh para equivalente
                elif car.combustivel == "Elétrico":
                    price = self.FUEL_TYPE_PRICES["Elétrico"]
                # Flex e Gasolina usam preço da gasolina

            return price

        except Exception as e:
            logger.warning(f"[EconomyAgent] Erro ao buscar preço: {e}")
            # Fallback: usar preço padrão do tipo
            return self.FUEL_TYPE_PRICES.get(car.combustivel, 6.17)

    def _estimate_monthly_km(self, profile: UserProfile) -> float:
        """
        Estima quilometragem mensal do usuário

        Args:
            profile: Perfil do usuário

        Returns:
            float: Km estimado por mês
        """
        # Se perfil tem km mensal explícito, usar
        if hasattr(profile, 'monthly_km') and profile.monthly_km:
            return float(profile.monthly_km)

        # Estimativa por uso principal
        usage_km_estimates = {
            "familia": 1200,              # Viagens casa-trabalho + fim de semana
            "trabalho": 1500,             # Uso diário intenso
            "comercial": 2500,            # Operação comercial
            "primeiro_carro": 800,        # Uso moderado
            "lazer": 600,                 # Uso esporádico
            "transporte_passageiros": 3000,  # Uber/99 - alto km
        }

        uso = profile.uso_principal
        return usage_km_estimates.get(uso, 1000)  # Padrão: 1000 km/mês

    def _normalize_fuel_efficiency(
        self,
        efficiency: float,
        categoria: str
    ) -> float:
        """
        Normaliza consumo para 0-1 baseado na categoria

        Compara o consumo do carro com a faixa típica da categoria.
        Um Hatch fazendo 15 km/L é ótimo, mas um SUV fazendo 15 km/L
        é excepcional.

        Args:
            efficiency: Consumo em km/L
            categoria: Categoria do veículo

        Returns:
            float: Score normalizado 0-1 (maior consumo = maior score)
        """
        # Obter referências da categoria
        category_ref = self.CATEGORY_FUEL_EFFICIENCY.get(
            categoria,
            {"min": 8.0, "avg": 11.0, "max": 15.0}
        )

        min_eff = category_ref["min"]
        max_eff = category_ref["max"]
        avg_eff = category_ref["avg"]

        # Casos extremos
        if efficiency >= max_eff:
            return 1.0  # Excelente para a categoria
        elif efficiency <= min_eff:
            return 0.2  # Muito ruim para a categoria

        # Normalização não-linear
        # Acima da média: cresce mais rápido
        # Abaixo da média: decresce mais devagar
        if efficiency >= avg_eff:
            # Mapear avg→max para 0.6→1.0
            normalized = 0.6 + 0.4 * (
                (efficiency - avg_eff) / (max_eff - avg_eff)
            )
        else:
            # Mapear min→avg para 0.2→0.6
            normalized = 0.2 + 0.4 * (
                (efficiency - min_eff) / (avg_eff - min_eff)
            )

        return max(0.0, min(1.0, normalized))

    def _normalize_fuel_cost(
        self,
        monthly_cost: float,
        profile: UserProfile
    ) -> float:
        """
        Normaliza custo mensal para 0-1

        Considera:
        - Custo absoluto (R$200-800/mês)
        - Percentual da renda (se disponível)

        Args:
            monthly_cost: Custo mensal em R$
            profile: Perfil do usuário

        Returns:
            float: Score normalizado 0-1 (menor custo = maior score)
        """
        # Referências de custo mensal
        MIN_COST = 200   # R$ 200/mês (muito econômico)
        MAX_COST = 800   # R$ 800/mês (caro)

        # Normalização básica por custo absoluto
        if monthly_cost <= MIN_COST:
            cost_score = 1.0
        elif monthly_cost >= MAX_COST:
            cost_score = 0.0
        else:
            # Inverter: custo baixo = score alto
            cost_score = 1.0 - (
                (monthly_cost - MIN_COST) / (MAX_COST - MIN_COST)
            )

        # Ajustar por percentual da renda (se disponível)
        if hasattr(profile, 'renda_mensal') and profile.renda_mensal:
            cost_percentage = (monthly_cost / profile.renda_mensal) * 100

            # Se custo é muito alto em relação à renda, penalizar
            if cost_percentage > 15:  # >15% da renda em combustível
                cost_score *= 0.7  # Penalizar 30%
            elif cost_percentage > 10:  # >10% da renda
                cost_score *= 0.85  # Penalizar 15%
            elif cost_percentage < 3:  # <3% da renda
                cost_score = min(1.0, cost_score * 1.1)  # Bonus 10%

        return max(0.0, min(1.0, cost_score))

    def _get_fuel_type_bonus(self, combustivel: str) -> float:
        """
        Bonus por tipo de combustível

        Combustíveis econômicos (Flex, Elétrico, GNV) ganham bonus.

        Args:
            combustivel: Tipo de combustível

        Returns:
            float: Bonus normalizado 0-1
        """
        return self.FUEL_TYPE_BONUS.get(combustivel, 0.7)

    def _get_fallback_score(self, car: Car) -> float:
        """
        Score de fallback quando cálculo falha

        Usa score_economia do carro se disponível, senão 0.5

        Args:
            car: Veículo

        Returns:
            float: Score de fallback
        """
        if hasattr(car, 'score_economia') and car.score_economia:
            return float(car.score_economia)
        return 0.5

    def _get_cache_ttl(self) -> int:
        """
        TTL do cache: 7 dias (preços mudam semanalmente)

        Returns:
            int: TTL em segundos
        """
        return 7 * 24 * 3600  # 7 dias
