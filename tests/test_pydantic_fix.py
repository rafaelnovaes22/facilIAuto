#!/usr/bin/env python3
"""
Test script to verify the Pydantic validation fix for CarroRecomendacao
"""

from app.models import CarroRecomendacao


def test_pydantic_fix():
    """Test that CarroRecomendacao handles None values correctly"""

    print("🧪 Testing Pydantic validation fix...")

    # Test data with None values for list fields
    test_data = {
        "id": "test-123",
        "marca": "Toyota",
        "modelo": "Corolla",
        "versao": "XEi",
        "ano": 2020,
        "preco": 85000,
        "categoria": "sedan",
        "score_compatibilidade": 95.5,
        # These fields are None (which was causing the error)
        "razoes_recomendacao": None,
        "pontos_fortes": None,
        "consideracoes": None,
        "fotos": None,
        "opcionais": None,
    }

    try:
        # This should work now with the field validators
        carro = CarroRecomendacao(**test_data)

        print("✅ CarroRecomendacao created successfully!")
        print(f"   ID: {carro.id}")
        print(f"   Marca: {carro.marca}")
        print(f"   Modelo: {carro.modelo}")
        print(f"   Opcionais: {carro.opcionais} (type: {type(carro.opcionais)})")
        print(
            f"   Razões: {carro.razoes_recomendacao} (type: {type(carro.razoes_recomendacao)})"
        )
        print(f"   Fotos: {carro.fotos} (type: {type(carro.fotos)})")

        # Verify all None values were converted to empty lists
        assert carro.opcionais == [], f"Expected empty list, got {carro.opcionais}"
        assert (
            carro.razoes_recomendacao == []
        ), f"Expected empty list, got {carro.razoes_recomendacao}"
        assert (
            carro.pontos_fortes == []
        ), f"Expected empty list, got {carro.pontos_fortes}"
        assert (
            carro.consideracoes == []
        ), f"Expected empty list, got {carro.consideracoes}"
        assert carro.fotos == [], f"Expected empty list, got {carro.fotos}"

        print("✅ All None values correctly converted to empty lists!")
        assert True

    except Exception as e:
        print(f"❌ Error creating CarroRecomendacao: {e}")
        assert False, f"Error creating CarroRecomendacao: {e}"


def test_normal_data():
    """Test that normal data still works correctly"""

    print("\n🧪 Testing normal data handling...")

    test_data = {
        "id": "test-456",
        "marca": "Honda",
        "modelo": "Civic",
        "ano": 2021,
        "preco": 95000,
        "categoria": "sedan",
        "score_compatibilidade": 88.0,
        "razoes_recomendacao": ["Econômico", "Confiável"],
        "pontos_fortes": ["Baixo consumo", "Boa revenda"],
        "consideracoes": ["Espaço traseiro limitado"],
        "fotos": ["foto1.jpg", "foto2.jpg"],
        "opcionais": ["Ar condicionado", "Direção hidráulica"],
    }

    try:
        carro = CarroRecomendacao(**test_data)

        print("✅ CarroRecomendacao with normal data created successfully!")
        print(f"   Opcionais: {carro.opcionais}")
        print(f"   Razões: {carro.razoes_recomendacao}")
        print(f"   Fotos: {carro.fotos}")

        # Verify data is preserved correctly
        assert len(carro.opcionais) == 2
        assert len(carro.razoes_recomendacao) == 2
        assert len(carro.fotos) == 2

        print("✅ Normal data preserved correctly!")
        assert True

    except Exception as e:
        print(f"❌ Error with normal data: {e}")
        assert False, f"Error with normal data: {e}"


if __name__ == "__main__":
    print("🔧 PYDANTIC VALIDATION FIX TEST")
    print("=" * 40)

    success1 = test_pydantic_fix()
    success2 = test_normal_data()

    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! The Pydantic fix is working correctly.")
        print("✅ CarroRecomendacao now handles None values properly")
        print("✅ The original validation error should be resolved")
    else:
        print("❌ Some tests failed. Check the implementation.")

    print("=" * 40)
