"""
🎯 Context-Based Recommendation Skill
Skill avançada que utiliza a base de conhecimento dos perfis de uso 
para recomendar carros baseado em contexto/intenção de busca

🤖 Agent Skills Framework Implementation
"""

import json
import os
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import difflib

from models.car import Car
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.app_transport_validator import AppTransportValidator


class SearchIntent(Enum):
    """Tipos de intenção de busca detectados"""
    UBER_99 = "transporte_passageiros"
    TRABALHO = "trabalho" 
    FAMILIA = "familia"
    LAZER = "lazer"
    COMERCIAL = "comercial"
    PRIMEIRO_CARRO = "primeiro_carro"
    MARCA_MODELO = "marca_modelo_especifico"
    PRECO = "faixa_preco"
    CATEGORIA = "categoria_veiculo"
    UNKNOWN = "desconhecido"


@dataclass
class SearchContext:
    """Contexto da busca do usuário"""
    raw_query: str
    detected_intent: SearchIntent
    confidence: float
    extracted_entities: Dict[str, Any]
    profile_match: Optional[str] = None
    priority_adjustments: Dict[str, int] = None


@dataclass
class ContextualRecommendation:
    """Recomendação contextualizada"""
    car: Car
    base_score: float
    context_boost: float
    final_score: float
    reasoning: List[str]
    profile_alignment: Dict[str, float]


