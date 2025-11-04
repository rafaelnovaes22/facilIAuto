"""
Verificar dados existentes no backend
"""
import json
import os

backend_data = '../backend/data'

files = {
    'RobustCar': 'robustcar_estoque.json',
    'AutoCenter': 'autocenter_estoque.json',
    'CarPlus': 'carplus_estoque.json'
}

print("\n" + "=" * 60)
print("📊 DADOS EXISTENTES NO BACKEND")
print("=" * 60)

total = 0
for name, filename in files.items():
    filepath = os.path.join(backend_data, filename)
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data)
                total += count
                
                print(f"\n✅ {name}")
                print(f"   Arquivo: {filename}")
                print(f"   Veículos: {count}")
                
                # Mostrar exemplo
                if count > 0:
                    exemplo = data[0]
                    print(f"   Exemplo: {exemplo.get('nome', 'N/A')}")
                    print(f"            R$ {exemplo.get('preco', 0):,.2f}")
                    print(f"            Ano: {exemplo.get('ano', 'N/A')}")
        
        except Exception as e:
            print(f"\n❌ {name}")
            print(f"   Erro ao ler: {e}")
    else:
        print(f"\n⚠️  {name}")
        print(f"   Arquivo não encontrado: {filename}")

print("\n" + "=" * 60)
print(f"TOTAL: {total} veículos de {len([f for f in files.values() if os.path.exists(os.path.join(backend_data, f))])} concessionárias")
print("=" * 60)

if total > 0:
    print("\n✅ VOCÊ JÁ TEM DADOS SUFICIENTES PARA O MVP!")
    print("\nPróximos passos:")
    print("1. Iniciar backend: cd platform/backend && python api/main.py")
    print("2. Iniciar frontend: cd platform/frontend && npm run dev")
    print("3. Testar: http://localhost:3000")
else:
    print("\n⚠️  Nenhum dado encontrado")
    print("\nOpções:")
    print("1. Usar extração manual + CSV")
    print("2. Verificar se arquivos estão no local correto")

print()
