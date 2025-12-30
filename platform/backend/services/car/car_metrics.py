"""
📊 Data Analyst + 🤖 AI Engineer: Cálculo de Métricas de "Carro Bom" (FASE 3)

Calcula automaticamente:
- Índice de revenda (liquidez + relação FIPE)
- Taxa de depreciação anual
- Custo de manutenção estimado
- Índice de confiabilidade

Autor: Data Analyst + AI Engineer
Data: Outubro 2024
"""

from typing import Dict, Optional
from datetime import datetime


class CarMetricsCalculator:
    """
    Calculadora de métricas avançadas para avaliação de carros
    """
    
    # 🤖 Base de dados de confiabilidade por marca (0-1)
    # Baseado em: recalls, problemas conhecidos, satisfação do consumidor
    BRAND_RELIABILITY = {
        # Muito Confiáveis (0.85-1.0)
        "Toyota": 0.95,
        "Honda": 0.93,
        "Lexus": 0.95,
        "Mazda": 0.90,
        "Subaru": 0.88,
        
        # Confiáveis (0.75-0.84)
        "Hyundai": 0.82,
        "Kia": 0.80,
        "Nissan": 0.78,
        "Volkswagen": 0.77,
        "BMW": 0.76,
        
        # Médias (0.65-0.74)
        "Ford": 0.72,
        "Chevrolet": 0.70,
        "Jeep": 0.68,
        "Peugeot": 0.67,
        "Renault": 0.65,
        
        # Abaixo da Média (0.50-0.64)
        "Fiat": 0.62,
        "Citroën": 0.60,
        "Chrysler": 0.58,
        
        # Default para marcas não listadas
        "DEFAULT": 0.65
    }
    
    # 📊 Índice de revenda por marca (0-1)
    # Baseado em: liquidez (velocidade de venda) + manutenção do valor
    BRAND_RESALE_INDEX = {
        # Excelente revenda (0.85-1.0)
        "Toyota": 0.92,
        "Honda": 0.90,
        "Jeep": 0.88,
        "Volkswagen": 0.85,
        
        # Boa revenda (0.75-0.84)
        "Hyundai": 0.82,
        "Nissan": 0.80,
        "Ford": 0.78,
        "Chevrolet": 0.76,
        
        # Média (0.65-0.74)
        "Fiat": 0.72,
        "Renault": 0.70,
        "Peugeot": 0.68,
        
        # Abaixo da média (0.50-0.64)
        "Citroën": 0.62,
        "Chrysler": 0.60,
        
        # Default
        "DEFAULT": 0.70
    }
    
    # 📊 Taxa de depreciação média por categoria (% ao ano)
    DEPRECIATION_BY_CATEGORY = {
        "Hatch": 0.18,      # 18% ao ano
        "Sedan": 0.16,      # 16% ao ano
        "SUV": 0.14,        # 14% ao ano (deprecia menos)
        "Pickup": 0.12,     # 12% ao ano (muito procurada)
        "Van": 0.15,        # 15% ao ano
        "Compacto": 0.20,   # 20% ao ano (deprecia mais)
        "DEFAULT": 0.15     # 15% ao ano
    }
    
    # 💰 Custo de manutenção médio por marca (R$/ano)
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
        
        # Caras (R$ 3.500-5.000/ano)
        "Renault": 3200,
        "Peugeot": 3500,
        "Jeep": 4000,
        
        # Premium (> R$ 5.000/ano)
        "BMW": 6500,
        "Mercedes": 7000,
        "Audi": 6800,
        
        # Default
        "DEFAULT": 2800
    }
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def calculate_reliability_index(
        self, 
        marca: str,
        ano: int,
        quilometragem: int
    ) -> float:
        """
        🤖 AI Engineer: Calcular índice de confiabilidade (0-1)
        
        Fatores:
        1. Confiabilidade base da marca (peso 60%)
        2. Idade do carro (peso 20%)
        3. Quilometragem (peso 20%)
        
        Returns:
            float: 0-1 (1 = muito confiável)
        """
        # 1. Confiabilidade base da marca
        base_reliability = self.BRAND_RELIABILITY.get(
            marca, 
            self.BRAND_RELIABILITY["DEFAULT"]
        )
        
        # 2. Penalidade por idade
        age = self.current_year - ano
        age_penalty = 0.0
        if age <= 2:
            age_penalty = 0.0      # Sem penalidade (novo)
        elif age <= 5:
            age_penalty = 0.05     # -5% (semi-novo)
        elif age <= 10:
            age_penalty = 0.10     # -10% (usado)
        else:
            age_penalty = 0.20     # -20% (antigo)
        
        # 3. Penalidade por quilometragem
        km_penalty = 0.0
        if quilometragem < 30000:
            km_penalty = 0.0       # Sem penalidade (baixa km)
        elif quilometragem < 60000:
            km_penalty = 0.03      # -3%
        elif quilometragem < 100000:
            km_penalty = 0.07      # -7%
        else:
            km_penalty = 0.15      # -15% (alta km)
        
        # Cálculo final
        reliability = base_reliability - age_penalty - km_penalty
        
        return max(0.0, min(1.0, reliability))
    
    def calculate_resale_index(
        self,
        marca: str,
        categoria: str,
        ano: int
    ) -> float:
        """
        📊 Data Analyst: Calcular índice de revenda (0-1)
        
        Fatores:
        1. Índice base da marca (peso 70%)
        2. Categoria (SUV/Pickup tem mais demanda) (peso 20%)
        3. Idade (peso 10%)
        
        Returns:
            float: 0-1 (1 = excelente revenda)
        """
        # 1. Índice base da marca
        base_resale = self.BRAND_RESALE_INDEX.get(
            marca,
            self.BRAND_RESALE_INDEX["DEFAULT"]
        )
        
        # 2. Boost por categoria procurada
        category_boost = 0.0
        high_demand_categories = ["SUV", "Pickup"]
        if categoria in high_demand_categories:
            category_boost = 0.10  # +10%
        
        # 3. Penalidade por idade
        age = self.current_year - ano
        age_penalty = 0.0
        if age <= 3:
            age_penalty = 0.0      # Sem penalidade
        elif age <= 5:
            age_penalty = 0.05     # -5%
        elif age <= 10:
            age_penalty = 0.10     # -10%
        else:
            age_penalty = 0.20     # -20%
        
        # Cálculo final
        resale = base_resale + category_boost - age_penalty
        
        return max(0.0, min(1.0, resale))
    
    def calculate_depreciation_rate(
        self,
        marca: str,
        categoria: str,
        ano: int
    ) -> float:
        """
        💻 Tech Lead: Calcular taxa de depreciação anual
        
        Fatores:
        1. Taxa base por categoria
        2. Ajuste por marca (marcas premium depreciam mais nos primeiros anos)
        3. Idade (depreciação é maior nos primeiros anos)
        
        Returns:
            float: Taxa anual (ex: 0.15 = 15% ao ano)
        """
        # 1. Taxa base por categoria
        base_rate = self.DEPRECIATION_BY_CATEGORY.get(
            categoria,
            self.DEPRECIATION_BY_CATEGORY["DEFAULT"]
        )
        
        # 2. Ajuste por marca premium
        premium_brands = ["BMW", "Mercedes", "Audi", "Lexus"]
        if marca in premium_brands:
            base_rate += 0.03  # +3% (depreciam mais rápido)
        
        # Marcas que mantêm valor
        value_holding_brands = ["Toyota", "Honda", "Jeep"]
        if marca in value_holding_brands:
            base_rate -= 0.02  # -2% (depreciam menos)
        
        # 3. Ajuste por idade (primeiro ano deprecia mais)
        age = self.current_year - ano
        if age == 0:
            # Primeiro ano deprecia muito (carro 0km vira usado)
            base_rate += 0.05  # +5%
        elif age <= 3:
            # Anos 2-3 depreciam normal
            pass
        else:
            # Após 3 anos, depreciação diminui
            base_rate -= 0.02  # -2%
        
        return max(0.05, min(0.30, base_rate))  # Entre 5% e 30%
    
    def estimate_maintenance_cost(
        self,
        marca: str,
        ano: int,
        quilometragem: int
    ) -> float:
        """
        💰 Estimar custo de manutenção anual (R$/ano)
        
        Fatores:
        1. Custo base da marca
        2. Aumento por idade (peças desgastam)
        3. Aumento por quilometragem
        
        Returns:
            float: Custo estimado em R$/ano
        """
        # 1. Custo base da marca
        base_cost = self.MAINTENANCE_COST_BY_BRAND.get(
            marca,
            self.MAINTENANCE_COST_BY_BRAND["DEFAULT"]
        )
        
        # 2. Aumento por idade
        age = self.current_year - ano
        age_multiplier = 1.0
        if age > 10:
            age_multiplier = 1.5   # +50% (muitas trocas)
        elif age > 5:
            age_multiplier = 1.2   # +20% (peças desgastadas)
        
        # 3. Aumento por quilometragem
        km_multiplier = 1.0
        if quilometragem > 100000:
            km_multiplier = 1.3    # +30% (alta km)
        elif quilometragem > 150000:
            km_multiplier = 1.6    # +60% (muito rodado)
        
        # Cálculo final
        total_cost = base_cost * age_multiplier * km_multiplier
        
        return round(total_cost, 2)
    
    def calculate_all_metrics(
        self,
        marca: str,
        categoria: str,
        ano: int,
        quilometragem: int
    ) -> Dict[str, float]:
        """
        Calcular todas as métricas de uma vez
        
        Returns:
            dict: {
                "indice_confiabilidade": float,
                "indice_revenda": float,
                "taxa_depreciacao_anual": float,
                "custo_manutencao_anual": float
            }
        """
        return {
            "indice_confiabilidade": self.calculate_reliability_index(
                marca, ano, quilometragem
            ),
            "indice_revenda": self.calculate_resale_index(
                marca, categoria, ano
            ),
            "taxa_depreciacao_anual": self.calculate_depreciation_rate(
                marca, categoria, ano
            ),
            "custo_manutencao_anual": self.estimate_maintenance_cost(
                marca, ano, quilometragem
            )
        }
    
    def get_car_total_cost_5_years(
        self,
        preco: float,
        taxa_depreciacao: float,
        custo_manutencao: float
    ) -> Dict[str, float]:
        """
        Calcular custo total de propriedade em 5 anos
        
        Útil para comparar carros considerando:
        - Depreciação
        - Manutenção
        
        Returns:
            dict: {
                "valor_final": float,
                "depreciacao_total": float,
                "manutencao_total": float,
                "custo_total": float
            }
        """
        valor_atual = preco
        depreciacao_acumulada = 0.0
        manutencao_total = 0.0
        
        # Simular 5 anos
        for ano in range(5):
            # Depreciação do ano
            depreciacao_ano = valor_atual * taxa_depreciacao
            depreciacao_acumulada += depreciacao_ano
            valor_atual -= depreciacao_ano
            
            # Manutenção do ano
            manutencao_total += custo_manutencao
        
        return {
            "valor_final": round(valor_atual, 2),
            "depreciacao_total": round(depreciacao_acumulada, 2),
            "manutencao_total": round(manutencao_total, 2),
            "custo_total": round(depreciacao_acumulada + manutencao_total, 2)
        }


