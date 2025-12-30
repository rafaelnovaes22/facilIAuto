"""
TCO (Total Cost of Ownership) Calculator

Calcula o custo total mensal de propriedade de um veículo, incluindo:
- Financiamento (Tabela Price)
- Combustível
- Manutenção (com ajuste para alta quilometragem)
- Seguro
- IPVA

Author: FacilIAuto
Date: 2025-11-05
"""

from typing import Dict, Optional, Any, Tuple, List
import asyncio
from pydantic import BaseModel


class TCOBreakdown(BaseModel):
    """Detalhamento do custo total de propriedade"""
    financing_monthly: float        # Parcela do financiamento
    fuel_monthly: float             # Combustível estimado
    maintenance_monthly: float      # Manutenção média
    insurance_monthly: float        # Seguro anual / 12
    ipva_monthly: float             # IPVA anual / 12
    total_monthly: float            # Soma de todos
    
    # Metadados para cálculo
    assumptions: Dict[str, Any] = {
        "down_payment_percent": 20,
        "financing_months": 60,
        "monthly_km": 1000,
        "fuel_price_per_liter": 5.20,
        "state": "SP",
        "annual_interest_rate": 24.0,  # 24% a.a. (2% a.m.) - média mercado 2025
        "fuel_efficiency": 12.0
    }


