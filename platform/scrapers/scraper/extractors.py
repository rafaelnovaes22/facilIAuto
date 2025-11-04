"""
Specific field extractors with normalization and validation.

This module provides specialized extraction functions for different
vehicle fields with regex patterns, normalization, and validation.

Requirements: 1.1, 1.4, 9.1, 9.2
"""

import re
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


class FieldExtractor:
    """
    Specialized field extractors with normalization.
    
    Requirements: 1.1, 1.4, 9.1, 9.2
    """
    
    def __init__(self, selector_config_path: str = "config/selectors.yaml"):
        """
        Initialize field extractor with configuration.
        
        Args:
            selector_config_path: Path to selectors YAML file
        """
        self.selector_config_path = selector_config_path
        self.config = self._load_config()
        
        # Compile regex patterns for performance
        self.price_patterns = [
            re.compile(pattern) for pattern in 
            self.config.get('patterns', {}).get('price', [])
        ]
        self.km_patterns = [
            re.compile(pattern) for pattern in 
            self.config.get('patterns', {}).get('km', [])
        ]
        self.year_patterns = [
            re.compile(pattern) for pattern in 
            self.config.get('patterns', {}).get('year', [])
        ]
        self.doors_patterns = [
            re.compile(pattern) for pattern in 
            self.config.get('patterns', {}).get('doors', [])
        ]
        
        logger.info("FieldExtractor initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(self.selector_config_path)
        
        if not config_path.exists():
            logger.warning(f"Config not found: {config_path}, using defaults")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def extract_price(self, text: str) -> Optional[float]:
        """
        Extract and normalize price from text.
        
        Handles formats like:
        - R$ 95.990,00
        - 95990
        - R$ 95.990
        - 95.990,00 reais
        
        Args:
            text: Text containing price
            
        Returns:
            Price as float or None
            
        Requirements: 1.1, 1.4, 9.1, 9.2
        """
        if not text:
            return None
        
        # Try each regex pattern
        for pattern in self.price_patterns:
            match = pattern.search(text)
            if match:
                # Get the numeric part
                price_str = match.group(1)
                
                try:
                    # Normalize Brazilian format: 95.990,00 -> 95990.00
                    # Remove thousand separators (.)
                    price_str = price_str.replace('.', '')
                    # Replace decimal separator (,) with (.)
                    price_str = price_str.replace(',', '.')
                    
                    price = float(price_str)
                    
                    # Validate range
                    if 10000 <= price <= 500000:
                        logger.debug(f"Extracted price: {price} from '{text}'")
                        return price
                    else:
                        logger.warning(f"Price out of range: {price}")
                
                except ValueError as e:
                    logger.debug(f"Failed to parse price '{price_str}': {e}")
                    continue
        
        # Fallback: try to extract any number
        numbers = re.findall(r'[\d.,]+', text)
        for num_str in numbers:
            try:
                # Clean and convert
                num_str = num_str.replace('.', '').replace(',', '.')
                price = float(num_str)
                
                if 10000 <= price <= 500000:
                    logger.debug(f"Extracted price (fallback): {price} from '{text}'")
                    return price
            except ValueError:
                continue
        
        logger.warning(f"Could not extract price from: '{text}'")
        return None
    
    def extract_km(self, text: str) -> Optional[int]:
        """
        Extract and normalize mileage from text.
        
        Handles formats like:
        - 50.000 km
        - 50000
        - 50.000 quilômetros
        - KM: 50.000
        
        Args:
            text: Text containing mileage
            
        Returns:
            Mileage as integer or None
            
        Requirements: 1.1, 1.4, 9.1, 9.2
        """
        if not text:
            return None
        
        # Try each regex pattern
        for pattern in self.km_patterns:
            match = pattern.search(text)
            if match:
                # Get the numeric part
                km_str = match.group(1)
                
                try:
                    # Remove separators
                    km_str = km_str.replace('.', '').replace(',', '')
                    km = int(km_str)
                    
                    # Validate range
                    if 0 <= km <= 500000:
                        logger.debug(f"Extracted km: {km} from '{text}'")
                        return km
                    else:
                        logger.warning(f"KM out of range: {km}")
                
                except ValueError as e:
                    logger.debug(f"Failed to parse km '{km_str}': {e}")
                    continue
        
        # Fallback: try to extract any number
        numbers = re.findall(r'[\d.,]+', text)
        for num_str in numbers:
            try:
                # Clean and convert
                num_str = num_str.replace('.', '').replace(',', '')
                km = int(num_str)
                
                if 0 <= km <= 500000:
                    logger.debug(f"Extracted km (fallback): {km} from '{text}'")
                    return km
            except ValueError:
                continue
        
        logger.warning(f"Could not extract km from: '{text}'")
        return None
    
    def extract_year(self, text: str) -> Optional[int]:
        """
        Extract year from text.
        
        Handles formats like:
        - 2022/2023 (returns 2023, the model year)
        - 2022
        - Ano: 2022
        
        Args:
            text: Text containing year
            
        Returns:
            Year as integer or None
        """
        if not text:
            return None
        
        # Try each regex pattern
        for pattern in self.year_patterns:
            match = pattern.search(text)
            if match:
                try:
                    # If format is YYYY/YYYY, take the second year (model year)
                    if len(match.groups()) == 2:
                        year = int(match.group(2))
                    else:
                        year = int(match.group(1))
                    
                    # Validate range
                    if 2010 <= year <= 2026:
                        logger.debug(f"Extracted year: {year} from '{text}'")
                        return year
                    else:
                        logger.warning(f"Year out of range: {year}")
                
                except ValueError as e:
                    logger.debug(f"Failed to parse year: {e}")
                    continue
        
        logger.warning(f"Could not extract year from: '{text}'")
        return None
    
    def extract_doors(self, text: str) -> Optional[int]:
        """
        Extract number of doors from text.
        
        Args:
            text: Text containing door count
            
        Returns:
            Number of doors or None
        """
        if not text:
            return None
        
        # Try each regex pattern
        for pattern in self.doors_patterns:
            match = pattern.search(text)
            if match:
                try:
                    doors = int(match.group(1))
                    
                    # Validate range
                    if 2 <= doors <= 5:
                        logger.debug(f"Extracted doors: {doors} from '{text}'")
                        return doors
                    else:
                        logger.warning(f"Doors out of range: {doors}")
                
                except ValueError as e:
                    logger.debug(f"Failed to parse doors: {e}")
                    continue
        
        # Fallback: look for single digit
        match = re.search(r'\b([2-5])\b', text)
        if match:
            doors = int(match.group(1))
            logger.debug(f"Extracted doors (fallback): {doors} from '{text}'")
            return doors
        
        logger.debug(f"Could not extract doors from: '{text}'")
        return None
    
    def normalize_cambio(self, text: str) -> Optional[str]:
        """
        Normalize transmission type.
        
        Maps various transmission descriptions to standard values:
        - Manual
        - Automático
        - Automático CVT
        - Automatizada
        
        Args:
            text: Text containing transmission type
            
        Returns:
            Normalized transmission type or None
            
        Requirements: 1.1, 1.4
        """
        if not text:
            return None
        
        # Normalize to lowercase for matching
        text_lower = text.lower().strip()
        
        # Get mapping from config
        mappings = self.config.get('mappings', {}).get('cambio', {})
        
        # Try exact match first
        if text_lower in mappings:
            result = mappings[text_lower]
            logger.debug(f"Normalized cambio: '{text}' -> '{result}'")
            return result
        
        # Try partial match
        for key, value in mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized cambio (partial): '{text}' -> '{value}'")
                return value
        
        # Default mappings if config not available
        default_mappings = {
            'manual': 'Manual',
            'automático': 'Automático',
            'automatico': 'Automático',
            'cvt': 'Automático CVT',
            'automatizada': 'Automatizada',
            'amt': 'Automatizada',
        }
        
        for key, value in default_mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized cambio (default): '{text}' -> '{value}'")
                return value
        
        logger.warning(f"Could not normalize cambio: '{text}'")
        return None
    
    def normalize_combustivel(self, text: str) -> Optional[str]:
        """
        Normalize fuel type.
        
        Maps various fuel descriptions to standard values:
        - Flex
        - Gasolina
        - Diesel
        - Elétrico
        - Híbrido
        
        Args:
            text: Text containing fuel type
            
        Returns:
            Normalized fuel type or None
        """
        if not text:
            return None
        
        # Normalize to lowercase for matching
        text_lower = text.lower().strip()
        
        # Get mapping from config
        mappings = self.config.get('mappings', {}).get('combustivel', {})
        
        # Try exact match first
        if text_lower in mappings:
            result = mappings[text_lower]
            logger.debug(f"Normalized combustivel: '{text}' -> '{result}'")
            return result
        
        # Try partial match
        for key, value in mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized combustivel (partial): '{text}' -> '{value}'")
                return value
        
        # Default mappings if config not available
        default_mappings = {
            'flex': 'Flex',
            'gasolina': 'Gasolina',
            'diesel': 'Diesel',
            'elétrico': 'Elétrico',
            'eletrico': 'Elétrico',
            'híbrido': 'Híbrido',
            'hibrido': 'Híbrido',
        }
        
        for key, value in default_mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized combustivel (default): '{text}' -> '{value}'")
                return value
        
        logger.warning(f"Could not normalize combustivel: '{text}'")
        return None
    
    def normalize_categoria(self, text: str) -> Optional[str]:
        """
        Normalize vehicle category.
        
        Maps various category descriptions to standard values:
        - Hatch
        - Sedan
        - SUV
        - Pickup
        - Compacto
        - Van
        
        Args:
            text: Text containing category
            
        Returns:
            Normalized category or None
        """
        if not text:
            return None
        
        # Normalize to lowercase for matching
        text_lower = text.lower().strip()
        
        # Get mapping from config
        mappings = self.config.get('mappings', {}).get('categoria', {})
        
        # Try exact match first
        if text_lower in mappings:
            result = mappings[text_lower]
            logger.debug(f"Normalized categoria: '{text}' -> '{result}'")
            return result
        
        # Try partial match
        for key, value in mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized categoria (partial): '{text}' -> '{value}'")
                return value
        
        # Default mappings if config not available
        default_mappings = {
            'hatch': 'Hatch',
            'sedan': 'Sedan',
            'suv': 'SUV',
            'pickup': 'Pickup',
            'picape': 'Pickup',
            'compacto': 'Compacto',
            'van': 'Van',
        }
        
        for key, value in default_mappings.items():
            if key in text_lower:
                logger.debug(f"Normalized categoria (default): '{text}' -> '{value}'")
                return value
        
        logger.warning(f"Could not normalize categoria: '{text}'")
        return None
    
    def validate_images(self, image_urls: List[str]) -> List[str]:
        """
        Validate and filter image URLs.
        
        Removes invalid URLs and duplicates.
        
        Args:
            image_urls: List of image URLs
            
        Returns:
            List of valid, unique image URLs
            
        Requirements: 1.1, 9.2
        """
        if not image_urls:
            return []
        
        valid_urls = []
        seen_urls = set()
        
        for url in image_urls:
            # Skip empty or whitespace-only URLs
            if not url or not url.strip():
                continue
            
            url = url.strip()
            
            # Skip duplicates
            if url in seen_urls:
                continue
            
            # Validate URL format
            try:
                parsed = urlparse(url)
                if not all([parsed.scheme in ('http', 'https'), parsed.netloc]):
                    logger.debug(f"Invalid image URL: {url}")
                    continue
                
                # Check if it looks like an image
                path_lower = parsed.path.lower()
                if not any(ext in path_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    # Allow URLs without extension (might be dynamic)
                    if '?' not in url and not path_lower.endswith('/'):
                        logger.debug(f"URL doesn't look like an image: {url}")
                        # Still include it, might be valid
                
                valid_urls.append(url)
                seen_urls.add(url)
            
            except Exception as e:
                logger.debug(f"Error validating image URL {url}: {e}")
                continue
        
        logger.debug(f"Validated {len(valid_urls)}/{len(image_urls)} image URLs")
        return valid_urls
    
    def extract_and_normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize all fields from raw data.
        
        Args:
            raw_data: Dictionary with raw extracted data
            
        Returns:
            Dictionary with normalized data
            
        Requirements: 1.4, 9.1, 9.2
        """
        normalized = {}
        
        # Price
        if 'preco' in raw_data:
            price = self.extract_price(str(raw_data['preco']))
            if price:
                normalized['preco'] = price
        
        # Mileage
        if 'quilometragem' in raw_data:
            km = self.extract_km(str(raw_data['quilometragem']))
            if km:
                normalized['quilometragem'] = km
        
        # Year
        if 'ano' in raw_data:
            year = self.extract_year(str(raw_data['ano']))
            if year:
                normalized['ano'] = year
        
        # Doors
        if 'portas' in raw_data:
            doors = self.extract_doors(str(raw_data['portas']))
            if doors:
                normalized['portas'] = doors
        
        # Transmission
        if 'cambio' in raw_data:
            cambio = self.normalize_cambio(str(raw_data['cambio']))
            if cambio:
                normalized['cambio'] = cambio
        
        # Fuel
        if 'combustivel' in raw_data:
            combustivel = self.normalize_combustivel(str(raw_data['combustivel']))
            if combustivel:
                normalized['combustivel'] = combustivel
        
        # Category
        if 'categoria' in raw_data:
            categoria = self.normalize_categoria(str(raw_data['categoria']))
            if categoria:
                normalized['categoria'] = categoria
        
        # Images
        if 'imagens' in raw_data:
            if isinstance(raw_data['imagens'], list):
                images = self.validate_images(raw_data['imagens'])
            else:
                images = self.validate_images([raw_data['imagens']])
            normalized['imagens'] = images
        
        # Copy string fields as-is
        for field in ['nome', 'marca', 'modelo', 'cor', 'descricao', 'url_original']:
            if field in raw_data and raw_data[field]:
                normalized[field] = str(raw_data[field]).strip()
        
        logger.debug(f"Normalized {len(normalized)} fields")
        return normalized
