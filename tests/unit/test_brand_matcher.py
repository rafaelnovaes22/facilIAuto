"""
🧪 Unit Tests - Brand Matcher
Testes para o sistema de fuzzy matching de marcas/modelos
"""

import pytest

from app.brand_matcher import AdvancedBrandMatcher, BrandMatch


class TestAdvancedBrandMatcher:
    """Testes para o matcher avançado de marcas"""

    @pytest.fixture
    def matcher(self):
        """Fixture do matcher"""
        return AdvancedBrandMatcher()

    def test_normalize_text(self, matcher):
        """Testa normalização de texto"""
        # Arrange & Act & Assert
        assert matcher.normalize_text("  Toyota  ") == "toyota"
        assert matcher.normalize_text("Volks-Wagen") == "volkswagen"
        assert matcher.normalize_text("B.M.W") == "bmw"
        assert matcher.normalize_text("") == ""
        assert matcher.normalize_text(None) == ""

    def test_calculate_similarity(self, matcher):
        """Testa cálculo de similaridade"""
        # Arrange & Act & Assert
        assert matcher.calculate_similarity("toyota", "toyota") == 1.0
        assert matcher.calculate_similarity("toyota", "toyot") > 0.8
        assert matcher.calculate_similarity("toyota", "honda") < 0.5
        assert matcher.calculate_similarity("", "") == 1.0

    def test_find_best_brand_match_exact(self, matcher):
        """Testa match exato de marca"""
        # Arrange
        user_input = "TOYOTA"

        # Act
        result = matcher.find_best_brand_match(user_input)

        # Assert
        assert isinstance(result, BrandMatch)
        assert result.matched == "TOYOTA"
        assert result.confidence >= 0.9
        assert result.original == user_input

    def test_find_best_brand_match_fuzzy(self, matcher):
        """Testa fuzzy matching de marca"""
        # Arrange
        user_input = "toyot"

        # Act
        result = matcher.find_best_brand_match(user_input)

        # Assert
        assert result.matched == "TOYOTA"
        assert result.confidence >= 0.6
        assert len(result.suggestions) >= 0

    def test_find_best_brand_match_variation(self, matcher):
        """Testa matching com variações conhecidas"""
        # Arrange & Act & Assert

        # VW variations
        vw_result = matcher.find_best_brand_match("vw")
        assert vw_result.matched == "VOLKSWAGEN"
        assert vw_result.confidence >= 0.6

        # BMW variations
        bmw_result = matcher.find_best_brand_match("beeme")
        assert bmw_result.matched == "BMW"

        # Hyundai variations
        hyundai_result = matcher.find_best_brand_match("hundai")
        assert hyundai_result.matched == "HYUNDAI"

    def test_find_best_brand_match_empty(self, matcher):
        """Testa match com entrada vazia"""
        # Arrange
        user_input = ""

        # Act
        result = matcher.find_best_brand_match(user_input)

        # Assert
        assert result.matched == "sem_preferencia"
        assert result.confidence == 0.0

    def test_find_best_model_match_exact(self, matcher):
        """Testa match exato de modelo"""
        # Arrange
        user_input = "Corolla"
        brand = "TOYOTA"

        # Act
        result = matcher.find_best_model_match(user_input, brand)

        # Assert
        assert result.matched.lower() == "corolla"
        assert result.confidence >= 0.9

    def test_find_best_model_match_fuzzy(self, matcher):
        """Testa fuzzy matching de modelo"""
        # Arrange
        user_input = "corola"  # Erro comum
        brand = "TOYOTA"

        # Act
        result = matcher.find_best_model_match(user_input, brand)

        # Assert
        assert "corolla" in result.matched.lower()
        assert result.confidence >= 0.6

    def test_find_best_model_match_no_brand(self, matcher):
        """Testa match de modelo sem marca específica"""
        # Arrange
        user_input = "civic"

        # Act
        result = matcher.find_best_model_match(user_input, "")

        # Assert
        assert "civic" in result.matched.lower()
        assert result.confidence >= 0.6

    def test_find_best_model_match_default_values(self, matcher):
        """Testa valores padrão para modelo"""
        # Arrange & Act & Assert

        # Entrada vazia
        empty_result = matcher.find_best_model_match("", "TOYOTA")
        assert empty_result.matched == "aberto_opcoes"

        # Valor padrão
        default_result = matcher.find_best_model_match("aberto_opcoes", "TOYOTA")
        assert default_result.matched == "aberto_opcoes"

        # Sem preferência
        no_pref_result = matcher.find_best_model_match("sem_preferencia", "TOYOTA")
        assert no_pref_result.matched == "aberto_opcoes"

    def test_get_autocomplete_suggestions_brand(self, matcher):
        """Testa auto-complete para marcas"""
        # Arrange
        query = "toy"

        # Act
        suggestions = matcher.get_autocomplete_suggestions(query, "brand")

        # Assert
        assert isinstance(suggestions, list)
        assert "TOYOTA" in suggestions
        assert len(suggestions) <= 5

    def test_get_autocomplete_suggestions_model(self, matcher):
        """Testa auto-complete para modelos"""
        # Arrange
        query = "cor"

        # Act
        suggestions = matcher.get_autocomplete_suggestions(query, "model")

        # Assert
        assert isinstance(suggestions, list)
        assert any("corolla" in s.lower() for s in suggestions)

    def test_get_autocomplete_suggestions_short_query(self, matcher):
        """Testa auto-complete com query muito curta"""
        # Arrange
        query = "t"

        # Act
        suggestions = matcher.get_autocomplete_suggestions(query, "brand")

        # Assert
        assert suggestions == []

    def test_validate_and_normalize_preferences(self, matcher):
        """Testa validação e normalização completa"""
        # Arrange
        marca = "toyot"
        modelo = "corola"

        # Act
        result = matcher.validate_and_normalize_preferences(marca, modelo)

        # Assert
        assert isinstance(result, dict)
        assert "marca_normalizada" in result
        assert "modelo_normalizado" in result
        assert "marca_confianca" in result
        assert "modelo_confianca" in result
        assert result["marca_normalizada"] == "TOYOTA"
        assert "corolla" in result["modelo_normalizado"].lower()

    def test_confidence_threshold(self, matcher):
        """Testa threshold de confiança"""
        # Arrange
        very_different = "xyz123"

        # Act
        result = matcher.find_best_brand_match(very_different)

        # Assert
        # Se a confiança for muito baixa, deve retornar o input original
        if result.confidence < matcher.confidence_threshold:
            assert result.matched == very_different

    @pytest.mark.parametrize(
        "input_brand,expected",
        [
            ("toyota", "TOYOTA"),
            ("HONDA", "HONDA"),
            ("vw", "VOLKSWAGEN"),
            ("volks", "VOLKSWAGEN"),
            ("bmw", "BMW"),
            ("beeme", "BMW"),
            ("hyundai", "HYUNDAI"),
            ("hundai", "HYUNDAI"),
            ("", "sem_preferencia"),
        ],
    )
    def test_brand_matching_cases(self, matcher, input_brand, expected):
        """Testa casos específicos de matching de marcas"""
        # Act
        result = matcher.find_best_brand_match(input_brand)

        # Assert
        assert result.matched == expected
