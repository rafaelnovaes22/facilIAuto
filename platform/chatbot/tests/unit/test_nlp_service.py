"""
Unit tests for NLP Service
"""

import pytest
from src.services.nlp_service import (
    NLPService,
    Intent,
    IntentClassifier,
    Sentiment,
)


class TestIntentClassifier:
    """Tests for IntentClassifier"""
    
    @pytest.fixture
    def classifier(self):
        return IntentClassifier()
    
    def test_greeting_intent(self, classifier):
        """Test greeting intent classification"""
        test_cases = [
            "oi",
            "olá",
            "bom dia",
            "boa tarde",
            "boa noite",
            "e aí",
            "tudo bem?",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.GREETING
            assert confidence > 0.5
    
    def test_budget_inquiry_intent(self, classifier):
        """Test budget inquiry intent classification"""
        test_cases = [
            "qual o preço?",
            "quanto custa?",
            "tenho 50 mil de orçamento",
            "posso gastar até R$ 80.000",
            "valor do carro",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.BUDGET_INQUIRY
            assert confidence > 0.5
    
    def test_car_recommendation_intent(self, classifier):
        """Test car recommendation intent classification"""
        test_cases = [
            "me recomenda um carro",
            "qual carro você sugere?",
            "preciso de um carro para família",
            "estou procurando um SUV",
            "quero comprar um carro",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.CAR_RECOMMENDATION
            assert confidence > 0.5
    
    def test_car_details_intent(self, classifier):
        """Test car details intent classification"""
        test_cases = [
            "quero saber mais detalhes",
            "qual o consumo?",
            "me fala sobre o motor",
            "quais são as especificações?",
            "ficha técnica",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.CAR_DETAILS
            assert confidence > 0.5
    
    def test_compare_cars_intent(self, classifier):
        """Test compare cars intent classification"""
        test_cases = [
            "comparar esses carros",
            "qual é melhor?",
            "diferença entre eles",
            "Civic ou Corolla?",
            "qual devo escolher?",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.COMPARE_CARS
            assert confidence > 0.5
    
    def test_test_drive_intent(self, classifier):
        """Test test drive intent classification"""
        test_cases = [
            "quero fazer test drive",
            "posso testar o carro?",
            "agendar test-drive",
            "quando posso dirigir?",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.SCHEDULE_TEST_DRIVE
            assert confidence > 0.5
    
    def test_human_handoff_intent(self, classifier):
        """Test human handoff intent classification"""
        test_cases = [
            "quero falar com um atendente",
            "preciso de uma pessoa",
            "falar com humano",
            "operador por favor",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.HUMAN_HANDOFF
            assert confidence > 0.5
    
    def test_feedback_positive_intent(self, classifier):
        """Test positive feedback intent classification"""
        test_cases = [
            "obrigado!",
            "muito bom",
            "excelente",
            "adorei",
            "perfeito",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.FEEDBACK_POSITIVE
            assert confidence > 0.5
    
    def test_feedback_negative_intent(self, classifier):
        """Test negative feedback intent classification"""
        test_cases = [
            "não gostei",
            "ruim",
            "péssimo",
            "não é isso que quero",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.FEEDBACK_NEGATIVE
            assert confidence > 0.5
    
    def test_unknown_intent(self, classifier):
        """Test unknown intent classification"""
        test_cases = [
            "xyzabc123",
            "asdfghjkl",
            "???",
        ]
        
        for text in test_cases:
            intent, confidence = classifier.classify(text.lower())
            assert intent == Intent.UNKNOWN
            assert confidence < 0.5


class TestNLPService:
    """Tests for NLPService"""
    
    @pytest.fixture
    async def nlp_service(self):
        return NLPService()
    
    @pytest.mark.asyncio
    async def test_process_greeting(self, nlp_service):
        """Test processing greeting message"""
        result = await nlp_service.process("Olá, bom dia!")
        
        assert result.intent == Intent.GREETING
        assert result.confidence > 0.5
        assert result.language == "pt-BR"
        assert result.normalized_text == "olá, bom dia!"
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_process_budget_inquiry(self, nlp_service):
        """Test processing budget inquiry"""
        result = await nlp_service.process("Tenho 60 mil de orçamento")
        
        assert result.intent == Intent.BUDGET_INQUIRY
        assert result.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_normalize_text(self, nlp_service):
        """Test text normalization"""
        test_cases = [
            ("OLÁ!!!!", "olá!"),
            ("Bom    dia", "bom dia"),
            ("  teste  ", "teste"),
            ("MAIÚSCULAS", "maiúsculas"),
        ]
        
        for input_text, expected in test_cases:
            normalized = nlp_service._normalize_text(input_text)
            assert normalized == expected
    
    @pytest.mark.asyncio
    async def test_processing_time_recorded(self, nlp_service):
        """Test that processing time is recorded"""
        result = await nlp_service.process("teste")
        
        assert result.processing_time_ms > 0
        assert result.processing_time_ms < 1000  # Should be fast
    
    @pytest.mark.asyncio
    async def test_multiple_intents_in_message(self, nlp_service):
        """Test message with multiple possible intents"""
        # Message has both greeting and budget inquiry
        result = await nlp_service.process("Olá, tenho 50 mil de orçamento")
        
        # Should pick the strongest intent
        assert result.intent in [Intent.GREETING, Intent.BUDGET_INQUIRY]
        assert result.confidence > 0.5


@pytest.mark.asyncio
async def test_nlp_service_initialization():
    """Test NLP service can be initialized"""
    service = NLPService()
    assert service is not None
    assert service.intent_classifier is not None


@pytest.mark.asyncio
async def test_intent_enum_values():
    """Test Intent enum has expected values"""
    expected_intents = [
        "greeting",
        "budget_inquiry",
        "car_recommendation",
        "car_details",
        "compare_cars",
        "schedule_test_drive",
        "contact_dealer",
        "human_handoff",
        "feedback_positive",
        "feedback_negative",
        "unknown",
    ]
    
    for intent_value in expected_intents:
        assert intent_value in [i.value for i in Intent]
