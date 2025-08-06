"""
🧪 Unit Tests - Enhanced Brand Processor
Testes para o processador avançado de preferências
"""

from unittest.mock import Mock, patch

import pytest

from app.enhanced_brand_processor import EnhancedBrandProcessor
from app.models import QuestionarioBusca


class TestEnhancedBrandProcessor:
    """Testes para o processador avançado de marcas"""

    @pytest.fixture
    def processor(self):
        """Fixture do processador"""
        return EnhancedBrandProcessor()

    @pytest.fixture
    def sample_questionario(self):
        """Questionário de exemplo"""
        return QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            marcas_alternativas=["HONDA"],
            modelos_alternativos=["Civic"],
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
        )

    @patch("app.enhanced_brand_processor.brand_matcher")
    def test_process_and_validate_preferences_success(self, mock_matcher, processor, sample_questionario):
        """Testa processamento bem-sucedido de preferências"""
        # Arrange
        mock_matcher.validate_and_normalize_preferences.return_value = {
            "marca_normalizada": "TOYOTA",
            "marca_confianca": 0.95,
            "marca_sugestoes": [],
            "modelo_normalizado": "Corolla",
            "modelo_confianca": 0.98,
            "modelo_sugestoes": [],
        }

        mock_matcher.find_best_brand_match.return_value = Mock(matched="HONDA", confidence=0.99, suggestions=[])

        mock_matcher.find_best_model_match.return_value = Mock(matched="Civic", confidence=0.97, suggestions=[])

        # Act
        result = processor.process_and_validate_preferences(sample_questionario)

        # Assert
        assert "marca_principal" in result
        assert "modelo_principal" in result
        assert "marcas_alternativas" in result
        assert "modelos_alternativos" in result
        assert "confidence_score" in result
        assert "processing_quality" in result

        assert result["marca_principal"]["normalizada"] == "TOYOTA"
        assert result["modelo_principal"]["normalizado"] == "Corolla"
        assert len(result["marcas_alternativas"]) == 1
        assert len(result["modelos_alternativos"]) == 1

    @patch("app.enhanced_brand_processor.brand_matcher")
    def test_process_low_confidence_brand(self, mock_matcher, processor, sample_questionario):
        """Testa processamento com baixa confiança na marca"""
        # Arrange
        mock_matcher.validate_and_normalize_preferences.return_value = {
            "marca_normalizada": "TOYOTA",
            "marca_confianca": 0.5,  # Baixa confiança
            "marca_sugestoes": ["HONDA", "HYUNDAI"],
            "modelo_normalizado": "Corolla",
            "modelo_confianca": 0.98,
            "modelo_sugestoes": [],
        }

        mock_matcher.find_best_brand_match.return_value = Mock(matched="HONDA", confidence=0.99, suggestions=[])

        # Act
        result = processor.process_and_validate_preferences(sample_questionario)

        # Assert
        assert len(result["validation_issues"]) > 0
        assert any(issue["type"] == "low_confidence_brand" for issue in result["validation_issues"])
        assert result["needs_user_confirmation"] is True

    @patch("app.enhanced_brand_processor.brand_matcher")
    def test_process_low_confidence_model(self, mock_matcher, processor, sample_questionario):
        """Testa processamento com baixa confiança no modelo"""
        # Arrange
        mock_matcher.validate_and_normalize_preferences.return_value = {
            "marca_normalizada": "TOYOTA",
            "marca_confianca": 0.95,
            "marca_sugestoes": [],
            "modelo_normalizado": "Corolla",
            "modelo_confianca": 0.4,  # Baixa confiança
            "modelo_sugestoes": ["Civic", "Accord"],
        }

        mock_matcher.find_best_brand_match.return_value = Mock(matched="HONDA", confidence=0.99, suggestions=[])

        # Act
        result = processor.process_and_validate_preferences(sample_questionario)

        # Assert
        assert len(result["validation_issues"]) > 0
        assert any(issue["type"] == "low_confidence_model" for issue in result["validation_issues"])

    def test_assess_processing_quality(self, processor):
        """Testa avaliação da qualidade do processamento"""
        # Arrange & Act & Assert

        # Excelente qualidade
        assert processor._assess_processing_quality(0.95, []) == "excellent"

        # Boa qualidade
        assert processor._assess_processing_quality(0.8, [{"type": "minor"}]) == "good"

        # Qualidade razoável
        assert processor._assess_processing_quality(0.6, []) == "fair"

        # Qualidade ruim
        assert processor._assess_processing_quality(0.3, []) == "poor"

    def test_generate_improvement_suggestions_poor_quality(self, processor):
        """Testa geração de sugestões para qualidade ruim"""
        # Arrange
        processing_result = {"processing_quality": "poor", "validation_issues": []}

        # Act
        suggestions = processor.generate_improvement_suggestions(processing_result)

        # Assert
        assert len(suggestions) > 0
        assert any("específico" in s for s in suggestions)

    def test_generate_improvement_suggestions_low_confidence_brand(self, processor):
        """Testa sugestões para baixa confiança de marca"""
        # Arrange
        processing_result = {
            "processing_quality": "good",
            "validation_issues": [
                {
                    "type": "low_confidence_brand",
                    "suggestions": ["TOYOTA", "HONDA", "FORD"],
                }
            ],
        }

        # Act
        suggestions = processor.generate_improvement_suggestions(processing_result)

        # Assert
        assert len(suggestions) > 0
        assert any("TOYOTA, HONDA, FORD" in s for s in suggestions)

    def test_generate_improvement_suggestions_conflicting_preferences(self, processor):
        """Testa sugestões para preferências conflitantes"""
        # Arrange
        processing_result = {
            "processing_quality": "good",
            "validation_issues": [{"type": "conflicting_preferences"}],
        }

        # Act
        suggestions = processor.generate_improvement_suggestions(processing_result)

        # Assert
        assert len(suggestions) > 0
        assert any("repetir" in s for s in suggestions)

    def test_generate_improvement_suggestions_no_alternatives(self, processor):
        """Testa sugestões quando não há alternativas"""
        # Arrange
        processing_result = {
            "processing_quality": "good",
            "validation_issues": [],
            "marcas_alternativas": [],
        }

        # Act
        suggestions = processor.generate_improvement_suggestions(processing_result)

        # Assert
        assert len(suggestions) > 0
        assert any("alternativas" in s for s in suggestions)

    @patch("app.enhanced_brand_processor.brand_matcher")
    @patch("app.enhanced_brand_processor.logger")
    def test_process_with_exception(self, mock_logger, mock_matcher, processor, sample_questionario):
        """Testa processamento com exceção"""
        # Arrange
        mock_matcher.validate_and_normalize_preferences.side_effect = Exception("Erro de teste")

        # Act
        result = processor.process_and_validate_preferences(sample_questionario)

        # Assert
        assert "error" in result
        assert result["fallback_result"] is True
        assert "marca_principal" in result
        assert "modelo_principal" in result
        mock_logger.error.assert_called_once()

    def test_conflicting_preferences_detection(self, processor):
        """Testa detecção de preferências conflitantes"""
        # Arrange
        questionario = QuestionarioBusca(
            marca_preferida="TOYOTA",
            modelo_especifico="Corolla",
            marcas_alternativas=["TOYOTA"],  # Conflito: mesma marca principal
            urgencia="hoje_amanha",
            regiao="SP",
            uso_principal=["urbano"],
            pessoas_transportar=4,
            criancas=False,
            animais=False,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="economia",
        )

        with patch("app.enhanced_brand_processor.brand_matcher") as mock_matcher:
            mock_matcher.validate_and_normalize_preferences.return_value = {
                "marca_normalizada": "TOYOTA",
                "marca_confianca": 0.95,
                "marca_sugestoes": [],
                "modelo_normalizado": "Corolla",
                "modelo_confianca": 0.98,
                "modelo_sugestoes": [],
            }

            mock_matcher.find_best_brand_match.return_value = Mock(matched="TOYOTA", confidence=0.99, suggestions=[])

            # Act
            result = processor.process_and_validate_preferences(questionario)

            # Assert
            assert any(issue["type"] == "conflicting_preferences" for issue in result["validation_issues"])
