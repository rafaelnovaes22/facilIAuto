"""
Financing Agent - SLM para previsão de taxas de financiamento
"""

from typing import Dict, Any, Optional
from services.agents.base_agent import BaseAgent
from models.car import Car
from models.user_profile import UserProfile

class FinancingAgent(BaseAgent):
    """
    Agente responsável por prever condições de financiamento baseadas no perfil do usuário.
    Atua como um SLM (Small Language Model) especializado em risco de crédito.
    """
    
    def __init__(self, cache_manager=None):
        super().__init__(cache_manager=cache_manager, name="financing")
        
    async def calculate_score(self, car: Car, profile: UserProfile) -> float:
        """
        Calcula um 'Credit Health Score' (0.0 a 1.0) para o usuário neste contexto.
        Quanto maior, melhores as condições de financiamento.
        """
        terms = self.predict_terms(profile)
        # Normalizar taxa inversa: menor taxa = maior score
        # Taxa base 1.5% am = 1.0 | Taxa teto 3.5% = 0.0
        rate = terms['monthly_interest_rate']
        score = 1.0 - ((rate - 0.015) / (0.035 - 0.015))
        return max(0.0, min(1.0, score))

    def predict_terms(self, profile: UserProfile) -> Dict[str, Any]:
        """
        Prevê os termos de financiamento baseados no perfil.
        
        Returns:
            Dict com:
            - annual_interest_rate (float): Taxa anual (ex: 0.18 para 18%)
            - monthly_interest_rate (float): Taxa mensal
            - max_months (int): Prazo máximo
            - min_down_payment (float): Entrada mínima
            - risk_level (str): "low", "medium", "high"
        """
        # 1. Determinar Risco Base
        risk_score = 0.5  # Começa neutro
        
        # Fatores de Risco (Simulação de SLM)
        if profile.financial_capacity and profile.financial_capacity.is_disclosed:
            income_str = profile.financial_capacity.monthly_income_range
            
            if income_str == "12000+":
                risk_score += 0.3  # Baixo risco
            elif income_str == "8000-12000":
                risk_score += 0.2
            elif income_str == "5000-8000":
                risk_score += 0.1
            elif income_str == "0-3000":
                risk_score -= 0.1
                
        if profile.primeiro_carro:
            risk_score -= 0.1  # Histórico incerto
            
        if profile.tem_criancas or profile.tem_idosos:
            risk_score += 0.05  # Estabilidade familiar (proxy)
            
        # Clamp score
        risk_score = max(0.0, min(1.0, risk_score))
        
        # 2. Mapear Risco para Taxa
        # Score 1.0 -> 1.49% a.m. (19.5% a.a.)
        # Score 0.0 -> 3.50% a.m. (51.1% a.a.)
        
        min_rate_monthly = 0.0149
        max_rate_monthly = 0.0350
        
        monthly_rate = max_rate_monthly - (risk_score * (max_rate_monthly - min_rate_monthly))
        annual_rate = monthly_rate * 12  # Simplificado (juros simples para a taxa nominal)
        
        # 3. Determinar Entrada e Prazo
        if risk_score > 0.7:
             min_down = 0.10  # 10%
             max_months = 72
             risk_level = "low"
        elif risk_score > 0.4:
             min_down = 0.20  # 20%
             max_months = 60
             risk_level = "medium"
        else:
             min_down = 0.30  # 30%
             max_months = 48
             risk_level = "high"
             
        return {
            "annual_interest_rate": round(annual_rate, 4),
            "monthly_interest_rate": round(monthly_rate, 4),
            "max_months": max_months,
            "min_down_payment": min_down,
            "risk_level": risk_level,
            "risk_score_raw": round(risk_score, 2)
        }
