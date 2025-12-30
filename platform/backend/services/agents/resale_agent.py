"""
Resale Agent - Agente especializado em cálculo de score de revenda

Calcula score de revenda baseado em:
- Taxa de depreciação por marca (FIPE/mercado)
- Idade do veículo (curva de depreciação)
- Quilometragem (impacto no valor)
- Demanda de mercado por categoria
- Histórico de valorização/desvalorização
- Fatores de liquidez (facilidade de venda)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from models.car import Car
from models.user_profile import UserProfile
from services.agents.base_agent import BaseAgent
from services.car.car_metrics import CarMetricsCalculator
from services.market_intelligence_service import MarketIntelligenceService

logger = logging.getLogger(__name__)


class ResaleAgent(BaseAgent):
    """
    Agente especialista em valor de revenda e depreciação.
    
    Versão Híbrida (Sprint 7):
    - Base: Tabela FIPE e histórico (Regras)
    - Ajuste: Inteligência de Mercado (SLM) via MarketIntelligenceService
    """

    # Taxa de retenção de valor por marca (% após 3 anos)
    # Baseado em dados FIPE e mercado brasileiro
    # Maior = melhor retenção de valor
    BRAND_VALUE_RETENTION = {
        # Excelente retenção (> 70%)
        "Toyota": 0.75,      # Corolla, Hilux mantêm valor
        "Honda": 0.73,       # Civic, Fit muito procurados
        "Jeep": 0.72,        # SUVs mantêm demanda

        # Boa retenção (65-70%)
        "Hyundai": 0.68,
        "Nissan": 0.67,
        "Mitsubishi": 0.66,
        "Kia": 0.65,

        # Média retenção (55-65%)
        "Volkswagen": 0.62,
        "Ford": 0.60,
        "Chevrolet": 0.58,
        "Fiat": 0.55,
        "Renault": 0.54,
        "Peugeot": 0.53,

        # Baixa retenção (< 55%) - Premium deprecia rápido
        "BMW": 0.50,
        "Mercedes": 0.48,
        "Audi": 0.52,
        "Volvo": 0.50,
        "Land Rover": 0.45,

        # Default
        "DEFAULT": 0.60
    }

    # Demanda de mercado por categoria
    # Maior = mais procurado = melhor liquidez
    CATEGORY_MARKET_DEMAND = {
        "SUV": 0.95,              # Alta demanda no Brasil
        "SUV Compacto": 0.90,     # Muito procurado
        "Pickup": 0.92,           # Boa demanda (trabalho)
        "Hatch": 0.85,            # Demanda estável
        "Sedan": 0.75,            # Demanda média
        "Sedan Compacto": 0.80,
        "Crossover": 0.88,
        "Pickup Grande": 0.85,
        "Minivan": 0.65,          # Demanda menor
        "Van": 0.60,              # Nicho específico
        "Furgão": 0.55,           # Mercado restrito
        "Compacto": 0.82,
    }

    # Curva de depreciação por ano (% de perda acumulada)
    # Ano 0 = novo, Ano 1 = primeiro ano, etc.
    DEPRECIATION_CURVE = {
        0: 0.00,   # Novo (0% depreciação)
        1: 0.15,   # 1 ano (perde 15%)
        2: 0.25,   # 2 anos (perde 25% acumulado)
        3: 0.35,   # 3 anos (perde 35%)
        4: 0.42,   # 4 anos
        5: 0.48,   # 5 anos
        6: 0.53,   # 6 anos
        7: 0.57,   # 7 anos
        8: 0.61,   # 8 anos
        9: 0.64,   # 9 anos
        10: 0.67,  # 10 anos
        15: 0.75,  # 15 anos (perde 75%)
        20: 0.82,  # 20 anos (perde 82%)
    }

    # Penalização por quilometragem alta
    # Maior km = menor valor de revenda
    MILEAGE_PENALTY = {
        "ranges": [
            (0, 30000, 0.00),       # Novo: sem penalização
            (30000, 60000, 0.05),   # Baixo: -5%
            (60000, 100000, 0.10),  # Médio: -10%
            (100000, 150000, 0.25), # Alto: -25%
            (150000, 200000, 0.40), # Muito alto: -40%
            (200000, float('inf'), 0.50),  # Extremo: -50%
        ]
    }

    def __init__(self, cache_manager=None):
        """
        Inicializa o ResaleAgent
        
        Args:
            cache_manager: Gerenciador de cache (opcional)
        """
        super().__init__(cache_manager, name="ResaleAgent")
        self.metrics_calculator = CarMetricsCalculator()
        self.current_year = datetime.now().year
        
        try:
            self.market_intelligence = MarketIntelligenceService()
            self.enable_market_intel = True
        except Exception as e:
            logger.warning(f"MarketIntelligenceService not available: {e}")
            self.enable_market_intel = False

    async def calculate_score(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula score de revenda (0-1)

        Fórmula Híbrida:
        1. Base (Regras): Retenção Marca + Depreciação Idade + Demanda + Km
        2. Ajuste (SLM): Fator de inteligência de mercado (Reviews/News)
        """
        try:
            # 1. Obter retenção de valor da marca
            brand_retention = self._get_brand_value_retention(car.marca)

            # 2. Calcular depreciação por idade
            age = self.current_year - car.ano
            age_depreciation = self._calculate_age_depreciation(age)
            age_score = 1.0 - age_depreciation  # Inverter: menos depreciação = maior score

            # 3. Obter demanda de mercado por categoria
            market_demand = self._get_market_demand(car.categoria)

            # 4. Calcular penalização por quilometragem
            mileage_penalty = self._calculate_mileage_penalty(car.quilometragem)
            mileage_score = 1.0 - mileage_penalty

            # 5. Calcular score base (ponderado)
            base_score = (
                0.35 * brand_retention +
                0.25 * age_score +
                0.15 * market_demand +
                0.25 * mileage_score
            )
            
            # 6. Ajuste de Mercado (Intelegência Conexionista)
            if self.enable_market_intel:
                market_metrics = self.market_intelligence.get_market_metrics(car.modelo)
                if market_metrics:
                    # Fator de revenda extraído de reviews/news pelo SLM
                    # Ex: 0.8 (deprecia rápido) a 1.2 (mantém valor)
                    resale_factor = market_metrics.get('resale_factor', 1.0)
                    
                    # Sentiment impact (-1 a 1)
                    sentiment = market_metrics.get('sentiment_score', 0.0)
                    
                    # Ajustar score
                    # Se resale_factor > 1 (valoriza), aumenta score
                    # Se sentiment > 0 (positivo), aumenta score levemente
                    
                    # Normalizar fator para multiplicador (1.0 +- 0.2)
                    adjustment = (resale_factor - 1.0) + (sentiment * 0.1)
                    
                    # Log
                    if abs(adjustment) > 0.01:
                        logger.debug(f"Market intel adjustment for {car.modelo}: {adjustment:.2f}")
                        
                    base_score = base_score * (1.0 + adjustment)

            final_score = max(0.0, min(1.0, base_score))
            
            logger.debug(
                f"[ResaleAgent] {car.marca} {car.modelo} ({car.ano}): "
                f"brand={brand_retention:.2f}, age={age_depreciation:.2f}, "
                f"market={market_demand:.2f}, km={mileage_penalty:.2f}, "
                f"final={final_score:.2f}"
            )

            return final_score

        except Exception as e:
            logger.error(f"[ResaleAgent] Erro para {car.nome}: {e}")
            return self._get_fallback_score(car)

    def _get_brand_value_retention(self, marca: str) -> float:
        """
        Obtém taxa de retenção de valor da marca

        Args:
            marca: Marca do veículo

        Returns:
            float: Taxa de retenção 0-1 (1 = mantém 100% do valor)
        """
        return self.BRAND_VALUE_RETENTION.get(
            marca,
            self.BRAND_VALUE_RETENTION["DEFAULT"]
        )

    def _calculate_age_depreciation(self, age: int) -> float:
        """
        Calcula depreciação acumulada por idade

        Usa curva de depreciação não-linear:
        - Primeiro ano: 15% de perda
        - Anos 2-5: perda desacelera
        - Anos 5+: perda estabiliza

        Args:
            age: Idade do veículo em anos

        Returns:
            float: Depreciação acumulada 0-1 (0 = novo, 1 = sem valor)
        """
        # Casos diretos na curva
        if age in self.DEPRECIATION_CURVE:
            return self.DEPRECIATION_CURVE[age]

        # Interpolação para idades intermediárias
        if age < 0:
            return 0.0
        elif age <= 10:
            # Interpolar entre pontos conhecidos
            lower_age = max(k for k in self.DEPRECIATION_CURVE.keys() if k <= age)
            upper_age = min(k for k in self.DEPRECIATION_CURVE.keys() if k > age)

            lower_dep = self.DEPRECIATION_CURVE[lower_age]
            upper_dep = self.DEPRECIATION_CURVE[upper_age]

            # Interpolação linear
            ratio = (age - lower_age) / (upper_age - lower_age)
            return lower_dep + ratio * (upper_dep - lower_dep)

        elif age <= 15:
            # Entre 10 e 15 anos
            return self._interpolate(age, 10, 15, 0.67, 0.75)

        elif age <= 20:
            # Entre 15 e 20 anos
            return self._interpolate(age, 15, 20, 0.75, 0.82)

        else:
            # Mais de 20 anos: perda estabiliza em ~85%
            return min(0.85, 0.82 + (age - 20) * 0.01)

    def _interpolate(
        self,
        value: float,
        min_val: float,
        max_val: float,
        min_result: float,
        max_result: float
    ) -> float:
        """
        Interpolação linear simples

        Args:
            value: Valor a interpolar
            min_val: Valor mínimo do range
            max_val: Valor máximo do range
            min_result: Resultado para min_val
            max_result: Resultado para max_val

        Returns:
            float: Valor interpolado
        """
        if max_val == min_val:
            return min_result

        ratio = (value - min_val) / (max_val - min_val)
        return min_result + ratio * (max_result - min_result)

    def _get_market_demand(self, categoria: str) -> float:
        """
        Obtém índice de demanda de mercado por categoria

        Args:
            categoria: Categoria do veículo

        Returns:
            float: Índice de demanda 0-1 (1 = alta liquidez)
        """
        return self.CATEGORY_MARKET_DEMAND.get(categoria, 0.70)

    def _calculate_mileage_penalty(self, quilometragem: int) -> float:
        """
        Calcula penalização por quilometragem

        Alto km reduz valor de revenda significativamente

        Args:
            quilometragem: Km rodados

        Returns:
            float: Penalização 0-1 (0 = sem penalização, 1 = máxima)
        """
        for min_km, max_km, penalty in self.MILEAGE_PENALTY["ranges"]:
            if min_km <= quilometragem < max_km:
                return penalty

        # Fallback: penalização máxima para km muito alto
        return 0.40

    def _get_fallback_score(self, car: Car) -> float:
        """
        Score de fallback quando cálculo falha

        Usa retenção de valor da marca ou 0.5

        Args:
            car: Veículo

        Returns:
            float: Score de fallback
        """
        # Tentar usar retenção de valor da marca
        try:
            retention = self._get_brand_value_retention(car.marca)
            if retention:
                return retention
        except Exception:
            pass  # Ignorar erro e usar default

        return 0.5

    def _get_cache_ttl(self) -> int:
        """
        TTL do cache: 14 dias (dados de mercado mudam mensalmente)

        Returns:
            int: TTL em segundos
        """
        return 14 * 24 * 3600  # 14 dias

    def get_resale_breakdown(self, car: Car) -> Dict:
        """
        Retorna detalhamento do cálculo de revenda (para debug/UI)

        Args:
            car: Veículo

        Returns:
            dict: Detalhamento com valores e scores
        """
        age = self.current_year - car.ano

        brand_retention = self._get_brand_value_retention(car.marca)
        age_depreciation = self._calculate_age_depreciation(age)
        market_demand = self._get_market_demand(car.categoria)
        mileage_penalty = self._calculate_mileage_penalty(car.quilometragem)

        # Estimativa de valor de revenda (% do valor original)
        estimated_value_percentage = brand_retention * (1.0 - age_depreciation) * (1.0 - mileage_penalty)

        # Estimativa de valor em reais (se temos preço original)
        estimated_value_brl = car.preco * estimated_value_percentage if car.preco else None

        return {
            "retencao_valor_marca": brand_retention,
            "depreciacao_idade": age_depreciation,
            "demanda_mercado": market_demand,
            "penalizacao_km": mileage_penalty,
            "idade_anos": age,
            "quilometragem": car.quilometragem,
            "percentual_valor_estimado": estimated_value_percentage,
            "valor_revenda_estimado": estimated_value_brl,
            "preco_original": car.preco,
            "liquidez": market_demand,  # Facilidade de venda
        }

    def estimate_resale_value(self, car: Car) -> Dict:
        """
        Estima valor de revenda do veículo

        Args:
            car: Veículo

        Returns:
            dict: Estimativa de valor com detalhes
        """
        breakdown = self.get_resale_breakdown(car)

        return {
            "valor_estimado": breakdown["valor_revenda_estimado"],
            "percentual_retencao": breakdown["percentual_valor_estimado"] * 100,
            "preco_original": breakdown["preco_original"],
            "idade_anos": breakdown["idade_anos"],
            "depreciacao_total": breakdown["depreciacao_idade"] * 100,
            "facilidade_venda": "Alta" if breakdown["liquidez"] > 0.8 else
                               "Média" if breakdown["liquidez"] > 0.6 else "Baixa",
        }
