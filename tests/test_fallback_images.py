"""
Testes unitários para o sistema de fallback de imagens
"""

import pytest

from app.fallback_images import (
    FallbackImageService,
    VehicleCategory,
    create_vehicle_placeholder,
    get_best_fallback,
    get_fallback_images,
)


class TestFallbackImageService:
    """Testes para a classe FallbackImageService"""

    def test_get_fallback_images_with_category(self):
        """Testa obtenção de fallbacks com categoria específica"""
        service = FallbackImageService()

        fallbacks = service.get_fallback_images("Toyota", "Corolla", "sedan")

        assert len(fallbacks) == 5
        assert all(isinstance(url, str) for url in fallbacks)
        assert all(url.startswith("http") for url in fallbacks)

    def test_get_fallback_images_without_category(self):
        """Testa obtenção de fallbacks sem categoria"""
        service = FallbackImageService()

        fallbacks = service.get_fallback_images("Honda", "Civic")

        assert len(fallbacks) == 5
        assert all(isinstance(url, str) for url in fallbacks)

    def test_get_category_fallback_images(self):
        """Testa fallbacks por categoria"""
        service = FallbackImageService()

        # Categoria válida
        sedan_fallbacks = service.get_category_fallback_images("sedan")
        assert len(sedan_fallbacks) >= 3

        # Categoria inválida
        invalid_fallbacks = service.get_category_fallback_images(
            "categoria_inexistente"
        )
        assert len(invalid_fallbacks) == 3  # Deve retornar fallbacks genéricos

    def test_get_brand_fallback_images(self):
        """Testa fallbacks por marca"""
        service = FallbackImageService()

        # Marca conhecida
        toyota_fallbacks = service.get_brand_fallback_images("Toyota")
        assert len(toyota_fallbacks) == 3
        assert "Toyota" in toyota_fallbacks[0] or "toyota" in toyota_fallbacks[0]

        # Marca desconhecida
        unknown_fallbacks = service.get_brand_fallback_images("MarcaInexistente")
        assert len(unknown_fallbacks) == 3

    def test_select_best_fallback_no_failed_urls(self):
        """Testa seleção da melhor opção sem URLs falhadas"""
        service = FallbackImageService()

        best = service.select_best_fallback("BMW", "X1", "suv_premium")

        assert isinstance(best, str)
        assert best.startswith("http")

    def test_select_best_fallback_with_failed_urls(self):
        """Testa seleção da melhor opção evitando URLs falhadas"""
        service = FallbackImageService()

        # Simular que a primeira opção falhou
        all_options = service.get_fallback_images("BMW", "X1", "suv_premium")
        failed_urls = [all_options[0]]

        best = service.select_best_fallback("BMW", "X1", "suv_premium", failed_urls)

        assert best not in failed_urls
        assert isinstance(best, str)
        assert best.startswith("http")

    def test_select_best_fallback_all_failed(self):
        """Testa seleção quando todas as opções falharam"""
        service = FallbackImageService()

        all_options = service.get_fallback_images("BMW", "X1", "suv_premium")

        best = service.select_best_fallback("BMW", "X1", "suv_premium", all_options)

        # Deve retornar o fallback final
        assert "Sem+Imagem" in best or "sem+imagem" in best.lower()

    def test_get_placeholder_with_info_basic(self):
        """Testa geração de placeholder básico"""
        service = FallbackImageService()

        placeholder = service.get_placeholder_with_info("Toyota", "Corolla")

        assert "TOYOTA" in placeholder.upper()
        assert "COROLLA" in placeholder.upper()
        assert "via.placeholder.com" in placeholder
        assert "400x300" in placeholder

    def test_get_placeholder_with_info_complete(self):
        """Testa geração de placeholder com todas as informações"""
        service = FallbackImageService()

        placeholder = service.get_placeholder_with_info(
            "BMW", "X1", 2024, "Preto", 500, 400
        )

        assert "BMW" in placeholder
        assert "X1" in placeholder
        assert "2024" in placeholder
        assert "500x400" in placeholder
        assert "212529" in placeholder  # Cor preta

    def test_get_placeholder_with_white_color(self):
        """Testa placeholder com cor branca"""
        service = FallbackImageService()

        placeholder = service.get_placeholder_with_info("Fiat", "Argo", 2023, "Branco")

        assert "F8F9FA" in placeholder  # Cor de fundo branca
        assert "333333" in placeholder  # Texto escuro

    def test_generate_vehicle_id_consistency(self):
        """Testa se o ID do veículo é consistente"""
        service = FallbackImageService()

        id1 = service._generate_vehicle_id("Toyota", "Corolla")
        id2 = service._generate_vehicle_id("Toyota", "Corolla")
        id3 = service._generate_vehicle_id("Honda", "Civic")

        assert id1 == id2  # Mesmo veículo deve ter mesmo ID
        assert id1 != id3  # Veículos diferentes devem ter IDs diferentes
        assert isinstance(id1, str)

    def test_is_dark_color(self):
        """Testa detecção de cores escuras"""
        service = FallbackImageService()

        # Cores escuras
        assert service._is_dark_color("#000000") is True  # Preto
        assert service._is_dark_color("#8B0000") is True  # Vermelho escuro

        # Cores claras
        assert service._is_dark_color("#FFFFFF") is False  # Branco
        assert service._is_dark_color("#FFCC00") is False  # Amarelo

    def test_get_category_enum(self):
        """Testa conversão de categoria para enum"""
        service = FallbackImageService()

        # Categorias válidas
        assert service._get_category_enum("sedan") == VehicleCategory.SEDAN
        assert service._get_category_enum("hatch") == VehicleCategory.HATCH
        assert service._get_category_enum("pickup") == VehicleCategory.PICKUP

        # Categoria inválida
        assert service._get_category_enum("categoria_inexistente") is None

    def test_brand_colors_mapping(self):
        """Testa mapeamento de cores por marca"""
        service = FallbackImageService()

        # Marcas conhecidas
        assert "TOYOTA" in service.brand_colors
        assert "BMW" in service.brand_colors
        assert "FIAT" in service.brand_colors

        # Cores são válidas (formato hex)
        for color in service.brand_colors.values():
            assert color.startswith("#")
            assert len(color) == 7


