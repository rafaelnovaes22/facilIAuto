"""
API melhorada com sistema de fallback de imagens integrado
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import QuestionarioBusca, RespostaBusca, CarroRecomendacao
from app.busca_inteligente import processar_busca_inteligente
from app.database import get_carros, get_carro_by_id
from app.fallback_images import get_fallback_images, get_best_fallback
from typing import List

def enhance_car_with_fallbacks(carro: CarroRecomendacao) -> CarroRecomendacao:
    """Melhora um carro com sistema de fallback de imagens"""
    
    # Se não tem fotos, gerar fallbacks
    if not carro.fotos or len(carro.fotos) == 0:
        fallback_images = get_fallback_images(carro.marca, carro.modelo, carro.categoria)
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
    resultado = processar_busca_inteligente(questionario)
    
    # Melhorar cada recomendação com fallbacks
    recomendacoes_melhoradas = []
    for recomendacao in resultado.recomendacoes:
        recomendacao_melhorada = enhance_car_with_fallbacks(recomendacao)
        recomendacoes_melhoradas.append(recomendacao_melhorada)
    
    # Retornar resultado melhorado
    resultado.recomendacoes = recomendacoes_melhoradas
    return resultado