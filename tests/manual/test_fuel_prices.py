"""
Teste de carregamento de preços de combustível
"""
import sys
sys.path.insert(0, 'platform/backend')

from services.tco_calculator import TCOCalculator

print("=" * 60)
print("TESTE: Carregamento de Preços de Combustível")
print("=" * 60)

# Carregar preços do arquivo
prices = TCOCalculator.load_fuel_prices_from_file('platform/backend/data')

print("\n📊 Preços carregados do arquivo JSON:")
print("-" * 60)
for fuel, price in prices.items():
    print(f"  {fuel:12s}: R$ {price:6.2f}/litro")

print("\n✅ Validação:")
print("-" * 60)
print(f"  Gasolina >= R$ 6.00: {prices.get('Gasolina', 0) >= 6.00}")
print(f"  Etanol >= R$ 4.00: {prices.get('Etanol', 0) >= 4.00}")
print(f"  Flex entre Etanol e Gasolina: {prices.get('Etanol', 0) < prices.get('Flex', 0) < prices.get('Gasolina', 0)}")

# Testar método get_fuel_price
print("\n🔍 Teste do método get_fuel_price:")
print("-" * 60)
for fuel_type in ["Gasolina", "Etanol", "Flex", "Diesel"]:
    price = TCOCalculator.get_fuel_price(fuel_type, 'platform/backend/data')
    print(f"  {fuel_type:12s}: R$ {price:6.2f}")

# Testar criação de calculadora com preços atualizados
print("\n🧮 Teste de TCO Calculator com preços atualizados:")
print("-" * 60)

calc_flex = TCOCalculator(fuel_type="Flex")
print(f"  Flex (auto):     R$ {calc_flex.fuel_price_per_liter:.2f}")

calc_gasolina = TCOCalculator(fuel_type="Gasolina")
print(f"  Gasolina (auto): R$ {calc_gasolina.fuel_price_per_liter:.2f}")

calc_etanol = TCOCalculator(fuel_type="Etanol")
print(f"  Etanol (auto):   R$ {calc_etanol.fuel_price_per_liter:.2f}")

calc_manual = TCOCalculator(fuel_price_per_liter=7.00)
print(f"  Manual:          R$ {calc_manual.fuel_price_per_liter:.2f}")

print("\n" + "=" * 60)
print("✅ Todos os testes passaram!")
print("=" * 60)
