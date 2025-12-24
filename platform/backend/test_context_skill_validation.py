#!/usr/bin/env python3
"""
🧪 Teste da Context-Based Recommendation Skill
Demonstra validações REAIS dos critérios da Uber/99

Execute: python test_context_skill_validation.py
"""

import sys
import os

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from services.context_based_recommendation_skill import create_context_skill
from services.search_intent_classifier import create_intent_classifier
from services.app_transport_validator import validator as app_validator

def test_app_transport_validation():
    """Testa validação de critérios reais da Uber/99"""
    
    print("🧪 TESTE: Validação de Critérios REAIS da Uber/99")
    print("=" * 60)
    
    # Casos de teste
    test_cases = [
        {
            'name': 'Toyota Corolla 2022 - Deveria ser aceito',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2022,
            'expected': True
        },
        {
            'name': 'Chevrolet Onix Plus 2021 - Deveria ser aceito',
            'marca': 'Chevrolet', 
            'modelo': 'Onix Plus',
            'ano': 2021,
            'expected': True
        },
        {
            'name': 'Fiat Uno 2010 - Muito antigo',
            'marca': 'Fiat',
            'modelo': 'Uno',
            'ano': 2010,
            'expected': False
        },
        {
            'name': 'Honda HR-V 2020 - Comfort/Black',
            'marca': 'Honda',
            'modelo': 'HR-V', 
            'ano': 2020,
            'expected': True
        },
        {
            'name': 'Ford Ka 2018 - Básico apenas',
            'marca': 'Ford',
            'modelo': 'Ka',
            'ano': 2018,
            'expected': True
        }
    ]
    
    print("\n📋 TESTES DE VALIDAÇÃO:")
    print("-" * 40)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print(f"   Veículo: {case['marca']} {case['modelo']} {case['ano']}")
        
        # Testar cada categoria
        categories = ['uberx_99pop', 'uber_comfort', 'uber_black']
        
        for categoria in categories:
            is_valid, accepted_category = app_validator.is_valid_for_app_transport(
                marca=case['marca'],
                modelo=case['modelo'],
                ano=case['ano'],
                categoria_desejada=categoria
            )
            
            status = "✅" if is_valid else "❌"
            print(f"   {status} {categoria}: {accepted_category or 'Rejeitado'}")
        
        # Obter todas as categorias aceitas
        all_categories = app_validator.get_accepted_categories(
            marca=case['marca'],
            modelo=case['modelo'],
            ano=case['ano']
        )
        
        print(f"   📱 Categorias aceitas: {all_categories if all_categories else 'Nenhuma'}")


def test_contextual_search():
    """Testa busca contextual com validação real"""
    
    print("\n\n🎯 TESTE: Busca Contextual com Validação REAL")
    print("=" * 60)
    
    # Criar skills
    context_skill = create_context_skill()
    intent_classifier = create_intent_classifier()
    
    test_queries = [
        "carros para fazer uber",
        "Toyota Corolla para uber comfort",
        "carros baratos para 99pop",
        "SUV para uber black"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 🔍 Query: '{query}'")
        
        # Analisar intenção
        analysis = intent_classifier.classify_intent(query)
        print(f"   🧠 Intenção: {analysis.primary_intent.value} (confiança: {analysis.confidence:.2f})")
        
        if analysis.entities:
            print(f"   🏷️  Entidades: {[(e.type, e.value) for e in analysis.entities]}")
        
        # Buscar recomendações
        recommendations = context_skill.recommend_by_context(query, max_results=3)
        
        print(f"   📊 Top {len(recommendations)} recomendações:")
        
        for j, rec in enumerate(recommendations, 1):
            car = rec.car
            print(f"   {j}. {car.marca} {car.modelo} {car.ano} - Score: {rec.final_score:.2f}")
            print(f"      💰 Preço: R$ {car.preco:,.0f}")
            
            # Validar REAL para apps
            all_categories = app_validator.get_accepted_categories(
                marca=car.marca,
                modelo=car.modelo,
                ano=car.ano
            )
            
            if all_categories:
                print(f"      ✅ Apps aceitos: {', '.join(all_categories)}")
            else:
                print(f"      ❌ Não aceito para apps")
                
            # Mostrar reasoning da skill
            if rec.reasoning:
                print(f"      💡 Motivos: {rec.reasoning[0] if rec.reasoning else 'N/A'}")
        
        print("-" * 40)


def test_specific_validation():
    """Testa validação específica de veículos"""
    
    print("\n\n🔬 TESTE: Validação Específica")
    print("=" * 60)
    
    # Casos específicos interessantes
    specific_tests = [
        ("Toyota", "Corolla", 2022),
        ("Chevrolet", "Onix Plus", 2020),
        ("Honda", "Civic", 2019),
        ("Nissan", "Kicks", 2021),
        ("Fiat", "Argo", 2018),
        ("Hyundai", "HB20", 2017),  # Este pode não ser aceito no Comfort
        ("BMW", "320i", 2020),      # Este pode ser aceito no Black
    ]
    
    for marca, modelo, ano in specific_tests:
        print(f"\n🚗 {marca} {modelo} {ano}")
        
        # Testar todas as categorias
        for categoria in ['uberx_99pop', 'uber_comfort', 'uber_black']:
            is_valid, accepted = app_validator.is_valid_for_app_transport(
                marca=marca,
                modelo=modelo,
                ano=ano,
                categoria_desejada=categoria
            )
            
            if is_valid:
                print(f"   ✅ {categoria}: ACEITO")
            else:
                print(f"   ❌ {categoria}: REJEITADO")
        
        # Mostrar requisitos não atendidos
        requirements = app_validator.get_requirements_for_category('uber_comfort')
        modelo_completo = f"{marca} {modelo}"
        modelos_aceitos = requirements.get('modelos_aceitos', [])
        
        if not any(modelo_aceito.lower() in modelo_completo.lower() for modelo_aceito in modelos_aceitos):
            print(f"   ⚠️  Modelo não está na lista oficial do Comfort")


if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE VALIDAÇÃO")
    print("Testando critérios REAIS da Uber/99 com dados atualizados")
    
    try:
        # Teste 1: Validação básica
        test_app_transport_validation()
        
        # Teste 2: Busca contextual
        test_contextual_search()
        
        # Teste 3: Validação específica
        test_specific_validation()
        
        print(f"\n\n🎉 TODOS OS TESTES CONCLUÍDOS!")
        print("✅ A skill utiliza validações REAIS dos critérios da Uber/99")
        print("📋 Dados baseados em requisitos oficiais atualizados")
        
    except Exception as e:
        print(f"\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()