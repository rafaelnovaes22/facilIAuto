"""
Utils package - Utilitários do backend FacilIAuto
"""

from .geo_distance import (
    haversine_distance,
    calculate_distance,
    is_within_radius,
    get_city_coordinates,
    CITY_COORDINATES
)

__all__ = [
    'haversine_distance',
    'calculate_distance',
    'is_within_radius',
    'get_city_coordinates',
    'CITY_COORDINATES',
]