class TestUtilityFunctions:
    """Testes para funções utilitárias"""

    def test_get_fallback_images_function(self):
        """Testa função utilitária get_fallback_images"""
        fallbacks = get_fallback_images("Toyota", "Corolla", "sedan")

        assert len(fallbacks) == 5
        assert all(isinstance(url, str) for url in fallbacks)

    def test_get_best_fallback_function(self):
        """Testa função utilitária get_best_fallback"""
        best = get_best_fallback("Honda", "Civic", "sedan")

        assert isinstance(best, str)
        assert best.startswith("http")

    def test_get_best_fallback_with_failed_urls(self):
        """Testa função utilitária com URLs falhadas"""
        failed_urls = ["https://example.com/broken.jpg"]
        best = get_best_fallback("Honda", "Civic", "sedan", failed_urls)

        assert best not in failed_urls
        assert isinstance(best, str)

    def test_create_vehicle_placeholder_function(self):
        """Testa função utilitária create_vehicle_placeholder"""
        placeholder = create_vehicle_placeholder("BMW", "X1", 2024, "Azul")

        assert "BMW" in placeholder
        assert "X1" in placeholder
        assert "2024" in placeholder
        assert "via.placeholder.com" in placeholder


class TestFallbackImageIntegration:
    """Testes de integração do sistema de fallback"""

    def test_fallback_priority_system(self):
        """Testa sistema de prioridade de fallback"""
        service = FallbackImageService()

        # Obter todas as opções
        all_options = service.get_fallback_images("Toyota", "Corolla", "sedan")

        # Simular falha da primeira opção
        failed_urls = [all_options[0]]
        best = service.select_best_fallback("Toyota", "Corolla", "sedan", failed_urls)

        # Deve ser a segunda opção
        assert best == all_options[1]

        # Simular falha das duas primeiras
        failed_urls = all_options[:2]
        best = service.select_best_fallback("Toyota", "Corolla", "sedan", failed_urls)

        # Deve ser a terceira opção
        assert best == all_options[2]

    def test_different_categories_different_fallbacks(self):
        """Testa se categorias diferentes geram fallbacks diferentes"""
        service = FallbackImageService()

        sedan_fallbacks = service.get_fallback_images("Toyota", "Corolla", "sedan")
        pickup_fallbacks = service.get_fallback_images("Ford", "Ranger", "pickup")

        # Pelo menos uma URL deve ser diferente entre as categorias
        assert sedan_fallbacks[0] != pickup_fallbacks[0]

    def test_consistent_fallbacks_same_vehicle(self):
        """Testa se o mesmo veículo sempre gera os mesmos fallbacks"""
        service = FallbackImageService()

        fallbacks1 = service.get_fallback_images("Honda", "Civic", "sedan")
        fallbacks2 = service.get_fallback_images("Honda", "Civic", "sedan")

        assert fallbacks1 == fallbacks2


# Fixtures para testes
@pytest.fixture
def fallback_service():
    """Fixture para instância do serviço de fallback"""
    return FallbackImageService()


@pytest.fixture
def sample_vehicle_data():
    """Fixture com dados de exemplo de veículos"""
    return [
        ("Toyota", "Corolla", "sedan", 2023, "Branco"),
        ("BMW", "X1", "suv_premium", 2024, "Preto"),
        ("Ford", "Ranger", "pickup", 2022, None),
        ("Honda", "Civic", "sedan", 2023, "Azul"),
    ]
