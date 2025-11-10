"""
Teste local para validar cálculo de TCO do Chery Tiggo
"""
import sys
sys.path.insert(0, 'platform/backend')

from services.tco_calculator import TCOCalculator

# Dados do Chery Tiggo 3x Plus
car_price = 83900
car_category = "SUV"
fuel_efficiency = 12.0
car_age = 3  # 2021
car_mileage = 167550  # Alta quilometragem

print("=" * 60)
print("TESTE TCO - Chery Tiggo 3x Plus")
print("=" * 60)
print(f"Preço: R$ {car_price:,.2f}")
print(f"Categoria: {car_category}")
print(f"Consumo: {fuel_efficiency} km/L")
print(f"Ano: 2021 (idade: {car_age} anos)")
print(f"Quilometragem: {car_mileage:,} km")
print("=" * 60)

# Criar calculadora
calculator = TCOCalculator(
    down_payment_percent=0.20,
    financing_months=60,
    annual_interest_rate=0.12,
    monthly_km=1000,
    fuel_price_per_liter=5.20,
    state="SP"
)

# Calcular TCO
tco = calculator.calculate_tco(
    car_price=car_price,
    car_category=car_category,
    fuel_efficiency_km_per_liter=fuel_efficiency,
    car_age=car_age,
    car_mileage=car_mileage
)

print("\n📊 RESULTADO DO CÁLCULO:")
print("-" * 60)
print(f"Financiamento:  R$ {tco.financing_monthly:>8,.2f}/mês")
print(f"Combustível:    R$ {tco.fuel_monthly:>8,.2f}/mês")
print(f"Manutenção:     R$ {tco.maintenance_monthly:>8,.2f}/mês")
print(f"Seguro:         R$ {tco.insurance_monthly:>8,.2f}/mês")
print(f"IPVA:           R$ {tco.ipva_monthly:>8,.2f}/mês")
print("-" * 60)
print(f"TOTAL:          R$ {tco.total_monthly:>8,.2f}/mês")
print("=" * 60)

print("\n🔍 PREMISSAS:")
print("-" * 60)
for key, value in tco.assumptions.items():
    if isinstance(value, dict):
        print(f"{key}:")
        for k, v in value.items():
            print(f"  {k}: {v}")
    else:
        print(f"{key}: {value}")
print("=" * 60)

# Validação manual
print("\n✅ VALIDAÇÃO MANUAL:")
print("-" * 60)

# 1. Financiamento
financed = car_price * 0.80
monthly_rate = 0.12 / 12
parcela = financed * (monthly_rate * (1 + monthly_rate) ** 60) / ((1 + monthly_rate) ** 60 - 1)
print(f"1. Financiamento (Price):")
print(f"   Financiado: R$ {financed:,.2f}")
print(f"   Taxa mensal: {monthly_rate*100:.2f}%")
print(f"   Parcela: R$ {parcela:,.2f}")
print(f"   ✓ Match: {abs(parcela - tco.financing_monthly) < 1}")

# 2. Combustível
litros = 1000 / fuel_efficiency
combustivel = litros * 5.20
print(f"\n2. Combustível:")
print(f"   Litros/mês: {litros:.2f}L")
print(f"   Custo: R$ {combustivel:,.2f}")
print(f"   ✓ Match: {abs(combustivel - tco.fuel_monthly) < 1}")

# 3. Manutenção
base_suv = 3000  # Anual
idade_mult = 1 + (car_age * 0.10)
manutencao_base = (base_suv * idade_mult) / 12
print(f"\n3. Manutenção:")
print(f"   Base SUV: R$ {base_suv}/ano")
print(f"   Multiplicador idade ({car_age} anos): {idade_mult}x")
print(f"   Base mensal: R$ {manutencao_base:,.2f}")

# Ajuste quilometragem
if car_mileage > 150000:
    manutencao_ajustada = manutencao_base * 2.0
    print(f"   Ajuste alta km (>150k): 2.0x")
    print(f"   Manutenção ajustada: R$ {manutencao_ajustada:,.2f}")
    print(f"   ✓ Match: {abs(manutencao_ajustada - tco.maintenance_monthly) < 1}")
else:
    print(f"   Sem ajuste de quilometragem")
    print(f"   ✓ Match: {abs(manutencao_base - tco.maintenance_monthly) < 1}")

# 4. Seguro
seguro_anual = car_price * 0.055
seguro_mensal = seguro_anual / 12
print(f"\n4. Seguro:")
print(f"   Taxa SUV: 5.5% ao ano")
print(f"   Anual: R$ {seguro_anual:,.2f}")
print(f"   Mensal: R$ {seguro_mensal:,.2f}")
print(f"   ✓ Match: {abs(seguro_mensal - tco.insurance_monthly) < 1}")

# 5. IPVA
ipva_anual = car_price * 0.04
ipva_mensal = ipva_anual / 12
print(f"\n5. IPVA:")
print(f"   Taxa SP: 4% ao ano")
print(f"   Anual: R$ {ipva_anual:,.2f}")
print(f"   Mensal: R$ {ipva_mensal:,.2f}")
print(f"   ✓ Match: {abs(ipva_mensal - tco.ipva_monthly) < 1}")

# Total esperado
total_esperado = parcela + combustivel + manutencao_ajustada + seguro_mensal + ipva_mensal
print(f"\n📊 TOTAL ESPERADO: R$ {total_esperado:,.2f}")
print(f"📊 TOTAL CALCULADO: R$ {tco.total_monthly:,.2f}")
print(f"✓ Diferença: R$ {abs(total_esperado - tco.total_monthly):.2f}")
print("=" * 60)
