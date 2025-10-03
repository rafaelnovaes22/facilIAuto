#!/usr/bin/env python3
"""
🔍 Análise da Estrutura do Site RobustCar
Agente: Data Analyst 📊

Script para analisar a estrutura HTML real do site
e identificar os seletores corretos para o scraping.
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def analisar_estrutura_site():
    """Analisar estrutura HTML do site RobustCar"""
    
    url = "https://robustcar.com.br/busca//pag/1/ordem/ano-desc/"
    
    print("🔍 Analisando estrutura do site RobustCar...")
    print(f"URL: {url}")
    print("="*60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Length: {len(response.content)} bytes")
        print(f"✅ Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Análise geral da página
        print(f"\n📄 Estrutura Geral:")
        print(f"- Title: {soup.title.string if soup.title else 'Não encontrado'}")
        print(f"- Total de divs: {len(soup.find_all('div'))}")
        print(f"- Total de links: {len(soup.find_all('a'))}")
        print(f"- Total de imagens: {len(soup.find_all('img'))}")
        
        # Procurar por possíveis containers de carros
        print(f"\n🚗 Análise de Containers de Carros:")
        
        # Tentar diferentes seletores comuns
        possible_selectors = [
            ('div[class*="car"]', 'Divs com "car" na classe'),
            ('div[class*="vehicle"]', 'Divs com "vehicle" na classe'),
            ('div[class*="produto"]', 'Divs com "produto" na classe'),
            ('div[class*="item"]', 'Divs com "item" na classe'),
            ('article', 'Tags article'),
            ('div[class*="card"]', 'Divs com "card" na classe'),
            ('.listing', 'Classe .listing'),
            ('.result', 'Classe .result'),
            ('div[id*="result"]', 'Divs com "result" no ID'),
        ]
        
        found_containers = []
        
        for selector, description in possible_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"  ✅ {description}: {len(elements)} elementos")
                    found_containers.extend(elements[:3])  # Pegar apenas 3 para análise
                else:
                    print(f"  ❌ {description}: 0 elementos")
            except Exception as e:
                print(f"  ❌ {description}: Erro - {e}")
        
        # Analisar containers encontrados
        if found_containers:
            print(f"\n🔍 Análise Detalhada dos Containers:")
            
            for i, container in enumerate(found_containers[:3], 1):
                print(f"\n--- Container {i} ---")
                print(f"Tag: {container.name}")
                print(f"Classes: {container.get('class', [])}")
                print(f"ID: {container.get('id', 'N/A')}")
                
                # Procurar texto que pareça nome de carro
                text_content = container.get_text(strip=True)
                if text_content:
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    print(f"Texto (primeiras 3 linhas):")
                    for line in lines[:3]:
                        print(f"  - {line}")
                
                # Procurar links
                links = container.find_all('a', href=True)
                if links:
                    print(f"Links encontrados: {len(links)}")
                    for link in links[:2]:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        print(f"  - {text[:50]}... → {href}")
                
                # Procurar imagens
                images = container.find_all('img')
                if images:
                    print(f"Imagens: {len(images)}")
                
                print(f"HTML snippet:")
                print(f"  {str(container)[:200]}...")
        
        # Procurar por preços
        print(f"\n💰 Análise de Preços:")
        price_selectors = [
            ('span[class*="preco"]', 'Spans com "preco"'),
            ('span[class*="price"]', 'Spans com "price"'),
            ('div[class*="preco"]', 'Divs com "preco"'),
            ('div[class*="price"]', 'Divs com "price"'),
            ('span[class*="valor"]', 'Spans com "valor"'),
            ('.preco', 'Classe .preco'),
            ('.price', 'Classe .price'),
        ]
        
        for selector, description in price_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    print(f"  ✅ {description}: {len(elements)} elementos")
                    for element in elements[:2]:
                        text = element.get_text(strip=True)
                        print(f"    - {text}")
                else:
                    print(f"  ❌ {description}: 0 elementos")
            except Exception as e:
                print(f"  ❌ {description}: Erro - {e}")
        
        # Salvar HTML para análise manual
        with open('robustcar_page_analysis.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"\n💾 HTML completo salvo em: robustcar_page_analysis.html")
        
        # Verificar se é página de JavaScript/SPA
        scripts = soup.find_all('script')
        js_indicators = ['React', 'Vue', 'Angular', 'jquery', 'ajax']
        
        js_found = []
        for script in scripts:
            script_text = script.string or ""
            for indicator in js_indicators:
                if indicator.lower() in script_text.lower():
                    js_found.append(indicator)
        
        if js_found:
            print(f"\n⚠️  Detectado JavaScript: {', '.join(set(js_found))}")
            print("   Site pode carregar conteúdo dinamicamente")
            print("   Considere usar Selenium para scraping")
        
        # Gerar recomendações
        print(f"\n💡 Recomendações:")
        if found_containers:
            print("✅ Encontrados possíveis containers de carros")
            print("📝 Ajuste os seletores no robustcar_scraper.py")
        else:
            print("❌ Nenhum container óbvio encontrado")
            print("🔍 Analise manualmente o arquivo robustcar_page_analysis.html")
            print("🤖 Considere usar Selenium se site usar JavaScript")
        
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar o site: {e}")
        print("\nPossíveis causas:")
        print("- Site fora do ar")
        print("- Bloqueio por User-Agent")
        print("- Necessário autenticação")
        print("- Site protegido por CloudFlare")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")

def gerar_seletores_sugeridos():
    """Gerar sugestões de seletores baseado na análise"""
    
    print(f"\n🔧 Seletores Sugeridos para Ajuste:")
    print("="*50)
    
    # Sugestões baseadas em padrões comuns de sites brasileiros
    selectors_suggestions = {
        "containers_carros": [
            "div.produto-item",
            "div.veiculo-item", 
            "div.carro-card",
            "article.produto",
            "div[data-produto]",
            ".listing-item",
            ".vehicle-card"
        ],
        "nome_carro": [
            "h2.titulo",
            "h3.nome-produto",
            "a.link-produto",
            ".produto-nome",
            ".titulo-veiculo"
        ],
        "preco": [
            "span.preco",
            "div.valor",
            ".price",
            "[data-preco]",
            ".produto-preco"
        ],
        "imagens": [
            "img.produto-imagem",
            ".galeria img",
            ".foto-principal",
            "img[data-src]"
        ]
    }
    
    for category, selectors in selectors_suggestions.items():
        print(f"\n{category.upper()}:")
        for selector in selectors:
            print(f"  - {selector}")
    
    print(f"\n📝 Para ajustar o scraper:")
    print("1. Abra robustcar_scraper.py")
    print("2. Localize a função extrair_carros_pagina()")
    print("3. Ajuste os seletores CSS na linha ~65")
    print("4. Teste novamente: python robustcar_scraper.py")

if __name__ == "__main__":
    analisar_estrutura_site()
    gerar_seletores_sugeridos()
