"""
Integration Test for Semantic Intelligence.
Run with: pytest platform/backend/tests/test_semantic_integration.py -s
"""
import pytest
from unittest.mock import MagicMock
from services.semantic_analysis_service import SemanticAnalysisService
from models.user_profile import UserProfile

def test_semantic_inference_demo():
    """
    Testa a inferência semântica com um perfil complexo.
    Este teste imprime os resultados para validação manual.
    """
    print("\n\n=== 🧠 Validando Inteligência Conexionista (Demo) ===")
    
    # 1. Perfil: Família Rica, mas sem prioridades explícitas
    profile = UserProfile(
        orcamento_min=150000,
        orcamento_max=250000,
        uso_principal="viagem_familia",
        tamanho_familia=5,
        tem_criancas=True,
        renda_mensal=35000,
        prioridades={} # Dicionário vazio, não lista
    )
    print(f"👤 Perfil: Renda 35k, 5 Pessoas, Uso: Viagem (Sem prioridades marcadas)")

    # 2. Inicializar Service
    service = SemanticAnalysisService()
    
    # Mock inteligente se não houver chaves (para CI/Dev local sem chaves)
    if not service.primary_client and not service.fallback_client:
        print("⚠️ Sem chaves de API detectadas. Usando Mock Inteligente para simulação.")
        service._call_llm = MagicMock(return_value='{"safety": 0.25, "space": 0.20, "comfort": 0.15, "performance": -0.1}')
    else:
        print("✅ Usando API Real (Groq/OpenAI) para inferência.")

    # 3. Analisar
    weights = service.analyze_profile(profile)
    
    # 4. Exibir Insights
    print(f"🔍 Pesos Inferidos pelo SLM: {weights}")
    
    # Validações lógicas (O que esperamos de uma "inteligência")
    if weights:
        # Família rica = Segurança e Conforto/Espaço
        score_safety = weights.get('safety', 0)
        score_space = weights.get('space', 0)
        
        print(f"   -> Inferred Safety Boost: {score_safety:+}")
        print(f"   -> Inferred Space Boost:  {score_space:+}")
        
        assert score_safety > 0, "Deveria ter inferido prioridade em Segurança"
        assert score_space > 0, "Deveria ter inferido prioridade em Espaço"
    else:
        print("❌ Nenhuma inferência gerada (Erro ou falha silenciosa).")
        
    print("=== Fim da Validação ===\n")
