"""
Debug: Testar extração de um único veículo
"""

import requests
from bs4 import BeautifulSoup
import re

url = "https://robustcar.com.br/motos/Yamaha/Neo/Automatic-125cc/Yamaha-Neo-Automatic-125cc-2021-São-Paulo-Sao-Paulo-6936084.html"

print(f"Testando: {url}\n")

response = requests.get(url, timeout=15)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

print("=" * 60)
print("1. Buscando seção 'Opcionais do Veículo'")
print("=" * 60)

# Estratégia 1: Buscar por heading
opcionais_heading = soup.find(['h2', 'h3', 'h4', 'h5', 'div', 'span'], string=re.compile(r'opcionais', re.IGNORECASE))
if opcionais_heading:
    print(f"✅ Encontrado heading: {opcionais_heading.name} - '{opcionais_heading.text.strip()}'")
    
    # Pegar próximo elemento
    next_elem = opcionais_heading.find_next(['div', 'section', 'ul', 'ol'])
    if next_elem:
        print(f"✅ Próximo elemento: {next_elem.name}")
        print(f"\nConteúdo da seção Opcionais:")
        print("-" * 60)
        print(next_elem.get_text()[:500])
        print("-" * 60)
        
        # Buscar câmbio
        opcionais_text = next_elem.get_text()
        if 'câmbio automático' in opcionais_text.lower() or 'cambio automatico' in opcionais_text.lower():
            print("\n✅ ENCONTRADO: Câmbio Automático")
        elif 'câmbio manual' in opcionais_text.lower() or 'cambio manual' in opcionais_text.lower():
            print("\n✅ ENCONTRADO: Câmbio Manual")
        else:
            print("\n⚠️  Câmbio não encontrado no texto")
else:
    print("❌ Heading 'Opcionais' não encontrado")

# Estratégia 2: Buscar por classe ou ID
print("\n" + "=" * 60)
print("2. Buscando por classe/ID 'opcionais'")
print("=" * 60)

opcionais_by_class = soup.find(class_=re.compile(r'opcionais', re.IGNORECASE))
if opcionais_by_class:
    print(f"✅ Encontrado por classe: {opcionais_by_class.name}")
    print(f"\nConteúdo:")
    print("-" * 60)
    print(opcionais_by_class.get_text()[:500])
else:
    print("❌ Não encontrado por classe")

opcionais_by_id = soup.find(id=re.compile(r'opcionais', re.IGNORECASE))
if opcionais_by_id:
    print(f"✅ Encontrado por ID: {opcionais_by_id.name}")
else:
    print("❌ Não encontrado por ID")

# Estratégia 3: Buscar "Câmbio" diretamente no texto
print("\n" + "=" * 60)
print("3. Buscando 'Câmbio' diretamente no texto da página")
print("=" * 60)

page_text = soup.get_text()
if 'câmbio automático' in page_text.lower():
    print("✅ ENCONTRADO: 'Câmbio Automático' no texto da página")
elif 'cambio automatico' in page_text.lower():
    print("✅ ENCONTRADO: 'Cambio Automatico' no texto da página")
elif 'câmbio manual' in page_text.lower():
    print("✅ ENCONTRADO: 'Câmbio Manual' no texto da página")
elif 'cambio manual' in page_text.lower():
    print("✅ ENCONTRADO: 'Cambio Manual' no texto da página")
else:
    print("❌ 'Câmbio' não encontrado no texto")

# Mostrar todas as ocorrências de "câmbio" ou "cambio"
cambio_matches = re.findall(r'.{0,30}[cC][âa]mbio.{0,30}', page_text)
if cambio_matches:
    print(f"\n📋 Todas as ocorrências de 'câmbio' ({len(cambio_matches)}):")
    for i, match in enumerate(cambio_matches[:5], 1):
        print(f"   {i}. {match.strip()}")
