"""
Modelo de Perfil de Usuário para sistema de recomendação
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FinancialCapacity(BaseModel):
    """
    Capacidade financeira do usuário
    
    Attributes:
        monthly_income_range: Faixa de renda mensal (ex: "3000-5000", "5000-8000")
        max_monthly_tco: TCO máximo mensal recomendado (30% da renda média)
        is_disclosed: Se o usuário informou ou pulou a pergunta
    """
    monthly_income_range: Optional[str] = Field(
        None,
        description="Faixa de renda mensal (ex: '3000-5000', '5000-8000', '12000+')"
    )
    max_monthly_tco: Optional[float] = Field(
        None,
        description="TCO máximo mensal recomendado (30% da renda média)"
        # Note: Validation moved to API endpoint for better error messages
    )
    is_disclosed: bool = Field(
        False,
        description="Se o usuário informou sua capacidade financeira"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "monthly_income_range": "5000-8000",
                "max_monthly_tco": 2400.0,
                "is_disclosed": True
            }
        }


class TCOBreakdown(BaseModel):
    """
    Detalhamento do custo total de propriedade (Total Cost of Ownership)
    
    Attributes:
        financing_monthly: Parcela mensal do financiamento
        fuel_monthly: Custo mensal estimado de combustível
        maintenance_monthly: Custo mensal estimado de manutenção
        insurance_monthly: Custo mensal estimado de seguro (anual / 12)
        ipva_monthly: Custo mensal de IPVA (anual / 12)
        total_monthly: Soma de todos os custos mensais
        assumptions: Premissas utilizadas no cálculo
    """
    financing_monthly: float = Field(
        ...,
        description="Parcela mensal do financiamento",
        ge=0
    )
    fuel_monthly: float = Field(
        ...,
        description="Custo mensal estimado de combustível",
        ge=0
    )
    maintenance_monthly: float = Field(
        ...,
        description="Custo mensal estimado de manutenção",
        ge=0
    )
    insurance_monthly: float = Field(
        ...,
        description="Custo mensal estimado de seguro",
        ge=0
    )
    ipva_monthly: float = Field(
        ...,
        description="Custo mensal de IPVA",
        ge=0
    )
    total_monthly: float = Field(
        ...,
        description="Custo total mensal (soma de todos)",
        ge=0
    )
    assumptions: Dict[str, Any] = Field(
        default_factory=lambda: {
            "down_payment_percent": 20,
            "financing_months": 60,
            "annual_interest_rate": 12.0,
            "monthly_km": 1000,
            "fuel_price_per_liter": 5.20,
            "state": "SP"
        },
        description="Premissas utilizadas no cálculo"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "financing_monthly": 1400.0,
                "fuel_monthly": 400.0,
                "maintenance_monthly": 150.0,
                "insurance_monthly": 200.0,
                "ipva_monthly": 117.0,
                "total_monthly": 2267.0,
                "assumptions": {
                    "down_payment_percent": 20,
                    "financing_months": 60,
                    "annual_interest_rate": 12.0,
                    "monthly_km": 1000,
                    "fuel_price_per_liter": 5.20,
                    "state": "SP"
                }
            }
        }


class UserProfile(BaseModel):
    """
    Perfil do usuário baseado no questionário
    """
    # Orçamento
    orcamento_min: float
    orcamento_max: float
    
    # Localização
    city: Optional[str] = None
    state: Optional[str] = None
    priorizar_proximas: bool = True  # Priorizar concessionárias próximas
    raio_maximo_km: Optional[int] = None  # 🤖 AI Engineer: Raio de busca em km (ex: 30, 50, 100)
    
    # Uso principal
    uso_principal: str  # "familia", "trabalho", "lazer", "comercial", "primeiro_carro", "transporte_passageiros"
    frequencia_uso: Optional[str] = "diaria"  # "diaria", "semanal", "eventual"
    
    # Composição familiar
    tamanho_familia: int = 1  # Número de pessoas
    necessita_espaco: bool = False
    tem_criancas: bool = False
    tem_idosos: bool = False
    
    # Prioridades (escala 1-5)
    prioridades: Dict[str, int] = {
        "economia": 3,
        "espaco": 3,
        "performance": 3,
        "conforto": 3,
        "seguranca": 3,
        # 📊 FASE 3: Métricas de "Carro Bom"
        "revenda": 3,          # Índice de revenda
        "confiabilidade": 3,   # Índice de confiabilidade
        "custo_manutencao": 3  # Custo de manutenção
    }
    
    # Preferências
    marcas_preferidas: List[str] = []
    marcas_rejeitadas: List[str] = []
    tipos_preferidos: List[str] = []  # ["Hatch", "Sedan", "SUV", "Pickup", "Compacto", "Van"]
    combustivel_preferido: Optional[str] = None
    cambio_preferido: Optional[str] = None
    
    # 🤖 AI Engineer: Filtros eliminatórios (FASE 1)
    ano_minimo: Optional[int] = None  # Ex: 2018 (elimina carros mais antigos)
    ano_maximo: Optional[int] = None  # Ex: 2020 (elimina carros mais novos)
    km_maxima: Optional[int] = None  # Ex: 80000 (elimina carros com mais quilometragem)
    must_haves: List[str] = []  # Ex: ["ISOFIX", "6_airbags", "camera_re", "controle_estabilidade"]  # "Manual", "Automatico"
    
    # Experiência
    primeiro_carro: bool = False
    experiencia_anos: Optional[int] = None
    
    # Capacidade Financeira (NOVO - Requirement 6)
    financial_capacity: Optional[FinancialCapacity] = Field(
        None,
        description="Capacidade financeira do usuário para cálculo de TCO"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "orcamento_min": 50000,
                "orcamento_max": 80000,
                "city": "São Paulo",
                "state": "SP",
                "uso_principal": "familia",
                "tamanho_familia": 4,
                "necessita_espaco": True,
                "tem_criancas": True,
                "prioridades": {
                    "economia": 4,
                    "espaco": 5,
                    "performance": 2,
                    "conforto": 4,
                    "seguranca": 5
                },
                "tipos_preferidos": ["SUV", "Sedan"],
                "ano_minimo": 2018,
                "km_maxima": 80000,
                "must_haves": ["ISOFIX", "6_airbags"],
                "raio_maximo_km": 30,
                "primeiro_carro": False
            }
        }

