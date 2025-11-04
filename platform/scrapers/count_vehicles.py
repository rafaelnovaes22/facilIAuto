import json

files = [
    '../backend/data/robustcar_estoque.json',
    '../backend/data/autocenter_estoque.json',
    '../backend/data/carplus_estoque.json'
]

print("\n📊 Contagem de Veículos no Backend\n")
print("=" * 50)

total = 0
for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = len(data)
            total += count
            dealership = file.split('/')[-1].replace('_estoque.json', '')
            print(f"{dealership:20} {count:3} veículos")
    except FileNotFoundError:
        dealership = file.split('/')[-1].replace('_estoque.json', '')
        print(f"{dealership:20}   0 veículos (arquivo não encontrado)")
    except Exception as e:
        print(f"Erro ao ler {file}: {e}")

print("=" * 50)
print(f"{'TOTAL':20} {total:3} veículos")
print()
