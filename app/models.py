from pydantic import BaseModel, field_validator
from typing import List, Optional

class QuestionarioBusca(BaseModel):
    # 1) Preferência de marca/modelo
    marca_preferida: str  # ou "sem_preferencia"
    modelo_especifico: str  # ou "aberto_opcoes"
    
    # 2) Urgência
    urgencia: str  # "imediato", "proximo_mes", "proximos_meses", "sem_pressa"
    
    # 3) Região
    regiao: str  # nome da cidade/região
    
    # 4) Uso Principal
    uso_principal: List[str]  # ["trabalho", "familia", "viagem", "urbano"]
    
    # 5) Família/Crianças/Animais
    pessoas_transportar: int  # número de pessoas
    criancas: bool = False
    animais: bool = False
    
    # 6) Espaço e Potência
    espaco_carga: str  # "pouco", "medio", "muito"
    potencia_desejada: str  # "economica", "media", "alta"
    
    # 7) Qualidade e Investimento
    prioridade: str  # "economia", "conforto", "seguranca", "performance", "equilibrio"
    
    # 8) Vamos definir sua faixa de investimento (campos opcionais)
    orcamento_min: Optional[int] = None
    orcamento_max: Optional[int] = None

class CarroRecomendacao(BaseModel):
    id: str
    marca: str
    modelo: str
    versao: Optional[str] = None
    ano: int
    preco: int
    preco_promocional: Optional[int] = None
    categoria: str
    cor: Optional[str] = None
    km: Optional[int] = None
    score_compatibilidade: float
    razoes_recomendacao: List[str] = []
    pontos_fortes: List[str] = []
    consideracoes: List[str] = []
    fotos: List[str] = []
    descricao: Optional[str] = None
    opcionais: List[str] = []
    
    @field_validator('opcionais', mode='before')
    @classmethod
    def validate_opcionais(cls, v):
        if v is None:
            return []
        return v
    
    @field_validator('razoes_recomendacao', 'pontos_fortes', 'consideracoes', 'fotos', mode='before')
    @classmethod
    def validate_lists(cls, v):
        if v is None:
            return []
        return v

class RespostaBusca(BaseModel):
    recomendacoes: List[CarroRecomendacao] = []
    resumo_perfil: str = ""
    sugestoes_gerais: List[str] = [] 