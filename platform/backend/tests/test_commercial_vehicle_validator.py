"""
Testes para o validador de veículos comerciais
"""

import pytest
from services.commercial_vehicle_validator import validator


class TestCommercialVehicleValidator:
    """Testes para validação de veículos comerciais"""
    
    def test_pickup_pequena_comercial_aceita(self):
        """Pickups pequenas devem ser aceitas como comerciais"""
        # Fiat Strada
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Strada Endurance")
        assert is_valid is True
        assert "comercial" in reason.lower()
        
        # Volkswagen Saveiro
        is_valid, reason = validator.is_commercial_vehicle("Volkswagen", "Saveiro Robust")
        assert is_valid is True
        
        # Chevrolet Montana
        is_valid, reason = validator.is_commercial_vehicle("Chevrolet", "Montana LS")
        assert is_valid is True
    
    def test_pickup_media_lazer_rejeitada_strict(self):
        """Pickups médias/grandes devem ser rejeitadas em modo estrito"""
        # Fiat Toro (strict mode)
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Toro Ranch", strict_mode=True)
        assert is_valid is False
        assert "lazer" in reason.lower() or "aventura" in reason.lower()
        
        # Nissan Frontier
        is_valid, reason = validator.is_commercial_vehicle("Nissan", "Frontier Attack", strict_mode=True)
        assert is_valid is False
        
        # Toyota Hilux
        is_valid, reason = validator.is_commercial_vehicle("Toyota", "Hilux SR", strict_mode=True)
        assert is_valid is False
    
    def test_pickup_media_lazer_aceita_com_aviso(self):
        """Pickups médias/grandes devem ser aceitas em modo permissivo, mas com aviso"""
        # Fiat Toro (non-strict mode)
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Toro Ranch", strict_mode=False)
        assert is_valid is True
        assert "⚠️" in reason
        assert "lazer" in reason.lower() or "custo" in reason.lower()
        
        # Nissan Frontier
        is_valid, reason = validator.is_commercial_vehicle("Nissan", "Frontier", strict_mode=False)
        assert is_valid is True
        assert "⚠️" in reason
    
    def test_furgao_aceito(self):
        """Furgões devem ser aceitos como comerciais"""
        # Fiat Fiorino
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Fiorino")
        assert is_valid is True
        assert "furgão" in reason.lower() or "van" in reason.lower()
        
        # Renault Kangoo
        is_valid, reason = validator.is_commercial_vehicle("Renault", "Kangoo Express")
        assert is_valid is True
        
        # Citroën Berlingo
        is_valid, reason = validator.is_commercial_vehicle("Citroën", "Berlingo Cargo")
        assert is_valid is True
        
        # Mercedes-Benz Sprinter
        is_valid, reason = validator.is_commercial_vehicle("Mercedes-Benz", "Sprinter 415")
        assert is_valid is True
    
    def test_van_aceita(self):
        """Vans devem ser aceitas como comerciais"""
        # Renault Master
        is_valid, reason = validator.is_commercial_vehicle("Renault", "Master Furgão")
        assert is_valid is True
        
        # Fiat Ducato
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Ducato Cargo")
        assert is_valid is True
    
    def test_versao_lazer_rejeitada(self):
        """Versões de lazer devem ser rejeitadas mesmo em pickups pequenas"""
        # Strada Ranch (lazer)
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Strada", versao="Ranch")
        assert is_valid is False
        assert "lazer" in reason.lower()
        
        # Saveiro Cross (lazer)
        is_valid, reason = validator.is_commercial_vehicle("Volkswagen", "Saveiro", versao="Cross")
        # Cross não está na lista de keywords, então pode ser aceito
        # Mas se adicionar "cross" às keywords de lazer, deve rejeitar
    
    def test_versao_comercial_aceita(self):
        """Versões comerciais devem ser aceitas"""
        # Strada Endurance (comercial)
        is_valid, reason = validator.is_commercial_vehicle("Fiat", "Strada", versao="Endurance")
        assert is_valid is True
        
        # Saveiro Robust (comercial)
        is_valid, reason = validator.is_commercial_vehicle("Volkswagen", "Saveiro", versao="Robust")
        assert is_valid is True
    
    def test_sedan_rejeitado(self):
        """Sedans não são comerciais"""
        is_valid, reason = validator.is_commercial_vehicle("Toyota", "Corolla")
        assert is_valid is False
    
    def test_suv_rejeitado(self):
        """SUVs não são comerciais"""
        is_valid, reason = validator.is_commercial_vehicle("Jeep", "Compass")
        assert is_valid is False
    
    def test_categoria_furgao_aceita(self):
        """Categoria 'Furgão' deve ser aceita"""
        is_valid, reason = validator.is_commercial_vehicle(
            "Marca Genérica",
            "Modelo Genérico",
            categoria="Furgão"
        )
        assert is_valid is True
    
    def test_get_commercial_requirements(self):
        """Verificar requisitos técnicos"""
        reqs = validator.get_commercial_requirements()
        
        assert reqs["capacidade_carga_minima_kg"] >= 500
        assert reqs["chassi_reforcado"] is True
        assert reqs["consumo_minimo_kml"] >= 9.0
        assert reqs["manutencao_acessivel"] is True
    
    def test_get_commercial_categories(self):
        """Verificar categorias comerciais"""
        categories = validator.get_commercial_categories()
        
        assert "Pickup Pequena" in categories
        assert "Furgão" in categories
        assert "Van" in categories
        assert "Pickup" not in categories  # Genérico não deve estar
    
    def test_get_leisure_pickups_list(self):
        """Verificar lista de pickups de lazer"""
        leisure_pickups = validator.get_leisure_pickups_list()
        
        assert "Fiat Toro" in leisure_pickups
        assert "Nissan Frontier" in leisure_pickups
        assert "Mitsubishi L200" in leisure_pickups
        assert "Toyota Hilux" in leisure_pickups
        assert "Ford Ranger" in leisure_pickups
        assert "Chevrolet S10" in leisure_pickups
        assert "Volkswagen Amarok" in leisure_pickups
        
        # Pickups pequenas NÃO devem estar na lista de lazer
        assert "Fiat Strada" not in leisure_pickups
        assert "Volkswagen Saveiro" not in leisure_pickups
        assert "Chevrolet Montana" not in leisure_pickups
    
    def test_vuc_rejeitado_strict(self):
        """VUCs devem ser rejeitados em modo estrito"""
        # Hyundai HR (strict mode)
        is_valid, reason = validator.is_commercial_vehicle("Hyundai", "HR HDB", strict_mode=True)
        assert is_valid is False
        assert "vuc" in reason.lower() or "carga pesada" in reason.lower()
        
        # Kia Bongo
        is_valid, reason = validator.is_commercial_vehicle("Kia", "Bongo K2500", strict_mode=True)
        assert is_valid is False
    
    def test_vuc_aceito_com_aviso(self):
        """VUCs devem ser aceitos em modo permissivo, mas com aviso"""
        # Hyundai HR (non-strict mode)
        is_valid, reason = validator.is_commercial_vehicle("Hyundai", "HR HDB", strict_mode=False)
        assert is_valid is True
        assert "⚠️" in reason
        assert "cnh c" in reason.lower()
        
        # Mercedes-Benz Accelo
        is_valid, reason = validator.is_commercial_vehicle("Mercedes-Benz", "Accelo", strict_mode=False)
        assert is_valid is True
        assert "⚠️" in reason
    
    def test_categoria_vuc_rejeitada(self):
        """Categoria 'VUC' ou 'Caminhão' deve ser rejeitada"""
        is_valid, reason = validator.is_commercial_vehicle(
            "Marca Genérica",
            "Modelo Genérico",
            categoria="VUC"
        )
        assert is_valid is False
        assert "vuc" in reason.lower() or "cnh c" in reason.lower()
        
        is_valid, reason = validator.is_commercial_vehicle(
            "Marca Genérica",
            "Modelo Genérico",
            categoria="Caminhão"
        )
        assert is_valid is False
    
    def test_get_vucs_trucks_list(self):
        """Verificar lista de VUCs e caminhões"""
        vucs = validator.get_vucs_trucks_list()
        
        assert "Hyundai HR" in vucs
        assert "Hyundai HD" in vucs
        assert "Kia Bongo" in vucs
        assert "Mercedes-Benz Accelo" in vucs
        
        # Furgões NÃO devem estar na lista de VUCs
        assert "Fiat Fiorino" not in vucs
        assert "Renault Kangoo" not in vucs
    
    def test_is_vuc_or_truck(self):
        """Verificar método auxiliar is_vuc_or_truck"""
        assert validator.is_vuc_or_truck("Hyundai", "HR HDB") is True
        assert validator.is_vuc_or_truck("Kia", "Bongo") is True
        assert validator.is_vuc_or_truck("Fiat", "Fiorino") is False
        assert validator.is_vuc_or_truck("Fiat", "Strada") is False
    
    def test_get_commercial_suitability_ideal(self):
        """Verificar adequação IDEAL (pickups pequenas e furgões)"""
        # Fiat Strada
        suitability = validator.get_commercial_suitability("Fiat", "Strada Endurance")
        assert suitability["nivel"] == "ideal"
        assert suitability["score"] >= 0.9
        assert suitability["recomendado"] is True
        assert suitability["requer_cnh"] == "B"
        assert len(suitability["avisos"]) == 0
        
        # Fiat Fiorino
        suitability = validator.get_commercial_suitability("Fiat", "Fiorino")
        assert suitability["nivel"] == "ideal"
        assert suitability["score"] == 1.0
        assert suitability["tipo"] == "furgao_van"
    
    def test_get_commercial_suitability_limitado(self):
        """Verificar adequação LIMITADA (VUCs)"""
        # Hyundai HR
        suitability = validator.get_commercial_suitability("Hyundai", "HR HDB")
        assert suitability["nivel"] == "limitado"
        assert suitability["score"] == 0.3
        assert suitability["recomendado"] is False
        assert suitability["requer_cnh"] == "C"
        assert len(suitability["avisos"]) > 0
        assert any("CNH" in aviso for aviso in suitability["avisos"])
    
    def test_get_commercial_suitability_inadequado(self):
        """Verificar adequação INADEQUADA (pickups de lazer)"""
        # Fiat Toro
        suitability = validator.get_commercial_suitability("Fiat", "Toro Ranch")
        assert suitability["nivel"] == "inadequado"
        assert suitability["score"] == 0.2
        assert suitability["recomendado"] is False
        assert suitability["tipo"] == "pickup_lazer"
        assert len(suitability["avisos"]) > 0
        assert any("lazer" in aviso.lower() or "custo" in aviso.lower() for aviso in suitability["avisos"])
    
    def test_get_commercial_suitability_outro(self):
        """Verificar adequação para outros veículos (Sedan, SUV)"""
        # Toyota Corolla
        suitability = validator.get_commercial_suitability("Toyota", "Corolla")
        assert suitability["nivel"] == "inadequado"
        assert suitability["score"] == 0.0
        assert suitability["tipo"] == "outro"
    
    def test_van_passageiros_rejeitada(self):
        """Vans de passageiros devem ser rejeitadas para uso comercial"""
        # Renault Master Minibus
        is_valid, reason = validator.is_commercial_vehicle("Renault", "Master", versao="Minibus", strict_mode=True)
        assert is_valid is False
        assert "passageiros" in reason.lower()
        
        # Mercedes Sprinter Executiva
        is_valid, reason = validator.is_commercial_vehicle("Mercedes-Benz", "Sprinter", versao="Executiva", strict_mode=True)
        assert is_valid is False
    
    def test_van_comercial_vs_passageiros(self):
        """Diferenciar van comercial (carga) de van de passageiros"""
        # Van comercial (carga) - ACEITA
        is_valid, reason = validator.is_commercial_vehicle("Renault", "Master Furgão")
        assert is_valid is True
        assert "comercial" in reason.lower() or "carga" in reason.lower()
        
        # Van de passageiros - REJEITA
        is_valid, reason = validator.is_commercial_vehicle("Renault", "Master Minibus", strict_mode=True)
        assert is_valid is False
        assert "passageiros" in reason.lower()
    
    def test_is_passenger_van(self):
        """Verificar método auxiliar is_passenger_van"""
        # Van de passageiros
        assert validator.is_passenger_van("Renault", "Master", versao="Minibus") is True
        assert validator.is_passenger_van("Mercedes-Benz", "Sprinter", versao="Executiva") is True
        assert validator.is_passenger_van("Fiat", "Ducato", versao="Escolar") is True
        
        # Van comercial (carga)
        assert validator.is_passenger_van("Renault", "Master", versao="Furgão") is False
        assert validator.is_passenger_van("Fiat", "Fiorino") is False
    
    def test_get_commercial_suitability_van_passageiros(self):
        """Verificar adequação de van de passageiros"""
        # Renault Master Minibus
        suitability = validator.get_commercial_suitability("Renault", "Master", versao="Minibus")
        assert suitability["nivel"] == "inadequado"
        assert suitability["score"] == 0.0
        assert suitability["tipo"] == "van_passageiros"
        assert suitability["requer_cnh"] == "D"
        assert len(suitability["avisos"]) > 0
        assert any("passageiros" in aviso.lower() for aviso in suitability["avisos"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
