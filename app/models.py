from typing import List, Optional

from pydantic import BaseModel, field_validator


class QuestionarioBusca(BaseModel):
    # 1) Preferência de marca/modelo (Sistema Avançado)
    marca_preferida: str  # ou "sem_preferencia"
    marcas_alternativas: Optional[List[str]] = []  # múltiplas marcas com prioridade
    modelo_especifico: str  # ou "aberto_opcoes"
    modelos_alternativos: Optional[List[str]] = []  # múltiplos modelos

    # 2) Urgência do Processo de Compra
    urgencia: str  # "hoje_amanha", "esta_semana", "ate_15_dias", "sem_pressa"

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

    @field_validator("marcas_alternativas", "modelos_alternativos", mode="before")
    @classmethod
    def validate_alternative_lists(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v] if v.strip() else []
        return v


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

    @field_validator("opcionais", mode="before")
    @classmethod
    def validate_opcionais(cls, v):
        if v is None:
            return []
        return v

    @field_validator(
        "razoes_recomendacao", "pontos_fortes", "consideracoes", "fotos", mode="before"
    )
    @classmethod
    def validate_lists(cls, v):
        if v is None:
            return []
        return v


class RespostaBusca(BaseModel):
    recomendacoes: List[CarroRecomendacao] = []
    resumo_perfil: str = ""
    sugestoes_gerais: List[str] = []
