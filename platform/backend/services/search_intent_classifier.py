"""
🧠 Search Intent Classifier
Classificador avançado de intenção de busca usando técnicas de NLP
para melhorar a precisão da detecção de contexto

🤖 Agent Skills Framework - NLP Component
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import difflib
from collections import defaultdict, Counter


class IntentCategory(Enum):
    """Categorias de intenção refinadas"""
    UBER_TRANSPORT = "transporte_passageiros"
    DAILY_COMMUTE = "trabalho_diario" 
    FAMILY_USE = "uso_familiar"
    LEISURE_TRAVEL = "lazer_viagem"
    COMMERCIAL_WORK = "comercial_trabalho"
    FIRST_CAR = "primeiro_carro"
    SPECIFIC_MODEL = "modelo_especifico"
    PRICE_RANGE = "faixa_preco"
    VEHICLE_TYPE = "tipo_veiculo"
    FUEL_ECONOMY = "economia_combustivel"
    UNKNOWN = "indefinido"


@dataclass
class EntityMatch:
    """Match de entidade específica"""
    type: str
    value: str
    confidence: float
    position: int
    context: str


@dataclass
class IntentAnalysis:
    """Análise completa de intenção"""
    primary_intent: IntentCategory
    confidence: float
    secondary_intents: List[Tuple[IntentCategory, float]]
    entities: List[EntityMatch]
    keywords: List[str]
    user_persona: Optional[str]
    priority_factors: Dict[str, float]


class SearchIntentClassifier:
    """
    Classificador de intenção de busca com múltiplas técnicas:
    - Pattern matching avançado
    - Análise de co-ocorrência  
    - Detecção de entidades
    - Inferência de persona
    """
    
    def __init__(self):
        self.intent_patterns = {}
        self.entity_patterns = {}
        self.keyword_weights = {}
        self.intent_transitions = {}
        self.user_personas = {}
        
        self._initialize_patterns()
        self._initialize_entities()
        self._initialize_personas()
        
    def _initialize_patterns(self):
        """Inicializa padrões avançados de intenção"""
        self.intent_patterns = {
            IntentCategory.UBER_TRANSPORT: {
                'primary_patterns': [
                    r'\b(uber|99|cabify|app[s]?\s+(?:de\s+)?transporte)\b',
                    r'\b(motorista|corrida[s]?|passageiro[s]?)\b',
                    r'\b(uberx|99pop|comfort|black|select)\b',
                    r'\b(ganhar\s+dinheiro|renda\s+extra|trabalhar\s+(?:de|como)\s+motorista)\b'
                ],
                'context_patterns': [
                    r'\b(?:carro\s+)?para\s+(?:fazer\s+)?(?:uber|99|corrida[s]?)\b',
                    r'\b(?:trabalhar|ganhar)\s+(?:dinheiro\s+)?(?:com|de|no)\s+(?:uber|app)\b',
                    r'\beconomico\s+(?:para|pra)\s+(?:uber|app[s]?)\b'
                ],
                'negative_patterns': [
                    r'\b(?:nao|não)\s+(?:quero|para|pra)\s+(?:uber|app[s]?)\b'
                ],
                'weight': 1.0
            },
            
            IntentCategory.DAILY_COMMUTE: {
                'primary_patterns': [
                    r'\b(trabalho|escritorio|empresa|emprego)\b',
                    r'\b(diario|dia[s]?\s+(?:a\s+)?dia[s]?|todo[s]?\s+(?:os\s+)?dia[s]?)\b',
                    r'\b(casa\s+(?:ao\s+)?trabalho|trabalho\s+(?:a\s+)?casa)\b',
                    r'\b(economico|economia|barato\s+(?:de|para)\s+manter)\b'
                ],
                'context_patterns': [
                    r'\bcarro\s+(?:para|pra)\s+(?:ir\s+(?:ao\s+)?)?trabalho\b',
                    r'\b(?:uso|usar)\s+(?:todo[s]?\s+(?:os\s+)?)?dia[s]?\b',
                    r'\b(?:gasta|consome)\s+pouco\b'
                ],
                'weight': 0.9
            },
            
            IntentCategory.FAMILY_USE: {
                'primary_patterns': [
                    r'\b(familia|familiar|familial)\b',
                    r'\b(crianca[s]?|bebe[s]?|filho[s]?|filha[s]?)\b',
                    r'\b(isofix|cadeirinha[s]?|seguranca\s+(?:da\s+)?familia)\b',
                    r'\b(espacoso|espaco|conforto\s+(?:da\s+)?familia)\b'
                ],
                'context_patterns': [
                    r'\bcarro\s+(?:para|pra)\s+(?:a\s+)?familia\b',
                    r'\b(?:suv|sedan)\s+(?:para|pra)\s+familia\b',
                    r'\b(?:com|para)\s+crianca[s]?\b'
                ],
                'weight': 0.8
            },
            
            IntentCategory.LEISURE_TRAVEL: {
                'primary_patterns': [
                    r'\b(lazer|passeio[s]?|viagem|viagens|turismo)\b',
                    r'\b(fim\s+(?:de\s+)?semana|weekend|final\s+(?:de\s+)?semana)\b',
                    r'\b(praia|montanha|campo|trilha[s]?|aventura)\b',
                    r'\b(off[\s-]?road|4x4|tracao|alto)\b'
                ],
                'context_patterns': [
                    r'\bcarro\s+(?:para|pra)\s+(?:viagem|passeio[s]?|lazer)\b',
                    r'\b(?:suv|pickup)\s+(?:para|pra)\s+aventura\b'
                ],
                'weight': 0.7
            },
            
            IntentCategory.COMMERCIAL_WORK: {
                'primary_patterns': [
                    r'\b(comercial|entrega[s]?|carga|frete[s]?)\b',
                    r'\b(pickup\s+(?:pequena|comercial)|furgao|van)\b',
                    r'\b(negocio|empresa|comercio|loja)\b',
                    r'\b(strada|saveiro|montana|fiorino|ducato)\b'
                ],
                'context_patterns': [
                    r'\bcarro\s+(?:para|pra)\s+(?:entrega[s]?|comercio|trabalho)\b',
                    r'\b(?:carregar|transportar)\s+(?:carga|mercadoria)\b'
                ],
                'negative_patterns': [
                    r'\b(hilux|ranger|amarok|frontier|toro)\b.*\b(?:lazer|passeio)\b'
                ],
                'weight': 0.9
            },
            
            IntentCategory.FIRST_CAR: {
                'primary_patterns': [
                    r'\b(primeiro|1[oº])\s+carro\b',
                    r'\b(iniciante|novato|aprendendo\s+(?:a\s+)?dirigir)\b',
                    r'\b(cnh\s+nova|carteira\s+nova|acabei\s+(?:de\s+)?tirar)\b',
                    r'\b(facil\s+(?:de\s+)?dirigir|simples|basico)\b'
                ],
                'context_patterns': [
                    r'\bmeu\s+primeiro\s+carro\b',
                    r'\b(?:carro\s+)?(?:para|pra)\s+iniciante\b'
                ],
                'weight': 0.8
            }
        }
        
    def _initialize_entities(self):
        """Inicializa padrões de entidades"""
        self.entity_patterns = {
            'brands': {
                'pattern': r'\b(toyota|honda|ford|chevrolet|volkswagen|fiat|nissan|hyundai|jeep|renault|peugeot|citroen|kia|mitsubishi|suzuki|bmw|mercedes|audi|byd|volvo)\b',
                'extract_func': self._extract_brands
            },
            'models': {
                'pattern': r'\b(corolla|civic|focus|onix|polo|argo|kicks|creta|compass|duster|208|hb20|march|fit)\b',
                'extract_func': self._extract_models
            },
            'years': {
                'pattern': r'\b(20[0-2][0-9]|[0-9]{4})\b',
                'extract_func': self._extract_years
            },
            'prices': {
                'pattern': r'(?:r\$|reais?)\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)|(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:r\$|reais?)',
                'extract_func': self._extract_prices
            },
            'categories': {
                'pattern': r'\b(suv|sedan|hatch|pickup|van|furgao|conversivel|coupe|crossover)\b',
                'extract_func': self._extract_categories
            },
            'fuel_types': {
                'pattern': r'\b(flex|gasolina|etanol|diesel|hibrido|eletrico|gnv)\b',
                'extract_func': self._extract_fuel_types
            }
        }
        
    def _initialize_personas(self):
        """Inicializa personas de usuário"""
        self.user_personas = {
            'young_professional': {
                'keywords': ['primeiro', 'trabalho', 'economico', 'novo', 'jovem'],
                'priorities': {'economia': 0.8, 'tecnologia': 0.6, 'seguranca': 0.7},
                'preferred_categories': ['Hatch', 'Sedan Compacto']
            },
            'family_oriented': {
                'keywords': ['familia', 'criancas', 'seguranca', 'espaco', 'conforto'],
                'priorities': {'seguranca': 0.9, 'espaco': 0.8, 'conforto': 0.7},
                'preferred_categories': ['SUV', 'Minivan', 'Sedan']
            },
            'business_owner': {
                'keywords': ['comercial', 'entrega', 'negocio', 'empresa', 'trabalho'],
                'priorities': {'durabilidade': 0.9, 'custo_manutencao': 0.8, 'capacidade_carga': 0.9},
                'preferred_categories': ['Pickup Pequena', 'Furgao', 'Van']
            },
            'weekend_warrior': {
                'keywords': ['aventura', 'lazer', 'viagem', 'trilha', 'off-road'],
                'priorities': {'performance': 0.8, 'tecnologia': 0.7, 'aventura': 0.9},
                'preferred_categories': ['SUV', 'Pickup', 'Crossover']
            },
            'urban_driver': {
                'keywords': ['cidade', 'urbano', 'estacionar', 'transito', 'manobrar'],
                'priorities': {'facilidade_dirigir': 0.8, 'economia': 0.7, 'tamanho_compacto': 0.8},
                'preferred_categories': ['Hatch', 'Sedan Compacto']
            }
        }
        
    def classify_intent(self, query: str, user_context: Dict = None) -> IntentAnalysis:
        """
        Classifica a intenção da busca do usuário
        
        Args:
            query: String de busca
            user_context: Contexto adicional do usuário
            
        Returns:
            IntentAnalysis com intenção classificada
        """
        query_lower = query.lower()
        
        # 1. Calcular scores para cada intenção
        intent_scores = self._calculate_intent_scores(query_lower)
        
        # 2. Extrair entidades
        entities = self._extract_all_entities(query)
        
        # 3. Detectar palavras-chave importantes
        keywords = self._extract_keywords(query_lower)
        
        # 4. Inferir persona do usuário
        user_persona = self._infer_user_persona(query_lower, keywords, entities)
        
        # 5. Ajustar scores baseado no contexto
        if user_context:
            intent_scores = self._adjust_scores_by_context(intent_scores, user_context)
            
        # 6. Determinar intenção principal
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        primary_category, primary_confidence = primary_intent
        
        # 7. Obter intenções secundárias
        secondary_intents = [
            (cat, score) for cat, score in intent_scores.items() 
            if cat != primary_category and score > 0.2
        ]
        secondary_intents.sort(key=lambda x: x[1], reverse=True)
        
        # 8. Calcular fatores de prioridade
        priority_factors = self._calculate_priority_factors(
            primary_category, user_persona, keywords, entities
        )
        
        return IntentAnalysis(
            primary_intent=primary_category,
            confidence=primary_confidence,
            secondary_intents=secondary_intents,
            entities=entities,
            keywords=keywords,
            user_persona=user_persona,
            priority_factors=priority_factors
        )
        
    def _calculate_intent_scores(self, query: str) -> Dict[IntentCategory, float]:
        """Calcula scores para cada categoria de intenção"""
        scores = defaultdict(float)
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            
            # Padrões primários
            for pattern in patterns.get('primary_patterns', []):
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches * 1.0
                
            # Padrões de contexto (peso menor)
            for pattern in patterns.get('context_patterns', []):
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score += matches * 0.5
                
            # Padrões negativos (reduzem score)
            for pattern in patterns.get('negative_patterns', []):
                matches = len(re.findall(pattern, query, re.IGNORECASE))
                score -= matches * 0.8
                
            # Aplicar peso da intenção
            weight = patterns.get('weight', 1.0)
            scores[intent] = max(0.0, score * weight)
            
        # Normalizar scores
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            for intent in scores:
                scores[intent] /= max_score
                
        return dict(scores)
        
    def _extract_all_entities(self, query: str) -> List[EntityMatch]:
        """Extrai todas as entidades da query"""
        entities = []
        
        for entity_type, config in self.entity_patterns.items():
            pattern = config['pattern']
            extract_func = config['extract_func']
            
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entity_value = extract_func(match.group())
                if entity_value:
                    entities.append(EntityMatch(
                        type=entity_type,
                        value=entity_value,
                        confidence=1.0,  # Por simplicidade
                        position=match.start(),
                        context=query[max(0, match.start()-10):match.end()+10]
                    ))
                    
        return entities
        
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave importantes"""
        # Palavras importantes para classificação
        important_words = [
            'economico', 'barato', 'caro', 'luxo', 'premium', 'basico',
            'novo', 'usado', 'seminovo', 'zero', 'primeiro',
            'rapido', 'lento', 'potente', 'forte', 'fraco',
            'grande', 'pequeno', 'medio', 'compacto', 'espacoso',
            'confortavel', 'simples', 'automatico', 'manual',
            'moderno', 'antigo', 'tecnologia', 'conectado'
        ]
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word in important_words]
        
        return keywords
        
    def _infer_user_persona(self, query: str, keywords: List[str], entities: List[EntityMatch]) -> Optional[str]:
        """Infere a persona do usuário baseado na query"""
        persona_scores = {}
        
        for persona_name, persona_data in self.user_personas.items():
            score = 0.0
            
            # Score baseado em keywords da persona
            persona_keywords = persona_data['keywords']
            for keyword in keywords:
                if keyword in persona_keywords:
                    score += 1.0
                    
            # Score baseado em palavras da query
            for persona_keyword in persona_keywords:
                if persona_keyword in query:
                    score += 0.5
                    
            persona_scores[persona_name] = score
            
        # Retornar persona com maior score se significativo
        if persona_scores:
            best_persona = max(persona_scores.items(), key=lambda x: x[1])
            if best_persona[1] > 0.5:
                return best_persona[0]
                
        return None
        
    def _calculate_priority_factors(
        self, 
        primary_intent: IntentCategory, 
        user_persona: Optional[str],
        keywords: List[str],
        entities: List[EntityMatch]
    ) -> Dict[str, float]:
        """Calcula fatores de prioridade para recomendação"""
        factors = {
            'economia': 0.5,
            'seguranca': 0.5, 
            'conforto': 0.5,
            'performance': 0.5,
            'espaco': 0.5,
            'tecnologia': 0.5,
            'durabilidade': 0.5
        }
        
        # Ajustar baseado na intenção principal
        intent_priorities = {
            IntentCategory.UBER_TRANSPORT: {
                'economia': 0.9, 'durabilidade': 0.8, 'conforto': 0.6
            },
            IntentCategory.DAILY_COMMUTE: {
                'economia': 0.8, 'conforto': 0.7, 'seguranca': 0.6
            },
            IntentCategory.FAMILY_USE: {
                'seguranca': 0.9, 'espaco': 0.8, 'conforto': 0.7
            },
            IntentCategory.LEISURE_TRAVEL: {
                'performance': 0.8, 'conforto': 0.7, 'tecnologia': 0.6
            },
            IntentCategory.COMMERCIAL_WORK: {
                'durabilidade': 0.9, 'economia': 0.8, 'espaco': 0.7
            },
            IntentCategory.FIRST_CAR: {
                'seguranca': 0.8, 'economia': 0.7, 'facilidade_dirigir': 0.8
            }
        }
        
        if primary_intent in intent_priorities:
            intent_factors = intent_priorities[primary_intent]
            for factor, value in intent_factors.items():
                if factor in factors:
                    factors[factor] = value
                    
        # Ajustar baseado na persona
        if user_persona and user_persona in self.user_personas:
            persona_priorities = self.user_personas[user_persona]['priorities']
            for factor, value in persona_priorities.items():
                if factor in factors:
                    factors[factor] = max(factors[factor], value)
                    
        # Ajustar baseado em keywords específicas
        keyword_adjustments = {
            'economico': {'economia': 0.9},
            'seguro': {'seguranca': 0.9},
            'confortavel': {'conforto': 0.8},
            'potente': {'performance': 0.8},
            'espacoso': {'espaco': 0.8},
            'moderno': {'tecnologia': 0.7}
        }
        
        for keyword in keywords:
            if keyword in keyword_adjustments:
                adjustments = keyword_adjustments[keyword]
                for factor, value in adjustments.items():
                    if factor in factors:
                        factors[factor] = max(factors[factor], value)
                        
        return factors
        
    def _adjust_scores_by_context(self, scores: Dict[IntentCategory, float], context: Dict) -> Dict[IntentCategory, float]:
        """Ajusta scores baseado no contexto do usuário"""
        adjusted_scores = scores.copy()
        
        # Exemplo de ajustes baseados no contexto
        if context.get('age') and context['age'] < 25:
            # Usuários jovens -> mais provável primeiro carro
            adjusted_scores[IntentCategory.FIRST_CAR] *= 1.2
            
        if context.get('has_children'):
            # Usuários com filhos -> mais provável uso familiar
            adjusted_scores[IntentCategory.FAMILY_USE] *= 1.3
            
        if context.get('business_owner'):
            # Donos de negócio -> mais provável uso comercial
            adjusted_scores[IntentCategory.COMMERCIAL_WORK] *= 1.4
            
        return adjusted_scores
        
    # Funções de extração de entidades
    def _extract_brands(self, match: str) -> str:
        return match.lower()
        
    def _extract_models(self, match: str) -> str:
        return match.lower()
        
    def _extract_years(self, match: str) -> str:
        year = int(match)
        if 1990 <= year <= 2030:  # Anos válidos
            return str(year)
        return None
        
    def _extract_prices(self, match: str) -> str:
        # Extrair número do preço
        numbers = re.findall(r'\d+(?:[.,]\d+)*', match)
        if numbers:
            return numbers[0]
        return None
        
    def _extract_categories(self, match: str) -> str:
        return match.lower()
        
    def _extract_fuel_types(self, match: str) -> str:
        return match.lower()


