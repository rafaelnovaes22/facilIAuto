"""
Teste TCO de SUV específico
"""
import requests
import json

API_URL = "http://localhost:8000"

profile = {
    "orcamento_min": 80000,
    "orcamento_max": 110000,
    "uso_principal": "familia",
    "state": "SP",
    "prioridades": {
        "economia": 4,
        "espaco": 5,
        "seguranca": 5,
        "conforto": 4,
        "performance": 2
    },
    "financial_capacity": {
        "monthly_income_range": "8000-12000",
        "max_monthly_tco": 3000.0,
        "is_disclosed": True
    }
}

print("=" * 80)
print("TESTE TCO - SUVs")
print("=" * 80)

response = requests.post(f"{API_URL}/recommend", json=profile, timeout=10)

if response.status_code == 200:
    data = response.json()
    
    print(f"\n✅ Total de recomendações: {data.get('total_recommendations', 0)}")
    
    # Mostrar todos os SUVs
    for rec in data.get('recommendations', []):
        car = rec.get('car', {})
        if car.get('categoria') == 'SUV':
            print("\n" + "=" * 80)
            print(f"🚗 {car.get('nome')}")
            print("=" * 80)
            print(f"Preço: R$ {car.get('preco'):,.2f}")
            print(f"Ano: {car.get('ano')}")
            print(f"Quilometragem: {car.get('quilometragem'):,} km")
            print(f"Categoria: {car.get('categoria')}")
            
            tco = rec.get('tco_breakdown')
            if tco:
                print("\n📊 TCO BREAKDOWN:")
                print("-" * 80)
                print(f"Financiamento:  R$ {tco.get('financing_monthly'):>8,.2f}/mês")
                print(f"Combustível:    R$ {tco.get('fuel_monthly'):>8,.2f}/mês")
                print(f"Manutenção:     R$ {tco.get('maintenance_monthly'):>8,.2f}/mês")
                print(f"Seguro:         R$ {tco.get('insurance_monthly'):>8,.2f}/mês")
                print(f"IPVA:           R$ {tco.get('ipva_monthly'):>8,.2f}/mês")
                print("-" * 80)
                print(f"TOTAL:          R$ {tco.get('total_monthly'):>8,.2f}/mês")
                
                # Premissas
                assumptions = tco.get('assumptions', {})
                print("\n🔍 PREMISSAS:")
                print("-" * 80)
                print(f"Entrada: {assumptions.get('down_payment_percent')}%")
                print(f"Prazo: {assumptions.get('financing_months')}x")
                print(f"Taxa de juros: {assumptions.get('annual_interest_rate')}% a.a.")
                print(f"Km/mês: {assumptions.get('monthly_km')} km")
                print(f"Combustível: R$ {assumptions.get('fuel_price_per_liter')}/L")
                print(f"Consumo: {assumptions.get('fuel_efficiency')} km/L")
                
                # Validação
                print("\n✅ VALIDAÇÃO:")
                if assumptions.get('fuel_price_per_liter') == 5.89:
                    print("✓ Preço combustível atualizado: R$ 5,89/L")
                else:
                    print(f"✗ Preço combustível desatualizado: R$ {assumptions.get('fuel_price_per_liter')}/L")
                
                fuel_eff = assumptions.get('fuel_efficiency')
                if fuel_eff and fuel_eff != 12.0:
                    print(f"✓ Consumo específico: {fuel_eff} km/L (não é o padrão 12.0)")
                elif fuel_eff == 12.0:
                    print(f"⚠️ Consumo padrão: {fuel_eff} km/L (pode ser estimativa)")
                
                # Status financeiro
                fits_budget = rec.get('fits_budget')
                if fits_budget is not None:
                    status = "Dentro do orçamento" if fits_budget else "Acima do orçamento"
                    print(f"💰 Status: {status}")
                
                financial_health = rec.get('financial_health')
                if financial_health:
                    print(f"🚦 Saúde financeira: {financial_health.get('status')} ({financial_health.get('color')})")
                    print(f"   Comprometimento: {financial_health.get('percentage'):.1f}% da renda")

print("\n" + "=" * 80)
