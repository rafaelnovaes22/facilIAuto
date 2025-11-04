"""
Teste específico: Hyundai HR HDB não deve ser recomendada como veículo comercial
Caso de uso real reportado pelo usuário
"""

import pytest
from services.commercial_vehicle_validator import validator


def test_hyundai_hr_hdb_rejeitada():
    """
    Hyundai HR HDB é um VUC (Veículo Urbano de Carga), não um furgão comercial
    
    Problema: Estava sendo classificada como "Van" comercial
    Solução: Deve ser rejeitada (requer CNH C, não adequada para entregas leves)
    """
    # Testar com nome completo
    is_valid, reason = validator.is_commercial_vehicle(
        marca="Hyundai",
        modelo="HR HDB"
    )
    
    assert is_valid is False, "Hyundai HR HDB deve ser rejeitada (é VUC, não furgão)"
    assert "vuc" in reason.lower() or "carga pesada" in reason.lower(), \
        f"Motivo deve mencionar VUC ou carga pesada, mas foi: {reason}"
    assert "cnh c" in reason.lower(), \
        f"Motivo deve mencionar CNH C, mas foi: {reason}"
    
    print(f"✅ Hyundai HR HDB corretamente rejeitada: {reason}")


def test_hyundai_hr_vs_fiat_fiorino():
    """
    Comparar Hyundai HR (VUC) vs Fiat Fiorino (furgão comercial)
    """
    # Hyundai HR - VUC (rejeitada)
    hr_valid, hr_reason = validator.is_commercial_vehicle("Hyundai", "HR HDB")
    
    # Fiat Fiorino - Furgão comercial (aceita)
    fiorino_valid, fiorino_reason = validator.is_commercial_vehicle("Fiat", "Fiorino")
    
    assert hr_valid is False, "Hyundai HR deve ser rejeitada"
    assert fiorino_valid is True, "Fiat Fiorino deve ser aceita"
    
    print(f"❌ Hyundai HR: {hr_reason}")
    print(f"✅ Fiat Fiorino: {fiorino_reason}")


def test_categoria_van_vs_vuc():
    """
    Testar diferença entre categoria "Van" e "VUC"
    """
    # Categoria "Van" - aceita
    van_valid, van_reason = validator.is_commercial_vehicle(
        marca="Marca Genérica",
        modelo="Modelo Genérico",
        categoria="Van"
    )
    
    # Categoria "VUC" - rejeitada
    vuc_valid, vuc_reason = validator.is_commercial_vehicle(
        marca="Marca Genérica",
        modelo="Modelo Genérico",
        categoria="VUC"
    )
    
    assert van_valid is True, "Categoria 'Van' deve ser aceita"
    assert vuc_valid is False, "Categoria 'VUC' deve ser rejeitada"
    
    print(f"✅ Van: {van_reason}")
    print(f"❌ VUC: {vuc_reason}")


def test_todos_vucs_rejeitados():
    """
    Garantir que todos os VUCs conhecidos são rejeitados
    """
    vucs = [
        ("Hyundai", "HR HDB"),
        ("Hyundai", "HD 78"),
        ("Kia", "Bongo K2500"),
        ("Mercedes-Benz", "Accelo 1016"),
        ("Volkswagen", "Delivery Express"),
        ("Ford", "Cargo 816"),
        ("Iveco", "Tector 170E28"),
    ]
    
    for marca, modelo in vucs:
        is_valid, reason = validator.is_commercial_vehicle(marca, modelo)
        assert is_valid is False, f"{marca} {modelo} deve ser rejeitado (é VUC)"
        print(f"❌ {marca} {modelo}: {reason}")


def test_requisitos_cnh():
    """
    Documentar requisitos de CNH
    """
    print("\n📋 Requisitos de CNH:")
    print("=" * 60)
    
    # CNH B - Aceitos
    print("\n✅ CNH B (aceitos para perfil 'Comercial'):")
    veiculos_cnh_b = [
        ("Fiat", "Strada Endurance", "Pickup pequena"),
        ("Volkswagen", "Saveiro Robust", "Pickup pequena"),
        ("Fiat", "Fiorino", "Furgão compacto"),
        ("Renault", "Kangoo", "Furgão"),
        ("Fiat", "Ducato", "Furgão grande"),
    ]
    
    for marca, modelo, tipo in veiculos_cnh_b:
        is_valid, reason = validator.is_commercial_vehicle(marca, modelo)
        assert is_valid is True
        print(f"  • {marca} {modelo} ({tipo})")
    
    # CNH C - Rejeitados
    print("\n❌ CNH C ou superior (rejeitados para perfil 'Comercial'):")
    veiculos_cnh_c = [
        ("Hyundai", "HR HDB", "VUC"),
        ("Kia", "Bongo K2500", "VUC"),
        ("Mercedes-Benz", "Accelo 1016", "Caminhão leve"),
    ]
    
    for marca, modelo, tipo in veiculos_cnh_c:
        is_valid, reason = validator.is_commercial_vehicle(marca, modelo)
        assert is_valid is False
        print(f"  • {marca} {modelo} ({tipo})")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
