"""
Shim de import para compatibilidade de testes.

Permite que `from vehicle_image_scraper import RobustCarScraper` funcione
apontando para `scripts.vehicle_image_scraper`.
"""

from scripts.vehicle_image_scraper import *  # noqa: F401,F403