# Factory function
def create_intent_classifier() -> SearchIntentClassifier:
    """Cria uma instância do classificador"""
    return SearchIntentClassifier()


# Exemplo de uso e testes
if __name__ == "__main__":
    classifier = create_intent_classifier()
    
    test_queries = [
        "preciso de um carro para fazer uber",
        "Toyota Corolla para trabalho diário",
        "SUV para família com crianças pequenas", 
        "pickup para entregas na minha empresa",
        "meu primeiro carro, algo econômico",
        "carro para viajar no fim de semana",
        "Honda Civic 2020 até 80 mil reais"
    ]
    
    print("🧠 Search Intent Classifier - Análise de Queries")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        analysis = classifier.classify_intent(query)
        
        print(f"   📋 Intent: {analysis.primary_intent.value}")
        print(f"   🎯 Confidence: {analysis.confidence:.2f}")
        
        if analysis.entities:
            print(f"   🏷️  Entities: {[(e.type, e.value) for e in analysis.entities[:3]]}")
            
        if analysis.keywords:
            print(f"   🔑 Keywords: {analysis.keywords[:3]}")
            
        if analysis.user_persona:
            print(f"   👤 Persona: {analysis.user_persona}")
            
        top_priorities = sorted(analysis.priority_factors.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   ⭐ Top Priorities: {[(p[0], f'{p[1]:.1f}') for p in top_priorities]}")
        
        print("-" * 40)