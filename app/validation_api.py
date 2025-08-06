"""
API de Validação de Preferências
Endpoint dedicado para validar preferências em tempo real
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.enhanced_brand_processor import enhanced_brand_processor

router = APIRouter()


class PreferenceValidationRequest(BaseModel):
    marca_preferida: str
    modelo_especifico: Optional[str] = "aberto_opcoes"
    marcas_alternativas: Optional[List[str]] = []
    modelos_alternativos: Optional[List[str]] = []


class PreferenceValidationResponse(BaseModel):
    is_valid: bool
    confidence_score: float
    suggestions: List[str]
    normalized_data: Dict
    validation_issues: List[Dict]
    processing_quality: str


@router.post("/validate-preferences", response_model=PreferenceValidationResponse)
async def validate_preferences(request: PreferenceValidationRequest):
    """
    Valida preferências de marca/modelo em tempo real
    Implementa as estratégias da pesquisa detalhada
    """
    try:
        # Criar questionário temporário para validação
        from app.models import QuestionarioBusca

        temp_questionario = QuestionarioBusca(
            marca_preferida=request.marca_preferida,
            modelo_especifico=request.modelo_especifico or "aberto_opcoes",
            marcas_alternativas=request.marcas_alternativas or [],
            modelos_alternativos=request.modelos_alternativos or [],
            urgencia="sem_pressa",  # Valores padrão para validação
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="equilibrio",
        )

        # Processar com sistema avançado
        result = enhanced_brand_processor.process_and_validate_preferences(
            temp_questionario
        )

        # Gerar sugestões de melhoria
        suggestions = enhanced_brand_processor.generate_improvement_suggestions(result)

        # Determinar se é válido
        is_valid = (
            result.get("confidence_score", 0) >= 0.6
            and len(
                [
                    issue
                    for issue in result.get("validation_issues", [])
                    if issue.get("type") in ["conflicting_preferences"]
                ]
            )
            == 0
        )

        return PreferenceValidationResponse(
            is_valid=is_valid,
            confidence_score=result.get("confidence_score", 0.0),
            suggestions=suggestions,
            normalized_data={
                "marca_principal": result.get("marca_principal", {}),
                "modelo_principal": result.get("modelo_principal", {}),
                "marcas_alternativas": result.get("marcas_alternativas", []),
                "modelos_alternativos": result.get("modelos_alternativos", []),
            },
            validation_issues=result.get("validation_issues", []),
            processing_quality=result.get("processing_quality", "fair"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")


@router.get("/autocomplete/models/{brand}")
async def get_model_autocomplete(brand: str, query: str = ""):
    """
    Endpoint para auto-complete de modelos baseado na marca
    """
    try:
        from app.brand_matcher import brand_matcher

        if len(query) < 2:
            return {"suggestions": []}

        suggestions = brand_matcher.get_autocomplete_suggestions(query, "model")

        # Filtrar por marca se fornecida
        if brand and brand != "sem_preferencia":
            brand_models = brand_matcher.popular_models.get(brand.upper(), [])
            filtered_suggestions = [
                s for s in suggestions if s.lower() in [m.lower() for m in brand_models]
            ]
            return {"suggestions": filtered_suggestions}

        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no auto-complete: {str(e)}")


@router.get("/autocomplete/brands")
async def get_brand_autocomplete(query: str = ""):
    """
    Endpoint para auto-complete de marcas
    """
    try:
        from app.brand_matcher import brand_matcher

        if len(query) < 2:
            return {"suggestions": []}

        suggestions = brand_matcher.get_autocomplete_suggestions(query, "brand")
        return {"suggestions": suggestions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no auto-complete: {str(e)}")
