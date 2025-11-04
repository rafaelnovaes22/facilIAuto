"""
Scraper para RP Multimarcas - Extração de dados de veículos
Site: https://rpmultimarcas.com.br/
Seção: Nossos veículos

IMPORTANTE: Segue princípio "Nunca Invente Dados"
- Retorna None quando dado não existe
- Não assume valores padrão
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import time
import hashlib


class RPMultimarcasScraper:
    """Scraper para o site RP Multimarcas"""
    
    def __init__(self):
        self.base_url = "https://rpmultimarcas.com.br"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_price(self, text: str) -> Optional[float]:
        """
        Extrair preço do texto
        Retorna None se não encontrar
        """
        if not text:
            return None
        
        # Remover "R$" e espaços
        text = text.replace('R$', '').replace(' ', '').strip()
        
        # Padrão: 95.990,00 ou 95990
        pattern = r'(\d+(?:\.\d+)*(?:,\d+)?)'
        match = re.search(pattern, text)
        
        if match:
            price_str = match.group(1)
            # Normalizar: remover pontos, trocar vírgula por ponto
            price_str = price_str.replace('.', '').replace(',', '.')
            
            try:
                price = float(price_str)
                if 10000 <= price <= 500000:
                    return price
            except ValueError:
                pass
        
        return None
    
    def extract_km(self, text: str) -> Optional[int]:
        """
        Extrair quilometragem do texto
        Retorna None se não encontrar
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Zero km
        if 'zero km' in text_lower or '0 km' in text_lower or '0km' in text_lower:
            return 0
        
        # Padrão: números seguidos de "km"
        pattern = r'(\d+(?:[.,]\d+)*)\s*(?:mil\s+)?km'
        match = re.search(pattern, text_lower)
        
        if match:
            km_str = match.group(1)
            km_str = km_str.replace('.', '').replace(',', '')
            
            try:
                km = int(km_str)
                
                # Se tem "mil" no texto, multiplicar por 1000
                if 'mil' in text_lower and km < 1000:
                    km *= 1000
                
                if 0 <= km <= 500000:
                    return km
            except ValueError:
                pass
        
        return None
    
    def extract_year(self, text: str) -> Optional[int]:
        """
        Extrair ano do texto
        Retorna None se não encontrar
        """
        if not text:
            return None
        
        # Padrão: YYYY/YYYY ou YYYY
        pattern = r'(\d{4})(?:/(\d{4}))?'
        match = re.search(pattern, text)
        
        if match:
            # Se tem formato YYYY/YYYY, pegar o segundo (ano modelo)
            year = int(match.group(2) if match.group(2) else match.group(1))
            
            if 2010 <= year <= 2026:
                return year
        
        return None
    
    def extract_cambio(self, text: str) -> Optional[str]:
        """
        Extrair tipo de câmbio do texto
        Retorna None se não encontrar (NÃO assume "Manual")
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Padrões de automático
        if 'automático cvt' in text_lower or 'automatico cvt' in text_lower or 'cvt' in text_lower:
            return "Automático CVT"
        elif 'automático' in text_lower or 'automatico' in text_lower or 'automatic' in text_lower:
            return "Automático"
        elif 'automatizada' in text_lower or 'amt' in text_lower:
            return "Automatizada"
        elif 'manual' in text_lower:
            return "Manual"
        
        # Padrões curtos
        if re.search(r'\bA\b', text):
            return "Automático"
        elif re.search(r'\bM\b', text):
            return "Manual"
        
        return None  # Não assumir valor padrão
    
    def extract_combustivel(self, text: str) -> Optional[str]:
        """
        Extrair tipo de combustível
        Retorna None se não encontrar
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        if 'flex' in text_lower:
            return "Flex"
        elif 'gasolina' in text_lower:
            return "Gasolina"
        elif 'diesel' in text_lower:
            return "Diesel"
        elif 'elétrico' in text_lower or 'eletrico' in text_lower:
            return "Elétrico"
        elif 'híbrido' in text_lower or 'hibrido' in text_lower:
            return "Híbrido"
        
        return None
    
    def extract_categoria(self, text: str) -> Optional[str]:
        """
        Extrair categoria do veículo
        Retorna None se não encontrar
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        if 'suv' in text_lower:
            return "SUV"
        elif 'sedan' in text_lower:
            return "Sedan"
        elif 'hatch' in text_lower:
            return "Hatch"
        elif 'pickup' in text_lower or 'picape' in text_lower:
            return "Pickup"
        elif 'van' in text_lower:
            return "Van"
        elif 'compacto' in text_lower:
            return "Compacto"
        
        return None
    
    def calculate_content_hash(self, data: Dict) -> str:
        """Calcular hash MD5 do conteúdo para detecção de mudanças"""
        hashable_data = {
            k: v for k, v in data.items()
            if k not in ['id', 'data_scraping', 'content_hash']
        }
        content_str = json.dumps(hashable_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()
    
    def extract_car_details(self, car_url: str) -> Optional[Dict]:
        """
        Extrair detalhes de um carro específico
        """
        try:
            print(f"      Acessando: {car_url}")
            response = self.session.get(car_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            car_data = {
                'url_original': car_url,
                'data_scraping': datetime.now().isoformat()
            }
            
            # Tentar extrair nome/título
            # Seletores comuns: h1, .title, .car-title, .vehicle-title
            title = (soup.find('h1') or 
                    soup.find(class_='title') or 
                    soup.find(class_='car-title') or
                    soup.find(class_='vehicle-title'))
            
            if title:
                car_data['nome'] = title.text.strip()
            
            # Tentar extrair preço
            # Seletores comuns: .price, .valor, .preco
            price = (soup.find(class_='price') or 
                    soup.find(class_='valor') or 
                    soup.find(class_='preco'))
            
            if price:
                price_value = self.extract_price(price.text)
                if price_value:
                    car_data['preco'] = price_value
            
            # Tentar extrair características
            # Procurar por lista de especificações
            specs = soup.find_all(['li', 'div'], class_=re.compile(r'spec|feature|caracteristica'))
            
            for spec in specs:
                text = spec.text.strip()
                
                # Tentar identificar o tipo de informação
                if 'ano' in text.lower() or 'fabricação' in text.lower():
                    year = self.extract_year(text)
                    if year:
                        car_data['ano'] = year
                
                elif 'km' in text.lower() or 'quilometragem' in text.lower():
                    km = self.extract_km(text)
                    if km is not None:
                        car_data['quilometragem'] = km
                
                elif 'câmbio' in text.lower() or 'cambio' in text.lower() or 'transmissão' in text.lower():
                    cambio = self.extract_cambio(text)
                    if cambio:
                        car_data['cambio'] = cambio
                
                elif 'combustível' in text.lower() or 'combustivel' in text.lower():
                    combustivel = self.extract_combustivel(text)
                    if combustivel:
                        car_data['combustivel'] = combustivel
                
                elif 'cor' in text.lower():
                    # Extrair cor (texto após "Cor:")
                    cor_match = re.search(r'cor:?\s*(.+)', text, re.IGNORECASE)
                    if cor_match:
                        car_data['cor'] = cor_match.group(1).strip()
                
                elif 'porta' in text.lower():
                    # Extrair número de portas
                    portas_match = re.search(r'(\d+)\s*porta', text, re.IGNORECASE)
                    if portas_match:
                        car_data['portas'] = int(portas_match.group(1))
            
            # Tentar extrair imagens
            images = soup.find_all('img', src=re.compile(r'\.(jpg|jpeg|png|webp)', re.IGNORECASE))
            car_images = []
            for img in images:
                src = img.get('src', '')
                # Filtrar imagens de veículos (geralmente contém 'car', 'vehicle', 'veiculo' no path)
                if src and ('car' in src.lower() or 'vehicle' in src.lower() or 'veiculo' in src.lower() or 'upload' in src.lower()):
                    if src.startswith('http'):
                        car_images.append(src)
                    elif src.startswith('/'):
                        car_images.append(self.base_url + src)
            
            if car_images:
                car_data['imagens'] = car_images[:10]  # Máximo 10 imagens
            
            # Tentar extrair descrição
            description = (soup.find(class_='description') or 
                          soup.find(class_='descricao') or
                          soup.find('div', class_=re.compile(r'desc')))
            
            if description:
                car_data['descricao'] = description.text.strip()[:5000]  # Máximo 5000 caracteres
            
            # Calcular hash
            car_data['content_hash'] = self.calculate_content_hash(car_data)
            
            return car_data
            
        except Exception as e:
            print(f"      ❌ Erro ao extrair detalhes: {e}")
            return None
    
    def scrape_listing_page(self) -> List[str]:
        """
        Extrair URLs de carros da página principal
        """
        try:
            print(f"\n📄 Acessando página de listagem...")
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar por links de veículos
            # Seletores comuns: a.car-link, a.vehicle-link, links dentro de .vehicle-card
            car_links = []
            
            # Estratégia 1: Links com classes específicas
            links = soup.find_all('a', class_=re.compile(r'car|vehicle|veiculo', re.IGNORECASE))
            car_links.extend(links)
            
            # Estratégia 2: Links dentro de cards/containers de veículos
            containers = soup.find_all(['div', 'article'], class_=re.compile(r'car|vehicle|veiculo|card', re.IGNORECASE))
            for container in containers:
                link = container.find('a', href=True)
                if link:
                    car_links.append(link)
            
            # Extrair URLs únicas
            urls = set()
            for link in car_links:
                href = link.get('href', '')
                if href:
                    # Garantir URL completa
                    if href.startswith('http'):
                        urls.add(href)
                    elif href.startswith('/'):
                        urls.add(self.base_url + href)
                    else:
                        urls.add(self.base_url + '/' + href)
            
            # Filtrar URLs que parecem ser de veículos
            vehicle_urls = [url for url in urls if any(keyword in url.lower() for keyword in ['veiculo', 'vehicle', 'car', 'estoque'])]
            
            return list(vehicle_urls)
            
        except Exception as e:
            print(f"❌ Erro ao extrair listagem: {e}")
            return []
    
    def scrape_all(self) -> List[Dict]:
        """
        Fazer scraping de todos os veículos
        """
        all_cars = []
        
        print(f"\n🔍 Iniciando scraping do RP Multimarcas...")
        print(f"Site: {self.base_url}")
        
        # Obter URLs dos veículos
        car_urls = self.scrape_listing_page()
        
        if not car_urls:
            print("⚠️  Nenhum veículo encontrado na listagem")
            print("   Isso pode significar que:")
            print("   1. O site usa JavaScript para carregar veículos")
            print("   2. Os seletores CSS precisam ser ajustados")
            print("   3. O site está temporariamente indisponível")
            return []
        
        print(f"   Encontrados {len(car_urls)} veículos")
        
        # Extrair detalhes de cada veículo
        for i, car_url in enumerate(car_urls, 1):
            print(f"\n   [{i}/{len(car_urls)}] Processando veículo...")
            
            car_data = self.extract_car_details(car_url)
            
            if car_data:
                # Validar campos obrigatórios
                required_fields = ['nome', 'preco', 'ano', 'quilometragem']
                missing_fields = [f for f in required_fields if f not in car_data]
                
                if missing_fields:
                    print(f"      ⚠️  Campos obrigatórios faltando: {missing_fields}")
                    print(f"      ⚠️  Veículo será rejeitado")
                else:
                    all_cars.append(car_data)
                    print(f"      ✅ {car_data.get('nome', 'N/A')}")
                    print(f"         Preço: R$ {car_data.get('preco', 0):,.2f}")
                    print(f"         Ano: {car_data.get('ano', 'N/A')}")
                    print(f"         KM: {car_data.get('quilometragem', 'N/A'):,}")
            
            # Delay para não sobrecarregar o servidor
            time.sleep(2)
        
        print(f"\n✅ Scraping concluído: {len(all_cars)} carros válidos de {len(car_urls)} encontrados")
        
        return all_cars
    
    def save_to_json(self, cars: List[Dict], filename: str):
        """
        Salvar dados em JSON
        """
        if not cars:
            print("\n⚠️  Nenhum carro para salvar")
            return
        
        # Adicionar metadata
        output = {
            'metadata': {
                'source': 'rpmultimarcas.com.br',
                'scraper_version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'total_vehicles': len(cars)
            },
            'vehicles': cars
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dados salvos em: {filename}")
        print(f"   Total de veículos: {len(cars)}")


def main():
    """Função principal"""
    scraper = RPMultimarcasScraper()
    
    # Fazer scraping
    cars = scraper.scrape_all()
    
    # Salvar
    if cars:
        scraper.save_to_json(cars, 'rpmultimarcas_estoque.json')
    else:
        print("\n❌ Nenhum carro extraído")
        print("\n💡 Dica: O site pode usar JavaScript para carregar veículos.")
        print("   Neste caso, será necessário:")
        print("   1. Usar Selenium/Playwright para renderizar JavaScript")
        print("   2. Ou extrair dados manualmente e importar via CSV")


if __name__ == "__main__":
    main()
