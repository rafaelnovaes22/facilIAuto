"""
Data Transformer for normalizing and transforming scraped vehicle data.

This module provides the DataTransformer class that orchestrates data
normalization, transformation, and hash calculation for change detection.

Requirements: 1.4, 5.1
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from scraper.extractors import FieldExtractor


logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transform and normalize raw scraped data into standardized format.
    
    This class orchestrates the transformation pipeline:
    1. Normalize price, km, cambio, and other fields
    2. Calculate content hash for change detection
    3. Add metadata (timestamps, IDs)
    
    Requirements: 1.4, 5.1
    """
    
    def __init__(self, selector_config_path: str = "config/selectors.yaml"):
        """
        Initialize DataTransformer with field extractor.
        
        Args:
            selector_config_path: Path to selectors configuration file
        """
        self.extractor = FieldExtractor(selector_config_path)
        logger.info("DataTransformer initialized")
    
    def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw data into normalized format.
        
        This is the main entry point that orchestrates all transformations:
        - Normalizes all fields using FieldExtractor
        - Adds metadata (timestamps)
        - Calculates content hash
        
        Args:
            raw_data: Dictionary with raw extracted data
            
        Returns:
            Dictionary with normalized and transformed data
            
        Requirements: 1.4, 5.1
        """
        logger.debug(f"Transforming raw data with {len(raw_data)} fields")
        
        # Step 1: Extract and normalize all fields
        normalized = self.extractor.extract_and_normalize(raw_data)
        
        # Step 2: Add timestamp if not present
        if 'data_scraping' not in normalized:
            normalized['data_scraping'] = datetime.now()
        
        # Step 3: Calculate content hash for change detection
        if 'id' in raw_data:
            normalized['id'] = raw_data['id']
        
        # Calculate hash (excluding metadata fields)
        normalized['content_hash'] = self.calculate_hash(normalized)
        
        logger.debug(f"Transformation complete: {len(normalized)} fields")
        return normalized
    
    def normalize_price(self, price_str: str) -> Optional[float]:
        """
        Normalize price from various formats to float.
        
        Handles Brazilian currency formats:
        - R$ 95.990,00 -> 95990.0
        - 95990 -> 95990.0
        - R$ 95.990 -> 95990.0
        
        Args:
            price_str: Price string in various formats
            
        Returns:
            Normalized price as float or None if invalid
            
        Requirements: 1.4
        """
        return self.extractor.extract_price(price_str)
    
    def normalize_km(self, km_str: str) -> Optional[int]:
        """
        Normalize mileage from various formats to integer.
        
        Handles various km formats:
        - 50.000 km -> 50000
        - 50000 -> 50000
        - 50.000 quilômetros -> 50000
        
        Args:
            km_str: Mileage string in various formats
            
        Returns:
            Normalized mileage as integer or None if invalid
            
        Requirements: 1.4
        """
        return self.extractor.extract_km(km_str)
    
    def normalize_cambio(self, cambio_str: str) -> Optional[str]:
        """
        Normalize transmission type to standard values.
        
        Maps various transmission descriptions to standard values:
        - Manual
        - Automático
        - Automático CVT
        - Automatizada
        
        Args:
            cambio_str: Transmission description
            
        Returns:
            Normalized transmission type or None if invalid
            
        Requirements: 1.4
        """
        return self.extractor.normalize_cambio(cambio_str)
    
    def calculate_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate MD5 hash of vehicle content for change detection.
        
        The hash is calculated from all vehicle data EXCEPT:
        - id (identifier, not content)
        - data_scraping (timestamp, changes every scrape)
        - content_hash (would be circular)
        
        This allows detecting when vehicle data has actually changed
        vs just being re-scraped.
        
        Args:
            data: Vehicle data dictionary
            
        Returns:
            32-character MD5 hash string
            
        Requirements: 5.1
        """
        # Exclude metadata fields from hash calculation
        hashable_data = {
            k: v for k, v in data.items()
            if k not in ['id', 'data_scraping', 'content_hash']
        }
        
        # Convert datetime objects to ISO format strings for consistent hashing
        for key, value in hashable_data.items():
            if isinstance(value, datetime):
                hashable_data[key] = value.isoformat()
        
        # Sort keys for consistent hashing
        content_str = json.dumps(hashable_data, sort_keys=True, ensure_ascii=False)
        
        # Calculate MD5 hash
        hash_value = hashlib.md5(content_str.encode('utf-8')).hexdigest()
        
        logger.debug(f"Calculated content hash: {hash_value}")
        return hash_value
    
    def normalize_year(self, year_str: str) -> Optional[int]:
        """
        Extract and normalize year from text.
        
        Handles formats like:
        - 2022/2023 -> 2023 (model year)
        - 2022 -> 2022
        - Ano: 2022 -> 2022
        
        Args:
            year_str: Year string in various formats
            
        Returns:
            Normalized year as integer or None if invalid
        """
        return self.extractor.extract_year(year_str)
    
    def normalize_combustivel(self, combustivel_str: str) -> Optional[str]:
        """
        Normalize fuel type to standard values.
        
        Maps various fuel descriptions to standard values:
        - Flex
        - Gasolina
        - Diesel
        - Elétrico
        - Híbrido
        
        Args:
            combustivel_str: Fuel type description
            
        Returns:
            Normalized fuel type or None if invalid
        """
        return self.extractor.normalize_combustivel(combustivel_str)
    
    def normalize_categoria(self, categoria_str: str) -> Optional[str]:
        """
        Normalize vehicle category to standard values.
        
        Maps various category descriptions to standard values:
        - Hatch
        - Sedan
        - SUV
        - Pickup
        - Compacto
        - Van
        
        Args:
            categoria_str: Category description
            
        Returns:
            Normalized category or None if invalid
        """
        return self.extractor.normalize_categoria(categoria_str)
    
    def validate_and_transform(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform and validate data in one step.
        
        This method combines transformation with basic validation,
        returning None if critical fields are missing or invalid.
        
        Args:
            raw_data: Dictionary with raw extracted data
            
        Returns:
            Transformed data dictionary or None if validation fails
        """
        try:
            # Transform data
            transformed = self.transform(raw_data)
            
            # Validate critical fields
            required_fields = ['nome', 'preco', 'ano', 'quilometragem']
            missing_fields = [f for f in required_fields if f not in transformed]
            
            if missing_fields:
                logger.warning(f"Missing required fields: {missing_fields}")
                return None
            
            # Validate price range
            if not (10000 <= transformed['preco'] <= 500000):
                logger.warning(f"Price out of range: {transformed['preco']}")
                return None
            
            # Validate year range
            if not (2010 <= transformed['ano'] <= 2026):
                logger.warning(f"Year out of range: {transformed['ano']}")
                return None
            
            # Validate km range
            if not (0 <= transformed['quilometragem'] <= 500000):
                logger.warning(f"KM out of range: {transformed['quilometragem']}")
                return None
            
            return transformed
        
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return None
