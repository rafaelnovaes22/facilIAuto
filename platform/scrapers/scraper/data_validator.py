"""
Data Validator for RobustCar scraper.

This module provides comprehensive validation for scraped vehicle data,
including field validation, type checking, range validation, and cross-validation.

Requirements: 4.1, 4.2, 4.3, 4.4, 1.3, 4.5
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from scraper.models import Vehicle, ValidationResult


class DataValidator:
    """
    Validates scraped vehicle data against business rules and quality standards.
    
    Provides:
    - Required field validation
    - Type and range validation
    - Enum validation (cambio, combustivel, categoria)
    - Completeness calculation
    - Cross-validation (km vs year, price vs category)
    - Anomaly detection
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 1.3, 4.5
    """
    
    # Required fields that must be present
    REQUIRED_FIELDS = [
        'id', 'nome', 'marca', 'modelo', 'ano', 'preco',
        'quilometragem', 'combustivel', 'cambio', 'categoria',
        'url_original', 'content_hash'
    ]
    
    # Optional fields that contribute to completeness
    OPTIONAL_FIELDS = [
        'cor', 'portas', 'imagens', 'descricao'
    ]
    
    # Valid enum values
    VALID_CAMBIO = ['Manual', 'Automático', 'Automático CVT', 'Automatizada']
    VALID_COMBUSTIVEL = ['Flex', 'Gasolina', 'Diesel', 'Elétrico', 'Híbrido']
    VALID_CATEGORIA = ['Hatch', 'Sedan', 'SUV', 'Pickup', 'Compacto', 'Van']
    
    # Validation ranges
    PRICE_MIN = 10000
    PRICE_MAX = 500000
    KM_MIN = 0
    KM_MAX = 500000
    YEAR_MIN = 2010
    YEAR_MAX = 2026
    DOORS_MIN = 2
    DOORS_MAX = 5
    
    # Cross-validation thresholds
    NEW_CAR_YEAR = 2024
    NEW_CAR_MAX_KM = 50000
    
    # Price ranges by category (for anomaly detection)
    CATEGORY_PRICE_RANGES = {
        'Hatch': (15000, 120000),
        'Sedan': (30000, 250000),
        'SUV': (50000, 500000),
        'Pickup': (60000, 400000),
        'Compacto': (15000, 80000),
        'Van': (40000, 300000)
    }
    
    def __init__(self):
        """Initialize the DataValidator."""
        pass
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete vehicle data.
        
        Performs all validation checks:
        - Required fields
        - Types and ranges
        - Enum values
        - Cross-validation
        - Completeness calculation
        
        Args:
            data: Vehicle data dictionary
            
        Returns:
            ValidationResult with validation status, errors, warnings, and completeness
            
        Requirements: 4.1, 4.2, 4.3, 4.4, 1.3, 4.5
        """
        errors = []
        warnings = []
        missing_fields = []
        
        # 1. Validate required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data or data[field] is None or data[field] == '':
                errors.append(f"Campo obrigatório ausente: {field}")
                missing_fields.append(field)
        
        # If critical fields are missing, return early
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                completeness=self.calculate_completeness(data),
                missing_fields=missing_fields
            )
        
        # 2. Validate types and ranges
        type_errors = self._validate_types_and_ranges(data)
        errors.extend(type_errors)
        
        # 3. Validate enums
        enum_errors = self._validate_enums(data)
        errors.extend(enum_errors)
        
        # 4. Cross-validation
        cross_errors, cross_warnings = self._validate_cross_checks(data)
        errors.extend(cross_errors)
        warnings.extend(cross_warnings)
        
        # 5. Calculate completeness
        completeness = self.calculate_completeness(data)
        
        # 6. Check for anomalies (warnings only)
        anomaly_warnings = self._detect_anomalies(data)
        warnings.extend(anomaly_warnings)
        
        # Determine if valid
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            completeness=completeness,
            missing_fields=missing_fields
        )
    
    def validate_field(self, field: str, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a specific field value.
        
        Args:
            field: Field name
            value: Field value
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Requirement: 4.1
        """
        # Check if required field is missing
        if field in self.REQUIRED_FIELDS:
            if value is None or value == '':
                return False, f"Campo obrigatório '{field}' está vazio"
        
        # Type and range validation
        if field == 'preco':
            if not isinstance(value, (int, float)):
                return False, f"Preço deve ser numérico, recebido: {type(value).__name__}"
            if value < self.PRICE_MIN or value > self.PRICE_MAX:
                return False, f"Preço fora da faixa válida (R$ {self.PRICE_MIN:,} - R$ {self.PRICE_MAX:,})"
        
        elif field == 'ano':
            if not isinstance(value, int):
                return False, f"Ano deve ser inteiro, recebido: {type(value).__name__}"
            if value < self.YEAR_MIN or value > self.YEAR_MAX:
                return False, f"Ano fora da faixa válida ({self.YEAR_MIN} - {self.YEAR_MAX})"
        
        elif field == 'quilometragem':
            if not isinstance(value, int):
                return False, f"Quilometragem deve ser inteiro, recebido: {type(value).__name__}"
            if value < self.KM_MIN or value > self.KM_MAX:
                return False, f"Quilometragem fora da faixa válida ({self.KM_MIN:,} - {self.KM_MAX:,} km)"
        
        elif field == 'cambio':
            if value not in self.VALID_CAMBIO:
                return False, f"Câmbio inválido: '{value}'. Valores válidos: {', '.join(self.VALID_CAMBIO)}"
        
        elif field == 'combustivel':
            if value not in self.VALID_COMBUSTIVEL:
                return False, f"Combustível inválido: '{value}'. Valores válidos: {', '.join(self.VALID_COMBUSTIVEL)}"
        
        elif field == 'categoria':
            if value not in self.VALID_CATEGORIA:
                return False, f"Categoria inválida: '{value}'. Valores válidas: {', '.join(self.VALID_CATEGORIA)}"
        
        elif field == 'portas':
            if value is not None:
                if not isinstance(value, int):
                    return False, f"Portas deve ser inteiro, recebido: {type(value).__name__}"
                if value < self.DOORS_MIN or value > self.DOORS_MAX:
                    return False, f"Número de portas inválido ({self.DOORS_MIN} - {self.DOORS_MAX})"
        
        return True, None
    
    def _validate_types_and_ranges(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate field types and value ranges.
        
        Requirements: 4.2, 4.3
        """
        errors = []
        
        # Validate each field
        fields_to_validate = ['preco', 'ano', 'quilometragem', 'portas']
        
        for field in fields_to_validate:
            if field in data and data[field] is not None:
                is_valid, error_msg = self.validate_field(field, data[field])
                if not is_valid:
                    errors.append(error_msg)
        
        return errors
    
    def _validate_enums(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate enum fields (cambio, combustivel, categoria).
        
        Requirement: 4.4
        """
        errors = []
        
        # Validate cambio
        if 'cambio' in data and data['cambio']:
            is_valid, error_msg = self.validate_field('cambio', data['cambio'])
            if not is_valid:
                errors.append(error_msg)
        
        # Validate combustivel
        if 'combustivel' in data and data['combustivel']:
            is_valid, error_msg = self.validate_field('combustivel', data['combustivel'])
            if not is_valid:
                errors.append(error_msg)
        
        # Validate categoria
        if 'categoria' in data and data['categoria']:
            is_valid, error_msg = self.validate_field('categoria', data['categoria'])
            if not is_valid:
                errors.append(error_msg)
        
        return errors
    
    def _validate_cross_checks(self, data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Perform cross-validation between related fields.
        
        Validates:
        - Quilometragem vs ano (new cars shouldn't have high mileage)
        - Preço vs categoria (price should be within category range)
        
        Requirements: 4.2, 4.3
        """
        errors = []
        warnings = []
        
        # 1. Validate quilometragem vs ano
        if 'ano' in data and 'quilometragem' in data:
            ano = data['ano']
            km = data['quilometragem']
            
            # New cars (2024+) shouldn't have very high mileage
            if ano >= self.NEW_CAR_YEAR and km > self.NEW_CAR_MAX_KM:
                errors.append(
                    f"Quilometragem muito alta ({km:,} km) para carro novo ({ano}). "
                    f"Máximo esperado: {self.NEW_CAR_MAX_KM:,} km"
                )
            
            # Calculate expected max km based on age
            current_year = datetime.now().year
            car_age = current_year - ano
            expected_max_km = car_age * 20000  # ~20k km/year is reasonable
            
            if km > expected_max_km * 1.5:  # 50% tolerance
                warnings.append(
                    f"Quilometragem ({km:,} km) parece alta para um carro de {ano} "
                    f"(esperado máximo ~{expected_max_km:,} km)"
                )
        
        # 2. Validate preço vs categoria
        if 'preco' in data and 'categoria' in data:
            preco = data['preco']
            categoria = data['categoria']
            
            if categoria in self.CATEGORY_PRICE_RANGES:
                min_price, max_price = self.CATEGORY_PRICE_RANGES[categoria]
                
                if preco < min_price * 0.7:  # 30% tolerance below
                    warnings.append(
                        f"Preço (R$ {preco:,.2f}) parece baixo para categoria {categoria} "
                        f"(faixa típica: R$ {min_price:,.2f} - R$ {max_price:,.2f})"
                    )
                elif preco > max_price * 1.3:  # 30% tolerance above
                    warnings.append(
                        f"Preço (R$ {preco:,.2f}) parece alto para categoria {categoria} "
                        f"(faixa típica: R$ {min_price:,.2f} - R$ {max_price:,.2f})"
                    )
        
        return errors, warnings
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """
        Detect potential anomalies in the data.
        
        Returns warnings for suspicious but not necessarily invalid data.
        
        Requirement: 4.3
        """
        warnings = []
        
        # Check for suspiciously round numbers
        if 'preco' in data:
            preco = data['preco']
            # Prices ending in exactly 000 might be estimates
            if preco % 1000 == 0 and preco > 50000:
                warnings.append(
                    f"Preço muito arredondado (R$ {preco:,.2f}) - pode ser estimativa"
                )
        
        # Check for missing images
        if 'imagens' in data:
            if not data['imagens'] or len(data['imagens']) == 0:
                warnings.append("Nenhuma imagem disponível")
            elif len(data['imagens']) < 3:
                warnings.append(f"Poucas imagens ({len(data['imagens'])}) - ideal ter 5+")
        
        # Check for missing description
        if 'descricao' not in data or not data['descricao']:
            warnings.append("Descrição ausente")
        elif len(data['descricao']) < 50:
            warnings.append("Descrição muito curta")
        
        # Check for missing color
        if 'cor' not in data or not data['cor']:
            warnings.append("Cor não especificada")
        
        return warnings
    
    def calculate_completeness(self, data: Dict[str, Any]) -> float:
        """
        Calculate data completeness score (0.0 to 1.0).
        
        Completeness is based on:
        - Required fields: 70% weight
        - Optional fields: 30% weight
        
        Args:
            data: Vehicle data dictionary
            
        Returns:
            Completeness score between 0.0 and 1.0
            
        Requirements: 1.3, 4.5
        """
        # Count required fields present
        required_present = sum(
            1 for field in self.REQUIRED_FIELDS
            if field in data and data[field] is not None and data[field] != ''
        )
        required_score = required_present / len(self.REQUIRED_FIELDS)
        
        # Count optional fields present
        optional_present = sum(
            1 for field in self.OPTIONAL_FIELDS
            if field in data and data[field] is not None and data[field] != ''
        )
        optional_score = optional_present / len(self.OPTIONAL_FIELDS) if self.OPTIONAL_FIELDS else 0.0
        
        # Weighted average: 70% required, 30% optional
        completeness = (required_score * 0.7) + (optional_score * 0.3)
        
        return round(completeness, 3)
    
    def generate_quality_report(self, vehicles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate quality report for a list of vehicles.
        
        Args:
            vehicles: List of vehicle data dictionaries
            
        Returns:
            Quality report with statistics per field and overall metrics
            
        Requirement: 4.5
        """
        if not vehicles:
            return {
                'total_vehicles': 0,
                'avg_completeness': 0.0,
                'field_completeness': {},
                'validation_summary': {
                    'valid': 0,
                    'invalid': 0,
                    'warnings': 0
                }
            }
        
        # Track field completeness
        field_counts = {field: 0 for field in self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS}
        total_completeness = 0.0
        valid_count = 0
        invalid_count = 0
        total_warnings = 0
        
        # Validate each vehicle
        for vehicle_data in vehicles:
            # Count field presence
            for field in field_counts.keys():
                if field in vehicle_data and vehicle_data[field] is not None and vehicle_data[field] != '':
                    field_counts[field] += 1
            
            # Validate and track results
            result = self.validate(vehicle_data)
            total_completeness += result.completeness
            
            if result.is_valid:
                valid_count += 1
            else:
                invalid_count += 1
            
            total_warnings += len(result.warnings)
        
        # Calculate field completeness percentages
        total_vehicles = len(vehicles)
        field_completeness = {
            field: round(count / total_vehicles, 3)
            for field, count in field_counts.items()
        }
        
        # Generate report
        report = {
            'total_vehicles': total_vehicles,
            'avg_completeness': round(total_completeness / total_vehicles, 3),
            'field_completeness': field_completeness,
            'validation_summary': {
                'valid': valid_count,
                'invalid': invalid_count,
                'valid_percentage': round(valid_count / total_vehicles, 3),
                'total_warnings': total_warnings,
                'avg_warnings_per_vehicle': round(total_warnings / total_vehicles, 2)
            },
            'quality_grade': self._calculate_quality_grade(
                valid_count / total_vehicles,
                total_completeness / total_vehicles
            )
        }
        
        return report
    
    def _calculate_quality_grade(self, valid_rate: float, avg_completeness: float) -> str:
        """
        Calculate quality grade based on validation rate and completeness.
        
        Args:
            valid_rate: Percentage of valid vehicles (0.0 to 1.0)
            avg_completeness: Average completeness score (0.0 to 1.0)
            
        Returns:
            Quality grade: A+, A, B, C, D, or F
        """
        # Combined score (60% validation, 40% completeness)
        score = (valid_rate * 0.6) + (avg_completeness * 0.4)
        
        if score >= 0.95:
            return 'A+'
        elif score >= 0.90:
            return 'A'
        elif score >= 0.80:
            return 'B'
        elif score >= 0.70:
            return 'C'
        elif score >= 0.60:
            return 'D'
        else:
            return 'F'
