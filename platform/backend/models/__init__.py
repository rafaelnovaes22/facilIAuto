"""
Models package - Modelos de dados da plataforma FacilIAuto
"""

from .car import Car, CarFilter
from .dealership import Dealership, DealershipStats
from .user_profile import UserProfile
from .feedback import (
    FeedbackAction,
    UserFeedback,
    UserInteractionHistory,
    WeightAdjustment,
    RefinementRequest,
    RefinementResponse
)

__all__ = [
    'Car',
    'CarFilter',
    'Dealership',
    'DealershipStats',
    'UserProfile',
    'FeedbackAction',
    'UserFeedback',
    'UserInteractionHistory',
    'WeightAdjustment',
    'RefinementRequest',
    'RefinementResponse',
]

