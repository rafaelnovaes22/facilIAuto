"""
Models package - Modelos de dados da plataforma FacilIAuto
"""

from .car import Car, CarFilter
from .dealership import Dealership, DealershipStats
from .user_profile import UserProfile

__all__ = [
    'Car',
    'CarFilter',
    'Dealership',
    'DealershipStats',
    'UserProfile',
]

