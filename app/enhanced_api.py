"""
API melhorada com sistema de fallback de imagens integrado
"""


from app.busca_inteligente_fallback import processar_busca_inteligente_robusta
from app.fallback_images import get_best_fallback, get_fallback_images
from app.models import CarroRecomendacao, QuestionarioBusca, RespostaBusca


def enhance_car_with_fallbacks(carro: CarroRecomendacao) -> CarroRecomendacao:
    """Melhora um carro com sistema de fallback de imagens"""

    # Se não tem fotos, gerar fallbacks
    if not carro.fotos or len(carro.fotos) == 0:
        fallback_images = get_fallback_images(
            carro.marca, carro.modelo, carro.categoria
        )
        carro.fotos = fallback_images[:2]  # Máximo 2 imagens

    # Garantir que sempre temos pelo menos uma imagem
    if len(carro.fotos) == 0:
        fallback = get_best_fallback(carro.marca, carro.modelo, carro.categoria)
        carro.fotos = [fallback]

    return carro


# Endpoint melhorado para busca com fallback integrado
async def buscar_carros_enhanced(questionario: QuestionarioBusca) -> RespostaBusca:
    """Endpoint melhorado com sistema de fallback integrado"""

    # Processar busca normal
    resultado = processar_busca_inteligente_robusta(questionario)

    # Melhorar cada recomendação com fallbacks
    recomendacoes_melhoradas = []
    for recomendacao in resultado.recomendacoes:
        recomendacao_melhorada = enhance_car_with_fallbacks(recomendacao)
        recomendacoes_melhoradas.append(recomendacao_melhorada)

    # Retornar resultado melhorado
    resultado.recomendacoes = recomendacoes_melhoradas
    return resultado
