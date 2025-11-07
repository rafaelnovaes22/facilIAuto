"""
Sistema de Recomendação Unificado - Agrega carros de TODAS as concessionárias
🤖 AI Engineer: FASE 1 - Filtros avançados implementados
"""

import json
import os
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile, TCOBreakdown
from models.dealership import Dealership
from utils.geo_distance import calculate_distance, get_city_coordinates
from services.car_metrics import CarMetricsCalculator
from services.app_transport_validator import validator as app_transport_validator
from services.commercial_vehicle_validator import validator as commercial_vehicle_validator
from services.tco_calculator import TCOCalculator
from services.fuel_price_service import fuel_price_service


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
                
                # ⚠️ VALIDAÇÃO: Ignorar carros com preço zero ou inválido
                preco = car_dict.get('preco', 0)
                if preco <= 0:
                    continue
                
                # ⚠️ VALIDAÇÃO: Ignorar motos (categoria Moto)
                categoria = car_dict.get('categoria', '')
                if categoria == 'Moto':
                    continue
                
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
        """
        Filtrar carros por orçamento
        
        REGRAS CRÍTICAS:
        - Preço deve ser > 0 (carros sem preço são ignorados)
        - Preço deve estar DENTRO da faixa especificada (inclusive)
        - Se nenhum carro atender, retorna lista vazia
        """
        filtered = [
            car for car in cars
            if car.preco > 0 and profile.orcamento_min <= car.preco <= profile.orcamento_max
        ]
        
        if not filtered:
            print(f"[AVISO] Nenhum carro encontrado na faixa R$ {profile.orcamento_min:,.2f} - R$ {profile.orcamento_max:,.2f}")
        
        return filtered
    
    def filter_by_year(self, cars: List[Car], ano_minimo: Optional[int], ano_maximo: Optional[int] = None) -> List[Car]:
        """
        🤖 AI Engineer (FASE 1): Filtrar por faixa de anos
        Elimina carros fora da faixa especificada
        """
        filtered = cars
        
        if ano_minimo:
            filtered = [car for car in filtered if car.ano >= ano_minimo]
        
        if ano_maximo:
            filtered = [car for car in filtered if car.ano <= ano_maximo]
        
        return filtered
    
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
    
    def filter_by_state(self, cars: List[Car], user_state: Optional[str]) -> List[Car]:
        """
        Filtrar carros por estado (hard constraint se especificado)
        
        Se o usuário especificar um estado, retorna APENAS carros daquele estado.
        Se não especificar, retorna todos os carros.
        
        Args:
            cars: Lista de carros
            user_state: Estado do usuário (ex: "SP", "RJ")
        
        Returns:
            Carros filtrados por estado (ou todos se não especificado)
        """
        if not user_state:
            # Usuário não especificou estado - retornar todos
            return cars
        
        # Filtrar apenas carros do estado especificado
        filtered = [
            car for car in cars 
            if car.dealership_state and car.dealership_state.upper() == user_state.upper()
        ]
        
        print(f"[FILTRO] Estado {user_state}: {len(filtered)} carros (de {len(cars)} totais)")
        
        return filtered
    
    def filter_by_city(self, cars: List[Car], user_city: Optional[str]) -> List[Car]:
        """
        Filtrar carros por cidade (hard constraint se especificado)
        
        Se o usuário especificar uma cidade, retorna APENAS carros daquela cidade.
        Se não especificar, retorna todos os carros.
        
        Args:
            cars: Lista de carros
            user_city: Cidade do usuário (ex: "São Paulo", "Rio de Janeiro")
        
        Returns:
            Carros filtrados por cidade (ou todos se não especificado)
        """
        if not user_city:
            # Usuário não especificou cidade - retornar todos
            return cars
        
        # Filtrar apenas carros da cidade especificada (case-insensitive)
        filtered = [
            car for car in cars 
            if car.dealership_city and car.dealership_city.lower() == user_city.lower()
        ]
        
        print(f"[FILTRO] Cidade {user_city}: {len(filtered)} carros (de {len(cars)} totais)")
        
        return filtered
    
    def prioritize_by_location(self, cars: List[Car], user_city: str, user_state: str) -> List[Car]:
        """Priorizar carros de concessionárias próximas (dentro do mesmo estado)"""
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
        
        # 5. 🚚 AJUSTE COMERCIAL: Penalizar veículos inadequados
        if profile.uso_principal == "comercial" and hasattr(car, 'commercial_suitability'):
            suitability = car.commercial_suitability
            # Multiplicar score pela adequação comercial
            final_score = final_score * suitability["score"]
            
            # Log de penalização
            if suitability["score"] < 1.0:
                print(f"[SCORE] {car.marca} {car.modelo}: {final_score:.2f} (penalizado por adequação comercial: {suitability['score']})")
        
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
                "Furgão": 0.95,   # Ideal - volume e proteção de carga
                "Van": 0.95,      # Ideal - volume
                "Pickup Pequena": 0.90,  # Muito bom - caçamba para carga
                "Utilitário": 0.85,  # Bom - versátil
                "Pickup": 0.30,   # Inadequado - geralmente são pickups médias/grandes de lazer
                "SUV": 0.20,      # Inadequado - não é comercial
                "Sedan": 0.15,    # Muito inadequado
                "Hatch": 0.10,    # Muito inadequado
                "Compacto": 0.10  # Muito inadequado
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
                "Sedan": 0.95,    # Ideal - UberX/99Pop/Comfort
                "SUV": 0.90,      # Muito bom - Uber Comfort/Black
                "Hatch": 0.70,    # Bom - UberX/99Pop (alguns modelos)
                "Compacto": 0.50, # Limitado - Apenas alguns aceitos
                "Van": 0.40,      # Inadequado para app (muito grande)
                "Pickup": 0.20    # Inadequado
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
    
    def filter_by_preferences(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """
        🔥 NOVO: Filtros de preferências agora são OBRIGATÓRIOS quando selecionados
        Elimina carros que não atendem às preferências especificadas
        """
        filtered = cars
        
        # Marcas preferidas: se especificadas, APENAS essas marcas
        if profile.marcas_preferidas:
            filtered = [car for car in filtered if car.marca in profile.marcas_preferidas]
            print(f"[FILTRO] Após marcas preferidas {profile.marcas_preferidas}: {len(filtered)} carros")
        
        # Marcas rejeitadas: ELIMINAR essas marcas
        if profile.marcas_rejeitadas:
            filtered = [car for car in filtered if car.marca not in profile.marcas_rejeitadas]
            print(f"[FILTRO] Após rejeitar marcas {profile.marcas_rejeitadas}: {len(filtered)} carros")
        
        # Tipos preferidos: se especificados, APENAS esses tipos
        if profile.tipos_preferidos:
            filtered = [car for car in filtered if car.categoria in profile.tipos_preferidos]
            print(f"[FILTRO] Após tipos preferidos {profile.tipos_preferidos}: {len(filtered)} carros")
        
        # Combustível preferido: se especificado, APENAS esse combustível
        if profile.combustivel_preferido:
            filtered = [car for car in filtered if car.combustivel == profile.combustivel_preferido]
            print(f"[FILTRO] Após combustível {profile.combustivel_preferido}: {len(filtered)} carros")
        
        # Câmbio preferido: se especificado, APENAS esse câmbio
        if profile.cambio_preferido:
            filtered = [car for car in filtered if car.cambio and profile.cambio_preferido in car.cambio]
            print(f"[FILTRO] Após câmbio {profile.cambio_preferido}: {len(filtered)} carros")
        
        return filtered
    
    def score_preferences(self, car: Car, profile: UserProfile) -> float:
        """
        Score baseado em preferências específicas
        ⚠️ NOTA: Este método agora é usado apenas para BONUS de score,
        pois os filtros obrigatórios já foram aplicados em filter_by_preferences()
        """
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
    
    def filter_by_app_transport(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """
        Filtro específico para transporte de passageiros (Uber, 99, etc)
        Valida se o carro atende aos requisitos das plataformas
        """
        # Se não é transporte de passageiros, não filtrar
        if profile.uso_principal != "transporte_passageiros":
            return cars
        
        # Categoria desejada (pode vir do perfil ou usar padrão)
        categoria_app = getattr(profile, 'categoria_app', 'uberx_99pop')
        
        valid_cars = []
        for car in cars:
            # Validar se o carro é aceito para transporte de app
            is_valid, reason = app_transport_validator.is_valid_for_app_transport(
                marca=car.marca,
                modelo=car.modelo,
                ano=car.ano,
                categoria_desejada=categoria_app
            )
            
            if is_valid:
                valid_cars.append(car)
            else:
                print(f"[FILTRO APP] {car.nome} ({car.ano}) rejeitado: {reason}")
        
        print(f"[FILTRO APP] {len(valid_cars)} de {len(cars)} carros válidos para {categoria_app}")
        
        # ⚠️ CRÍTICO: Não usar fallback! Se nenhum carro atende aos requisitos do Uber/99,
        # retornar lista vazia para que o usuário saiba que precisa ajustar critérios
        if not valid_cars:
            print(f"[AVISO] Nenhum carro atende aos requisitos do {categoria_app}")
        
        return valid_cars
    
    def filter_by_commercial_use(self, cars: List[Car], profile: UserProfile) -> List[Car]:
        """
        🚚 Filtro específico para uso comercial
        Classifica veículos por adequação ao uso comercial
        
        MODO: Semi-permissivo com avisos
        - Aceita: IDEAL, ADEQUADO, LIMITADO
        - Rejeita: INADEQUADO (pickups de lazer, SUVs, sedans)
        - Veículos limitados recebem avisos claros (ex: requer CNH C)
        
        Classificação:
        - IDEAL (score 1.0): Pickups pequenas, furgões, vans ✅
        - ADEQUADO (score 0.8-0.95): Versões específicas ✅
        - LIMITADO (score 0.3): VUCs/caminhões (requer CNH C) ⚠️
        - INADEQUADO (score 0.0-0.2): Pickups de lazer, SUVs ❌ REJEITADO
        """
        # Se não é uso comercial, não filtrar
        if profile.uso_principal != "comercial":
            return cars
        
        classified_cars = []
        rejected_cars = []
        
        for car in cars:
            # Obter adequação do veículo
            suitability = commercial_vehicle_validator.get_commercial_suitability(
                marca=car.marca,
                modelo=car.modelo,
                versao=getattr(car, 'versao', None),
                categoria=car.categoria
            )
            
            # Adicionar metadados de adequação ao carro
            car.commercial_suitability = suitability
            
            # Filtrar: aceitar apenas IDEAL, ADEQUADO e LIMITADO
            # Rejeitar: INADEQUADO
            if suitability["nivel"] in ["ideal", "adequado", "limitado"]:
                classified_cars.append(car)
                
                # Log de classificação
                if suitability["nivel"] == "ideal":
                    print(f"[COMERCIAL] ✅ {car.marca} {car.modelo} - {suitability['tipo']} (score: {suitability['score']})")
                elif suitability["nivel"] == "adequado":
                    print(f"[COMERCIAL] ✓ {car.marca} {car.modelo} - {suitability['tipo']} (score: {suitability['score']})")
                elif suitability["nivel"] == "limitado":
                    print(f"[COMERCIAL] ⚠️ {car.marca} {car.modelo} - {suitability['tipo']} (score: {suitability['score']}) - {suitability['avisos'][0]}")
            else:
                rejected_cars.append(car)
                print(f"[COMERCIAL] ❌ {car.marca} {car.modelo} - {suitability['tipo']} (score: {suitability['score']}) - REJEITADO (inadequado)")
        
        # Ordenar por adequação (ideais primeiro)
        classified_cars.sort(key=lambda c: c.commercial_suitability["score"], reverse=True)
        
        ideal_count = len([c for c in classified_cars if c.commercial_suitability["nivel"] == "ideal"])
        adequate_count = len([c for c in classified_cars if c.commercial_suitability["nivel"] == "adequado"])
        limited_count = len([c for c in classified_cars if c.commercial_suitability["nivel"] == "limitado"])
        
        print(f"[COMERCIAL] Resultado: {ideal_count} ideais, {adequate_count} adequados, {limited_count} limitados")
        
        return classified_cars
    
    def _estimate_fuel_efficiency_by_category(self, category: str) -> float:
        """
        Estima consumo de combustível baseado na categoria do veículo
        Valores baseados em médias de mercado (km/L - gasolina/flex)
        
        Args:
            category: Categoria do veículo
            
        Returns:
            Consumo estimado em km/L
        """
        efficiency_by_category = {
            "Hatch": 13.5,           # Compactos econômicos
            "Sedan Compacto": 13.0,  # Sedans pequenos
            "Sedan": 11.5,           # Sedans médios
            "SUV Compacto": 11.0,    # SUVs compactos
            "SUV": 9.5,              # SUVs médios/grandes
            "Pickup": 9.0,           # Pickups
            "Van": 8.5,              # Vans
            "Furgão": 9.0,           # Furgões
            "Crossover": 11.5,       # Crossovers
            "Minivan": 10.0          # Minivans
        }
        
        return efficiency_by_category.get(category, 11.0)  # Default: 11 km/L
    
    def calculate_tco_for_car(
        self,
        car: Car,
        profile: UserProfile
    ) -> Optional[TCOBreakdown]:
        """
        Calcula TCO (Total Cost of Ownership) para um carro específico
        
        Args:
            car: Carro para calcular TCO
            profile: Perfil do usuário (para obter estado, km mensal, etc)
            
        Returns:
            TCOBreakdown com detalhamento de custos ou None se não for possível calcular
        """
        try:
            # Obter consumo do carro (km/L)
            # Prioridade: consumo_cidade > consumo_estrada > consumo > estimativa por categoria
            fuel_efficiency = (
                getattr(car, 'consumo_cidade', None) or 
                getattr(car, 'consumo_estrada', None) or 
                getattr(car, 'consumo', None) or
                self._estimate_fuel_efficiency_by_category(car.categoria)
            )
            
            # Calcular idade do carro
            current_year = datetime.now().year
            car_age = current_year - car.ano
            
            # Obter quilometragem do carro (com fallback para 0 se não disponível)
            car_mileage = getattr(car, 'quilometragem', 0) or 0
            
            # Obter preço atualizado do combustível
            # Busca de: variável de ambiente > cache > API > padrão
            fuel_price = fuel_price_service.get_current_price(state=profile.state or "SP")
            
            # Criar calculadora de TCO com parâmetros do usuário
            calculator = TCOCalculator(
                down_payment_percent=0.20,
                financing_months=60,
                annual_interest_rate=0.24,  # 24% a.a. (2% a.m.) - média mercado 2025
                monthly_km=1000,  # Padrão, pode ser ajustado baseado no perfil
                fuel_price_per_liter=fuel_price,
                state=profile.state or "SP",
                user_profile="standard"
            )
            
            # Calcular TCO com quilometragem para ajuste de manutenção
            tco = calculator.calculate_tco(
                car_price=car.preco,
                car_category=car.categoria,
                fuel_efficiency_km_per_liter=fuel_efficiency,
                car_age=car_age,
                car_mileage=car_mileage  # Passar quilometragem para ajuste
            )
            
            return tco
        
        except Exception as e:
            print(f"[ERRO] Falha ao calcular TCO para {car.nome}: {e}")
            return None
    
    def assess_financial_health(
        self,
        tco: TCOBreakdown,
        profile: UserProfile
    ) -> Optional[Dict[str, Any]]:
        """
        Avalia saúde financeira baseado em TCO vs renda
        
        Args:
            tco: Breakdown de TCO do veículo
            profile: Perfil do usuário com financial_capacity
            
        Returns:
            Dicionário com status, percentage, color, message ou None se não disponível
            
        Regras:
        - Verde (≤20%): Saudável
        - Amarelo (20-30%): Atenção
        - Vermelho (>30%): Alto comprometimento
        """
        # Se não há capacidade financeira informada, não avaliar
        if not profile.financial_capacity or not profile.financial_capacity.is_disclosed:
            return None
        
        # Obter faixa de renda
        income_range = profile.financial_capacity.monthly_income_range
        if not income_range:
            return None
        
        # Calcular renda média da faixa
        income_brackets = {
            "0-3000": (0, 3000),
            "3000-5000": (3000, 5000),
            "5000-8000": (5000, 8000),
            "8000-12000": (8000, 12000),
            "12000+": (12000, 16000)
        }
        
        if income_range not in income_brackets:
            return None
        
        min_income, max_income = income_brackets[income_range]
        avg_income = (min_income + max_income) / 2
        
        # Calcular percentual do TCO em relação à renda
        percentage = (tco.total_monthly / avg_income) * 100
        
        # Determinar status baseado no percentual
        if percentage <= 20:
            status = "healthy"
            color = "green"
            message = "Saudável"
        elif percentage <= 30:
            status = "caution"
            color = "yellow"
            message = "Atenção"
        else:
            status = "high_commitment"
            color = "red"
            message = "Alto comprometimento"
        
        return {
            "status": status,
            "percentage": round(percentage, 1),
            "color": color,
            "message": message
        }
    
    def validate_budget_status(
        self,
        tco: TCOBreakdown,
        profile: UserProfile
    ) -> Tuple[Optional[bool], str]:
        """
        Valida se o veículo cabe no orçamento do usuário
        
        Args:
            tco: Breakdown de TCO do veículo
            profile: Perfil do usuário com financial_capacity
            
        Returns:
            Tupla com (fits_budget: bool ou None, status_message: str)
            
        Regras:
        - Compara tco.total_monthly com profile.financial_capacity.max_monthly_tco
        - Retorna True se TCO <= max_monthly_tco
        - Retorna False se TCO > max_monthly_tco
        - Retorna None se não há dados de capacidade financeira
        """
        # Se não há capacidade financeira informada, retornar None
        if not profile.financial_capacity or not profile.financial_capacity.is_disclosed:
            return (None, "Orçamento não informado")
        
        max_tco = profile.financial_capacity.max_monthly_tco
        if not max_tco:
            return (None, "Orçamento não informado")
        
        # Comparar TCO total mensal com orçamento máximo
        fits = tco.total_monthly <= max_tco
        
        if fits:
            return (True, "Dentro do orçamento")
        else:
            return (False, "Acima do orçamento")
    
    def filter_by_financial_capacity(
        self,
        cars_with_tco: List[Tuple[Car, Optional[TCOBreakdown]]],
        profile: UserProfile
    ) -> List[Tuple[Car, Optional[TCOBreakdown]]]:
        """
        Filtra carros por capacidade financeira do usuário
        
        Args:
            cars_with_tco: Lista de tuplas (car, tco_breakdown)
            profile: Perfil do usuário com financial_capacity
            
        Returns:
            Lista filtrada de carros que cabem no orçamento (com 10% de tolerância)
        """
        # Se usuário não informou capacidade financeira, não filtrar
        if not profile.financial_capacity or not profile.financial_capacity.is_disclosed:
            return cars_with_tco
        
        max_tco = profile.financial_capacity.max_monthly_tco
        if not max_tco:
            return cars_with_tco
        
        # Filtrar carros com TCO dentro do orçamento (10% de tolerância)
        tolerance = 1.10
        filtered = [
            (car, tco) for car, tco in cars_with_tco
            if tco and tco.total_monthly <= max_tco * tolerance
        ]
        
        print(f"[FILTRO TCO] {len(filtered)} de {len(cars_with_tco)} carros cabem no orçamento (max: R$ {max_tco:.2f}/mês)")
        
        return filtered
    
    def apply_financial_bonus(
        self,
        base_score: float,
        tco: Optional[TCOBreakdown],
        profile: UserProfile
    ) -> float:
        """
        Aplica bonus de score para carros que cabem bem no orçamento
        
        Args:
            base_score: Score base do carro
            tco: Breakdown de TCO
            profile: Perfil do usuário com financial_capacity
            
        Returns:
            Score ajustado com bonus financeiro
        """
        # Se não há TCO ou capacidade financeira, retornar score base
        if not tco or not profile.financial_capacity or not profile.financial_capacity.is_disclosed:
            return base_score
        
        max_tco = profile.financial_capacity.max_monthly_tco
        if not max_tco:
            return base_score
        
        actual_tco = tco.total_monthly
        
        # Calcular % do orçamento usado
        budget_usage = actual_tco / max_tco
        
        # Bonus para carros que usam 70-90% do orçamento (sweet spot)
        if 0.70 <= budget_usage <= 0.90:
            bonus = 0.05  # +5% no score
        elif 0.50 <= budget_usage < 0.70:
            bonus = 0.03  # +3% no score (mais econômico)
        elif 0.90 < budget_usage <= 1.0:
            bonus = 0.02  # +2% no score (no limite)
        elif budget_usage > 1.0:
            bonus = -0.10  # -10% no score (acima do orçamento)
        else:
            bonus = 0.01  # +1% no score (muito abaixo)
        
        adjusted_score = min(1.0, base_score + bonus)
        
        return adjusted_score
    
    def recommend(
        self,
        profile: UserProfile,
        limit: int = 10,
        score_threshold: float = 0.2
    ) -> List[Dict]:
        """
        Gerar recomendações de TODAS as concessionárias
        🤖 AI Engineer (FASE 1): Filtros avançados aplicados
        
        🔥 REGRA CRÍTICA: Todo filtro opcional, quando selecionado, torna-se OBRIGATÓRIO
        
        Filtros eliminatórios (hard constraints):
        1. Orçamento (sempre aplicado)
        2. Ano mínimo/máximo (se especificado)
        3. Quilometragem máxima (se especificada)
        4. Must-haves / itens obrigatórios (se especificados)
        5. Raio geográfico em km (se especificado)
        6. Marcas preferidas (se especificadas - APENAS essas marcas)
        7. Marcas rejeitadas (se especificadas - ELIMINA essas marcas)
        8. Tipos preferidos (se especificados - APENAS esses tipos)
        9. Combustível preferido (se especificado - APENAS esse combustível)
        10. Câmbio preferido (se especificado - APENAS esse câmbio)
        
        Returns:
            Lista de dicionários com car, score, match_percentage, justificativa
        """
        # 1. Filtrar por orçamento (hard constraint)
        filtered_cars = self.filter_by_budget(self.all_cars, profile)
        
        print(f"[FILTRO] Após orçamento: {len(filtered_cars)} carros")
        
        # 2. 🤖 FASE 1: Filtrar por faixa de anos
        filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo, profile.ano_maximo)
        if profile.ano_minimo and profile.ano_maximo:
            print(f"[FILTRO] Após ano {profile.ano_minimo}-{profile.ano_maximo}: {len(filtered_cars)} carros")
            # 🐛 DEBUG: Verificar se há carros fora da faixa
            anos_invalidos = [c for c in filtered_cars if c.ano < profile.ano_minimo or c.ano > profile.ano_maximo]
            if anos_invalidos:
                print(f"[BUG] ❌ {len(anos_invalidos)} carros FORA da faixa após filtro!")
                for car in anos_invalidos[:3]:
                    print(f"  - {car.nome} ({car.ano})")
        elif profile.ano_minimo:
            print(f"[FILTRO] Após ano >= {profile.ano_minimo}: {len(filtered_cars)} carros")
        elif profile.ano_maximo:
            print(f"[FILTRO] Após ano <= {profile.ano_maximo}: {len(filtered_cars)} carros")
        
        # 3. 🤖 FASE 1: Filtrar por quilometragem máxima
        filtered_cars = self.filter_by_km(filtered_cars, profile.km_maxima)
        if profile.km_maxima:
            print(f"[FILTRO] Após km <= {profile.km_maxima}: {len(filtered_cars)} carros")
        
        # 4. 📊 FASE 1: Filtrar por must-haves
        filtered_cars = self.filter_by_must_haves(filtered_cars, profile.must_haves)
        if profile.must_haves:
            print(f"[FILTRO] Após must-haves {profile.must_haves}: {len(filtered_cars)} carros")
        
        # 4.5. 📍 Filtrar por estado (se especificado)
        filtered_cars = self.filter_by_state(filtered_cars, profile.state)
        
        # 4.6. 📍 Filtrar por cidade (se especificado)
        filtered_cars = self.filter_by_city(filtered_cars, profile.city)
        
        # 5. 💻 FASE 1: Filtrar por raio geográfico
        filtered_cars = self.filter_by_radius(filtered_cars, profile.city, profile.raio_maximo_km)
        if profile.raio_maximo_km:
            print(f"[FILTRO] Após raio {profile.raio_maximo_km}km: {len(filtered_cars)} carros")
        
        # 6. 🔥 NOVO: Filtrar por preferências (marcas, tipos, combustível, câmbio)
        filtered_cars = self.filter_by_preferences(filtered_cars, profile)
        
        # 7. Filtro de contexto: família com crianças
        filtered_cars = self.filter_by_family_context(filtered_cars, profile)
        
        # 8. Filtro de contexto: primeiro carro
        filtered_cars = self.filter_by_first_car(filtered_cars, profile)
        
        # 9. 🚕 Filtro de contexto: transporte de passageiros (Uber, 99)
        filtered_cars = self.filter_by_app_transport(filtered_cars, profile)
        
        # 10. 🚚 Filtro de contexto: uso comercial (pickups pequenas e furgões)
        filtered_cars = self.filter_by_commercial_use(filtered_cars, profile)
        
        if not filtered_cars:
            # ⚠️ CRÍTICO: Não usar fallback que ignora orçamento!
            # Se nenhum carro atende aos filtros, retornar lista vazia
            # O frontend deve mostrar mensagem apropriada
            print("[AVISO] Nenhum carro após filtros. Retornando lista vazia.")
            return []
        
        # 11. 💰 Calcular TCO para cada carro (Requirement 6.2)
        cars_with_tco = []
        for car in filtered_cars:
            tco = self.calculate_tco_for_car(car, profile)
            cars_with_tco.append((car, tco))
        
        # 12. 💰 Filtrar por capacidade financeira (Requirement 6.3)
        cars_with_tco = self.filter_by_financial_capacity(cars_with_tco, profile)
        
        if not cars_with_tco:
            print("[AVISO] Nenhum carro após filtro de capacidade financeira. Retornando lista vazia.")
            return []
        
        # 13. Priorizar por localização (se especificado)
        if profile.city and profile.priorizar_proximas:
            # Extrair apenas os carros para priorização
            cars_only = [car for car, tco in cars_with_tco]
            prioritized_cars = self.prioritize_by_location(
                cars_only,
                profile.city,
                profile.state or ""
            )
            # Reconstruir lista com TCO mantendo a ordem
            car_to_tco = {car.id: tco for car, tco in cars_with_tco}
            cars_with_tco = [(car, car_to_tco[car.id]) for car in prioritized_cars]
        
        # 14. Calcular scores com bonus financeiro
        scored_cars = []
        for car, tco in cars_with_tco:
            if not car.disponivel:
                continue
            
            # Score base
            base_score = self.calculate_match_score(car, profile)
            
            # Aplicar bonus financeiro (Requirement 6.3)
            final_score = self.apply_financial_bonus(base_score, tco, profile)
            
            if final_score >= score_threshold:
                # Validar status do orçamento usando novo método
                fits_budget = None
                budget_status_message = "Orçamento não informado"
                
                if tco:
                    fits_budget, budget_status_message = self.validate_budget_status(tco, profile)
                
                # Calcular percentual da renda (para compatibilidade)
                budget_percentage = None
                if tco and profile.financial_capacity and profile.financial_capacity.is_disclosed:
                    income_range = profile.financial_capacity.monthly_income_range
                    if income_range:
                        # Calcular renda média
                        income_brackets = {
                            "0-3000": (0, 3000),
                            "3000-5000": (3000, 5000),
                            "5000-8000": (5000, 8000),
                            "8000-12000": (8000, 12000),
                            "12000+": (12000, 16000)
                        }
                        if income_range in income_brackets:
                            min_income, max_income = income_brackets[income_range]
                            avg_income = (min_income + max_income) / 2
                            budget_percentage = (tco.total_monthly / avg_income) * 100
                
                # Avaliar saúde financeira
                financial_health = None
                if tco:
                    financial_health = self.assess_financial_health(tco, profile)
                
                scored_cars.append({
                    'car': car,
                    'score': final_score,
                    'match_percentage': int(final_score * 100),
                    'justificativa': self.generate_justification(car, profile, final_score),
                    'tco_breakdown': tco,  # Requirement 6.4
                    'fits_budget': fits_budget,
                    'budget_percentage': budget_percentage,
                    'financial_health': financial_health  # NEW: Financial health indicator
                })
        
        # 15. Ordenar por score
        scored_cars.sort(key=lambda x: x['score'], reverse=True)
        
        # 🐛 DEBUG: Verificar anos antes de retornar
        if profile.ano_minimo or profile.ano_maximo:
            print(f"\n[DEBUG] Verificando anos antes de retornar {len(scored_cars)} carros:")
            for rec in scored_cars[:limit]:
                car = rec['car']
                status = "✅" if (not profile.ano_minimo or car.ano >= profile.ano_minimo) and (not profile.ano_maximo or car.ano <= profile.ano_maximo) else "❌"
                print(f"  {status} {car.nome} ({car.ano}) - Score: {rec['score']:.2f}")
        
        # 5. Retornar top N
        return scored_cars[:limit]
    
    def generate_justification(self, car: Car, profile: UserProfile, score: float) -> str:
        """Gerar justificativa para a recomendação"""
        reasons = []
        warnings = []
        
        # 🚚 AVISOS COMERCIAIS (se aplicável)
        if profile.uso_principal == "comercial" and hasattr(car, 'commercial_suitability'):
            suitability = car.commercial_suitability
            
            if suitability["nivel"] == "ideal":
                reasons.append(f"✅ Veículo comercial ideal ({suitability['tipo'].replace('_', ' ')})")
            elif suitability["nivel"] == "limitado":
                warnings.extend(suitability["avisos"])
            elif suitability["nivel"] == "inadequado":
                warnings.extend(suitability["avisos"])
        
        # Categoria apropriada
        if self.score_category_by_usage(car, profile) > 0.7:
            reasons.append(f"Categoria {car.categoria} ideal para {profile.uso_principal}")
        
        # Prioridades atendidas
        # Economia: verificar consumo REAL, não apenas score relativo
        if profile.prioridades.get("economia", 0) >= 4 and car.score_economia > 0.7:
            # Obter consumo real do carro (mesma lógica do TCO)
            consumo_estimado = (
                getattr(car, 'consumo_cidade', None) or 
                getattr(car, 'consumo_estrada', None) or 
                getattr(car, 'consumo', None) or
                self._estimate_fuel_efficiency_by_category(car.categoria)
            )
            
            # Só mencionar "excelente economia" se consumo for realmente bom (>= 12 km/L)
            if consumo_estimado >= 12:
                reasons.append("Excelente economia de combustível")
            elif consumo_estimado >= 10:
                reasons.append("Boa economia de combustível para a categoria")
            # Se consumo < 10 km/L, não mencionar economia (mesmo que score seja alto)
        
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
        
        # Montar justificativa
        justification = ". ".join(reasons) + "."
        
        # Adicionar avisos se houver
        if warnings:
            justification += " | AVISOS: " + " | ".join(warnings)
        
        return justification
    
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

