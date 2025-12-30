"""
Script de teste para validar o Unified Recommendation Engine
"""

import sys
import os
import json

# Adicionar diretório correto ao path para imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
platform_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

# Imports absolutos
from models.car import Car
from models.dealership import Dealership
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def test_basic_recommendation():
    """Teste básico de recomendação"""
    print("="* 80)
    print("TESTE: UNIFIED RECOMMENDATION ENGINE")
    print("=" * 80)
    
    # Inicializar engine
    print("\n1. Inicializando engine...")
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Mostrar estatísticas
    print("\n2. Estatisticas da plataforma:")
    stats = engine.get_stats()
    print(f"   - Concessionarias ativas: {stats['active_dealerships']}")
    print(f"   - Total de carros: {stats['total_cars']}")
    print(f"   - Carros disponiveis: {stats['available_cars']}")
    print(f"   - Por estado: {stats['dealerships_by_state']}")
    print(f"   - Por categoria: {stats['cars_by_category']}")
    
    # Criar perfil de usuário família
    print("\n3. Criando perfil de usuario (familia em SP)...")
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=100000,
        city="São Paulo",
        state="SP",
        uso_principal="familia",
        tamanho_familia=4,
        tem_criancas=True,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "seguranca": 5,
            "conforto": 4,
            "performance": 2
        },
        tipos_preferidos=["SUV", "Sedan"]
    )
    
    # Gerar recomendações
    print("\n4. Gerando recomendacoes...")
    recommendations = engine.recommend(profile, limit=10)
    
    print(f"\n5. Resultados: {len(recommendations)} carros recomendados\n")
    print("=" * 80)
    
    # Mostrar top 5
    for i, rec in enumerate(recommendations[:5], 1):
        car = rec['car']
        print(f"\n#{i} - {rec['match_percentage']}% MATCH")
        print(f"   Carro: {car.nome}")
        print(f"   Preco: R$ {car.preco:,.2f}")
        print(f"   Ano: {car.ano} | KM: {car.quilometragem:,}")
        print(f"   Categoria: {car.categoria} | Combustivel: {car.combustivel}")
        print(f"   ---")
        print(f"   Concessionaria: {car.dealership_name}")
        print(f"   Localizacao: {car.dealership_city} - {car.dealership_state}")
        print(f"   Contato: {car.dealership_phone}")
        print(f"   WhatsApp: {car.dealership_whatsapp}")
        print(f"   ---")
        print(f"   Justificativa: {rec['justificativa']}")
    
    print("\n" + "=" * 80)
    
    # Verificar diversidade de concessionárias
    dealerships_in_results = set(rec['car'].dealership_id for rec in recommendations)
    print(f"\nDiversidade de concessionarias nos resultados:")
    for dealership_id in dealerships_in_results:
        count = sum(1 for rec in recommendations if rec['car'].dealership_id == dealership_id)
        dealership_name = recommendations[0]['car'].dealership_name if recommendations else "N/A"
        for rec in recommendations:
            if rec['car'].dealership_id == dealership_id:
                dealership_name = rec['car'].dealership_name
                break
        print(f"   - {dealership_name}: {count} carros")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUIDO COM SUCESSO!")
    print("=" * 80)


def test_different_profiles():
    """Teste com diferentes perfis"""
    print("\n\n" + "="* 80)
    print("TESTE: DIFERENTES PERFIS DE USUARIO")
    print("=" * 80)
    
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    # Perfil 1: Primeiro carro (econômico)
    print("\n1. PERFIL: Primeiro carro (economico)")
    profile1 = UserProfile(
        orcamento_min=30000,
        orcamento_max=60000,
        uso_principal="primeiro_carro",
        prioridades={
            "economia": 5,
            "conforto": 3,
            "seguranca": 4,
            "performance": 2,
            "espaco": 2
        },
        tipos_preferidos=["Hatch", "Compacto"]
    )
    
    recommendations1 = engine.recommend(profile1, limit=3)
    for rec in recommendations1:
        print(f"   - {rec['match_percentage']}% | {rec['car'].nome} | {rec['car'].dealership_city}")
    
    # Perfil 2: Executivo (conforto)
    print("\n2. PERFIL: Executivo (conforto e performance)")
    profile2 = UserProfile(
        orcamento_min=80000,
        orcamento_max=150000,
        uso_principal="trabalho",
        prioridades={
            "economia": 2,
            "conforto": 5,
            "seguranca": 4,
            "performance": 5,
            "espaco": 3
        },
        tipos_preferidos=["Sedan"]
    )
    
    recommendations2 = engine.recommend(profile2, limit=3)
    for rec in recommendations2:
        print(f"   - {rec['match_percentage']}% | {rec['car'].nome} | {rec['car'].dealership_city}")
    
    # Perfil 3: Aventureiro (SUV)
    print("\n3. PERFIL: Aventureiro (lazer e espaco)")
    profile3 = UserProfile(
        orcamento_min=70000,
        orcamento_max=120000,
        uso_principal="lazer",
        prioridades={
            "economia": 3,
            "conforto": 4,
            "seguranca": 4,
            "performance": 4,
            "espaco": 5
        },
        tipos_preferidos=["SUV"]
    )
    
    recommendations3 = engine.recommend(profile3, limit=3)
    for rec in recommendations3:
        print(f"   - {rec['match_percentage']}% | {rec['car'].nome} | {rec['car'].dealership_city}")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUIDO!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_basic_recommendation()
        test_different_profiles()
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()

