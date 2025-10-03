"""
Modelo de Perfil de Usuário para sistema de recomendação
"""

from pydantic import BaseModel
from typing import Optional, List, Dict


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
    
    # Uso principal
    uso_principal: str  # "familia", "trabalho", "lazer", "comercial", "primeiro_carro"
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
        "seguranca": 3
    }
    
    # Preferências
    marcas_preferidas: List[str] = []
    marcas_rejeitadas: List[str] = []
    tipos_preferidos: List[str] = []  # ["Hatch", "Sedan", "SUV"]
    combustivel_preferido: Optional[str] = None
    cambio_preferido: Optional[str] = None  # "Manual", "Automatico"
    
    # Experiência
    primeiro_carro: bool = False
    experiencia_anos: Optional[int] = None
    
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
                "primeiro_carro": False
            }
        }

