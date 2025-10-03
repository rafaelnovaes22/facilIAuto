"""
Sistema de Recomendação Unificado - Agrega carros de TODAS as concessionárias
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile
from models.dealership import Dealership


class UnifiedRecommendationEngine:
    """
    Engine de recomendação que busca carros em TODAS as concessionárias ativas
    """
    
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
                print(f"[OK] {len(self.dealerships)} concessionarias carregadas")
        else:
            print(f"[AVISO] Arquivo {dealerships_file} nao encontrado")
            self.dealerships = []
    
    def load_all_cars(self):
        """Carregar carros de TODAS as concessionárias ativas"""
        self.all_cars = []
        
        for dealership in self.dealerships:
            if not dealership.active:
                continue
            
            # Arquivo de estoque da concessionária
            stock_file = os.path.join(self.data_dir, f"{dealership.id}_estoque.json")
            
            if not os.path.exists(stock_file):
                print(f"[AVISO] Estoque nao encontrado: {stock_file}")
                continue
            
            # Carregar carros
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
                    
                    try:
                        car = Car(**car_data)
                        self.all_cars.append(car)
                    except Exception as e:
                        print(f"[ERRO] Erro ao carregar carro: {e}")
                        continue
            
            print(f"[OK] {dealership.name}: {len([c for c in self.all_cars if c.dealership_id == dealership.id])} carros")
        
        print(f"[OK] Total: {len(self.all_cars)} carros de {len(self.dealerships)} concessionarias")
    
    def filter_by_budget(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """Filtrar carros por orçamento"""
        return [
            car for car in cars
            if profile.orcamento_min <= car.preco <= profile.orcamento_max
        ]
    
    def prioritize_by_location(self, cars: List[Car], user_city: str, user_state: str) -> List[Car]:
        """Priorizar carros de concessionárias próximas"""
        same_city = []
        same_state = []
        others = []
        
        for car in cars:
            if car.dealership_city.lower() == user_city.lower():
                same_city.append(car)
            elif car.dealership_state.upper() == user_state.upper():
                same_state.append(car)
            else:
                others.append(car)
        
        # Retornar com priorização geográfica
        return same_city + same_state + others
    
    def calculate_match_score(self, car: Car, profile: UserProfile) -> float:
        """
        Calcular score de compatibilidade (0.0 a 1.0)
        """
        score = 0.0
        weights_sum = 0.0
        
        # 1. Score de categoria baseado no uso (peso 30%)
        category_weight = 0.3
        category_score = self.score_category_by_usage(car, profile)
        score += category_score * category_weight
        weights_sum += category_weight
        
        # 2. Score de prioridades do usuário (peso 40%)
        priorities_weight = 0.4
        priorities_score = self.score_priorities(car, profile)
        score += priorities_score * priorities_weight
        weights_sum += priorities_weight
        
        # 3. Score de preferências (peso 20%)
        preferences_weight = 0.2
        preferences_score = self.score_preferences(car, profile)
        score += preferences_score * preferences_weight
        weights_sum += preferences_weight
        
        # 4. Score de posição no orçamento (peso 10%)
        budget_weight = 0.1
        budget_score = self.score_budget_position(car, profile)
        score += budget_score * budget_weight
        weights_sum += budget_weight
        
        # Normalizar
        final_score = score / weights_sum if weights_sum > 0 else 0.0
        
        return max(0.0, min(1.0, final_score))
    
    def score_category_by_usage(self, car: Car, profile: UserProfile) -> float:
        """Score baseado na adequação da categoria ao uso"""
        uso_categoria_map = {
            "familia": {"SUV": 0.9, "Sedan": 0.8, "Hatch": 0.5, "Pickup": 0.4, "Compacto": 0.3},
            "trabalho": {"Sedan": 0.9, "Hatch": 0.8, "SUV": 0.6, "Compacto": 0.7, "Pickup": 0.5},
            "lazer": {"SUV": 0.9, "Pickup": 0.8, "Sedan": 0.6, "Hatch": 0.5, "Compacto": 0.4},
            "comercial": {"Pickup": 0.9, "SUV": 0.7, "Sedan": 0.6, "Hatch": 0.5, "Compacto": 0.4},
            "primeiro_carro": {"Hatch": 0.9, "Compacto": 0.9, "Sedan": 0.6, "SUV": 0.4, "Pickup": 0.3}
        }
        
        uso = profile.uso_principal
        categoria = car.categoria
        
        return uso_categoria_map.get(uso, {}).get(categoria, 0.5)
    
    def score_priorities(self, car: Car, profile: UserProfile) -> float:
        """Score baseado nas prioridades do usuário"""
        priorities = profile.prioridades
        
        # Mapear prioridades para scores do carro
        priority_scores = {
            "economia": car.score_economia,
            "espaco": car.score_familia,  # Espaço correlaciona com família
            "performance": car.score_performance,
            "conforto": car.score_conforto,
            "seguranca": car.score_seguranca
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for priority, user_value in priorities.items():
            if priority in priority_scores:
                # Normalizar user_value (1-5) para 0-1
                normalized_weight = user_value / 5.0
                car_score = priority_scores[priority]
                
                total_score += car_score * normalized_weight
                total_weight += normalized_weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def score_preferences(self, car: Car, profile: UserProfile) -> float:
        """Score baseado em preferências específicas"""
        score = 0.5  # Base neutra
        
        # Marcas preferidas (+30%)
        if profile.marcas_preferidas and car.marca in profile.marcas_preferidas:
            score += 0.3
        
        # Marcas rejeitadas (-50%)
        if profile.marcas_rejeitadas and car.marca in profile.marcas_rejeitadas:
            score -= 0.5
        
        # Tipos preferidos (+20%)
        if profile.tipos_preferidos and car.categoria in profile.tipos_preferidos:
            score += 0.2
        
        # Combustível preferido (+10%)
        if profile.combustivel_preferido and car.combustivel == profile.combustivel_preferido:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def score_budget_position(self, car: Car, profile: UserProfile) -> float:
        """Score baseado na posição do carro no orçamento"""
        budget_range = profile.orcamento_max - profile.orcamento_min
        
        if budget_range == 0:
            return 1.0 if car.preco == profile.orcamento_max else 0.0
        
        # Carros no meio do orçamento são melhores
        middle = (profile.orcamento_min + profile.orcamento_max) / 2
        distance_from_middle = abs(car.preco - middle)
        normalized_distance = distance_from_middle / (budget_range / 2)
        
        # Score maior quando mais próximo do meio
        return max(0.0, 1.0 - normalized_distance)
    
    def recommend(
        self,
        profile: UserProfile,
        limit: int = 10,
        score_threshold: float = 0.2
    ) -> List[Dict]:
        """
        Gerar recomendações de TODAS as concessionárias
        
        Returns:
            Lista de dicionários com car, score, match_percentage, justificativa
        """
        # 1. Filtrar por orçamento (hard constraint)
        filtered_cars = self.filter_by_budget(self.all_cars, profile)
        
        if not filtered_cars:
            # Fallback: pegar os 5 carros mais próximos do orçamento
            all_sorted = sorted(
                self.all_cars,
                key=lambda c: abs(c.preco - profile.orcamento_max)
            )
            filtered_cars = all_sorted[:5]
        
        # 2. Priorizar por localização (se especificado)
        if profile.city and profile.priorizar_proximas:
            filtered_cars = self.prioritize_by_location(
                filtered_cars,
                profile.city,
                profile.state or ""
            )
        
        # 3. Calcular scores
        scored_cars = []
        for car in filtered_cars:
            if not car.disponivel:
                continue
            
            score = self.calculate_match_score(car, profile)
            
            if score >= score_threshold:
                scored_cars.append({
                    'car': car,
                    'score': score,
                    'match_percentage': int(score * 100),
                    'justificativa': self.generate_justification(car, profile, score)
                })
        
        # 4. Ordenar por score
        scored_cars.sort(key=lambda x: x['score'], reverse=True)
        
        # 5. Retornar top N
        return scored_cars[:limit]
    
    def generate_justification(self, car: Car, profile: UserProfile, score: float) -> str:
        """Gerar justificativa para a recomendação"""
        reasons = []
        
        # Categoria apropriada
        if self.score_category_by_usage(car, profile) > 0.7:
            reasons.append(f"Categoria {car.categoria} ideal para {profile.uso_principal}")
        
        # Prioridades atendidas
        if profile.prioridades.get("economia", 0) >= 4 and car.score_economia > 0.7:
            reasons.append("Excelente economia de combustível")
        
        if profile.prioridades.get("espaco", 0) >= 4 and car.score_familia > 0.7:
            reasons.append("Amplo espaço para família")
        
        # Localização
        if car.dealership_city == profile.city:
            reasons.append(f"Concessionária em {car.dealership_city}")
        
        # Marca preferida
        if car.marca in profile.marcas_preferidas:
            reasons.append(f"Marca {car.marca} de sua preferência")
        
        if not reasons:
            reasons.append("Boa opção dentro do seu orçamento")
        
        return ". ".join(reasons) + "."
    
    def get_stats(self) -> Dict:
        """Estatísticas gerais da plataforma"""
        return {
            "total_dealerships": len(self.dealerships),
            "active_dealerships": len([d for d in self.dealerships if d.active]),
            "total_cars": len(self.all_cars),
            "available_cars": len([c for c in self.all_cars if c.disponivel]),
            "dealerships_by_state": self._group_by_state(),
            "cars_by_category": self._group_by_category()
        }
    
    def _group_by_state(self) -> Dict[str, int]:
        """Agrupar concessionárias por estado"""
        result = {}
        for d in self.dealerships:
            result[d.state] = result.get(d.state, 0) + 1
        return result
    
    def _group_by_category(self) -> Dict[str, int]:
        """Agrupar carros por categoria"""
        result = {}
        for car in self.all_cars:
            result[car.categoria] = result.get(car.categoria, 0) + 1
        return result