if __name__ == "__main__":
    # Testes
    print("Data Analyst: Testando calculo de metricas")
    print("=" * 60)
    
    calculator = CarMetricsCalculator()
    
    # Teste 1: Toyota Corolla 2022
    print("\n1. Toyota Corolla 2022 (30.000 km) - R$ 115.990")
    metrics = calculator.calculate_all_metrics(
        marca="Toyota",
        categoria="Sedan",
        ano=2022,
        quilometragem=30000
    )
    print(f"   Confiabilidade: {metrics['indice_confiabilidade']:.2f}")
    print(f"   Revenda: {metrics['indice_revenda']:.2f}")
    print(f"   Depreciacao: {metrics['taxa_depreciacao_anual']:.1%}/ano")
    print(f"   Manutencao: R$ {metrics['custo_manutencao_anual']:,.0f}/ano")
    
    tco = calculator.get_car_total_cost_5_years(
        preco=115990,
        taxa_depreciacao=metrics['taxa_depreciacao_anual'],
        custo_manutencao=metrics['custo_manutencao_anual']
    )
    print(f"   Custo Total 5 anos: R$ {tco['custo_total']:,.0f}")
    
    # Teste 2: Fiat Argo 2020
    print("\n2. Fiat Argo 2020 (80.000 km) - R$ 65.000")
    metrics = calculator.calculate_all_metrics(
        marca="Fiat",
        categoria="Hatch",
        ano=2020,
        quilometragem=80000
    )
    print(f"   Confiabilidade: {metrics['indice_confiabilidade']:.2f}")
    print(f"   Revenda: {metrics['indice_revenda']:.2f}")
    print(f"   Depreciacao: {metrics['taxa_depreciacao_anual']:.1%}/ano")
    print(f"   Manutencao: R$ {metrics['custo_manutencao_anual']:,.0f}/ano")
    
    print("\n" + "=" * 60)
    print("[OK] Testes concluidos!")

