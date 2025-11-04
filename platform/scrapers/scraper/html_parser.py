"""
HTML Parser and data extraction module.

This module provides HTML parsing functionality with fallback selectors,
specific field extractors, and error handling.

Requirements: 1.1, 1.4, 9.1, 9.2, 9.3, 6.3
"""

import re
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse


logger = logging.getLogger(__name__)


class HTMLParser:
    """
    HTML parser with fallback selector support and field extraction.
    
    Requirements: 9.1, 9.2, 9.3, 6.3
    """
    
    def __init__(self, selector_config_path: str = "config/selectors.yaml"):
        """
        Initialize HTML parser with selector configuration.
        
        Args:
            selector_config_path: Path to selectors YAML file
        """
        self.selector_config_path = selector_config_path
        self.selectors = self._load_selectors()
        
        # Statistics for selector usage
        self.selector_stats: Dict[str, Dict[str, int]] = {}
        
        logger.info(f"HTMLParser initialized with config: {selector_config_path}")
    
    def _load_selectors(self) -> Dict[str, Any]:
        """
        Load CSS selectors from YAML configuration.
        
        Returns:
            Dictionary with selector configuration
            
        Raises:
            FileNotFoundError: If config file not found
            yaml.YAMLError: If config file is invalid
        """
        config_path = Path(self.selector_config_path)
        
        if not config_path.exists():
            logger.error(f"Selector config not found: {config_path}")
            raise FileNotFoundError(f"Selector config not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded {len(config.get('vehicle', {}))} vehicle field selectors")
            return config
        
        except yaml.YAMLError as e:
            logger.error(f"Error parsing selector config: {e}")
            raise
    
    def parse(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.
        
        Args:
            html: HTML string to parse
            
        Returns:
            BeautifulSoup object
            
        Raises:
            ValueError: If HTML is empty or invalid
        """
        if not html or not html.strip():
            raise ValueError("HTML content is empty")
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Verify we got valid HTML
            if not soup.find():
                raise ValueError("No HTML elements found in content")
            
            logger.debug(f"Parsed HTML: {len(html)} bytes")
            return soup
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            raise ValueError(f"Failed to parse HTML: {e}")
    
    def extract_field(self, soup: BeautifulSoup, field: str, 
                     base_url: Optional[str] = None) -> Optional[str]:
        """
        Extract field value using fallback selectors.
        
        Tries multiple CSS selectors in order until one succeeds.
        Tracks which selector was successful for analytics.
        
        Args:
            soup: BeautifulSoup object
            field: Field name to extract
            base_url: Base URL for resolving relative URLs (for images)
            
        Returns:
            Extracted value or None if not found
            
        Requirements: 9.1, 9.2
        """
        # Get selectors for this field
        field_selectors = self.selectors.get('vehicle', {}).get(field, [])
        
        if not field_selectors:
            logger.warning(f"No selectors configured for field: {field}")
            return None
        
        # Try each selector in order
        for idx, selector in enumerate(field_selectors):
            try:
                # Handle special case for images (multiple elements)
                if field == 'imagens':
                    elements = soup.select(selector)
                    if elements:
                        self._record_selector_success(field, idx, selector)
                        # Extract src or data-src attributes
                        urls = []
                        for elem in elements:
                            url = elem.get('src') or elem.get('data-src') or elem.get('content')
                            if url:
                                # Resolve relative URLs
                                if base_url:
                                    url = urljoin(base_url, url)
                                urls.append(url)
                        
                        if urls:
                            logger.debug(f"Extracted {field} using selector #{idx}: {selector}")
                            return ','.join(urls)  # Return comma-separated URLs
                
                # Standard single-element extraction
                element = soup.select_one(selector)
                
                if element:
                    # Extract text content
                    value = self._extract_text(element)
                    
                    if value:
                        self._record_selector_success(field, idx, selector)
                        logger.debug(f"Extracted {field} using selector #{idx}: {selector}")
                        return value
            
            except Exception as e:
                logger.debug(f"Selector {idx} failed for {field}: {e}")
                continue
        
        # All selectors failed
        logger.warning(f"All selectors failed for field: {field}")
        self._record_selector_failure(field)
        return None
    
    def _extract_text(self, element: Tag) -> Optional[str]:
        """
        Extract and clean text from HTML element.
        
        Args:
            element: BeautifulSoup Tag element
            
        Returns:
            Cleaned text or None
        """
        if not element:
            return None
        
        # Try to get content from meta tags
        if element.name == 'meta':
            return element.get('content')
        
        # Get text content
        text = element.get_text(strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text if text else None
    
    def _record_selector_success(self, field: str, selector_idx: int, selector: str):
        """Record successful selector usage for analytics"""
        if field not in self.selector_stats:
            self.selector_stats[field] = {}
        
        key = f"{selector_idx}:{selector}"
        self.selector_stats[field][key] = self.selector_stats[field].get(key, 0) + 1
    
    def _record_selector_failure(self, field: str):
        """Record selector failure for analytics"""
        if field not in self.selector_stats:
            self.selector_stats[field] = {}
        
        self.selector_stats[field]['_failures'] = \
            self.selector_stats[field].get('_failures', 0) + 1
    
    def get_selector_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get selector usage statistics.
        
        Returns:
            Dictionary with selector usage counts per field
        """
        return self.selector_stats
    
    def extract_vehicle(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract all vehicle fields from HTML.
        
        Args:
            html: HTML content
            url: Page URL (for resolving relative URLs)
            
        Returns:
            Dictionary with extracted vehicle data
            
        Requirements: 1.1, 1.2, 9.1, 9.2
        """
        try:
            soup = self.parse(html)
        except ValueError as e:
            logger.error(f"Failed to parse HTML for {url}: {e}")
            return {}
        
        # Extract all fields
        data = {}
        
        # Basic fields
        for field in ['nome', 'marca', 'modelo', 'ano', 'preco', 
                     'quilometragem', 'combustivel', 'cambio', 
                     'cor', 'portas', 'categoria', 'descricao']:
            value = self.extract_field(soup, field)
            if value:
                data[field] = value
        
        # Images (special handling)
        images_str = self.extract_field(soup, 'imagens', base_url=url)
        if images_str:
            data['imagens'] = images_str.split(',')
        else:
            data['imagens'] = []
        
        # Add URL
        data['url_original'] = url
        
        logger.info(f"Extracted {len(data)} fields from {url}")
        return data
    
    def extract_vehicle_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract vehicle listing URLs from listing page.
        
        Args:
            html: HTML content of listing page
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute vehicle URLs
            
        Requirements: 1.1
        """
        try:
            soup = self.parse(html)
        except ValueError as e:
            logger.error(f"Failed to parse listing HTML: {e}")
            return []
        
        # Get selectors for vehicle links
        link_selectors = self.selectors.get('listing', {}).get('vehicle_links', [])
        
        urls = []
        for selector in link_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        href = elem.get('href')
                        if href:
                            # Resolve relative URL
                            absolute_url = urljoin(base_url, href)
                            # Validate URL
                            if self._is_valid_url(absolute_url):
                                urls.append(absolute_url)
                    
                    if urls:
                        logger.info(
                            f"Found {len(urls)} vehicle links using selector: {selector}"
                        )
                        break
            
            except Exception as e:
                logger.debug(f"Link selector failed: {e}")
                continue
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(urls))
        
        logger.info(f"Extracted {len(unique_urls)} unique vehicle URLs")
        return unique_urls
    
    def extract_next_page_url(self, html: str, base_url: str) -> Optional[str]:
        """
        Extract next page URL from listing page.
        
        Args:
            html: HTML content of listing page
            base_url: Base URL for resolving relative links
            
        Returns:
            Absolute URL of next page or None
        """
        try:
            soup = self.parse(html)
        except ValueError as e:
            logger.error(f"Failed to parse listing HTML: {e}")
            return None
        
        # Get selectors for next page link
        next_selectors = self.selectors.get('listing', {}).get('next_page', [])
        
        for selector in next_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    href = element.get('href')
                    if href:
                        # Resolve relative URL
                        absolute_url = urljoin(base_url, href)
                        if self._is_valid_url(absolute_url):
                            logger.debug(f"Found next page: {absolute_url}")
                            return absolute_url
            
            except Exception as e:
                logger.debug(f"Next page selector failed: {e}")
                continue
        
        logger.debug("No next page found")
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid HTTP(S) URL
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False
    
    def save_debug_html(self, html: str, filename: str):
        """
        Save HTML to file for debugging.
        
        Args:
            html: HTML content
            filename: Output filename
            
        Requirement: 9.4
        """
        debug_dir = Path("debug")
        debug_dir.mkdir(exist_ok=True)
        
        output_path = debug_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Saved debug HTML to: {output_path}")
        
        except Exception as e:
            logger.error(f"Failed to save debug HTML: {e}")
