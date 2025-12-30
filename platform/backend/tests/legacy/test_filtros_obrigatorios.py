"""
Teste manual dos filtros obrigatórios
🔥 Validar que filtros opcionais se tornam obrigatórios quando selecionados
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.car import Car
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


def create_test_cars():
    """Criar carros de teste com diferentes características"""
    cars = [
        Car(
            id="1", nome="Toyota Corolla Cross", marca="Toyota", modelo="Corolla Cross",
            categoria="SUV", ano=2022, preco=150000, quilometragem=30000,
            combustivel="Flex", cambio="Automático CVT", disponivel=True,
            score_economia=0.8, score_familia=0.9, score_performance=0.7,
            score_conforto=0.8, score_seguranca=0.9,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
        Car(
            id="2", nome="Honda HR-V", marca="Honda", modelo="HR-V",
            categoria="SUV", ano=2021, preco=120000, quilometragem=40000,
            combustivel="Flex", cambio="Automático CVT", disponivel=True,
            score_economia=0.8, score_familia=0.85, score_performance=0.7,
            score_conforto=0.8, score_seguranca=0.85,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
        Car(
            id="3", nome="Fiat Argo", marca="Fiat", modelo="Argo",
            categoria="Hatch", ano=2020, preco=70000, quilometragem=50000,
            combustivel="Flex", cambio="Manual", disponivel=True,
            score_economia=0.9, score_familia=0.6, score_performance=0.6,
            score_conforto=0.6, score_seguranca=0.7,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
        Car(
            id="4", nome="Chevrolet Onix", marca="Chevrolet", modelo="Onix",
            categoria="Hatch", ano=2021, preco=75000, quilometragem=35000,
            combustivel="Flex", cambio="Automático", disponivel=True,
            score_economia=0.85, score_familia=0.65, score_performance=0.6,
            score_conforto=0.7, score_seguranca=0.75,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
        Car(
            id="5", nome="Volkswagen T-Cross", marca="Volkswagen", modelo="T-Cross",
            categoria="SUV", ano=2022, preco=130000, quilometragem=25000,
            combustivel="Flex", cambio="Automático", disponivel=True,
            score_economia=0.75, score_familia=0.85, score_performance=0.75,
            score_conforto=0.8, score_seguranca=0.85,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
        Car(
            id="6", nome="Toyota Yaris Sedan", marca="Toyota", modelo="Yaris",
            categoria="Sedan", ano=2021, preco=90000, quilometragem=45000,
            combustivel="Flex", cambio="Automático CVT", disponivel=True,
            score_economia=0.9, score_familia=0.7, score_performance=0.65,
            score_conforto=0.75, score_seguranca=0.8,
            dealership_id="test", dealership_name="Test Dealer",
            dealership_city="São Paulo", dealership_state="SP",
            dealership_phone="(11) 1234-5678", dealership_whatsapp="(11) 91234-5678"
        ),
    ]
    return cars


def test_marcas_preferidas():
    """Teste: Marcas preferidas devem ser obrigatórias"""
    print("\n" + "="*80)
    print("TESTE 1: Marcas Preferidas (Toyota, Honda)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        marcas_preferidas=["Toyota", "Honda"]
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.categoria})")
    
    # Validar
    assert all(car.marca in ["Toyota", "Honda"] for car in filtered), "❌ FALHOU: Carros de outras marcas encontrados"
    assert len(filtered) == 3, f"❌ FALHOU: Esperado 3 carros (2 Toyota + 1 Honda), encontrado {len(filtered)}"
    print("\n✅ PASSOU: Apenas Toyota e Honda retornados")


def test_marcas_rejeitadas():
    """Teste: Marcas rejeitadas devem ser eliminadas"""
    print("\n" + "="*80)
    print("TESTE 2: Marcas Rejeitadas (Fiat, Chevrolet)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        marcas_rejeitadas=["Fiat", "Chevrolet"]
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.categoria})")
    
    # Validar
    assert all(car.marca not in ["Fiat", "Chevrolet"] for car in filtered), "❌ FALHOU: Marcas rejeitadas encontradas"
    assert len(filtered) == 4, f"❌ FALHOU: Esperado 4 carros, encontrado {len(filtered)}"
    print("\n✅ PASSOU: Fiat e Chevrolet eliminados")


def test_tipos_preferidos():
    """Teste: Tipos preferidos devem ser obrigatórios"""
    print("\n" + "="*80)
    print("TESTE 3: Tipos Preferidos (SUV)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        tipos_preferidos=["SUV"]
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.categoria})")
    
    # Validar
    assert all(car.categoria == "SUV" for car in filtered), "❌ FALHOU: Carros de outras categorias encontrados"
    assert len(filtered) == 3, f"❌ FALHOU: Esperado 3 SUVs, encontrado {len(filtered)}"
    print("\n✅ PASSOU: Apenas SUVs retornados")


def test_combustivel_preferido():
    """Teste: Combustível preferido deve ser obrigatório"""
    print("\n" + "="*80)
    print("TESTE 4: Combustível Preferido (Flex)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        combustivel_preferido="Flex"
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.combustivel})")
    
    # Validar
    assert all(car.combustivel == "Flex" for car in filtered), "❌ FALHOU: Carros com outro combustível encontrados"
    assert len(filtered) == 6, f"❌ FALHOU: Esperado 6 carros Flex, encontrado {len(filtered)}"
    print("\n✅ PASSOU: Apenas Flex retornados")


def test_cambio_preferido():
    """Teste: Câmbio preferido deve ser obrigatório"""
    print("\n" + "="*80)
    print("TESTE 5: Câmbio Preferido (Automático)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        cambio_preferido="Automático"
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.cambio})")
    
    # Validar
    assert all(car.cambio and "Automático" in car.cambio for car in filtered), "❌ FALHOU: Carros com câmbio manual encontrados"
    assert len(filtered) == 5, f"❌ FALHOU: Esperado 5 carros automáticos, encontrado {len(filtered)}"
    print("\n✅ PASSOU: Apenas automáticos retornados")


def test_multiplos_filtros():
    """Teste: Múltiplos filtros devem ser aplicados simultaneamente"""
    print("\n" + "="*80)
    print("TESTE 6: Múltiplos Filtros (Toyota + SUV + Flex)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        marcas_preferidas=["Toyota"],
        tipos_preferidos=["SUV"],
        combustivel_preferido="Flex"
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    print("\nCarros retornados:")
    for car in filtered:
        print(f"  - {car.marca} {car.modelo} ({car.categoria}, {car.combustivel})")
    
    # Validar
    assert all(car.marca == "Toyota" for car in filtered), "❌ FALHOU: Marca incorreta"
    assert all(car.categoria == "SUV" for car in filtered), "❌ FALHOU: Categoria incorreta"
    assert all(car.combustivel == "Flex" for car in filtered), "❌ FALHOU: Combustível incorreto"
    assert len(filtered) == 1, f"❌ FALHOU: Esperado 1 carro (Corolla Cross), encontrado {len(filtered)}"
    print("\n✅ PASSOU: Apenas Toyota Corolla Cross SUV Flex retornado")


def test_filtros_impossiveis():
    """Teste: Filtros impossíveis devem retornar lista vazia"""
    print("\n" + "="*80)
    print("TESTE 7: Filtros Impossíveis (Ferrari)")
    print("="*80)
    
    cars = create_test_cars()
    engine = UnifiedRecommendationEngine(data_dir="data")
    
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=200000,
        uso_principal="familia",
        tamanho_familia=4,
        marcas_preferidas=["Ferrari"]  # Marca que não existe
    )
    
    filtered = engine.filter_by_preferences(cars, profile)
    
    print(f"\nCarros antes do filtro: {len(cars)}")
    print(f"Carros após filtro: {len(filtered)}")
    
    # Validar
    assert len(filtered) == 0, f"❌ FALHOU: Esperado 0 carros, encontrado {len(filtered)}"
    print("\n✅ PASSOU: Lista vazia retornada (nenhum carro atende aos critérios)")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔥 TESTES DE FILTROS OBRIGATÓRIOS")
    print("Validando que filtros opcionais se tornam obrigatórios quando selecionados")
    print("="*80)
    
    try:
        test_marcas_preferidas()
        test_marcas_rejeitadas()
        test_tipos_preferidos()
        test_combustivel_preferido()
        test_cambio_preferido()
        test_multiplos_filtros()
        test_filtros_impossiveis()
        
        print("\n" + "="*80)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*80)
        print("\n🎉 Filtros obrigatórios implementados com sucesso!")
        print("📋 Regra aplicada: Qualquer filtro opcional selecionado torna-se obrigatório")
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
