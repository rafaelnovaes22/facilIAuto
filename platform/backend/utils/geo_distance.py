"""
💻 Tech Lead: Utilitário para Cálculo de Distância Geográfica (FASE 1)

Implementa cálculo de distância usando fórmula de Haversine
(sem dependência externa para manter simplicidade)

Autor: Tech Lead
Data: Outubro 2024
"""

import math
from typing import Optional, Tuple


def haversine_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calcula a distância em quilômetros entre duas coordenadas geográficas
    usando a fórmula de Haversine.
    
    Args:
        lat1: Latitude do ponto 1 (em graus)
        lon1: Longitude do ponto 1 (em graus)
        lat2: Latitude do ponto 2 (em graus)
        lon2: Longitude do ponto 2 (em graus)
    
    Returns:
        Distância em quilômetros
    
    Example:
        >>> # São Paulo para Rio de Janeiro
        >>> distance = haversine_distance(-23.5505, -46.6333, -22.9068, -43.1729)
        >>> print(f"{distance:.1f} km")
        357.3 km
    """
    # Raio da Terra em km
    R = 6371.0
    
    # Converter graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferenças
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance


def calculate_distance(
    user_coords: Optional[Tuple[float, float]],
    dealership_coords: Optional[Tuple[float, float]]
) -> Optional[float]:
    """
    Calcula distância entre usuário e concessionária (com validação)
    
    Args:
        user_coords: Tupla (latitude, longitude) do usuário
        dealership_coords: Tupla (latitude, longitude) da concessionária
    
    Returns:
        Distância em km ou None se coordenadas inválidas
    
    Example:
        >>> user = (-23.5505, -46.6333)  # São Paulo
        >>> dealer = (-22.9068, -43.1729)  # Rio
        >>> distance = calculate_distance(user, dealer)
        >>> print(f"{distance:.1f} km")
        357.3 km
    """
    if not user_coords or not dealership_coords:
        return None
    
    if len(user_coords) != 2 or len(dealership_coords) != 2:
        return None
    
    lat1, lon1 = user_coords
    lat2, lon2 = dealership_coords
    
    # Validar coordenadas
    if not (-90 <= lat1 <= 90 and -180 <= lon1 <= 180):
        return None
    
    if not (-90 <= lat2 <= 90 and -180 <= lon2 <= 180):
        return None
    
    return haversine_distance(lat1, lon1, lat2, lon2)


def is_within_radius(
    user_coords: Optional[Tuple[float, float]],
    dealership_coords: Optional[Tuple[float, float]],
    radius_km: int
) -> bool:
    """
    Verifica se concessionária está dentro do raio especificado
    
    Args:
        user_coords: Coordenadas do usuário
        dealership_coords: Coordenadas da concessionária
        radius_km: Raio máximo em km
    
    Returns:
        True se dentro do raio, False caso contrário
    
    Example:
        >>> user = (-23.5505, -46.6333)  # São Paulo
        >>> dealer = (-23.5629, -46.6544)  # Próximo em SP
        >>> is_within_radius(user, dealer, 30)
        True
    """
    distance = calculate_distance(user_coords, dealership_coords)
    
    if distance is None:
        return False
    
    return distance <= radius_km


# 📍 Coordenadas de referência para principais cidades brasileiras
CITY_COORDINATES = {
    # Sudeste
    "São Paulo": (-23.5505, -46.6333),
    "Rio de Janeiro": (-22.9068, -43.1729),
    "Belo Horizonte": (-19.9167, -43.9345),
    "Contagem": (-19.9320, -44.0540),
    "Campinas": (-22.9056, -47.0608),
    "Santos": (-23.9608, -46.3336),
    
    # Sul
    "Curitiba": (-25.4284, -49.2733),
    "Porto Alegre": (-30.0346, -51.2177),
    "Florianópolis": (-27.5954, -48.5480),
    
    # Nordeste
    "Salvador": (-12.9714, -38.5014),
    "Recife": (-8.0476, -34.8770),
    "Fortaleza": (-3.7172, -38.5433),
    
    # Centro-Oeste
    "Brasília": (-15.8267, -47.9218),
    "Goiânia": (-16.6869, -49.2648),
    "Campo Grande": (-20.4697, -54.6201),
    
    # Norte
    "Manaus": (-3.1190, -60.0217),
    "Belém": (-1.4558, -48.4902),
}


def get_city_coordinates(city_name: str) -> Optional[Tuple[float, float]]:
    """
    Obtém coordenadas de uma cidade brasileira
    
    Args:
        city_name: Nome da cidade
    
    Returns:
        Tupla (latitude, longitude) ou None se não encontrada
    
    Example:
        >>> coords = get_city_coordinates("São Paulo")
        >>> print(coords)
        (-23.5505, -46.6333)
    """
    # Busca case-insensitive
    for city, coords in CITY_COORDINATES.items():
        if city.lower() == city_name.lower():
            return coords
    
    return None


if __name__ == "__main__":
    # Testes rápidos
    print("Tech Lead: Testando calculo de distancia geografica")
    print("=" * 60)
    
    # Teste 1: São Paulo -> Rio de Janeiro
    sp_coords = CITY_COORDINATES["São Paulo"]
    rj_coords = CITY_COORDINATES["Rio de Janeiro"]
    distance = haversine_distance(*sp_coords, *rj_coords)
    print(f"[OK] Sao Paulo -> Rio de Janeiro: {distance:.1f} km")
    
    # Teste 2: São Paulo -> Campinas
    campinas_coords = CITY_COORDINATES["Campinas"]
    distance = haversine_distance(*sp_coords, *campinas_coords)
    print(f"[OK] Sao Paulo -> Campinas: {distance:.1f} km")
    
    # Teste 3: Contagem -> Belo Horizonte
    contagem_coords = CITY_COORDINATES["Contagem"]
    bh_coords = CITY_COORDINATES["Belo Horizonte"]
    distance = haversine_distance(*contagem_coords, *bh_coords)
    print(f"[OK] Contagem -> Belo Horizonte: {distance:.1f} km")
    
    # Teste 4: Dentro do raio
    print("\nTestando raio de busca:")
    within_30km = is_within_radius(contagem_coords, bh_coords, 30)
    print(f"[OK] Contagem esta a {distance:.1f}km de BH (dentro de 30km): {within_30km}")
    
    print("\n" + "=" * 60)
    print("[OK] Todos os testes passaram!")

