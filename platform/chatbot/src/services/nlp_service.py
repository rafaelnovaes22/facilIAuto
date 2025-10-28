"""
NLP Service for WhatsApp Chatbot

Provides natural language processing capabilities including:
- Intent classification
- Named Entity Recognition (NER)
- Sentiment analysis
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """Intenções identificadas no processamento de mensagens"""
    
    GREETING = "greeting"
    BUDGET_INQUIRY = "budget_inquiry"
    CAR_RECOMMENDATION = "car_recommendation"
    CAR_DETAILS = "car_details"
    COMPARE_CARS = "compare_cars"
    SCHEDULE_TEST_DRIVE = "schedule_test_drive"
    CONTACT_DEALER = "contact_dealer"
    HUMAN_HANDOFF = "human_handoff"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    LOCATION_INQUIRY = "location_inquiry"
    FINANCING_INQUIRY = "financing_inquiry"
    USAGE_INQUIRY = "usage_inquiry"
    PREFERENCE_INQUIRY = "preference_inquiry"
    UNKNOWN = "unknown"


class Entity(BaseModel):
    """Entidade extraída da mensagem"""
    
    type: str  # budget, brand, model, category, year, location, preference
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None


class Sentiment(str, Enum):
    """Sentimento da mensagem"""
    
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class NLPResult(BaseModel):
    """Resultado do processamento NLP"""
    
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    entities: List[Entity] = Field(default_factory=list)
    sentiment: Sentiment = Sentiment.NEUTRAL
    language: str = "pt-BR"
    normalized_text: str = ""
    processing_time_ms: float = 0.0


class IntentClassifier:
    """Classificador de intenções baseado em regras e padrões"""
    
    def __init__(self):
        # Padrões de intenção (keywords e regex patterns)
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(oi|olá|ola|hey|opa|e aí|eai|bom dia|boa tarde|boa noite)\b',
                r'\b(tudo bem|como vai|tudo certo)\b',
            ],
            Intent.BUDGET_INQUIRY: [
                r'\b(orçamento|quanto|preço|valor|custo|pagar|gastar)\b',
                r'\b(r\$|reais?|mil|k)\b',
                r'\b(\d+\.?\d*)\s*(mil|k|reais?)\b',
            ],
            Intent.CAR_RECOMMENDATION: [
                r'\b(recomendar|recomendação|recomenda|sugerir|sugestão|sugere|indicar|indicação)\b',
                r'\b(qual carro|que carro|me ajuda|preciso de um carro)\b',
                r'\b(procurando|procuro|quero|busco|gostaria|comprar)\b.*\b(carro|veículo|automóvel|suv|sedan)\b',
                r'\b(me|você)\s+(recomenda|sugere|indica)\b',
            ],
            Intent.CAR_DETAILS: [
                r'\b(detalhes?|informações?|especificações?|ficha técnica)\b',
                r'\b(mais sobre|falar sobre|saber mais)\b',
                r'\b(consumo|motor|potência|itens de série)\b',
            ],
            Intent.COMPARE_CARS: [
                r'\b(comparar|comparação|diferença|versus|vs|ou)\b',
                r'\b(qual é melhor|qual escolher|qual comprar)\b',
            ],
            Intent.SCHEDULE_TEST_DRIVE: [
                r'\b(test[- ]?drive|testar|experimentar|dirigir)\b',
                r'\b(agendar|marcar|quando posso)\b.*\b(test|testar)\b',
            ],
            Intent.CONTACT_DEALER: [
                r'\b(falar com|contato|telefone|whatsapp|email)\b.*\b(vendedor|concessionária|loja)\b',
                r'\b(vendedor|concessionária|loja)\b',
            ],
            Intent.HUMAN_HANDOFF: [
                r'\b(atendente|humano|pessoa|alguém|operador)\b',
                r'\b(falar com alguém|preciso de ajuda|não entendi)\b',
            ],
            Intent.FEEDBACK_POSITIVE: [
                r'\b(obrigad[oa]|valeu|legal|ótimo|excelente|perfeito|adorei|amei)\b',
                r'\b(muito bom|show|top|massa|bacana)\b',
            ],
            Intent.FEEDBACK_NEGATIVE: [
                r'\b(ruim|péssimo|horrível|não gostei|não quero)\b',
                r'\b(não serve|não atende|não é isso)\b',
            ],
            Intent.LOCATION_INQUIRY: [
                r'\b(onde|localização|endereço|cidade|estado|região)\b',
                r'\b(fica onde|está onde|tem em)\b',
            ],
            Intent.FINANCING_INQUIRY: [
                r'\b(financiamento|financiar|parcelar|parcelas?|entrada)\b',
                r'\b(consórcio|crédito|empréstimo)\b',
            ],
            Intent.USAGE_INQUIRY: [
                r'\b(uso|usar|utilizar|finalidade)\b',
                r'\b(trabalho|família|lazer|viagem)\b',
            ],
            Intent.PREFERENCE_INQUIRY: [
                r'\b(preferência|prioridade|importante|essencial)\b',
                r'\b(economia|espaço|performance|conforto|segurança|tecnologia)\b',
            ],
        }
        
        # Compilar regex patterns
        self.compiled_patterns: Dict[Intent, List[re.Pattern]] = {}
        for intent, patterns in self.intent_patterns.items():
            self.compiled_patterns[intent] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def classify(self, text: str) -> Tuple[Intent, float]:
        """
        Classificar intenção da mensagem
        
        Args:
            text: Texto normalizado da mensagem
            
        Returns:
            Tupla (Intent, confidence)
        """
        # Contar matches para cada intenção
        intent_scores: Dict[Intent, int] = {}
        
        for intent, patterns in self.compiled_patterns.items():
            matches = 0
            for pattern in patterns:
                if pattern.search(text):
                    matches += 1
            
            if matches > 0:
                intent_scores[intent] = matches
        
        # Se não encontrou nenhuma intenção
        if not intent_scores:
            return Intent.UNKNOWN, 0.3
        
        # Pegar intenção com mais matches
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent, score = best_intent
        
        # Calcular confidence (normalizado)
        # Mais matches = maior confidence
        max_possible_matches = len(self.compiled_patterns[intent])
        confidence = min(0.5 + (score / max_possible_matches) * 0.5, 1.0)
        
        return intent, confidence


class EntityExtractor:
    """Extrator de entidades nomeadas (NER)"""
    
    def __init__(self):
        # Padrões para extração de entidades
        self.patterns = {
            "budget": [
                r'(?:r\$|reais?)\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',
                r'(\d+(?:\.\d{3})*)\s*(?:mil|k)',
                r'(\d+)\s*(?:mil|k)',
            ],
            "brand": [
                r'\b(toyota|honda|volkswagen|vw|ford|chevrolet|fiat|hyundai|nissan|'
                r'renault|peugeot|citroën|jeep|bmw|mercedes|audi|volvo|mitsubishi|'
                r'kia|mazda|subaru|suzuki|chery|caoa|byd)\b',
            ],
            "model": [
                r'\b(corolla|civic|onix|hb20|gol|polo|up|fox|ka|fiesta|focus|'
                r'fusion|cruze|tracker|equinox|s10|hilux|ranger|toro|strada|'
                r'renegade|compass|kicks|versa|march|sandero|logan|duster|'
                r'208|2008|3008|c3|c4|hr-v|cr-v|fit|city|tucson|creta|ix35|'
                r'sportage|cerato|soul|picanto|argo|mobi|uno|palio|siena|'
                r'cronos|pulse|fastback|nivus|t-cross|taos|tiguan|jetta|'
                r'virtus|saveiro|amarok)\b',
            ],
            "category": [
                r'\b(suv|sedan|hatch|hatchback|pickup|caminhonete|minivan|'
                r'crossover|compacto|subcompacto|esportivo|conversível)\b',
            ],
            "year": [
                r'\b(20\d{2})\b',
                r'\b(\d{4})\b',
            ],
            "location": [
                r'\b(são paulo|sp|rio de janeiro|rj|belo horizonte|mg|brasília|df|'
                r'salvador|ba|fortaleza|ce|recife|pe|curitiba|pr|porto alegre|rs|'
                r'manaus|am|belém|pa|goiânia|go|campinas|guarulhos|são bernardo|'
                r'santo andré|osasco|ribeirão preto|sorocaba|maceió|al|natal|rn|'
                r'joão pessoa|pb|aracaju|se|cuiabá|mt|campo grande|ms|vitória|es|'
                r'florianópolis|sc)\b',
            ],
            "preference": [
                r'\b(economia|econômico|econômica|espaço|espaçoso|espaçosa|'
                r'performance|potência|potente|conforto|confortável|segurança|'
                r'seguro|tecnologia|tecnológico|luxo|luxuoso|design|bonito|'
                r'moderno|robusto|resistente|durável)\b',
            ],
        }
        
        # Compilar regex patterns
        self.compiled_patterns: Dict[str, List[re.Pattern]] = {}
        for entity_type, patterns in self.patterns.items():
            self.compiled_patterns[entity_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def extract(self, text: str) -> List[Entity]:
        """
        Extrair entidades do texto
        
        Args:
            text: Texto normalizado
            
        Returns:
            Lista de entidades encontradas
        """
        entities: List[Entity] = []
        
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Processar valor baseado no tipo
                    if entity_type == "budget":
                        value = self._normalize_budget(value)
                    
                    entity = Entity(
                        type=entity_type,
                        value=value.strip(),
                        confidence=0.9,  # Alta confiança para regex matches
                        start_pos=match.start(),
                        end_pos=match.end(),
                    )
                    entities.append(entity)
        
        # Remover duplicatas (mesma entidade encontrada múltiplas vezes)
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _normalize_budget(self, value: str) -> str:
        """Normalizar valores de orçamento para formato padrão"""
        # Extrair apenas números primeiro
        num = re.search(r'(\d+)', value)
        if num:
            return f"{int(num.group(1)) * 1000}"
        
        return value
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remover entidades duplicadas"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.type, entity.value.lower())
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities


class SentimentAnalyzer:
    """Analisador de sentimento"""
    
    def __init__(self):
        # Palavras positivas
        self.positive_words = {
            'obrigado', 'obrigada', 'valeu', 'legal', 'ótimo', 'excelente', 'perfeito',
            'adorei', 'amei', 'muito bom', 'show', 'top', 'massa', 'bacana', 'maravilhoso',
            'fantástico', 'incrível', 'sensacional', 'gostei', 'adoro', 'amo', 'feliz',
            'satisfeito', 'satisfeita', 'contente', 'alegre', 'positivo', 'positiva',
        }
        
        # Palavras negativas
        self.negative_words = {
            'ruim', 'péssimo', 'horrível', 'não gostei', 'não quero', 'não serve',
            'não atende', 'não é isso', 'terrível', 'pior', 'decepcionado', 'decepcionada',
            'frustrado', 'frustrada', 'chato', 'chata', 'difícil', 'complicado',
            'problema', 'erro', 'falha', 'insatisfeito', 'insatisfeita', 'triste',
            'negativo', 'negativa', 'mal', 'desagradável',
        }
        
        # Palavras neutras/modificadoras
        self.negation_words = {'não', 'nunca', 'jamais', 'nada', 'nenhum', 'nenhuma'}
    
    def analyze(self, text: str) -> Sentiment:
        """
        Analisar sentimento do texto
        
        Args:
            text: Texto normalizado
            
        Returns:
            Sentiment (POSITIVE, NEUTRAL, NEGATIVE)
        """
        words = text.lower().split()
        
        positive_score = 0.0
        negative_score = 0.0
        
        # Contar palavras positivas e negativas
        for i, word in enumerate(words):
            # Verificar se há negação antes da palavra (até 2 palavras antes)
            is_negated = False
            if i > 0 and words[i-1] in self.negation_words:
                is_negated = True
            elif i > 1 and words[i-2] in self.negation_words:
                is_negated = True
            
            # Verificar palavras positivas
            if word in self.positive_words:
                if is_negated:
                    negative_score += 1.5  # "não gostei" é negativo (peso maior)
                else:
                    positive_score += 1.5
            
            # Verificar palavras negativas
            if word in self.negative_words:
                if is_negated:
                    positive_score += 1.0  # "não é ruim" é positivo (peso menor)
                else:
                    negative_score += 1.5
            
            # Verificar frases compostas (bigrams)
            if i < len(words) - 1:
                bigram = f"{word} {words[i+1]}"
                if bigram in self.positive_words:
                    positive_score += 2.0  # Frases compostas têm peso maior
                elif bigram in self.negative_words:
                    negative_score += 2.0
        
        # Determinar sentimento com threshold
        threshold = 0.5
        
        if positive_score > negative_score + threshold:
            return Sentiment.POSITIVE
        elif negative_score > positive_score + threshold:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL


class NLPService:
    """Serviço de processamento de linguagem natural"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        logger.info("NLP Service initialized")
    
    async def process(self, text: str) -> NLPResult:
        """
        Processar texto e extrair intenção + entidades + sentimento
        
        Args:
            text: Mensagem do usuário
            
        Returns:
            NLPResult com intenção, entidades e sentimento
        """
        start_time = datetime.now()
        
        # Normalizar texto
        normalized = self._normalize_text(text)
        
        # Classificar intenção
        intent, confidence = self.intent_classifier.classify(normalized)
        
        # Extrair entidades
        entities = self.entity_extractor.extract(normalized)
        
        # Analisar sentimento
        sentiment = self.sentiment_analyzer.analyze(normalized)
        
        # Calcular tempo de processamento
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        result = NLPResult(
            intent=intent,
            confidence=confidence,
            entities=entities,
            sentiment=sentiment,
            normalized_text=normalized,
            processing_time_ms=processing_time,
        )
        
        logger.info(
            f"NLP processed: intent={intent.value}, confidence={confidence:.2f}, "
            f"time={processing_time:.2f}ms"
        )
        
        return result
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalizar texto para processamento
        
        - Lowercase
        - Remover múltiplos espaços
        - Remover pontuação excessiva
        """
        # Lowercase
        normalized = text.lower()
        
        # Remover múltiplos espaços
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remover pontuação excessiva (manter apenas uma)
        normalized = re.sub(r'([!?.]){2,}', r'\1', normalized)
        
        # Trim
        normalized = normalized.strip()
        
        return normalized