class ContextBasedRecommendationSkill:
    """
    Skill que combina NLP básico com base de conhecimento
    para recomendar carros baseado no contexto de uso
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.recommendation_engine = UnifiedRecommendationEngine(data_dir)
        self.app_transport_validator = AppTransportValidator(data_dir)
        self.usage_profiles = {}
        self.search_patterns = {}
        
        self._load_knowledge_base()
        self._initialize_search_patterns()
        
    def _load_knowledge_base(self):
        """Carrega base de conhecimento dos perfis de uso"""
        usage_profiles_file = os.path.join(self.data_dir, "usage_profiles.json")
        
        if os.path.exists(usage_profiles_file):
            with open(usage_profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.usage_profiles = data.get('perfis', {})
        else:
            print(f"[ERRO] Arquivo {usage_profiles_file} não encontrado")
            
    def _initialize_search_patterns(self):
        """Inicializa padrões de busca para detecção de intenção"""
        self.search_patterns = {
            SearchIntent.UBER_99: [
                r'\buber\b', r'\b99\b', r'\btransporte\b.*\bpassageiros\b', 
                r'\bmotorista\b', r'\bapp\b.*\btransporte\b', r'\bcorrida\b',
                r'\buberx\b', r'\b99pop\b', r'\bcomfort\b', r'\bblack\b'
            ],
            SearchIntent.TRABALHO: [
                r'\btrabalho\b', r'\bescritorio\b', r'\bempresa\b', 
                r'\beconomico\b', r'\beconomia\b', r'\bbarato\b.*\bmanter\b',
                r'\bdiario\b', r'\bdia.*dia\b', r'\bcasa.*trabalho\b'
            ],
            SearchIntent.FAMILIA: [
                r'\bfamilia\b', r'\bcriancas\b', r'\bbebe\b', r'\bisofix\b',
                r'\bseguro\b.*\bfamilia\b', r'\bespacoso\b', r'\bsuv\b.*\bfamilia\b',
                r'\bfilhos\b', r'\besposa\b', r'\bfamiliar\b'
            ],
            SearchIntent.LAZER: [
                r'\blazer\b', r'\bviagem\b', r'\bpasseio\b', r'\bfim.*semana\b',
                r'\bpraia\b', r'\bmontanha\b', r'\bturismo\b', r'\baventura\b',
                r'\boff.*road\b', r'\b4x4\b'
            ],
            SearchIntent.COMERCIAL: [
                r'\bcomercial\b', r'\bentrega\b', r'\bcarga\b', r'\bfurgao\b',
                r'\bpickup\b.*\bpequena\b', r'\bstrada\b', r'\bsaveiro\b',
                r'\bmontana\b', r'\btrabalhar\b.*\bentrega\b', r'\bnegocio\b'
            ],
            SearchIntent.PRIMEIRO_CARRO: [
                r'\bprimeiro\b.*\bcarro\b', r'\biniciante\b', r'\bnovato\b',
                r'\baprendendo\b.*\bdirigir\b', r'\bcnh\b.*\bnova\b', 
                r'\bfacil\b.*\bdirigir\b', r'\bsimples\b'
            ]
        }
        
    def analyze_search_context(self, query: str, user_data: Dict[str, Any] = None) -> SearchContext:
        """
        Analisa o contexto da busca do usuário
        
        Args:
            query: String de busca do usuário
            user_data: Dados opcionais do usuário (orçamento, localização, etc.)
            
        Returns:
            SearchContext com intenção detectada e entidades extraídas
        """
        query_lower = query.lower()
        
        # Detectar intenção principal
        intent_scores = {}
        
        for intent, patterns in self.search_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            intent_scores[intent] = score
            
        # Intenção com maior score
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / len(self.search_patterns[best_intent]), 1.0)
        
        # Se score muito baixo, marcar como unknown
        if confidence < 0.1:
            best_intent = SearchIntent.UNKNOWN
            confidence = 0.0
            
        # Extrair entidades específicas
        entities = self._extract_entities(query_lower, best_intent)
        
        # Mapear para perfil de uso
        profile_match = None
        if best_intent != SearchIntent.UNKNOWN:
            profile_match = best_intent.value
            
        return SearchContext(
            raw_query=query,
            detected_intent=best_intent,
            confidence=confidence,
            extracted_entities=entities,
            profile_match=profile_match
        )
        
    def _extract_entities(self, query: str, intent: SearchIntent) -> Dict[str, Any]:
        """Extrai entidades específicas baseado na intenção"""
        entities = {}
        
        # Extrair marcas
        marcas_conhecidas = [
            'toyota', 'honda', 'ford', 'chevrolet', 'volkswagen', 'fiat',
            'nissan', 'hyundai', 'jeep', 'renault', 'peugeot', 'citroën',
            'kia', 'mitsubishi', 'suzuki', 'bmw', 'mercedes', 'audi',
            'byd', 'volvo', 'land rover', 'porsche'
        ]
        
        marcas_encontradas = []
        for marca in marcas_conhecidas:
            if marca in query:
                marcas_encontradas.append(marca)
        
        if marcas_encontradas:
            entities['marcas'] = marcas_encontradas
            
        # Extrair anos
        anos_match = re.findall(r'\b(20[0-2][0-9])\b', query)
        if anos_match:
            entities['anos'] = [int(ano) for ano in anos_match]
            
        # Extrair valores monetários
        valores_match = re.findall(r'r?\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', query)
        if valores_match:
            # Converter para float
            valores = []
            for valor in valores_match:
                valor_clean = valor.replace('.', '').replace(',', '.')
                try:
                    valores.append(float(valor_clean))
                except ValueError:
                    pass
            if valores:
                entities['valores'] = valores
                
        # Extrações específicas por intenção
        if intent == SearchIntent.UBER_99:
            if 'uberx' in query or '99pop' in query:
                entities['categoria_app'] = 'basica'
            elif 'comfort' in query:
                entities['categoria_app'] = 'comfort'
            elif 'black' in query:
                entities['categoria_app'] = 'premium'
                
        elif intent == SearchIntent.COMERCIAL:
            if any(word in query for word in ['pickup', 'caçamba']):
                entities['tipo_comercial'] = 'pickup_pequena'
            elif any(word in query for word in ['furgao', 'van', 'fechado']):
                entities['tipo_comercial'] = 'furgao'
                
        return entities
        
    def recommend_by_context(
        self, 
        query: str, 
        user_data: Dict[str, Any] = None,
        max_results: int = 10
    ) -> List[ContextualRecommendation]:
        """
        Recomenda carros baseado no contexto de busca
        
        Args:
            query: Consulta do usuário
            user_data: Dados do usuário (orçamento, localização, etc.)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de recomendações contextualizadas
        """
        # 1. Analisar contexto
        context = self.analyze_search_context(query, user_data)
        
        # 2. Obter perfil de uso correspondente
        usage_profile = None
        if context.profile_match and context.profile_match in self.usage_profiles:
            usage_profile = self.usage_profiles[context.profile_match]
            
        # 3. Obter carros candidatos
        all_cars = self.recommendation_engine.all_cars
        
        # 4. Aplicar filtros básicos baseados nas entidades extraídas
        filtered_cars = self._apply_entity_filters(all_cars, context)
        
        # 5. Calcular scores contextuais
        contextual_recommendations = []
        
        for car in filtered_cars:
            # Score base do sistema existente
            base_score = self._calculate_base_score(car, context, user_data)
            
            # Boost contextual baseado no perfil de uso
            context_boost = 0.0
            reasoning = []
            profile_alignment = {}
            
            if usage_profile:
                context_boost, reasoning, profile_alignment = self._calculate_context_boost(
                    car, usage_profile, context
                )
                
            final_score = base_score * (1.0 + context_boost)
            
            contextual_recommendations.append(ContextualRecommendation(
                car=car,
                base_score=base_score,
                context_boost=context_boost,
                final_score=final_score,
                reasoning=reasoning,
                profile_alignment=profile_alignment
            ))
            
        # 6. Ordenar por score final
        contextual_recommendations.sort(key=lambda x: x.final_score, reverse=True)
        
        return contextual_recommendations[:max_results]
        
    def _apply_entity_filters(self, cars: List[Car], context: SearchContext) -> List[Car]:
        """Aplica filtros baseados nas entidades extraídas"""
        filtered_cars = cars.copy()
        entities = context.extracted_entities
        
        # Filtro por marcas
        if 'marcas' in entities:
            marcas_lower = [m.lower() for m in entities['marcas']]
            filtered_cars = [
                car for car in filtered_cars 
                if car.marca.lower() in marcas_lower
            ]
            
        # Filtro por anos
        if 'anos' in entities:
            anos = entities['anos']
            filtered_cars = [
                car for car in filtered_cars 
                if car.ano in anos
            ]
            
        # Filtro por valores
        if 'valores' in entities and len(entities['valores']) >= 1:
            max_valor = max(entities['valores'])
            filtered_cars = [
                car for car in filtered_cars 
                if car.preco <= max_valor
            ]
            
        return filtered_cars
        
    def _calculate_base_score(self, car: Car, context: SearchContext, user_data: Dict[str, Any]) -> float:
        """Calcula score base do carro"""
        # Por enquanto, usar score simples baseado em critérios básicos
        score = 0.5  # Score base neutro
        
        # Ajuste por ano (carros mais novos = melhor)
        if car.ano >= 2020:
            score += 0.2
        elif car.ano >= 2018:
            score += 0.1
            
        # Ajuste por quilometragem (se disponível)
        if hasattr(car, 'quilometragem') and car.quilometragem:
            if car.quilometragem < 30000:
                score += 0.1
            elif car.quilometragem > 100000:
                score -= 0.1
                
        # Ajuste por categoria popular
        categorias_populares = ['Sedan', 'Hatch', 'SUV', 'SUV Compacto']
        if car.categoria in categorias_populares:
            score += 0.05
            
        return min(max(score, 0.0), 1.0)
        
    def _calculate_context_boost(
        self, 
        car: Car, 
        usage_profile: Dict[str, Any], 
        context: SearchContext
    ) -> Tuple[float, List[str], Dict[str, float]]:
        """
        Calcula boost contextual baseado no perfil de uso
        
        Returns:
            Tuple com (boost_score, reasoning_list, profile_alignment)
        """
        boost = 0.0
        reasoning = []
        alignment = {}
        
        # 1. Verificar categorias ideais
        categorias_ideais = usage_profile.get('categorias_ideais', [])
        if car.categoria in categorias_ideais:
            category_boost = 0.3
            boost += category_boost
            reasoning.append(f"Categoria {car.categoria} é ideal para {usage_profile['nome']}")
            alignment['categoria'] = 1.0
        else:
            alignment['categoria'] = 0.0
            
        # 2. Verificar requisitos essenciais
        requisitos = usage_profile.get('requisitos_essenciais', {})
        requisitos_atendidos = 0
        total_requisitos = len(requisitos)
        
        for req_name, req_value in requisitos.items():
            atendido = self._check_requirement(car, req_name, req_value)
            if atendido:
                requisitos_atendidos += 1
                reasoning.append(f"Atende requisito: {req_name}")
                
        if total_requisitos > 0:
            req_ratio = requisitos_atendidos / total_requisitos
            req_boost = req_ratio * 0.2  # Até 20% de boost
            boost += req_boost
            alignment['requisitos'] = req_ratio
            
        # 3. Verificar se está nos top modelos
        top_modelos = usage_profile.get('top_modelos', [])
        modelo_completo = f"{car.marca} {car.modelo}"
        
        for top_modelo in top_modelos:
            if isinstance(top_modelo, dict):
                nome_top = top_modelo.get('nome', '')
            else:
                nome_top = str(top_modelo)
                
            # Usar similaridade de strings
            similarity = difflib.SequenceMatcher(
                None, 
                modelo_completo.lower(), 
                nome_top.lower()
            ).ratio()
            
            if similarity > 0.8:  # 80% de similaridade
                top_boost = 0.4 * similarity  # Até 40% de boost
                boost += top_boost
                reasoning.append(f"Modelo recomendado para {usage_profile['nome']}")
                alignment['top_modelo'] = similarity
                break
        else:
            alignment['top_modelo'] = 0.0
            
        # 4. Validações específicas por perfil
        profile_name = usage_profile.get('nome', '').lower()
        
        if 'comercial' in profile_name:
            # Aplicar validações comerciais específicas
            commercial_valid = self._validate_commercial_vehicle(car, usage_profile)
            if not commercial_valid:
                boost -= 0.5  # Penalizar veículos não adequados para uso comercial
                reasoning.append("⚠️ Não adequado para uso comercial")
                alignment['commercial_suitability'] = 0.0
            else:
                alignment['commercial_suitability'] = 1.0
                
        elif 'passageiros' in profile_name or 'uber' in profile_name:
            # Validações REAIS para transporte de passageiros
            is_valid, accepted_category, all_categories = self._validate_app_transport(car, context)
            
            if is_valid:
                # Boost baseado na categoria aceita
                if accepted_category == 'uber_black':
                    boost += 0.4  # Premium = maior boost
                elif accepted_category == 'uber_comfort':
                    boost += 0.3  # Comfort = boost médio
                elif accepted_category == 'uberx_99pop':
                    boost += 0.2  # Básico = boost menor
                    
                reasoning.append(f"✅ Aceito para {accepted_category}")
                if len(all_categories) > 1:
                    reasoning.append(f"📱 Múltiplas categorias: {', '.join(all_categories)}")
                    
                alignment['app_transport'] = 1.0
                alignment['app_categories'] = len(all_categories) / 3.0  # Normalizar por 3 categorias máximas
            else:
                # Penalizar veículos não aceitos
                boost -= 0.3
                reasoning.append("❌ Não aceito para apps de transporte")
                alignment['app_transport'] = 0.0
                
        return boost, reasoning, alignment
        
    def _check_requirement(self, car: Car, req_name: str, req_value: Any) -> bool:
        """Verifica se o carro atende um requisito específico"""
        
        # Mapeamento de requisitos para atributos do carro
        requirement_mapping = {
            'airbags_minimo': ('airbags', '>='),
            'isofix': ('isofix', '=='),
            'controle_estabilidade': ('controle_estabilidade', '=='),
            'abs_ebd': ('abs', '=='),
            'porta_malas_minimo_litros': ('porta_malas_litros', '>='),
            'lugares_minimo': ('lugares', '>='),
            'portas_minimo': ('portas', '>='),
            'consumo_minimo_cidade_kml': ('consumo_cidade', '>='),
            'ar_condicionado': ('ar_condicionado', '=='),
            'direcao_eletrica': ('direcao_eletrica', '=='),
            'capacidade_carga_kg': ('capacidade_carga', '>='),
            'tecnologia_multimidia': ('central_multimidia', '=='),
            'motor_potente': ('potencia', '>=')
        }
        
        if req_name in requirement_mapping:
            attr_name, operator = requirement_mapping[req_name]
            
            # Verificar se o carro tem o atributo
            car_value = getattr(car, attr_name, None)
            
            if car_value is None:
                return False
                
            # Aplicar operador
            if operator == '>=':
                return car_value >= req_value
            elif operator == '==':
                return car_value == req_value
            elif operator == '<=':
                return car_value <= req_value
                
        return False
        
    def _validate_commercial_vehicle(self, car: Car, usage_profile: Dict[str, Any]) -> bool:
        """Valida se veículo é adequado para uso comercial"""
        
        # Obter listas de veículos válidos e inválidos
        valid_vehicles = usage_profile.get('veiculos_comerciais_validos', {})
        invalid_vehicles = usage_profile.get('veiculos_nao_comerciais', {})
        
        modelo_completo = f"{car.marca} {car.modelo}".lower()
        
        # Verificar listas de pickups de lazer (não comerciais)
        pickups_lazer = invalid_vehicles.get('pickups_lazer', [])
        for pickup in pickups_lazer:
            if pickup.lower() in modelo_completo:
                return False
                
        # Verificar listas de VUCs (não comerciais para este contexto)
        vucs = invalid_vehicles.get('vucs_caminhoes', [])
        for vuc in vucs:
            if vuc.lower() in modelo_completo:
                return False
                
        # Verificar categorias rejeitadas
        categorias_rejeitadas = usage_profile.get('categorias_rejeitadas', [])
        if car.categoria in categorias_rejeitadas:
            return False
            
        # Se passou nas validações negativas, verificar se está nas categorias ideais
        categorias_ideais = usage_profile.get('categorias_ideais', [])
        return car.categoria in categorias_ideais
        
    def _validate_app_transport(self, car: Car, context: SearchContext) -> Tuple[bool, str, List[str]]:
        """
        Valida se veículo é adequado para transporte por app usando dados REAIS
        
        Returns:
            Tuple com (é_válido, categoria_detectada, categorias_aceitas)
        """
        
        # Verificar categoria do app se especificada na query
        categoria_solicitada = context.extracted_entities.get('categoria_app', 'basica')
        
        # Mapear categoria da query para código interno
        categoria_mapping = {
            'basica': 'uberx_99pop',
            'comfort': 'uber_comfort', 
            'premium': 'uber_black'
        }
        
        categoria_codigo = categoria_mapping.get(categoria_solicitada, 'uberx_99pop')
        
        # Usar o validador REAL dos apps
        is_valid, accepted_category = self.app_transport_validator.is_valid_for_app_transport(
            marca=car.marca,
            modelo=car.modelo,
            ano=car.ano,
            categoria_desejada=categoria_codigo
        )
        
        # Obter todas as categorias aceitas para este veículo
        all_categories = self.app_transport_validator.get_accepted_categories(
            marca=car.marca,
            modelo=car.modelo,
            ano=car.ano
        )
        
        return is_valid, accepted_category or "nenhuma", all_categories
        

def create_context_skill(data_dir: str = "data") -> ContextBasedRecommendationSkill:
    """Factory function para criar a skill"""
    return ContextBasedRecommendationSkill(data_dir)


# Exemplo de uso
if __name__ == "__main__":
    # Criar skill
    skill = create_context_skill()
    
    # Exemplos de busca
    test_queries = [
        "carros para fazer uber",
        "preciso de um carro para trabalho",
        "SUV para família com crianças",
        "pickup para entregas",
        "primeiro carro barato",
        "Toyota Corolla para uber comfort"
    ]
    
    print("🎯 Context-Based Recommendation Skill - Testes")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Analisar contexto
        context = skill.analyze_search_context(query)
        print(f"   Intent: {context.detected_intent.value} (confidence: {context.confidence:.2f})")
        print(f"   Entities: {context.extracted_entities}")
        
        # Obter recomendações
        recommendations = skill.recommend_by_context(query, max_results=3)
        print(f"   Top {len(recommendations)} recomendações:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec.car.marca} {rec.car.modelo} - Score: {rec.final_score:.2f}")
            print(f"      Base: {rec.base_score:.2f}, Boost: {rec.context_boost:.2f}")
            if rec.reasoning:
                print(f"      Motivos: {', '.join(rec.reasoning[:2])}")
                
        print("-" * 40)