class TCOCalculator:
    """Calculadora de TCO (Total Cost of Ownership)"""
    
    # Preços médios de combustíveis (atualizados em março/2025)
    # Fonte: ANP (Agência Nacional do Petróleo)
    # Última atualização: 06/11/2024
    FUEL_PRICES = {
        "Gasolina": 6.17,   # R$/litro (março 2025)
        "Etanol": 4.28,     # R$/litro (fevereiro 2025)
        "Flex": 5.50,       # Média ponderada (70% gasolina, 30% etanol)
        "Diesel": 6.00,     # Estimativa para diesel
        "GNV": 4.50         # Estimativa para GNV
    }
    
    # Data da última atualização dos preços
    FUEL_PRICES_LAST_UPDATE = "2024-11-06"
    
    @staticmethod
    def load_fuel_prices_from_file(data_dir: str = "data") -> Dict[str, float]:
        """
        Carrega preços de combustíveis do arquivo JSON
        
        Args:
            data_dir: Diretório onde está o arquivo fuel_prices.json
            
        Returns:
            Dicionário com preços por tipo de combustível
        """
        import json
        import os
        
        fuel_prices_file = os.path.join(data_dir, "fuel_prices.json")
        
        if os.path.exists(fuel_prices_file):
            try:
                with open(fuel_prices_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    prices = {}
                    for fuel_type, info in data.get("prices", {}).items():
                        prices[fuel_type] = info.get("price", 0.0)
                    return prices
            except Exception as e:
                print(f"[AVISO] Erro ao carregar fuel_prices.json: {e}")
                return TCOCalculator.FUEL_PRICES
        else:
            print(f"[AVISO] Arquivo {fuel_prices_file} não encontrado, usando preços padrão")
            return TCOCalculator.FUEL_PRICES
    
    @staticmethod
    def get_fuel_price(fuel_type: str, data_dir: str = "data") -> float:
        """
        Obtém preço atualizado de combustível
        
        Args:
            fuel_type: Tipo de combustível (Gasolina, Etanol, Flex, etc)
            data_dir: Diretório dos dados
            
        Returns:
            Preço por litro em R$
        """
        prices = TCOCalculator.load_fuel_prices_from_file(data_dir)
        return prices.get(fuel_type, prices.get("Flex", 5.50))
    
    # Custo anual base de manutenção por categoria (dados de mercado)
    MAINTENANCE_COSTS = {
        "Hatch": 1500,
        "Sedan Compacto": 1800,
        "Sedan": 2200,
        "SUV Compacto": 2500,
        "SUV": 3000,
        "Pickup": 2800,
        "Van": 3200,
        "Furgão": 2600,
        "Crossover": 2700,
        "Minivan": 3100
    }
    
    # Taxa base de seguro por categoria (% do valor do carro ao ano)
    INSURANCE_RATES = {
        "Hatch": 0.035,          # 3.5% ao ano
        "Sedan Compacto": 0.040,
        "Sedan": 0.045,
        "SUV Compacto": 0.050,
        "SUV": 0.055,
        "Pickup": 0.048,
        "Van": 0.052,
        "Furgão": 0.045,
        "Crossover": 0.050,
        "Minivan": 0.052
    }
    
    # Alíquotas de IPVA por estado (2025)
    IPVA_RATES = {
        "SP": 0.04,   # 4%
        "RJ": 0.04,
        "MG": 0.04,
        "RS": 0.03,
        "PR": 0.035,
        "SC": 0.02,
        "BA": 0.025,
        "PE": 0.03,
        "CE": 0.03,
        "GO": 0.035,
        "ES": 0.02,
        "PA": 0.025,
        "AM": 0.03,
        "MA": 0.025,
        "MS": 0.035,
        "MT": 0.03,
        "DF": 0.035,
        "RN": 0.03,
        "PB": 0.03,
        "AL": 0.03,
        "SE": 0.03,
        "PI": 0.03,
        "RO": 0.03,
        "AC": 0.02,
        "AP": 0.03,
        "RR": 0.03,
        "TO": 0.025
    }
    
    def __init__(
        self,
        down_payment_percent: float = 0.20,
        financing_months: int = 60,
        annual_interest_rate: float = 0.24,  # 24% a.a. (2% a.m.)
        monthly_km: int = 1000,
        fuel_price_per_liter: float = None,
        fuel_type: str = "Flex",
        state: str = "SP",
        user_profile: str = "standard"
    ):
        """
        Inicializa calculadora de TCO
        
        Args:
            down_payment_percent: Percentual de entrada (padrão 20%)
            financing_months: Número de parcelas (padrão 60)
            annual_interest_rate: Taxa anual de juros (padrão 24% a.a. = 2% a.m.)
            monthly_km: Quilometragem mensal estimada (padrão 1000)
            fuel_price_per_liter: Preço do combustível (se None, usa preço médio do tipo)
            fuel_type: Tipo de combustível (Gasolina, Etanol, Flex, Diesel, GNV)
            state: Estado para cálculo de IPVA (padrão SP)
            user_profile: Perfil do segurado (standard, young, senior)
        """
        self.down_payment_percent = down_payment_percent
        self.financing_months = financing_months
        self.annual_interest_rate = annual_interest_rate
        self.monthly_km = monthly_km
        self.fuel_type = fuel_type
        
        # Se preço não foi especificado, usar preço médio do tipo de combustível
        if fuel_price_per_liter is None:
            self.fuel_price_per_liter = self.FUEL_PRICES.get(fuel_type, self.FUEL_PRICES["Flex"])
        else:
            self.fuel_price_per_liter = fuel_price_per_liter
        
        self.state = state
        self.user_profile = user_profile
    
    def validate_financing_terms(
        self,
        down_payment_percent: float,
        financing_months: int,
        annual_interest_rate: float
    ) -> Tuple[float, int, float]:
        """
        Valida e corrige termos de financiamento para prevenir erros de exibição
        
        Args:
            down_payment_percent: Percentual de entrada (0.0-1.0)
            financing_months: Número de parcelas
            annual_interest_rate: Taxa anual de juros (0.0-1.0)
            
        Returns:
            Tupla com (down_payment validado, months validado, rate validado)
        """
        # Validar entrada (0-100%)
        if down_payment_percent < 0 or down_payment_percent > 1:
            down_payment_percent = 0.20  # Default 20%
        
        # Validar prazo (12-84 meses)
        if financing_months < 12 or financing_months > 84:
            financing_months = 60  # Default 60 meses
        
        # Validar taxa de juros (0.5-5% ao mês = 6-60% ao ano)
        monthly_rate = annual_interest_rate / 12
        if monthly_rate < 0.005 or monthly_rate > 0.05:
            annual_interest_rate = 0.24  # Default 24% ao ano (2% ao mês)
        
        return down_payment_percent, financing_months, annual_interest_rate
    
    def adjust_maintenance_for_mileage(
        self,
        base_maintenance: float,
        mileage: int
    ) -> Tuple[float, Optional[Dict[str, Any]]]:
        """
        Ajusta custos de manutenção baseado na quilometragem do veículo
        
        Args:
            base_maintenance: Custo base de manutenção mensal
            mileage: Quilometragem atual do veículo
            
        Returns:
            Tupla com (custo ajustado, dict com fator e razão ou None)
            
        Regras:
        - ≤100k km: sem ajuste (fator 1.0)
        - 100k-150k km: +50% (fator 1.5)
        - >150k km: +100% (fator 2.0)
        """
        if mileage <= 100000:
            return base_maintenance, None
        elif mileage <= 150000:
            adjusted = base_maintenance * 1.5
            return adjusted, {
                "factor": 1.5,
                "reason": "Quilometragem alta (100k-150k km)"
            }
        else:
            adjusted = base_maintenance * 2.0
            return adjusted, {
                "factor": 2.0,
                "reason": "Quilometragem muito alta (>150k km)"
            }
    
    def calculate_tco(
        self,
        car_price: float,
        car_category: str,
        fuel_efficiency_km_per_liter: float,
        car_age: int = 0,
        car_mileage: int = 0
    ) -> TCOBreakdown:
        """
        Calcula TCO completo para um carro com ajuste de quilometragem
        
        Args:
            car_price: Preço do carro
            car_category: Categoria do carro
            fuel_efficiency_km_per_liter: Consumo do carro (km/L)
            car_age: Idade do carro em anos (0 = novo)
            car_mileage: Quilometragem atual do veículo (0 = novo)
            
        Returns:
            TCOBreakdown com todos os custos detalhados
        """
        # Validar termos de financiamento
        validated_down, validated_months, validated_rate = self.validate_financing_terms(
            self.down_payment_percent,
            self.financing_months,
            self.annual_interest_rate
        )
        
        # Usar valores validados
        original_down = self.down_payment_percent
        original_months = self.financing_months
        original_rate = self.annual_interest_rate
        
        self.down_payment_percent = validated_down
        self.financing_months = validated_months
        self.annual_interest_rate = validated_rate
        
        # Calcular componentes
        financing = self.calculate_financing_monthly(car_price)
        fuel = self.calculate_fuel_monthly(fuel_efficiency_km_per_liter)
        
        # Manutenção base (por idade)
        base_maintenance = self.estimate_maintenance_monthly(car_category, car_age)
        
        # Ajustar manutenção por quilometragem
        maintenance, mileage_adjustment = self.adjust_maintenance_for_mileage(
            base_maintenance,
            car_mileage
        )
        
        insurance = self.estimate_insurance_monthly(car_price, car_category)
        ipva = self.calculate_ipva_monthly(car_price)
        
        total = financing + fuel + maintenance + insurance + ipva
        
        # Construir assumptions com transparência total
        # Garantir que percentuais sejam exibidos corretamente (0-100)
        down_payment_display = self.down_payment_percent
        if down_payment_display <= 1.0:
            down_payment_display = down_payment_display * 100
        
        interest_rate_display = self.annual_interest_rate
        if interest_rate_display <= 1.0:
            interest_rate_display = interest_rate_display * 100
        
        assumptions = {
            "down_payment_percent": round(down_payment_display, 1),
            "financing_months": self.financing_months,
            "annual_interest_rate": round(interest_rate_display, 1),
            "monthly_km": self.monthly_km,
            "fuel_price_per_liter": self.fuel_price_per_liter,
            "fuel_efficiency": fuel_efficiency_km_per_liter,
            "state": self.state
        }
        
        # Adicionar ajuste de manutenção se aplicável
        if mileage_adjustment:
            assumptions["maintenance_adjustment"] = mileage_adjustment
        
        # Restaurar valores originais
        self.down_payment_percent = original_down
        self.financing_months = original_months
        self.annual_interest_rate = original_rate
        
        return TCOBreakdown(
            financing_monthly=round(financing, 2),
            fuel_monthly=round(fuel, 2),
            maintenance_monthly=round(maintenance, 2),
            insurance_monthly=round(insurance, 2),
            ipva_monthly=round(ipva, 2),
            total_monthly=round(total, 2),
            assumptions=assumptions
        )
    
    def calculate_financing_monthly(self, car_price: float) -> float:
        """
        Calcula parcela mensal do financiamento usando Tabela Price
        
        Args:
            car_price: Preço do carro
            
        Returns:
            Valor da parcela mensal
        """
        financed_amount = car_price * (1 - self.down_payment_percent)
        monthly_rate = self.annual_interest_rate / 12
        
        # Fórmula Price: PMT = PV * (i * (1 + i)^n) / ((1 + i)^n - 1)
        if monthly_rate > 0:
            monthly_payment = financed_amount * (
                monthly_rate * (1 + monthly_rate) ** self.financing_months
            ) / (
                (1 + monthly_rate) ** self.financing_months - 1
            )
        else:
            # Sem juros
            monthly_payment = financed_amount / self.financing_months
        
        return monthly_payment
    
    def calculate_fuel_monthly(
        self,
        fuel_efficiency_km_per_liter: float
    ) -> float:
        """
        Calcula custo mensal de combustível
        
        Args:
            fuel_efficiency_km_per_liter: Consumo do carro (km/L)
            
        Returns:
            Custo mensal de combustível
        """
        if fuel_efficiency_km_per_liter <= 0:
            return 0.0
        
        liters_needed = self.monthly_km / fuel_efficiency_km_per_liter
        monthly_cost = liters_needed * self.fuel_price_per_liter
        
        return monthly_cost
    
    def estimate_maintenance_monthly(
        self,
        car_category: str,
        car_age: int = 0
    ) -> float:
        """
        Estima custo mensal de manutenção baseado em categoria
        
        Args:
            car_category: Categoria do carro
            car_age: Idade do carro em anos (0 = novo)
            
        Returns:
            Custo mensal estimado de manutenção
        """
        base_cost = self.MAINTENANCE_COSTS.get(car_category, 2000)
        
        # Ajuste por idade (aumenta 10% por ano)
        age_multiplier = 1 + (car_age * 0.10)
        
        annual_cost = base_cost * age_multiplier
        monthly_cost = annual_cost / 12
        
        return monthly_cost
    
    def estimate_insurance_monthly(
        self,
        car_price: float,
        car_category: str
    ) -> float:
        """
        Estima custo mensal de seguro
        
        Args:
            car_price: Preço do carro
            car_category: Categoria do carro
            
        Returns:
            Custo mensal estimado de seguro
        """
        base_rate = self.INSURANCE_RATES.get(car_category, 0.045)
        
        # Ajuste por perfil do segurado
        profile_multipliers = {
            "standard": 1.0,
            "young": 1.3,      # Jovens pagam mais
            "senior": 0.9      # Idosos pagam menos
        }
        
        multiplier = profile_multipliers.get(self.user_profile, 1.0)
        
        annual_cost = car_price * base_rate * multiplier
        monthly_cost = annual_cost / 12
        
        return monthly_cost
    
    def calculate_ipva_monthly(self, car_price: float) -> float:
        """
        Calcula IPVA mensal baseado no estado
        
        Args:
            car_price: Preço do carro
            
        Returns:
            IPVA mensal
        """
        rate = self.IPVA_RATES.get(self.state, 0.04)
        annual_ipva = car_price * rate
        monthly_ipva = annual_ipva / 12
        
        return monthly_ipva
    
    @staticmethod
    def calculate_max_monthly_tco(income_range: str) -> float:
        """
        Calcula TCO máximo baseado em 30% da renda média da faixa
        
        Args:
            income_range: String no formato "3000-5000" ou "12000+"
            
        Returns:
            TCO máximo mensal em reais
        """
        income_brackets = {
            "0-3000": (0, 3000),
            "3000-5000": (3000, 5000),
            "5000-8000": (5000, 8000),
            "8000-12000": (8000, 12000),
            "12000+": (12000, 16000)  # Assumir teto de 16k para cálculo
        }
        
        if income_range not in income_brackets:
            return 0.0
        
        min_income, max_income = income_brackets[income_range]
        avg_income = (min_income + max_income) / 2
        
        # 30% da renda média
        max_tco = avg_income * 0.30
        
        return max_tco
    
    @staticmethod
    def get_income_range_info(income_range: str) -> Dict[str, Any]:
        """
        Retorna informações sobre uma faixa de renda
        
        Args:
            income_range: String no formato "3000-5000" ou "12000+"
            
        Returns:
            Dicionário com informações da faixa
        """
        max_tco = TCOCalculator.calculate_max_monthly_tco(income_range)
        
        # Estimativa de preço máximo do carro (baseado em TCO)
        # Assumindo: TCO = 30% financiamento + 70% outros custos
        # Financiamento ≈ 2% do preço do carro por mês (60x, 12% a.a.)
        estimated_max_price = (max_tco * 0.60) / 0.02  # 60% do TCO para financiamento
        
        return {
            "income_range": income_range,
            "max_monthly_tco": round(max_tco, 2),
            "estimated_max_car_price": round(estimated_max_price, 2),
            "recommended_percentage": 30
        }

    async def calculate_batch_tco(
        self,
        cars_data: List[Dict[str, Any]]
    ) -> List[TCOBreakdown]:
        """
        Calcula TCO para múltiplos carros em paralelo
        
        Útil para processar listas grandes de recomendações.
        
        Args:
            cars_data: Lista de dicts com dados dos carros:
                [
                    {
                        "price": 50000,
                        "category": "Hatch",
                        "efficiency": 12.0,
                        "age": 2,
                        "mileage": 30000
                    },
                    ...
                ]
                
        Returns:
            Lista de TCOBreakdown na mesma ordem
        """
        # Como o cálculo é CPU-bound mas muito rápido, asyncio ajudaria
        # principalmente se houvesse I/O (ex: fetch de preços online).
        # Aqui simulamos a estrutura para futura escalabilidade.
        
        # Função wrapper para execução
        def _calc_single(data):
            # Preservar estado original
            original_down = self.down_payment_percent
            original_months = self.financing_months
            original_rate = self.annual_interest_rate
            
            try:
                # Aplicar overrides se fornecidos no data
                # (Lógica opcional, mantemos simples por enquanto)
                
                return self.calculate_tco(
                    car_price=data.get("price", 0),
                    car_category=data.get("category", "Hatch"),
                    fuel_efficiency_km_per_liter=data.get("efficiency", 10.0),
                    car_age=data.get("age", 0),
                    car_mileage=data.get("mileage", 0)
                )
            finally:
                # Restaurar estado
                self.down_payment_percent = original_down
                self.financing_months = original_months
                self.annual_interest_rate = original_rate

        # Executar (em thread pool se for muito pesado, mas aqui loop direto é ok)
        # Para simular "paralelismo" real em I/O, usaríamos gather.
        # Para CPU-bound em Python, Threads não ajudam muito devido ao GIL,
        # mas asyncio permite concorrência cooperativa se houver await.
        # Como calculate_tco é síncrono pura matemática, rodar em executor é melhor prática.
        
        loop = asyncio.get_event_loop()
        tasks = []
        
        for data in cars_data:
            tasks.append(
                loop.run_in_executor(None, _calc_single, data)
            )
            
        results = await asyncio.gather(*tasks)
        return results
