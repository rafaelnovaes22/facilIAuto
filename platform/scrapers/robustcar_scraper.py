"""
Scraper para RobustCar - Extração de dados de veículos
Corrigido para extrair câmbio e quilometragem corretamente
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import time


class RobustCarScraper:
    """Scraper para o site RobustCar"""
    
    def __init__(self):
        self.base_url = "https://robustcar.com.br"
        # URL que funcionou anteriormente
        self.search_url_template = "https://robustcar.com.br/busca//pag/{}/ordem/ano-desc/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_cambio(self, text: str) -> Optional[str]:
        """
        Extrair tipo de câmbio do texto
        
        Padrões comuns:
        - "Câmbio: Manual"
        - "Câmbio: Automático"
        - "Câmbio: Automático CVT"
        - "M" ou "A" ou "CVT"
        
        IMPORTANTE: Retorna None se não encontrar, NÃO assume valor padrão
        """
        if not text:
            return None  # Não assumir valor padrão
        
        text_lower = text.lower()
        
        # Padrões de automático
        if 'automático cvt' in text_lower or 'automatico cvt' in text_lower or 'cvt' in text_lower:
            return "Automático CVT"
        elif 'automático' in text_lower or 'automatico' in text_lower or 'automatic' in text_lower:
            return "Automático"
        elif 'automatizada' in text_lower:
            return "Automatizada"
        elif 'manual' in text_lower:
            return "Manual"
        
        # Padrões curtos
        if re.search(r'\bA\b', text):  # "A" isolado
            return "Automático"
        elif re.search(r'\bM\b', text):  # "M" isolado
            return "Manual"
        
        return None  # Não assumir valor padrão se não encontrar
    
    def extract_quilometragem(self, text: str) -> int:
        """
        Extrair quilometragem do texto
        
        Padrões comuns:
        - "50.000 km"
        - "50000 km"
        - "50 mil km"
        - "0 km" ou "Zero km"
        """
        if not text:
            return 0
        
        text_lower = text.lower()
        
        # Zero km
        if 'zero km' in text_lower or '0 km' in text_lower or '0km' in text_lower:
            return 0
        
        # Padrão: números seguidos de "km"
        # Ex: "50.000 km", "50000 km", "50,000 km"
        pattern = r'(\d+(?:[.,]\d+)*)\s*(?:mil\s+)?km'
        match = re.search(pattern, text_lower)
        
        if match:
            km_str = match.group(1)
            # Remover pontos e vírgulas
            km_str = km_str.replace('.', '').replace(',', '')
            
            try:
                km = int(km_str)
                
                # Se tem "mil" no texto, multiplicar por 1000
                if 'mil' in text_lower and km < 1000:
                    km *= 1000
                
                return km
            except ValueError:
                return 0
        
        return 0
    
    def extract_car_details(self, car_url: str) -> Optional[Dict]:
        """
        Extrair detalhes de um carro específico
        Dados estão na seção "Resumo" com formato: Combustível FLEX Cor BRANCO KM 51.985 Ano Fab 2024 Ano Modelo 2025
        """
        try:
            response = self.session.get(car_url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            car_data = {
                'url_original': car_url,
                'data_scraping': datetime.now().isoformat()
            }
            
            # Buscar seção "Resumo" especificamente
            resumo_section = None
            
            # Estratégia 1: Buscar por ID ou classe "resumo"
            resumo_section = (soup.find(id=re.compile(r'resumo', re.IGNORECASE)) or
                            soup.find(class_=re.compile(r'resumo', re.IGNORECASE)))
            
            # Estratégia 2: Buscar por heading "Resumo" e pegar a seção seguinte
            if not resumo_section:
                resumo_heading = soup.find(['h2', 'h3', 'h4'], string=re.compile(r'resumo', re.IGNORECASE))
                if resumo_heading:
                    resumo_section = resumo_heading.find_next(['div', 'section', 'ul'])
            
            # Se encontrou a seção Resumo, extrair texto dela
            if resumo_section:
                resumo_text = resumo_section.get_text()
            else:
                # Fallback: usar texto completo da página
                resumo_text = soup.get_text()
            
            # Extrair nome/título - geralmente em h1
            title = soup.find('h1')
            if title:
                # O título pode conter ano + marca + modelo (ex: "2025 RENAULT KWID ZEN 2")
                title_text = title.text.strip()
                car_data['nome'] = title_text
                
                # Extrair ano do título se presente
                ano_match = re.search(r'^(\d{4})\s+', title_text)
                if ano_match:
                    car_data['ano'] = int(ano_match.group(1))
                    # Remover ano do nome para extrair marca/modelo
                    nome_sem_ano = title_text.replace(ano_match.group(0), '').strip()
                else:
                    nome_sem_ano = title_text
                
                # Extrair marca e modelo
                nome_parts = nome_sem_ano.split()
                if len(nome_parts) >= 2:
                    car_data['marca'] = nome_parts[0].title()
                    car_data['modelo'] = ' '.join(nome_parts[1:])
            
            # Extrair preço - buscar logo após o título (topo da página)
            # Padrão: "R$ 62.990,00"
            page_text = soup.get_text()
            
            # Buscar preço próximo ao título
            price_match = re.search(r'R\$\s*([\d.,]+)', page_text)
            if price_match:
                price_str = price_match.group(1)
                # Normalizar formato brasileiro: 62.990,00 -> 62990.00
                price_str = price_str.replace('.', '').replace(',', '.')
                try:
                    price_value = float(price_str)
                    if 10000 <= price_value <= 500000:
                        car_data['preco'] = price_value
                except ValueError:
                    pass
            
            # Padrão específico RobustCar: "Combustível FLEX"
            combustivel_match = re.search(r'Combustível\s+(\w+)', resumo_text, re.IGNORECASE)
            if combustivel_match:
                comb = combustivel_match.group(1).strip()
                if 'flex' in comb.lower():
                    car_data['combustivel'] = 'Flex'
                elif 'gasolina' in comb.lower():
                    car_data['combustivel'] = 'Gasolina'
                elif 'diesel' in comb.lower():
                    car_data['combustivel'] = 'Diesel'
                elif 'eletrico' in comb.lower() or 'elétrico' in comb.lower():
                    car_data['combustivel'] = 'Elétrico'
            
            # Padrão específico RobustCar: "Cor BRANCO"
            cor_match = re.search(r'Cor\s+([A-ZÀ-Ú\s]+?)(?:Placa|KM|Ano|\n)', resumo_text, re.IGNORECASE)
            if cor_match:
                car_data['cor'] = cor_match.group(1).strip().title()
            
            # Padrão específico RobustCar: "KM 51.985"
            km_match = re.search(r'KM\s+([\d.,]+)', resumo_text, re.IGNORECASE)
            if km_match:
                km_str = km_match.group(1).replace('.', '').replace(',', '')
                try:
                    km_value = int(km_str)
                    if 0 <= km_value <= 500000:
                        car_data['quilometragem'] = km_value
                except ValueError:
                    pass
            
            # Padrão específico RobustCar: "Ano Fab 2024 Ano Modelo 2025"
            # Priorizar Ano Modelo
            ano_modelo_match = re.search(r'Ano\s+Modelo\s+(\d{4})', resumo_text, re.IGNORECASE)
            if ano_modelo_match:
                car_data['ano'] = int(ano_modelo_match.group(1))
            else:
                # Fallback: Ano Fab
                ano_fab_match = re.search(r'Ano\s+Fab\s+(\d{4})', resumo_text, re.IGNORECASE)
                if ano_fab_match:
                    car_data['ano'] = int(ano_fab_match.group(1))
            
                # Buscar seção "Opcionais do Veículo" para extrair câmbio
            opcionais_section = None
            
            # Estratégia 1: Buscar por heading "Opcionais" (com encoding correto)
            opcionais_heading = soup.find(['h2', 'h3', 'h4', 'h5'], string=re.compile(r'opcionais', re.IGNORECASE))
            if opcionais_heading:
                opcionais_section = opcionais_heading.find_next(['div', 'section', 'ul'])
            
            # Estratégia 2: Buscar por classe
            if not opcionais_section:
                opcionais_section = soup.find(class_=re.compile(r'opcionais', re.IGNORECASE))
            
            # Extrair câmbio da seção de opcionais
            if opcionais_section:
                opcionais_text = opcionais_section.get_text()
                
                # Normalizar texto para lidar com encoding issues
                # Remover espaços extras e normalizar
                opcionais_text_clean = ' '.join(opcionais_text.split())
                
                # Buscar "Câmbio Manual" ou "Câmbio Automático" (com variações de encoding)
                # Aceitar: câmbio, cambio, c�mbio
                if re.search(r'c[âa�]mbio\s+autom[áa�]tico', opcionais_text_clean, re.IGNORECASE):
                    if 'cvt' in opcionais_text_clean.lower():
                        car_data['cambio'] = 'Automático CVT'
                    else:
                        car_data['cambio'] = 'Automático'
                elif re.search(r'c[âa�]mbio\s+manual', opcionais_text_clean, re.IGNORECASE):
                    car_data['cambio'] = 'Manual'
            
            # Fallback 1: buscar câmbio no nome do veículo (ex: "AUT.", "MT", "MEC")
            if 'cambio' not in car_data and 'nome' in car_data:
                nome_upper = car_data['nome'].upper()
                
                # Padrões comuns no nome: AUT., AUT, AT, AUTOMÁTICO
                if re.search(r'\bAUT\.?\b|\bAT\b|AUTOM[ÁA]TICO', nome_upper):
                    if 'CVT' in nome_upper:
                        car_data['cambio'] = 'Automático CVT'
                    else:
                        car_data['cambio'] = 'Automático'
                # Padrões manuais: MT, MEC, MANUAL
                elif re.search(r'\bMT\b|\bMEC\.?\b|MANUAL', nome_upper):
                    car_data['cambio'] = 'Manual'
            
            # Fallback 2: buscar câmbio no texto geral se ainda não encontrou
            if 'cambio' not in car_data:
                # Normalizar texto da página
                page_text_clean = ' '.join(page_text.split())
                
                # Buscar padrões mais específicos primeiro
                cambio_match = re.search(r'c[âa�]mbio[:\s]+([a-záàâãéêíóôõúç\s]+?)(?:\n|Cor|KM|Ano|Placa)', page_text_clean, re.IGNORECASE)
                if cambio_match:
                    cambio_text = cambio_match.group(1).strip().lower()
                    if 'autom' in cambio_text:
                        if 'cvt' in cambio_text:
                            car_data['cambio'] = 'Automático CVT'
                        else:
                            car_data['cambio'] = 'Automático'
                    elif 'manual' in cambio_text:
                        car_data['cambio'] = 'Manual'
                # Fallback genérico
                elif re.search(r'autom[áa�]tico', page_text_clean, re.IGNORECASE):
                    if 'cvt' in page_text_clean.lower():
                        car_data['cambio'] = 'Automático CVT'
                    else:
                        car_data['cambio'] = 'Automático'
                elif 'manual' in page_text_clean.lower():
                    car_data['cambio'] = 'Manual'
            
            # Extrair imagens - RobustCar usa data-src para lazy loading
            images = []
            for img in soup.find_all('img'):
                src = img.get('data-src') or img.get('src', '')
                if src and ('carro57' in src or 'robustcar' in src):
                    if src.startswith('http'):
                        images.append(src)
                    elif src.startswith('/'):
                        images.append(self.base_url + src)
            
            if images:
                car_data['imagens'] = list(set(images))[:10]  # Remover duplicatas, máximo 10
            
            # Inferir categoria baseado no nome
            if 'nome' in car_data:
                nome_lower = car_data['nome'].lower()
                if any(term in nome_lower for term in ['suv', 'crossover', 'tracker', 'creta', 'compass', 'renegade']):
                    car_data['categoria'] = 'SUV'
                elif any(term in nome_lower for term in ['sedan', 'cruze', 'civic', 'corolla', 'hb20s']):
                    car_data['categoria'] = 'Sedan'
                elif any(term in nome_lower for term in ['hatch', 'onix', 'hb20', 'gol']):
                    car_data['categoria'] = 'Hatch'
                elif any(term in nome_lower for term in ['pickup', 'strada', 'saveiro', 'montana']):
                    car_data['categoria'] = 'Pickup'
                elif any(term in nome_lower for term in ['mobi', 'up', 'kwid']):
                    car_data['categoria'] = 'Compacto'
            
            return car_data
            
        except Exception as e:
            print(f"      ❌ Erro ao extrair detalhes: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_listing_page(self, page: int = 1) -> List[str]:
        """
        Extrair URLs de carros da página de busca
        Usando URL que funcionou anteriormente
        """
        try:
            # URL que funcionou: /busca//pag/{}/ordem/ano-desc/
            page_url = self.search_url_template.format(page)
            
            print(f"   Acessando: {page_url}")
            response = self.session.get(page_url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Fix encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Seletores específicos que funcionaram
            urls = set()
            
            # Estratégia 1: Buscar div.carro (seletor específico do RobustCar)
            car_divs = soup.find_all('div', class_='carro')
            print(f"   Encontrados {len(car_divs)} div.carro")
            
            for car_div in car_divs:
                link = car_div.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if href:
                        if href.startswith('http'):
                            urls.add(href)
                        elif href.startswith('/'):
                            urls.add(self.base_url + href)
            
            # Estratégia 2: Fallback para div.card
            if not urls:
                card_divs = soup.find_all('div', class_='card')
                print(f"   Fallback: Encontrados {len(card_divs)} div.card")
                
                for card_div in card_divs:
                    link = card_div.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        if href and '/carros/' in href:
                            if href.startswith('http'):
                                urls.add(href)
                            elif href.startswith('/'):
                                urls.add(self.base_url + href)
            
            return list(urls)
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair listagem: {e}")
            return []
    
    def scrape_all(self, max_pages: int = 3) -> List[Dict]:
        """
        Fazer scraping de múltiplas páginas
        """
        all_cars = []
        all_urls = set()
        
        print(f"\n🔍 Iniciando scraping do RobustCar...")
        print(f"Site: {self.base_url}")
        print(f"Páginas a processar: {max_pages}")
        
        # Coletar URLs de todas as páginas primeiro
        for page in range(1, max_pages + 1):
            print(f"\n📄 Coletando URLs da página {page}...")
            
            car_urls = self.scrape_listing_page(page)
            
            if not car_urls:
                print(f"   ⚠️  Nenhuma URL encontrada, parando...")
                break
            
            print(f"   Encontrados {len(car_urls)} URLs")
            all_urls.update(car_urls)
            
            # Delay entre páginas
            time.sleep(2)
        
        print(f"\n📊 Total de URLs únicas coletadas: {len(all_urls)}")
        
        if not all_urls:
            print("\n⚠️  Nenhum veículo encontrado")
            print("   Possíveis causas:")
            print("   1. Site usa JavaScript para carregar veículos")
            print("   2. Seletores CSS precisam ser ajustados")
            print("   3. Site está temporariamente indisponível")
            return []
        
        # Extrair detalhes de cada veículo
        for i, car_url in enumerate(sorted(all_urls), 1):
            print(f"\n   [{i}/{len(all_urls)}] Processando...")
            print(f"   URL: {car_url}")
            
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
            else:
                print(f"      ❌ Falha ao extrair dados")
            
            # Delay para não sobrecarregar o servidor
            time.sleep(2)
        
        print(f"\n✅ Scraping concluído: {len(all_cars)} carros válidos de {len(all_urls)} URLs")
        
        return all_cars
    
    def validate_car_data(self, car: Dict) -> List[str]:
        """
        Validar dados extraídos
        """
        warnings = []
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'preco', 'ano']
        for field in required_fields:
            if field not in car or not car[field]:
                warnings.append(f"Campo obrigatório ausente: {field}")
        
        # Validar câmbio
        if 'cambio' in car:
            valid_cambios = ['Manual', 'Automático', 'Automático CVT', 'Automatizada']
            if car['cambio'] not in valid_cambios:
                warnings.append(f"Câmbio inválido: {car['cambio']}")
        else:
            warnings.append("Câmbio não extraído")
        
        # Validar quilometragem
        if 'quilometragem' not in car:
            warnings.append("Quilometragem não extraída")
        elif car['quilometragem'] == 0 and car.get('ano', 2025) < 2024:
            warnings.append(f"Carro de {car.get('ano')} com 0km é suspeito")
        
        # Validar preço
        if 'preco' in car and car['preco'] <= 0:
            warnings.append("Preço inválido")
        
        return warnings
    
    def save_to_json(self, cars: List[Dict], filename: str):
        """
        Salvar dados em JSON
        """
        # Validar todos os carros
        print(f"\n🔍 Validando {len(cars)} carros...")
        
        total_warnings = 0
        for car in cars:
            warnings = self.validate_car_data(car)
            if warnings:
                total_warnings += len(warnings)
                print(f"\n⚠️  {car.get('nome', 'N/A')}:")
                for warning in warnings:
                    print(f"   - {warning}")
        
        if total_warnings == 0:
            print("✅ Todos os carros validados com sucesso!")
        else:
            print(f"\n⚠️  Total de avisos: {total_warnings}")
        
        # Salvar
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cars, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dados salvos em: {filename}")


def main():
    """Função principal"""
    scraper = RobustCarScraper()
    
    # Fazer scraping - 5 páginas para pegar ~100 veículos
    cars = scraper.scrape_all(max_pages=5)
    
    # Salvar
    if cars:
        scraper.save_to_json(cars, 'robustcar_estoque_new.json')
    else:
        print("\n❌ Nenhum carro extraído")


if __name__ == "__main__":
    main()
