"""
Data models for the RobustCar scraper.

This module defines Pydantic models for data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import hashlib
import json


class Vehicle(BaseModel):
    """
    Vehicle model with comprehensive validation.
    
    Requirements: 1.1, 1.4, 4.1, 4.2, 4.3, 4.4
    """
    
    id: str = Field(..., description="Unique vehicle identifier")
    nome: str = Field(..., min_length=3, max_length=200, description="Vehicle full name")
    marca: str = Field(..., min_length=2, max_length=50, description="Brand name")
    modelo: str = Field(..., min_length=2, max_length=100, description="Model name")
    ano: int = Field(..., ge=2010, le=2026, description="Vehicle year")
    preco: float = Field(..., ge=10000, le=500000, description="Price in BRL")
    quilometragem: int = Field(..., ge=0, le=500000, description="Mileage in kilometers")
    combustivel: str = Field(
        ..., 
        pattern="^(Flex|Gasolina|Diesel|Elétrico|Híbrido)$",
        description="Fuel type"
    )
    cambio: str = Field(
        ...,
        pattern="^(Manual|Automático|Automático CVT|Automatizada)$",
        description="Transmission type"
    )
    cor: Optional[str] = Field(None, max_length=50, description="Vehicle color")
    portas: Optional[int] = Field(None, ge=2, le=5, description="Number of doors")
    categoria: str = Field(
        ...,
        pattern="^(Hatch|Sedan|SUV|Pickup|Compacto|Van)$",
        description="Vehicle category"
    )
    imagens: List[str] = Field(default_factory=list, description="List of image URLs")
    descricao: Optional[str] = Field(None, max_length=5000, description="Vehicle description")
    url_original: str = Field(..., pattern="^https?://", description="Original listing URL")
    data_scraping: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when data was scraped"
    )
    content_hash: str = Field(
        ...,
        min_length=32,
        max_length=32,
        description="MD5 hash of vehicle content"
    )
    
    @field_validator('preco')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """
        Validate that price is positive.
        
        Requirement: 4.3
        """
        if v <= 0:
            raise ValueError('Preço deve ser positivo')
        return v
    
    @field_validator('quilometragem')
    @classmethod
    def validate_km(cls, v: int, info) -> int:
        """
        Validate mileage against vehicle year.
        
        Requirement: 4.2
        """
        # Get ano from values if available
        if info.data.get('ano'):
            ano = info.data['ano']
            # New cars (2024+) shouldn't have very high mileage
            if ano >= 2024 and v > 50000:
                raise ValueError('Quilometragem muito alta para carro novo')
        return v
    
    @field_validator('imagens')
    @classmethod
    def validate_images(cls, v: List[str]) -> List[str]:
        """
        Validate that all image URLs are valid HTTP(S) URLs.
        
        Requirement: 1.1
        """
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'URL de imagem inválida: {url}')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert vehicle to dictionary format.
        
        Returns:
            Dictionary representation of the vehicle
        """
        data = self.model_dump()
        # Convert datetime to ISO format string
        if isinstance(data.get('data_scraping'), datetime):
            data['data_scraping'] = data['data_scraping'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vehicle':
        """
        Create Vehicle instance from dictionary.
        
        Args:
            data: Dictionary with vehicle data
            
        Returns:
            Vehicle instance
        """
        # Convert ISO format string to datetime if needed
        if isinstance(data.get('data_scraping'), str):
            data['data_scraping'] = datetime.fromisoformat(data['data_scraping'])
        return cls(**data)
    
    @staticmethod
    def calculate_content_hash(data: Dict[str, Any]) -> str:
        """
        Calculate MD5 hash of vehicle content for change detection.
        
        Args:
            data: Vehicle data dictionary
            
        Returns:
            32-character MD5 hash
            
        Requirement: 5.1
        """
        # Exclude metadata fields from hash calculation
        hashable_data = {
            k: v for k, v in data.items()
            if k not in ['id', 'data_scraping', 'content_hash']
        }
        # Sort keys for consistent hashing
        content_str = json.dumps(hashable_data, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()


class Config(BaseModel):
    """
    Configuration model for scraper settings.
    
    Requirements: 8.1, 8.2, 8.4
    """
    
    # Scraper identification
    scraper_name: str = Field(default="robustcar-scraper", description="Scraper name")
    scraper_version: str = Field(default="1.0.0", description="Scraper version")
    
    # HTTP settings
    http_timeout: int = Field(default=30, ge=5, le=120, description="HTTP timeout in seconds")
    http_max_retries: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    http_retry_backoff: float = Field(default=2.0, ge=1.0, le=10.0, description="Retry backoff multiplier")
    http_user_agent: str = Field(
        default="FacilIAuto-Scraper/1.0 (contact@faciliauto.com)",
        description="User agent string"
    )
    
    # Rate limiting
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=1,
        le=300,
        description="Maximum requests per minute"
    )
    rate_limit_delay_between_requests: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between requests in seconds"
    )
    rate_limit_respect_429: bool = Field(
        default=True,
        description="Respect 429 Too Many Requests responses"
    )
    rate_limit_business_hours_throttle: float = Field(
        default=0.5,
        ge=0.1,
        le=1.0,
        description="Throttle factor during business hours (8h-18h)"
    )
    
    # Worker settings
    workers_max_concurrent: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum concurrent workers"
    )
    workers_queue_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Worker queue size"
    )
    
    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl_hours: int = Field(default=24, ge=1, le=168, description="Cache TTL in hours")
    cache_max_size_mb: int = Field(default=100, ge=10, le=1000, description="Max cache size in MB")
    
    # Output settings
    output_format: str = Field(
        default="json",
        pattern="^(json|csv)$",
        description="Output format"
    )
    output_compression: str = Field(
        default="gzip",
        pattern="^(gzip|none)$",
        description="Output compression"
    )
    output_schema_version: str = Field(default="1.0", description="Output schema version")
    
    # Quality settings
    quality_min_completeness: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Minimum data completeness threshold"
    )
    quality_fail_threshold: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Maximum failure rate before stopping"
    )
    
    # Logging settings
    logging_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )
    logging_format: str = Field(
        default="json",
        pattern="^(json|text)$",
        description="Logging format"
    )
    logging_file: str = Field(default="logs/scraper.log", description="Log file path")
    
    # Metrics settings
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    metrics_prometheus_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Prometheus metrics port"
    )
    
    @field_validator('rate_limit_business_hours_throttle')
    @classmethod
    def validate_throttle(cls, v: float) -> float:
        """Validate throttle is between 0.1 and 1.0"""
        if not 0.1 <= v <= 1.0:
            raise ValueError('Throttle deve estar entre 0.1 e 1.0')
        return v
    
    @model_validator(mode='after')
    def validate_quality_thresholds(self) -> 'Config':
        """Validate that quality thresholds are consistent"""
        if self.quality_min_completeness < 0.5:
            raise ValueError('Completude mínima deve ser pelo menos 0.5')
        if self.quality_fail_threshold > 0.5:
            raise ValueError('Threshold de falha não deve exceder 0.5')
        return self


