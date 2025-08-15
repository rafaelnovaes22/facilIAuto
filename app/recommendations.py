"""
🧠 CarFinder Recommendation Engine - Versão Prática

Sistema de recomendação focado nos critérios reais:
- Faixa de preço (filtro principal)
- Motivo de compra (prioridade #1)
- Frequência de uso
- Necessidades de espaço/família
- Economia de combustível
- Experiência do usuário
- Prioridades específicas (confiabilidade, revenda, economia)
- Preferências de marca ("eu quero")

Algoritmo transparente e baseado no que realmente importa para o cliente.
"""

import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class CarRecommender:
    """
    Engine de recomendação baseado em critérios práticos e reais
    """
    
    def __init__(self):
        self.reliability_scores = self._load_reliability_data()
        self.resale_scores = self._load_resale_data()
        self.maintenance_costs = self._load_maintenance_data()
        
    def _load_reliability_data(self) -> Dict[str, float]:
        """
        Dados de confiabilidade baseados em pesquisas reais
        Score: 0-100 (100 = mais confiável)
        """
        return {
            # Japonesas - Conhecidas pela durabilidade
            "toyota": 95,
            "honda": 92,
            "nissan": 85,
            "mitsubishi": 82,
            
            # Alemãs - Tecnologia, mas manutenção mais cara
            "volkswagen": 78,
            "audi": 75,
            "bmw": 72,
            "mercedes": 70,
            
            # Americanas - Populares no Brasil
            "chevrolet": 80,
            "ford": 77,
            
            # Coreanas - Boa relação custo-benefício
            "hyundai": 88,
            "kia": 85,
            
            # Francesas - Design, confiabilidade média
            "renault": 72,
            "peugeot": 70,
            "citroen": 68,
            
            # Italianas - Estilo, mas problemas conhecidos
            "fiat": 65,
            "jeep": 68,
            
            # Default para marcas não listadas
            "default": 70
        }
    
    def _load_resale_data(self) -> Dict[str, float]:
        """
        Dados de valorização/desvalorização baseados no mercado brasileiro
        Score: 0-100 (100 = melhor revenda)
        """
        return {
            "toyota": 90,      # Corolla, Hilux - excelente revenda
            "honda": 88,       # Civic, CR-V - muito procurados
            "volkswagen": 82,  # Polo, Jetta - marca tradicional
            "chevrolet": 78,   # Onix popular, mas desvaloriza
            "ford": 75,        # Ka, Focus - mercado médio
            "hyundai": 80,     # Crescimento no Brasil
            "nissan": 77,      # Modelos específicos valorizam
            "renault": 70,     # Sandero popular, mas desvaloriza
            "fiat": 68,        # Grande volume, desvalorização alta
            "peugeot": 65,     # Mercado limitado
            "jeep": 75,        # SUVs valorizam melhor
            "mitsubishi": 72,  # Outlander específico
            "default": 70
        }
    
    def _load_maintenance_data(self) -> Dict[str, float]:
        """
        Custo de manutenção relativo
        Score: 0-100 (100 = mais barato de manter)
        """
        return {
            "toyota": 85,      # Peças abundantes, mecânicos conhecem
            "honda": 82,       # Similar ao Toyota
            "chevrolet": 90,   # Rede ampla, peças baratas
            "ford": 85,        # Boa rede no Brasil
            "volkswagen": 70,  # Peças mais caras, complexidade
            "fiat": 88,        # Muito popular, peças baratas
            "renault": 80,     # Rede razoável
            "hyundai": 78,     # Crescendo no Brasil
            "nissan": 75,      # Rede menor
            "peugeot": 65,     # Peças caras, rede limitada
            "bmw": 40,         # Muito caro de manter
            "audi": 45,        # Similar BMW
            "jeep": 70,        # Depende do modelo
            "default": 75
        }

    def recommend(self, answers: Dict[str, Any], cars_data: List[Dict]) -> List[Dict]:
        """
        Recomendação principal baseada nos novos critérios práticos
        """
        if not cars_data:
            return []
        
        logger.info(f"Processando recomendações para {len(cars_data)} carros")
        logger.info(f"Respostas: {answers}")
        
        # 1. Filtrar por orçamento (critério eliminatório)
        budget_filtered = self._filter_by_budget(cars_data, answers.get('budget'))
        
        if not budget_filtered:
            logger.warning("Nenhum carro encontrado na faixa de preço")
            return []
        
        # 2. Calcular score para cada carro
        scored_cars = []
        for car in budget_filtered:
            try:
                score = self._calculate_comprehensive_score(car, answers)
                reasons = self._generate_detailed_reasons(car, answers, score)
                
                scored_cars.append({
                    'car': car,
                    'score': round(score, 1),
                    'reasons': reasons
                })
            except Exception as e:
                logger.error(f"Erro ao processar carro {car.get('id', 'unknown')}: {e}")
                continue
        
        # 3. Aplicar boost de texto livre se fornecido
        if answers.get('details'):
            scored_cars = self._apply_text_boost(scored_cars, answers['details'])
        
        # 4. Ordenar por score e retornar top 5
        scored_cars.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_cars[:5]

    def _filter_by_budget(self, cars: List[Dict], budget: str) -> List[Dict]:
        """
        Filtro rigoroso por faixa de preço
        """
        if not budget:
            return cars
        
        budget_ranges = {
            'up_30k': (0, 30000),
            '30k_50k': (30000, 50000),
            '50k_80k': (50000, 80000),
            '80k_120k': (80000, 120000),
            '120k_plus': (120000, float('inf'))
        }
        
        if budget not in budget_ranges:
            return cars
        
        min_price, max_price = budget_ranges[budget]
        
        filtered = []
        for car in cars:
            price = car.get('price', 0)
            if min_price <= price <= max_price:
                filtered.append(car)
        
        logger.info(f"Filtro orçamento {budget}: {len(filtered)}/{len(cars)} carros")
        return filtered

    def _calculate_comprehensive_score(self, car: Dict, answers: Dict[str, Any]) -> float:
        """
        Cálculo de score baseado nos critérios práticos com pesos realistas
        """
        scores = {}
        
        # 1. MOTIVO PRINCIPAL (peso alto - 30%)
        scores['main_purpose'] = self._score_main_purpose(car, answers.get('main_purpose', ''))
        
        # 2. FREQUÊNCIA DE USO (peso alto - 20%)
        scores['frequency'] = self._score_frequency(car, answers.get('frequency', ''))
        
        # 3. NECESSIDADES DE ESPAÇO (peso médio - 15%)
        scores['space'] = self._score_space_needs(car, answers.get('space_needs', ''))
        
        # 4. ECONOMIA DE COMBUSTÍVEL (peso médio - 15%)
        scores['fuel'] = self._score_fuel_priority(car, answers.get('fuel_priority', ''))
        
        # 5. PRIORIDADE PRINCIPAL (peso alto - 10%)
        scores['priority'] = self._score_top_priority(car, answers.get('top_priority', ''))
        
        # 6. EXPERIÊNCIA DO USUÁRIO (peso baixo - 5%)
        scores['experience'] = self._score_experience_level(car, answers.get('experience_level', ''))
        
        # 7. PREFERÊNCIA DE MARCA (boost adicional - 5%)
        scores['brand'] = self._score_brand_preference(car, answers.get('brand_preference', []))
        
        # Cálculo final com pesos
        weights = {
            'main_purpose': 0.30,
            'frequency': 0.20,
            'space': 0.15,
            'fuel': 0.15,
            'priority': 0.10,
            'experience': 0.05,
            'brand': 0.05
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores)
        
        logger.debug(f"Carro {car.get('brand', '')} {car.get('model', '')}: {scores} = {final_score:.1f}")
        
        return final_score

    def _score_main_purpose(self, car: Dict, purpose: str) -> float:
        """
        Score baseado no motivo principal de compra
        """
        brand = car.get('brand', '').lower()
        category = car.get('category', '').lower()
        consumption = car.get('consumption', 10)
        year = car.get('year', 2020)
        price = car.get('price', 50000)
        
        if purpose == 'work_app':
            # Trabalho (Uber/99): prioriza economia máxima e durabilidade
            score = 50
            
            # Consumo excelente
            if consumption >= 14:
                score += 30
            elif consumption >= 12:
                score += 20
            elif consumption >= 10:
                score += 10
            
            # Marcas confiáveis para trabalho
            reliable_brands = ['toyota', 'honda', 'chevrolet', 'ford', 'hyundai']
            if brand in reliable_brands:
                score += 15
            
            # Categoria adequada (evita SUV grandes)
            if category in ['hatch', 'sedan']:
                score += 15
            elif category == 'suv':
                score -= 10
            
            # Não muito caro (menos depreciação)
            if price <= 50000:
                score += 10
            
            return min(score, 100)
            
        elif purpose == 'family_daily':
            # Família: prioriza segurança, espaço e conforto
            score = 50
            
            # Espaço para família
            if category in ['sedan', 'suv']:
                score += 25
            elif category == 'hatch' and car.get('seats', 5) >= 5:
                score += 15
            
            # Marcas confiáveis para família
            family_brands = ['toyota', 'honda', 'volkswagen', 'hyundai']
            if brand in family_brands:
                score += 20
            
            # Não muito antigo (segurança moderna)
            if year >= 2018:
                score += 15
            elif year >= 2015:
                score += 10
            
            # Consumo razoável
            if consumption >= 10:
                score += 10
            
            return min(score, 100)
            
        elif purpose == 'first_car':
            # Primeiro carro: prioriza simplicidade e confiabilidade
            score = 50
            
            # Marcas conhecidas por simplicidade
            beginner_brands = ['toyota', 'honda', 'chevrolet', 'ford']
            if brand in beginner_brands:
                score += 25
            
            # Categoria simples
            if category == 'hatch':
                score += 20
            elif category == 'sedan':
                score += 15
            
            # Não muito caro
            if price <= 40000:
                score += 15
            
            # Boa economia
            if consumption >= 12:
                score += 15
            
            return min(score, 100)
            
        elif purpose == 'upgrade':
            # Upgrade: prioriza conforto e tecnologia
            score = 50
            
            # Categoria mais premium
            if category in ['sedan', 'suv']:
                score += 20
            
            # Marcas premium
            premium_brands = ['honda', 'toyota', 'volkswagen', 'hyundai']
            if brand in premium_brands:
                score += 20
            
            # Mais novo
            if year >= 2019:
                score += 20
            elif year >= 2017:
                score += 10
            
            # Não precisa ser o mais econômico
            if consumption >= 8:
                score += 10
            
            return min(score, 100)
            
        elif purpose == 'investment':
            # Investimento: prioriza revenda
            score = 50
            
            # Marcas com boa revenda
            resale_brands = ['toyota', 'honda', 'volkswagen']
            if brand in resale_brands:
                score += 30
            
            # Modelos específicos que valorizam
            model = car.get('model', '').lower()
            popular_models = ['corolla', 'civic', 'hilux', 'cr-v', 'jetta']
            if any(m in model for m in popular_models):
                score += 20
            
            # Não muito antigo
            if year >= 2018:
                score += 15
            
            return min(score, 100)
        
        return 50  # Default

    def _score_frequency(self, car: Dict, frequency: str) -> float:
        """
        Score baseado na frequência de uso
        """
        brand = car.get('brand', '').lower()
        consumption = car.get('consumption', 10)
        reliability = self.reliability_scores.get(brand, 70)
        maintenance = self.maintenance_costs.get(brand, 75)
        
        if frequency == 'daily_work':
            # Todo dia trabalhando: máxima durabilidade
            score = reliability * 0.6  # 60% confiabilidade
            score += maintenance * 0.3  # 30% custo manutenção
            score += min(consumption * 5, 50) * 0.1  # 10% economia
            return min(score, 100)
            
        elif frequency == 'daily_personal':
            # Todo dia pessoal: conforto + economia
            score = 50
            score += (reliability - 70) * 0.5  # Confiabilidade moderada
            score += min(consumption * 3, 30)  # Economia importante
            return min(score, 100)
            
        elif frequency == 'weekends':
            # Fins de semana: pode priorizar outros fatores
            score = 60
            score += min(consumption * 2, 20)  # Economia menos importante
            return min(score, 100)
            
        elif frequency == 'occasional':
            # Esporádico: confiabilidade é chave
            score = reliability * 0.8
            score += 20  # Boost base
            return min(score, 100)
        
        return 70  # Default

    def _score_space_needs(self, car: Dict, space_needs: str) -> float:
        """
        Score baseado nas necessidades de espaço
        """
        category = car.get('category', '').lower()
        seats = car.get('seats', 5)
        
        space_mapping = {
            'solo': {
                'hatch': 100,
                'sedan': 80,
                'suv': 60,
                'pickup': 50
            },
            'couple': {
                'hatch': 90,
                'sedan': 100,
                'suv': 80,
                'pickup': 60
            },
            'small_family': {
                'hatch': 70,
                'sedan': 90,
                'suv': 100,
                'pickup': 70
            },
            'large_family': {
                'hatch': 40,
                'sedan': 70,
                'suv': 100,
                'pickup': 80
            },
            'cargo': {
                'hatch': 30,
                'sedan': 50,
                'suv': 90,
                'pickup': 100
            }
        }
        
        if space_needs in space_mapping and category in space_mapping[space_needs]:
            base_score = space_mapping[space_needs][category]
            
            # Ajuste por número de assentos
            if seats >= 7 and space_needs in ['large_family', 'cargo']:
                base_score += 10
            elif seats < 5 and space_needs in ['large_family']:
                base_score -= 20
                
            return min(base_score, 100)
        
        return 70  # Default

    def _score_fuel_priority(self, car: Dict, fuel_priority: str) -> float:
        """
        Score baseado na prioridade de combustível
        """
        consumption = car.get('consumption', 10)
        category = car.get('category', '').lower()
        
        if fuel_priority == 'maximum_economy':
            # Máxima economia: cada litro conta
            if consumption >= 15:
                return 100
            elif consumption >= 13:
                return 90
            elif consumption >= 11:
                return 70
            elif consumption >= 9:
                return 50
            else:
                return 30
                
        elif fuel_priority == 'good_economy':
            # Boa economia: equilíbrio
            if consumption >= 12:
                return 90
            elif consumption >= 10:
                return 80
            elif consumption >= 8:
                return 70
            else:
                return 50
                
        elif fuel_priority == 'performance_first':
            # Performance primeiro: consumo menos importante
            if consumption >= 8:
                return 80
            elif consumption >= 6:
                return 70
            else:
                return 60
                
        elif fuel_priority == 'not_important':
            # Não é prioridade: score neutro
            return 75
        
        return 70  # Default

    def _score_top_priority(self, car: Dict, priority: str) -> float:
        """
        Score baseado na prioridade máxima do cliente
        """
        brand = car.get('brand', '').lower()
        year = car.get('year', 2020)
        consumption = car.get('consumption', 10)
        category = car.get('category', '').lower()
        
        if priority == 'reliability':
            # Não dar problema
            return self.reliability_scores.get(brand, 70)
            
        elif priority == 'resale_value':
            # Boa revenda
            base_score = self.resale_scores.get(brand, 70)
            
            # Ajuste por ano
            if year >= 2019:
                base_score += 10
            elif year <= 2015:
                base_score -= 15
                
            return min(base_score, 100)
            
        elif priority == 'economy':
            # Economia total (combustível + manutenção)
            fuel_score = min(consumption * 6, 60)
            maintenance_score = self.maintenance_costs.get(brand, 75) * 0.4
            return min(fuel_score + maintenance_score, 100)
            
        elif priority == 'comfort':
            # Conforto
            score = 50
            
            if category in ['sedan', 'suv']:
                score += 30
            
            if year >= 2018:
                score += 20
                
            # Marcas conhecidas pelo conforto
            comfort_brands = ['honda', 'toyota', 'volkswagen']
            if brand in comfort_brands:
                score += 15
                
            return min(score, 100)
            
        elif priority == 'performance':
            # Potência
            score = 50
            
            if category in ['suv', 'sedan']:
                score += 20
                
            if consumption <= 10:  # Motores maiores consomem mais
                score += 20
                
            performance_brands = ['ford', 'chevrolet', 'volkswagen']
            if brand in performance_brands:
                score += 15
                
            return min(score, 100)
        
        return 70  # Default

    def _score_experience_level(self, car: Dict, experience: str) -> float:
        """
        Score baseado na experiência do usuário
        """
        brand = car.get('brand', '').lower()
        category = car.get('category', '').lower()
        year = car.get('year', 2020)
        
        if experience == 'beginner':
            # Primeira vez: simplicidade
            simple_brands = ['toyota', 'honda', 'chevrolet']
            if brand in simple_brands and category == 'hatch':
                return 90
            elif brand in simple_brands:
                return 80
            else:
                return 60
                
        elif experience == 'some_experience':
            # Alguma experiência: abertura moderada
            return 75
            
        elif experience == 'experienced':
            # Experiente: pode avaliar qualquer modelo
            return 80
            
        elif experience == 'enthusiast':
            # Entusiasta: gosta de especificações
            if year >= 2018 and category != 'hatch':
                return 90
            else:
                return 70
        
        return 75  # Default

    def _score_brand_preference(self, car: Dict, preferences: List[str]) -> float:
        """
        Score baseado na preferência de marca (boost do "eu quero")
        """
        if not preferences:
            return 75
        
        brand = car.get('brand', '').lower()
        
        if 'no_preference' in preferences:
            return 75
        
        # Se a marca está na preferência, boost significativo
        if brand in preferences:
            return 100
        
        # Se não está, penalização moderada
        return 50

    def _apply_text_boost(self, scored_cars: List[Dict], details: str) -> List[Dict]:
        """
        Aplica boost baseado no texto livre do usuário
        """
        if not details:
            return scored_cars
        
        details_lower = details.lower()
        
        for item in scored_cars:
            car = item['car']
            brand = car.get('brand', '').lower()
            consumption = car.get('consumption', 10)
            category = car.get('category', '').lower()
            
            boost = 0
            new_reasons = []
            
            # Palavras-chave de trabalho/apps
            work_keywords = ['uber', '99', 'ifood', 'app', 'motorista', 'trabalh', 'renda', 'ganhar']
            if any(keyword in details_lower for keyword in work_keywords):
                if consumption >= 13 and brand in ['toyota', 'honda', 'chevrolet']:
                    boost += 15
                    new_reasons.append("💼 Ideal para trabalho com apps")
            
            # Palavras-chave de economia
            economy_keywords = ['econom', 'barato', 'gasto', 'combust', 'litro', 'km/l']
            if any(keyword in details_lower for keyword in economy_keywords):
                if consumption >= 12:
                    boost += 10
                    new_reasons.append("⛽ Excelente economia de combustível")
            
            # Palavras-chave de família
            family_keywords = ['famil', 'criança', 'filho', 'esposa', 'esposo', 'segur', 'viagem']
            if any(keyword in details_lower for keyword in family_keywords):
                if category in ['sedan', 'suv'] and brand in ['toyota', 'honda', 'volkswagen']:
                    boost += 12
                    new_reasons.append("👨‍👩‍👧‍👦 Perfeito para família")
            
            # Palavras-chave de confiabilidade
            reliability_keywords = ['confiav', 'problem', 'duravel', 'quebr', 'manutenc']
            if any(keyword in details_lower for keyword in reliability_keywords):
                reliability_score = self.reliability_scores.get(brand, 70)
                if reliability_score >= 85:
                    boost += 8
                    new_reasons.append("🛡️ Marca conhecida pela confiabilidade")
            
            # Aplicar boost
            if boost > 0:
                item['score'] = min(item['score'] + boost, 100)
                item['reasons'].extend(new_reasons)
        
        return scored_cars

    def _generate_detailed_reasons(self, car: Dict, answers: Dict, score: float) -> List[str]:
        """
        Gera razões detalhadas e práticas para a recomendação
        """
        reasons = []
        brand = car.get('brand', '').lower()
        consumption = car.get('consumption', 10)
        category = car.get('category', '').lower()
        price = car.get('price', 0)
        year = car.get('year', 2020)
        
        # Razões baseadas na pontuação
        if score >= 90:
            reasons.append("🎯 Excelente compatibilidade com suas necessidades")
        elif score >= 80:
            reasons.append("✅ Muito boa opção para seu perfil")
        elif score >= 70:
            reasons.append("👍 Boa opção considerando seus critérios")
        
        # Razões específicas por critério
        main_purpose = answers.get('main_purpose', '')
        
        if main_purpose == 'work_app' and consumption >= 13:
            reasons.append("🚖 Economia ideal para trabalho com apps")
        
        if main_purpose == 'family_daily' and category in ['sedan', 'suv']:
            reasons.append("👨‍👩‍👧‍👦 Espaço adequado para família")
        
        # Confiabilidade
        reliability = self.reliability_scores.get(brand, 70)
        if reliability >= 90:
            reasons.append("🛡️ Marca muito confiável")
        elif reliability >= 80:
            reasons.append("✅ Boa confiabilidade")
        
        # Economia
        if consumption >= 14:
            reasons.append("⛽ Muito econômico no combustível")
        elif consumption >= 12:
            reasons.append("💰 Boa economia de combustível")
        
        # Manutenção
        maintenance = self.maintenance_costs.get(brand, 75)
        if maintenance >= 85:
            reasons.append("🔧 Manutenção acessível")
        
        # Revenda
        if answers.get('top_priority') == 'resale_value':
            resale = self.resale_scores.get(brand, 70)
            if resale >= 85:
                reasons.append("📈 Excelente valor de revenda")
        
        # Limitar a 3 razões principais
        return reasons[:3]


def create_recommender() -> CarRecommender:
    """Factory function para criar instância do recomendador"""
    return CarRecommender()


# Compatibilidade com código existente
class SimpleCarRecommender(CarRecommender):
    """Alias para compatibilidade"""
    pass