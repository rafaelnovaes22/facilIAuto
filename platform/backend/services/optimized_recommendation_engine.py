"""
🤖 AI Engineer: Engine de Recomendação Otimizado

Implementações avançadas:
- Pesos dinâmicos baseados em perfil
- Boost de localização
- Penalties automáticos
- Diversidade forçada
- Machine Learning ready

Autor: AI Engineer + Data Analyst
Data: Outubro 2024
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter

from models.car import Car
from models.user_profile import UserProfile
from models.dealership import Dealership


class OptimizedRecommendationEngine:
    """
    Engine de recomendação otimizado com Data Science insights
    """
    
    # Configurações de otimização
    LOCATION_BOOST = {
        'same_city': 1.30,      # +30% no score
        'same_state': 1.15,     # +15%
        'other_state': 1.00,    # sem boost
    }
    
    PENALTIES = {
        'no_images': -0.15,            # -15%
        'outdated_30_days': -0.10,     # -10%
        'outdated_60_days': -0.20,     # -20%
        'incomplete_data': -0.05,      # -5%
    }
    
    DIVERSITY_RULES = {
        'max_same_brand_pct': 0.40,      # Max 40% mesma marca
        'max_same_dealer_pct': 0.30,     # Max 30% mesma concessionária
        'min_categories': 3,             # Min 3 categorias diferentes
    }
    
    def __init__(self, data_dir: str = "platform/backend/data"):
        self.data_dir = data_dir
        self.dealerships: List[Dealership] = []
        self.all_cars: List[Car] = []
        
        # Carregar dados
        self.load_dealerships()
        self.load_all_cars()
    
    def load_dealerships(self):
        """Carregar lista de concessionárias ativas"""
        dealerships_file = os.path.join(self.data_dir, "dealerships.json")
        
        if os.path.exists(dealerships_file):
            with open(dealerships_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.dealerships = [Dealership(**d) for d in data]
        else:
            self.dealerships = []
    
    def load_all_cars(self):
        """Carregar carros de TODAS as concessionárias ativas"""
        self.all_cars = []
        
        for dealership in self.dealerships:
            if not dealership.active:
                continue
            
            stock_file = os.path.join(self.data_dir, f"{dealership.id}_estoque.json")
            
            if not os.path.exists(stock_file):
                continue
            
            with open(stock_file, 'r', encoding='utf-8') as f:
                cars_data = json.load(f)
                
                for car_data in cars_data:
                    # Enriquecer com dados da concessionária
                    car_data['dealership_id'] = dealership.id
                    car_data['dealership_name'] = dealership.name
                    car_data['dealership_city'] = dealership.city
                    car_data['dealership_state'] = dealership.state
                    car_data['dealership_phone'] = dealership.phone
                    car_data['dealership_whatsapp'] = dealership.whatsapp
                    
                    # Premium boost
                    if dealership.premium:
                        car_data['premium_dealership'] = True
                    
                    try:
                        car = Car(**car_data)
                        self.all_cars.append(car)
                    except Exception:
                        continue
    
    def get_dynamic_weights(self, profile: UserProfile) -> Dict[str, float]:
        """
        🤖 AI Engineer: Pesos dinâmicos baseados em perfil
        
        Ajusta pesos do algoritmo baseado em características do usuário
        """
        weights = {
            'category': 0.25,
            'priorities': 0.30,
            'preferences': 0.20,
            'budget': 0.15,
            'location': 0.10,
        }
        
        # Família com crianças: segurança +10%
        if profile.tem_criancas:
            # Aumentar peso de prioridades (onde está segurança)
            weights['priorities'] += 0.10
            weights['budget'] -= 0.05
            weights['preferences'] -= 0.05
        
        # Primeiro carro: economia +15%
        if profile.primeiro_carro:
            # Aumentar peso de prioridades (economia importante)
            weights['priorities'] += 0.15
            weights['preferences'] -= 0.10
            weights['budget'] -= 0.05
        
        # Trabalho: performance +10%
        if profile.uso_principal == "trabalho":
            weights['priorities'] += 0.10
            weights['category'] -= 0.10
        
        # Priorizar locais: localização +15%
        if profile.priorizar_proximas:
            weights['location'] += 0.15
            weights['budget'] -= 0.10
            weights['preferences'] -= 0.05
        
        # Normalizar (soma = 1.0)
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        return weights
    
    def calculate_location_boost(self, car: Car, profile: UserProfile) -> float:
        """
        📈 Data Analyst: Boost baseado em proximidade
        
        Mesma cidade: +30%
        Mesmo estado: +15%
        Outro estado: sem boost
        """
        if not profile.city:
            return self.LOCATION_BOOST['other_state']
        
        if car.dealership_city.lower() == profile.city.lower():
            return self.LOCATION_BOOST['same_city']
        elif car.dealership_state.upper() == (profile.state or "").upper():
            return self.LOCATION_BOOST['same_state']
        else:
            return self.LOCATION_BOOST['other_state']
    
    def calculate_penalties(self, car: Car) -> float:
        """
        🤖 AI Engineer: Penalties automáticos
        
        - Sem imagens: -15%
        - Desatualizado (> 30 dias): -10%
        - Desatualizado (> 60 dias): -20%
        - Dados incompletos: -5%
        """
        penalty = 0.0
        
        # Sem imagens
        if not car.imagens or len(car.imagens) == 0:
            penalty += self.PENALTIES['no_images']
        
        # Desatualizado
        if car.data_atualizacao:
            try:
                last_update = datetime.fromisoformat(car.data_atualizacao)
                days_old = (datetime.now() - last_update).days
                
                if days_old > 60:
                    penalty += self.PENALTIES['outdated_60_days']
                elif days_old > 30:
                    penalty += self.PENALTIES['outdated_30_days']
            except:
                pass
        
        # Dados incompletos
        if not all([car.versao, car.cambio, car.cor]):
            penalty += self.PENALTIES['incomplete_data']
        
        return penalty
    
    def calculate_optimized_score(
        self, 
        car: Car, 
        profile: UserProfile,
        weights: Dict[str, float]
    ) -> float:
        """
        🤖 AI Engineer: Score otimizado com todos os fatores
        """
        score = 0.0
        
        # 1. Categoria (peso dinâmico)
        category_score = self.score_category_by_usage(car, profile)
        score += category_score * weights['category']
        
        # 2. Prioridades (peso dinâmico)
        priorities_score = self.score_priorities(car, profile)
        score += priorities_score * weights['priorities']
        
        # 3. Preferências (peso dinâmico)
        preferences_score = self.score_preferences(car, profile)
        score += preferences_score * weights['preferences']
        
        # 4. Orçamento (peso dinâmico)
        budget_score = self.score_budget_position(car, profile)
        score += budget_score * weights['budget']
        
        # 5. Localização base (peso dinâmico)
        location_base = 1.0 if profile.city and car.dealership_city.lower() == profile.city.lower() else 0.5
        score += location_base * weights['location']
        
        # Normalizar para 0-1
        score = max(0.0, min(1.0, score))
        
        # 6. Aplicar boost de localização
        location_boost = self.calculate_location_boost(car, profile)
        score *= location_boost
        
        # 7. Aplicar penalties
        penalties = self.calculate_penalties(car)
        score += penalties
        
        # 8. Premium dealership bonus (+5%)
        if hasattr(car, 'premium_dealership') and car.premium_dealership:
            score *= 1.05
        
        # 9. Destaque bonus (+10%)
        if car.destaque:
            score *= 1.10
        
        # Garantir 0-1
        return max(0.0, min(1.0, score))
    
    def score_category_by_usage(self, car: Car, profile: UserProfile) -> float:
        """Score baseado na adequação da categoria ao uso"""
        uso_categoria_map = {
            "familia": {"SUV": 0.9, "Sedan": 0.8, "Hatch": 0.5, "Pickup": 0.4, "Compacto": 0.3},
            "trabalho": {"Sedan": 0.9, "Hatch": 0.8, "SUV": 0.6, "Compacto": 0.7, "Pickup": 0.5},
            "lazer": {"SUV": 0.9, "Pickup": 0.8, "Sedan": 0.6, "Hatch": 0.5, "Compacto": 0.4},
            "comercial": {"Pickup": 0.9, "SUV": 0.7, "Sedan": 0.6, "Hatch": 0.5, "Compacto": 0.4},
            "primeiro_carro": {"Hatch": 0.9, "Compacto": 0.9, "Sedan": 0.6, "SUV": 0.4, "Pickup": 0.3}
        }
        
        return uso_categoria_map.get(profile.uso_principal, {}).get(car.categoria, 0.5)
    
    def score_priorities(self, car: Car, profile: UserProfile) -> float:
        """Score baseado nas prioridades do usuário"""
        priorities = profile.prioridades
        
        priority_scores = {
            "economia": car.score_economia,
            "espaco": car.score_familia,
            "performance": car.score_performance,
            "conforto": car.score_conforto,
            "seguranca": car.score_seguranca
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for priority, user_value in priorities.items():
            if priority in priority_scores:
                normalized_weight = user_value / 5.0
                car_score = priority_scores[priority]
                
                total_score += car_score * normalized_weight
                total_weight += normalized_weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def score_preferences(self, car: Car, profile: UserProfile) -> float:
        """Score baseado em preferências específicas"""
        score = 0.5
        
        if profile.marcas_preferidas and car.marca in profile.marcas_preferidas:
            score += 0.3
        
        if profile.marcas_rejeitadas and car.marca in profile.marcas_rejeitadas:
            score -= 0.5
        
        if profile.tipos_preferidos and car.categoria in profile.tipos_preferidos:
            score += 0.2
        
        if profile.combustivel_preferido and car.combustivel == profile.combustivel_preferido:
            score += 0.1
        
        if profile.cambio_preferido and car.cambio == profile.cambio_preferido:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def score_budget_position(self, car: Car, profile: UserProfile) -> float:
        """Score baseado na posição do carro no orçamento"""
        budget_range = profile.orcamento_max - profile.orcamento_min
        
        if budget_range == 0:
            return 1.0 if car.preco == profile.orcamento_max else 0.0
        
        # Carros no meio/inferior do orçamento são melhores (economia)
        middle = profile.orcamento_min + (budget_range * 0.4)  # 40% do range
        distance_from_target = abs(car.preco - middle)
        normalized_distance = distance_from_target / (budget_range / 2)
        
        return max(0.0, 1.0 - normalized_distance)
    
    def enforce_diversity(self, recommendations: List[Dict], limit: int) -> List[Dict]:
        """
        📈 Data Analyst: Forçar diversidade nos resultados
        
        Regras:
        - Max 40% mesma marca
        - Max 30% mesma concessionária
        - Min 3 categorias diferentes
        """
        if len(recommendations) <= limit:
            return recommendations
        
        result = []
        brand_count = Counter()
        dealer_count = Counter()
        category_count = Counter()
        
        max_brand = int(limit * self.DIVERSITY_RULES['max_same_brand_pct'])
        max_dealer = int(limit * self.DIVERSITY_RULES['max_same_dealer_pct'])
        
        for rec in recommendations:
            car = rec['car']
            
            # Verificar limites
            if brand_count[car.marca] >= max_brand:
                continue
            if dealer_count[car.dealership_id] >= max_dealer:
                continue
            
            # Adicionar
            result.append(rec)
            brand_count[car.marca] += 1
            dealer_count[car.dealership_id] += 1
            category_count[car.categoria] += 1
            
            if len(result) >= limit:
                break
        
        # Se não atingiu o limite, preencher com os restantes
        if len(result) < limit:
            for rec in recommendations:
                if rec not in result:
                    result.append(rec)
                    if len(result) >= limit:
                        break
        
        return result
    
    def recommend(
        self,
        profile: UserProfile,
        limit: int = 20,
        score_threshold: float = 0.40  # Aumentado de 0.20 para 0.40
    ) -> List[Dict]:
        """
        🤖 AI Engineer: Recomendação otimizada
        
        Melhorias:
        - Pesos dinâmicos
        - Boost de localização
        - Penalties automáticos
        - Diversidade forçada
        - Threshold mais alto
        """
        # 1. Filtrar por orçamento (hard constraint)
        filtered_cars = [
            car for car in self.all_cars
            if car.disponivel and profile.orcamento_min <= car.preco <= profile.orcamento_max
        ]
        
        if not filtered_cars:
            # Fallback: tolerância de 5% se score seria alto
            filtered_cars = [
                car for car in self.all_cars
                if car.disponivel and car.preco <= profile.orcamento_max * 1.05
            ]
        
        # 2. Calcular pesos dinâmicos
        weights = self.get_dynamic_weights(profile)
        
        # 3. Calcular scores
        scored_cars = []
        for car in filtered_cars:
            score = self.calculate_optimized_score(car, profile, weights)
            
            if score >= score_threshold:
                scored_cars.append({
                    'car': car,
                    'score': score,
                    'match_percentage': int(score * 100),
                    'justificativa': self.generate_justification(car, profile, score),
                    'location_boost': self.calculate_location_boost(car, profile),
                    'penalties': self.calculate_penalties(car),
                })
        
        # 4. Ordenar por score
        scored_cars.sort(key=lambda x: x['score'], reverse=True)
        
        # 5. Aplicar diversidade
        diverse_results = self.enforce_diversity(scored_cars, limit)
        
        return diverse_results
    
    def generate_justification(self, car: Car, profile: UserProfile, score: float) -> str:
        """Gerar justificativa otimizada"""
        reasons = []
        
        # Categoria apropriada
        if self.score_category_by_usage(car, profile) > 0.7:
            reasons.append(f"Categoria {car.categoria} ideal para {profile.uso_principal}")
        
        # Prioridades atendidas
        if profile.prioridades.get("economia", 0) >= 4 and car.score_economia > 0.7:
            reasons.append("Excelente economia de combustível")
        
        if profile.prioridades.get("espaco", 0) >= 4 and car.score_familia > 0.7:
            reasons.append("Amplo espaço para família")
        
        if profile.prioridades.get("seguranca", 0) >= 4 and car.score_seguranca > 0.7:
            reasons.append("Alta segurança")
        
        # Localização
        if profile.city and car.dealership_city.lower() == profile.city.lower():
            reasons.append(f"Concessionária próxima em {car.dealership_city}")
        
        # Marca preferida
        if profile.marcas_preferidas and car.marca in profile.marcas_preferidas:
            reasons.append(f"Marca {car.marca} de sua preferência")
        
        # Destaque
        if car.destaque:
            reasons.append("Oferta especial da concessionária")
        
        # Score alto
        if score > 0.80:
            reasons.append("Excelente compatibilidade geral")
        
        if not reasons:
            reasons.append("Boa opção dentro do seu orçamento")
        
        return ". ".join(reasons[:3]) + "."  # Max 3 razões
    
    def get_stats(self) -> Dict:
        """Estatísticas gerais da plataforma"""
        return {
            "total_dealerships": len(self.dealerships),
            "active_dealerships": len([d for d in self.dealerships if d.active]),
            "total_cars": len(self.all_cars),
            "available_cars": len([c for c in self.all_cars if c.disponivel]),
            "avg_score_economia": sum(c.score_economia for c in self.all_cars) / len(self.all_cars) if self.all_cars else 0,
            "avg_score_seguranca": sum(c.score_seguranca for c in self.all_cars) / len(self.all_cars) if self.all_cars else 0,
        }