class Checkpoint(BaseModel):
    """
    Checkpoint model for resumable scraping.
    
    Requirement: 6.5
    """
    
    id: str = Field(..., description="Checkpoint unique identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Checkpoint timestamp")
    processed_count: int = Field(default=0, ge=0, description="Number of vehicles processed")
    success_count: int = Field(default=0, ge=0, description="Number of successful extractions")
    error_count: int = Field(default=0, ge=0, description="Number of errors")
    last_vehicle_id: Optional[str] = Field(None, description="Last processed vehicle ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        data = self.model_dump()
        if isinstance(data.get('timestamp'), datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create Checkpoint from dictionary"""
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class ValidationResult(BaseModel):
    """
    Result of data validation.
    
    Requirement: 7.4
    """
    
    is_valid: bool = Field(..., description="Whether data is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Data completeness score")
    missing_fields: List[str] = Field(default_factory=list, description="List of missing fields")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Create ValidationResult from dictionary"""
        return cls(**data)


class ScrapingResult(BaseModel):
    """
    Result of a scraping execution.
    
    Requirement: 7.4
    """
    
    id: str = Field(..., description="Scraping run unique identifier")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    mode: str = Field(..., pattern="^(full|incremental)$", description="Scraping mode")
    total_processed: int = Field(default=0, ge=0, description="Total vehicles processed")
    total_success: int = Field(default=0, ge=0, description="Total successful extractions")
    total_errors: int = Field(default=0, ge=0, description="Total errors")
    total_skipped: int = Field(default=0, ge=0, description="Total skipped (unchanged)")
    vehicles: List[Vehicle] = Field(default_factory=list, description="Extracted vehicles")
    rejected_vehicles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rejected vehicles with reasons"
    )
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics")
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds"""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_processed == 0:
            return 0.0
        return self.total_success / self.total_processed
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_processed == 0:
            return 0.0
        return self.total_errors / self.total_processed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scraping result to dictionary"""
        data = self.model_dump()
        if isinstance(data.get('start_time'), datetime):
            data['start_time'] = data['start_time'].isoformat()
        if isinstance(data.get('end_time'), datetime):
            data['end_time'] = data['end_time'].isoformat()
        # Convert vehicles to dict
        data['vehicles'] = [v.to_dict() if isinstance(v, Vehicle) else v for v in data['vehicles']]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingResult':
        """Create ScrapingResult from dictionary"""
        if isinstance(data.get('start_time'), str):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if isinstance(data.get('end_time'), str):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        # Convert vehicles from dict
        if 'vehicles' in data:
            data['vehicles'] = [
                Vehicle.from_dict(v) if isinstance(v, dict) else v
                for v in data['vehicles']
            ]
        return cls(**data)
