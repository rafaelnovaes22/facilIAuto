"""
Sistema de Recomendação Unificado - Agrega carros de TODAS as concessionárias
🤖 AI Engineer: FASE 1 - Filtros avançados implementados
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile
from models.dealership import Dealership
from utils.geo_distance import calculate_distance, get_city_coordinates
from services.car_metrics import CarMetricsCalculator


class UnifiedRecommendationEngine:
    """
    Engine de recomendação que busca carros em TODAS as concessionárias ativas
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.dealerships: List[Dealership] = []
        self.all_cars: List[Car] = []
        self.metrics_calculator = CarMetricsCalculator()  # 📊 FASE 3
        
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
            
            # Carros agora estão dentro do dealerships.json no campo 'carros'
            cars_data = dealership.carros if hasattr(dealership, 'carros') else []
            
            if not cars_data:
                print(f"[AVISO] Nenhum carro na concessionaria: {dealership.name}")
                continue
            
            # Processar cada carro
            for car_data in cars_data:
                # Converter para dict se for objeto Pydantic
                if isinstance(car_data, dict):
                    car_dict = car_data.copy()
                else:
                    car_dict = car_data.dict() if hasattr(car_data, 'dict') else dict(car_data)
                
                # Enriquecer com dados da concessionária
                car_dict['dealership_id'] = dealership.id
                car_dict['dealership_name'] = dealership.name
                car_dict['dealership_city'] = dealership.city
                car_dict['dealership_state'] = dealership.state
                car_dict['dealership_phone'] = dealership.phone
                car_dict['dealership_whatsapp'] = dealership.whatsapp
                
                # 🏗️ FASE 1: Adicionar coordenadas da concessionária
                car_dict['dealership_latitude'] = dealership.latitude
                car_dict['dealership_longitude'] = dealership.longitude
                
                try:
                    # 📊 FASE 3: Calcular métricas automaticamente se não existirem
                    if not car_dict.get('indice_confiabilidade') or car_dict.get('indice_confiabilidade') == 0.5:
                        metrics = self.metrics_calculator.calculate_all_metrics(
                            marca=car_dict.get('marca', ''),
                            categoria=car_dict.get('categoria', ''),
                            ano=car_dict.get('ano', 2020),
                            quilometragem=car_dict.get('quilometragem', 50000)
                        )
                        car_dict['indice_confiabilidade'] = metrics['indice_confiabilidade']
                        car_dict['indice_revenda'] = metrics['indice_revenda']
                        car_dict['taxa_depreciacao_anual'] = metrics['taxa_depreciacao_anual']
                        car_dict['custo_manutencao_anual'] = metrics['custo_manutencao_anual']
                    
                    car = Car(**car_dict)
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
    
    def filter_by_year(self, cars: List[Car], ano_minimo: Optional[int]) -> List[Car]:
        """
        🤖 AI Engineer (FASE 1): Filtrar por ano mínimo
        Elimina carros mais antigos que o ano especificado
        """
        if not ano_minimo:
            return cars
        
        return [car for car in cars if car.ano >= ano_minimo]
    
    def filter_by_km(self, cars: List[Car], km_maxima: Optional[int]) -> List[Car]:
        """
        🤖 AI Engineer (FASE 1): Filtrar por quilometragem máxima
        Elimina carros com mais km que o especificado
        """
        if not km_maxima:
            return cars
        
        return [car for car in cars if car.quilometragem <= km_maxima]
    
    def filter_by_must_haves(self, cars: List[Car], must_haves: List[str]) -> List[Car]:
        """
        📊 Data Analyst (FASE 1): Filtrar por itens obrigatórios
        Elimina carros que não possuem TODOS os itens especificados
        
        Exemplos de must_haves:
        - "ISOFIX": sistema de fixação para cadeirinha
        - "6_airbags": 6 airbags ou mais
        - "controle_estabilidade": ESP/ESC
        - "camera_re": câmera de ré
        - "ABS": freios ABS
        """
        if not must_haves:
            return cars
        
        filtered = []
        for car in cars:
            # Verificar se o carro tem TODOS os itens obrigatórios
            car_items = set(car.itens_seguranca + car.itens_conforto)
            required_items = set(must_haves)
            
            if required_items.issubset(car_items):
                filtered.append(car)
        
        return filtered
    
    def filter_by_radius(
        self, 
        cars: List[Car], 
        user_city: Optional[str],
        raio_km: Optional[int]
    ) -> List[Car]:
        """
        💻 Tech Lead (FASE 1): Filtrar por raio geográfico
        Elimina concessionárias fora do raio especificado
        
        Args:
            cars: Lista de carros
            user_city: Cidade do usuário
            raio_km: Raio máximo em km
        
        Returns:
            Carros de concessionárias dentro do raio
        """
        if not raio_km or not user_city:
            return cars
        
        # Obter coordenadas do usuário
        user_coords = get_city_coordinates(user_city)
        if not user_coords:
            print(f"[AVISO] Coordenadas não encontradas para: {user_city}")
            return cars
        
        filtered = []
        for car in cars:
            # Verificar se carro tem coordenadas da concessionária
            if car.dealership_latitude is None or car.dealership_longitude is None:
                # Se não tiver coordenadas, incluir por fallback
                continue
            
            dealer_coords = (car.dealership_latitude, car.dealership_longitude)
            distance = calculate_distance(user_coords, dealer_coords)
            
            if distance is not None and distance <= raio_km:
                filtered.append(car)
        
        return filtered
    
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
    
    def get_dynamic_weights(self, profile: UserProfile) -> Dict[str, float]:
        """
        Ajustar pesos baseado no perfil de uso
        Pesos dinâmicos otimizam matching por contexto do usuário
        """
        # Pesos padrão
        default_weights = {
            'category': 0.30,
            'priorities': 0.40,
            'preferences': 0.20,
            'budget': 0.10
        }
        
        # Ajustes por perfil de uso
        if profile.uso_principal == "familia":
            # Família: categoria e prioridades são críticas
            return {
                'category': 0.40,   # +10% (SUV/Van críticos)
                'priorities': 0.45,  # +5% (segurança/espaço)
                'preferences': 0.10, # -10% (menos relevante)
                'budget': 0.05      # -5% (mais flexível)
            }
        
        elif profile.uso_principal == "primeiro_carro":
            # Primeiro carro: prioridades (economia/confiabilidade) críticas
            return {
                'category': 0.35,   # +5% (Hatch/Compacto importantes)
                'priorities': 0.50,  # +10% (economia crucial)
                'preferences': 0.10, # -10% (menos importante)
                'budget': 0.05      # -5% (orçamento apertado)
            }
        
        elif profile.uso_principal == "trabalho":
            # Trabalho: economia e categoria importantes
            return {
                'category': 0.25,   # -5% (mais flexível)
                'priorities': 0.45,  # +5% (economia importante)
                'preferences': 0.20, # mantém
                'budget': 0.10      # mantém
            }
        
        elif profile.uso_principal == "comercial":
            # Comercial: categoria é tudo (Pickup/Van)
            return {
                'category': 0.45,   # +15% (tipo de veículo crítico)
                'priorities': 0.35,  # -5% (confiabilidade importante mas secundário)
                'preferences': 0.15, # -5%
                'budget': 0.05      # -5%
            }
        
        elif profile.uso_principal == "lazer":
            # Lazer: categoria e performance importantes
            return {
                'category': 0.35,   # +5% (SUV/Pickup)
                'priorities': 0.40,  # mantém
                'preferences': 0.15, # -5%
                'budget': 0.10      # mantém
            }
        
        elif profile.uso_principal == "transporte_passageiros":
            # Transporte: categoria é crítica (Van)
            return {
                'category': 0.50,   # +20% (Van essencial)
                'priorities': 0.35,  # -5%
                'preferences': 0.10, # -10%
                'budget': 0.05      # -5%
            }
        
        return default_weights
    
    def calculate_match_score(self, car: Car, profile: UserProfile) -> float:
        """
        Calcular score de compatibilidade (0.0 a 1.0)
        Usando pesos dinâmicos baseados no perfil
        """
        # Obter pesos dinâmicos
        weights = self.get_dynamic_weights(profile)
        
        score = 0.0
        weights_sum = 0.0
        
        # 1. Score de categoria baseado no uso (peso dinâmico)
        category_score = self.score_category_by_usage(car, profile)
        score += category_score * weights['category']
        weights_sum += weights['category']
        
        # 2. Score de prioridades do usuário (peso dinâmico)
        priorities_score = self.score_priorities(car, profile)
        score += priorities_score * weights['priorities']
        weights_sum += weights['priorities']
        
        # 3. Score de preferências (peso dinâmico)
        preferences_score = self.score_preferences(car, profile)
        score += preferences_score * weights['preferences']
        weights_sum += weights['preferences']
        
        # 4. Score de posição no orçamento (peso dinâmico)
        budget_score = self.score_budget_position(car, profile)
        score += budget_score * weights['budget']
        weights_sum += weights['budget']
        
        # Normalizar
        final_score = score / weights_sum if weights_sum > 0 else 0.0
        
        return max(0.0, min(1.0, final_score))
    
    def score_category_by_usage(self, car: Car, profile: UserProfile) -> float:
        """
        Score baseado na adequação da categoria ao uso
        Valores refinados para matching mais preciso por perfil
        """
        uso_categoria_map = {
            "familia": {
                "SUV": 0.95,      # Ideal - espaço + segurança
                "Van": 0.90,      # Muito bom - máximo espaço
                "Sedan": 0.75,    # Bom, mas menos espaço
                "Hatch": 0.40,    # Inadequado para família
                "Pickup": 0.35,   # Inadequado
                "Compacto": 0.20  # Muito inadequado
            },
            "primeiro_carro": {
                "Hatch": 0.95,    # Ideal - fácil dirigir
                "Compacto": 0.95, # Ideal - econômico
                "Sedan": 0.55,    # Grande demais
                "SUV": 0.30,      # Inadequado
                "Pickup": 0.20,   # Muito inadequado
                "Van": 0.15       # Completamente inadequado
            },
            "trabalho": {
                "Sedan": 0.95,    # Ideal - profissional
                "Hatch": 0.85,    # Bom - econômico
                "Compacto": 0.75, # Bom para cidade
                "SUV": 0.50,      # Consome muito
                "Pickup": 0.40,   # Não profissional
                "Van": 0.30       # Inadequado
            },
            "comercial": {
                "Pickup": 0.95,   # Ideal - capacidade de carga
                "Van": 0.90,      # Ideal - volume
                "SUV": 0.60,      # Ok mas limitado
                "Sedan": 0.40,    # Inadequado
                "Hatch": 0.30,    # Inadequado
                "Compacto": 0.25  # Muito inadequado
            },
            "lazer": {
                "SUV": 0.95,      # Ideal - aventura/off-road
                "Pickup": 0.85,   # Muito bom - off-road
                "Van": 0.70,      # Bom para viagens
                "Sedan": 0.55,    # Limitado
                "Hatch": 0.40,    # Inadequado
                "Compacto": 0.30  # Muito inadequado
            },
            "transporte_passageiros": {
                "Van": 0.95,      # Ideal - capacidade
                "SUV": 0.70,      # Limitado a 5-7 lugares
                "Sedan": 0.50,    # Apenas 5 lugares
                "Pickup": 0.35,   # Inadequado
                "Hatch": 0.25,    # Muito inadequado
                "Compacto": 0.15  # Completamente inadequado
            }
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
            "seguranca": car.score_seguranca,
            # 📊 FASE 3: Métricas avançadas
            "revenda": car.indice_revenda,
            "confiabilidade": car.indice_confiabilidade,
            "custo_manutencao": self._normalize_maintenance_cost(car.custo_manutencao_anual)
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
    
    def _normalize_maintenance_cost(self, cost: Optional[float]) -> float:
        """
        📊 FASE 3: Normalizar custo de manutenção para 0-1
        Quanto MENOR o custo, MAIOR o score
        """
        if cost is None:
            return 0.5
        
        # Custos de referência
        MIN_COST = 1500  # R$ 1.500/ano (muito barato)
        MAX_COST = 8000  # R$ 8.000/ano (muito caro)
        
        # Inverter: custo baixo = score alto
        if cost <= MIN_COST:
            return 1.0
        elif cost >= MAX_COST:
            return 0.0
        else:
            # Normalizar invertido
            normalized = 1.0 - ((cost - MIN_COST) / (MAX_COST - MIN_COST))
            return max(0.0, min(1.0, normalized))
    
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
    
    def filter_by_family_context(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """
        Filtro de contexto para família
        Se tem crianças, priorizar carros com características adequadas
        """
        # Se não é perfil família ou não tem crianças, não filtrar
        if profile.uso_principal != "familia" or not profile.tem_criancas:
            return cars
        
        # Priorizar carros com características familiares
        family_friendly = []
        others = []
        
        for car in cars:
            # Critérios preferenciais para família com crianças:
            has_isofix = 'ISOFIX' in car.itens_seguranca or 'isofix' in [i.lower() for i in car.itens_seguranca]
            good_space = car.score_familia >= 0.6
            is_good_category = car.categoria in ['SUV', 'Van', 'Sedan']
            
            if has_isofix or (good_space and is_good_category):
                family_friendly.append(car)
            else:
                others.append(car)
        
        # Retornar family-friendly primeiro, depois outros
        return family_friendly + others
    
    def filter_by_first_car(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """
        Filtro de contexto para primeiro carro
        Evitar carros muito grandes, potentes ou complexos
        """
        # Se não é primeiro carro, não filtrar
        if not profile.primeiro_carro and profile.uso_principal != "primeiro_carro":
            return cars
        
        # Filtrar carros inadequados para primeiro carro
        suitable = []
        less_suitable = []
        
        for car in cars:
            # Critérios para primeiro carro:
            is_small = car.categoria in ['Hatch', 'Compacto']
            is_economical = car.score_economia >= 0.7
            is_simple_transmission = car.cambio and 'Manual' in car.cambio
            is_not_too_big = car.categoria not in ['SUV', 'Pickup', 'Van']
            
            # Preferir pequenos, econômicos e manuais
            if is_small and (is_economical or is_simple_transmission):
                suitable.append(car)
            elif is_not_too_big:
                less_suitable.append(car)
            # Carros grandes ficam de fora se houver opções menores
        
        # Se há carros adequados, usar só eles; senão, incluir menos adequados
        if suitable:
            return suitable + less_suitable
        return cars
    
    def recommend(
        self,
        profile: UserProfile,
        limit: int = 10,
        score_threshold: float = 0.2
    ) -> List[Dict]:
        """
        Gerar recomendações de TODAS as concessionárias
        🤖 AI Engineer (FASE 1): Filtros avançados aplicados
        
        Filtros eliminatórios (hard constraints):
        1. Orçamento (sempre aplicado)
        2. Ano mínimo (se especificado)
        3. Quilometragem máxima (se especificada)
        4. Must-haves / itens obrigatórios (se especificados)
        5. Raio geográfico em km (se especificado)
        
        Returns:
            Lista de dicionários com car, score, match_percentage, justificativa
        """
        # 1. Filtrar por orçamento (hard constraint)
        filtered_cars = self.filter_by_budget(self.all_cars, profile)
        
        print(f"[FILTRO] Após orçamento: {len(filtered_cars)} carros")
        
        # 2. 🤖 FASE 1: Filtrar por ano mínimo
        filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo)
        if profile.ano_minimo:
            print(f"[FILTRO] Após ano >= {profile.ano_minimo}: {len(filtered_cars)} carros")
        
        # 3. 🤖 FASE 1: Filtrar por quilometragem máxima
        filtered_cars = self.filter_by_km(filtered_cars, profile.km_maxima)
        if profile.km_maxima:
            print(f"[FILTRO] Após km <= {profile.km_maxima}: {len(filtered_cars)} carros")
        
        # 4. 📊 FASE 1: Filtrar por must-haves
        filtered_cars = self.filter_by_must_haves(filtered_cars, profile.must_haves)
        if profile.must_haves:
            print(f"[FILTRO] Após must-haves {profile.must_haves}: {len(filtered_cars)} carros")
        
        # 5. 💻 FASE 1: Filtrar por raio geográfico
        filtered_cars = self.filter_by_radius(filtered_cars, profile.city, profile.raio_maximo_km)
        if profile.raio_maximo_km:
            print(f"[FILTRO] Após raio {profile.raio_maximo_km}km: {len(filtered_cars)} carros")
        
        # 6. Filtro de contexto: família com crianças
        filtered_cars = self.filter_by_family_context(filtered_cars, profile)
        
        # 7. Filtro de contexto: primeiro carro
        filtered_cars = self.filter_by_first_car(filtered_cars, profile)
        
        if not filtered_cars:
            # Fallback: pegar os 5 carros mais próximos do orçamento (sem filtros avançados)
            print("[AVISO] Nenhum carro após filtros. Usando fallback.")
            all_sorted = sorted(
                self.all_cars,
                key=lambda c: abs(c.preco - profile.orcamento_max)
            )
            filtered_cars = all_sorted[:5]
        
        # 6. Priorizar por localização (se especificado)
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
        
        # 📊 FASE 3: Métricas avançadas
        if profile.prioridades.get("revenda", 0) >= 4 and car.indice_revenda > 0.8:
            reasons.append("Excelente revenda")
        
        if profile.prioridades.get("confiabilidade", 0) >= 4 and car.indice_confiabilidade > 0.8:
            reasons.append("Alta confiabilidade")
        
        if profile.prioridades.get("custo_manutencao", 0) >= 4 and car.custo_manutencao_anual and car.custo_manutencao_anual < 2500:
            reasons.append("Baixo custo de manutenção")
        
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

