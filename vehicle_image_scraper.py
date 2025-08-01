#!/usr/bin/env python3
"""
Sistema de scraping inteligente para imagens de veículos do RobustCar
Busca imagens de alta qualidade no site www.robustcar.com.br
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from urllib.parse import quote, urljoin, urlparse
import time
import random
from bs4 import BeautifulSoup
import difflib

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'robustcar_scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RobustCarScraper:
    """Scraper especializado para o site www.robustcar.com.br"""
    
    def __init__(self):
        self.base_url = "https://www.robustcar.com.br"
        self.scraped_images = {}
        self.failed_searches = []
        self.vehicle_matches = {}
        
        self.stats = {
            'vehicles_processed': 0,
            'successful_matches': 0,
            'failed_matches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'total_images_found': 0,
            'high_quality_images': 0,
            'robustcar_vehicles_found': 0
        }
        
        # Configurações de qualidade
        self.min_width = 400
        self.min_height = 300
        self.preferred_width = 800
        self.preferred_height = 600
        
        # User agents para rotação
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Cache de veículos do RobustCar
        self.robustcar_vehicles = []
    
    async def get_robustcar_vehicles(self, session: aiohttp.ClientSession) -> List[Dict]:
        """Obtém lista de veículos disponíveis no RobustCar usando o padrão de busca"""
        if self.robustcar_vehicles:  # Cache
            return self.robustcar_vehicles
        
        logger.info("Buscando veículos disponíveis no RobustCar...")
        
        all_vehicles = []
        
        try:
            # Usar o padrão específico do RobustCar para busca paginada
            base_search_url = f"{self.base_url}/busca//pag"
            
            # Buscar nas primeiras páginas (geralmente suficiente)
            for page in range(1, 6):  # Páginas 1 a 5
                search_url = f"{base_search_url}/{page}/ordem/ano-desc/"
                
                try:
                    logger.info(f"Buscando página {page}: {search_url}")
                    
                    async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            html = await response.text()
                            vehicles = self._parse_vehicle_listing(html, search_url)
                            
                            if vehicles:
                                all_vehicles.extend(vehicles)
                                logger.info(f"Encontrados {len(vehicles)} veículos na página {page}")
                            else:
                                logger.info(f"Nenhum veículo encontrado na página {page}")
                                # Se não encontrou veículos, pode ter chegado ao fim
                                if page > 1:
                                    break
                        else:
                            logger.warning(f"Erro HTTP {response.status} na página {page}")
                            
                except Exception as e:
                    logger.warning(f"Erro ao acessar página {page}: {str(e)}")
                    continue
                
                # Pausa entre páginas para ser respeitoso
                await asyncio.sleep(1)
            
            if all_vehicles:
                # Remover duplicatas baseado na combinação marca+modelo+ano
                unique_vehicles = []
                seen = set()
                
                for vehicle in all_vehicles:
                    key = f"{vehicle['marca']}-{vehicle['modelo']}-{vehicle.get('ano', '')}"
                    if key not in seen:
                        seen.add(key)
                        unique_vehicles.append(vehicle)
                
                self.robustcar_vehicles = unique_vehicles
                self.stats['robustcar_vehicles_found'] = len(unique_vehicles)
                logger.info(f"Total: {len(unique_vehicles)} veículos únicos encontrados no RobustCar")
                return unique_vehicles
            else:
                logger.warning("Nenhum veículo encontrado no RobustCar")
                return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar veículos no RobustCar: {str(e)}")
            return []
    
    def _parse_vehicle_listing(self, html: str, base_url: str) -> List[Dict]:
        """Extrai informações de veículos da página de listagem"""
        vehicles = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Padrões comuns para cards de veículos
            vehicle_selectors = [
                '.vehicle-card', '.car-card', '.produto', '.item-veiculo',
                '.veiculo', '.card-veiculo', '.listing-item', '.vehicle-item',
                '[data-vehicle]', '[data-car]'
            ]
            
            vehicle_elements = []
            for selector in vehicle_selectors:
                elements = soup.select(selector)
                if elements:
                    vehicle_elements = elements
                    break
            
            # Se não encontrou com seletores específicos, tentar padrões genéricos
            if not vehicle_elements:
                # Buscar por links que contenham palavras-chave de veículos
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    # Verificar se o link parece ser de um veículo
                    if any(keyword in href.lower() or keyword in text for keyword in 
                           ['veiculo', 'carro', 'auto', 'seminovo', 'usado']):
                        vehicle_elements.append(link)
            
            for element in vehicle_elements:
                try:
                    vehicle_data = self._extract_vehicle_data(element, base_url)
                    if vehicle_data:
                        vehicles.append(vehicle_data)
                except Exception as e:
                    logger.debug(f"Erro ao extrair dados do veículo: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse da listagem: {str(e)}")
        
        return vehicles
    
    def _extract_vehicle_data(self, element, base_url: str) -> Optional[Dict]:
        """Extrai dados de um veículo específico do HTML"""
        try:
            # Extrair texto do elemento
            text = element.get_text(strip=True)
            
            # Extrair link se disponível
            link = element.get('href') if element.name == 'a' else element.find('a')
            if link and hasattr(link, 'get'):
                link = link.get('href')
            elif isinstance(link, str):
                pass
            else:
                link = None
            
            if link and not link.startswith('http'):
                link = urljoin(base_url, link)
            
            # Tentar extrair marca e modelo do texto
            marca, modelo, ano = self._parse_vehicle_info(text)
            
            if marca and modelo:
                return {
                    'marca': marca,
                    'modelo': modelo,
                    'ano': ano,
                    'link': link,
                    'text': text,
                    'source': 'robustcar'
                }
        
        except Exception as e:
            logger.debug(f"Erro ao extrair dados do veículo: {str(e)}")
        
        return None
    
    def _parse_vehicle_info(self, text: str) -> tuple:
        """Extrai marca, modelo e ano do texto"""
        # Marcas conhecidas
        marcas_conhecidas = [
            'TOYOTA', 'HONDA', 'VOLKSWAGEN', 'HYUNDAI', 'CHEVROLET', 'FORD',
            'NISSAN', 'BMW', 'FIAT', 'JEEP', 'RENAULT', 'KIA', 'MITSUBISHI',
            'PEUGEOT', 'CAOA', 'AUDI', 'MERCEDES', 'VOLVO', 'SUBARU'
        ]
        
        text_upper = text.upper()
        marca = None
        modelo = None
        ano = None
        
        # Buscar marca
        for m in marcas_conhecidas:
            if m in text_upper:
                marca = m
                break
        
        # Buscar ano (4 dígitos entre 1990 e 2030)
        ano_match = re.search(r'\b(19[9]\d|20[0-3]\d)\b', text)
        if ano_match:
            ano = int(ano_match.group(1))
        
        # Tentar extrair modelo (palavra após a marca)
        if marca:
            marca_pos = text_upper.find(marca)
            if marca_pos >= 0:
                after_marca = text[marca_pos + len(marca):].strip()
                # Pegar as próximas palavras como modelo
                modelo_words = after_marca.split()[:3]  # Máximo 3 palavras
                if modelo_words:
                    modelo = ' '.join(modelo_words).strip('.,!?-')
        
        return marca, modelo, ano
    
    def find_best_match(self, target_vehicle: Dict, robustcar_vehicles: List[Dict]) -> Optional[Dict]:
        """Encontra o melhor match entre veículo do banco e veículos do RobustCar"""
        target_marca = target_vehicle['marca'].upper()
        target_modelo = target_vehicle['modelo'].upper()
        target_ano = target_vehicle.get('ano')
        
        best_match = None
        best_score = 0
        
        for rc_vehicle in robustcar_vehicles:
            score = 0
            
            # Score por marca (peso 40%)
            if rc_vehicle['marca'] == target_marca:
                score += 40
            
            # Score por modelo (peso 50%)
            if rc_vehicle['modelo']:
                modelo_similarity = difflib.SequenceMatcher(
                    None, 
                    target_modelo, 
                    rc_vehicle['modelo'].upper()
                ).ratio()
                score += modelo_similarity * 50
            
            # Score por ano (peso 10%)
            if target_ano and rc_vehicle['ano']:
                ano_diff = abs(target_ano - rc_vehicle['ano'])
                if ano_diff == 0:
                    score += 10
                elif ano_diff <= 2:
                    score += 5
            
            if score > best_score and score >= 60:  # Mínimo 60% de similaridade
                best_score = score
                best_match = rc_vehicle
        
        return best_match
    
    async def extract_images_from_vehicle_page(self, vehicle_url: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Extrai imagens da página específica do veículo no RobustCar"""
        images = []
        
        try:
            async with session.get(vehicle_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.warning(f"Erro HTTP {response.status} ao acessar {vehicle_url}")
                    return images
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Padrões comuns para imagens de veículos
                image_selectors = [
                    'img[src*="veiculo"]', 'img[src*="carro"]', 'img[src*="auto"]',
                    '.vehicle-image img', '.car-image img', '.produto-image img',
                    '.gallery img', '.carousel img', '.slider img',
                    'img[alt*="veículo"]', 'img[alt*="carro"]'
                ]
                
                found_images = set()
                
                for selector in image_selectors:
                    imgs = soup.select(selector)
                    for img in imgs:
                        src = img.get('src') or img.get('data-src') or img.get('data-lazy')
                        if src:
                            if not src.startswith('http'):
                                src = urljoin(vehicle_url, src)
                            found_images.add(src)
                
                # Se não encontrou com seletores específicos, buscar todas as imagens
                if not found_images:
                    all_imgs = soup.find_all('img', src=True)
                    for img in all_imgs:
                        src = img.get('src')
                        if src and not src.startswith('data:'):
                            if not src.startswith('http'):
                                src = urljoin(vehicle_url, src)
                            
                            # Filtrar imagens que parecem ser de veículos
                            if any(keyword in src.lower() for keyword in 
                                   ['veiculo', 'carro', 'auto', 'car', 'vehicle']):
                                found_images.add(src)
                
                # Processar imagens encontradas
                for img_url in found_images:
                    try:
                        # Verificar se a imagem é válida
                        async with session.head(img_url, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                            if img_response.status == 200:
                                content_type = img_response.headers.get('content-type', '')
                                if 'image' in content_type:
                                    images.append({
                                        'url': img_url,
                                        'source': 'robustcar',
                                        'width': 800,  # Estimado
                                        'height': 600,  # Estimado
                                        'quality_score': 90,  # Alta qualidade por ser do site oficial
                                        'content_type': content_type
                                    })
                    except Exception as e:
                        logger.debug(f"Erro ao verificar imagem {img_url}: {str(e)}")
                        continue
                
        except Exception as e:
            logger.error(f"Erro ao extrair imagens de {vehicle_url}: {str(e)}")
        
        return images
    
    async def scrape_robustcar_vehicle_images(self, vehicle: Dict, session: aiohttp.ClientSession) -> List[Dict]:
        """Busca imagens específicas no RobustCar para um veículo"""
        logger.info(f"🔍 Buscando {vehicle['marca']} {vehicle['modelo']} no RobustCar...")
        
        # 1. Obter lista de veículos do RobustCar
        robustcar_vehicles = await self.get_robustcar_vehicles(session)
        
        if not robustcar_vehicles:
            logger.warning("⚠️ Nenhum veículo encontrado no RobustCar")
            return []
        
        # 2. Encontrar melhor match
        best_match = self.find_best_match(vehicle, robustcar_vehicles)
        
        if not best_match:
            logger.warning(f"❌ Nenhum match encontrado para {vehicle['marca']} {vehicle['modelo']}")
            self.stats['failed_matches'] += 1
            return []
        
        logger.info(f"✅ Match encontrado: {best_match['marca']} {best_match['modelo']} ({best_match.get('ano', 'N/A')})")
        self.stats['successful_matches'] += 1
        
        # 3. Extrair imagens da página do veículo
        if best_match['link']:
            images = await self.extract_images_from_vehicle_page(best_match['link'], session)
            
            if images:
                logger.info(f"🖼️ Encontradas {len(images)} imagens no RobustCar")
                return images
        
        # 4. Se não encontrou imagens específicas, usar fallbacks
        logger.warning(f"⚠️ Nenhuma imagem encontrada no RobustCar, usando fallbacks")
        return await self.search_placeholder_images(
            vehicle['marca'], 
            vehicle['modelo'], 
            vehicle.get('ano')
        )
    
    async def search_unsplash_images(self, search_term: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Busca imagens no Unsplash"""
        images = []
        
        try:
            # Unsplash Source API com alta resolução
            base_urls = [
                f"https://source.unsplash.com/1200x800/?{quote(search_term)}",
                f"https://source.unsplash.com/1400x900/?{quote(search_term)}",
                f"https://source.unsplash.com/1600x1000/?{quote(search_term)}"
            ]
            
            for i, url in enumerate(base_urls):
                # Adicionar parâmetro único para evitar cache
                unique_url = f"{url}&sig={int(time.time())}{i}"
                
                try:
                    async with session.head(unique_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            images.append({
                                'url': str(response.url),  # URL final após redirecionamentos
                                'source': 'unsplash',
                                'width': 800 + (i * 200),
                                'height': 600 + (i * 100),
                                'quality_score': 85 + (i * 5)
                            })
                except Exception as e:
                    logger.debug(f"Erro ao verificar Unsplash URL {unique_url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Erro na busca Unsplash para '{search_term}': {str(e)}")
        
        return images
    
    async def search_picsum_images(self, search_term: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Busca imagens no Picsum (Lorem Picsum)"""
        images = []
        
        try:
            # Picsum com alta resolução
            sizes = [
                (1200, 800),
                (1400, 900),
                (1600, 1000)
            ]
            
            for i, (width, height) in enumerate(sizes):
                # Usar ID baseado no hash do termo de busca para consistência
                image_id = abs(hash(search_term)) % 1000 + i
                url = f"https://picsum.photos/{width}/{height}?random={image_id}"
                
                try:
                    async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            images.append({
                                'url': url,
                                'source': 'picsum',
                                'width': width,
                                'height': height,
                                'quality_score': 70 + (i * 5)
                            })
                except Exception as e:
                    logger.debug(f"Erro ao verificar Picsum URL {url}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Erro na busca Picsum para '{search_term}': {str(e)}")
        
        return images
    
    async def search_placeholder_images(self, marca: str, modelo: str, ano: int = None) -> List[Dict]:
        """Gera placeholders personalizados de alta qualidade"""
        images = []
        
        # Cores por marca
        brand_colors = {
            'TOYOTA': 'CC0000', 'HONDA': 'E60012', 'VOLKSWAGEN': '1E3A8A',
            'HYUNDAI': '002C5F', 'CHEVROLET': 'FCC200', 'FORD': '003478',
            'NISSAN': 'C3002F', 'BMW': '0066B2', 'FIAT': '8B0000',
            'JEEP': '1B4332', 'RENAULT': 'FFCC00', 'KIA': '05141F'
        }
        
        brand_color = brand_colors.get(marca.upper(), '666666')
        text_color = 'FFFFFF' if self._is_dark_color(f"#{brand_color}") else '000000'
        
        # Diferentes tamanhos e textos
        configs = [
            (800, 600, f"{marca} {modelo}"),
            (1024, 768, f"{marca} {modelo} {ano}" if ano else f"{marca} {modelo}"),
            (1200, 800, f"{marca}\n{modelo}")
        ]
        
        for i, (width, height, text) in enumerate(configs):
            url = f"https://via.placeholder.com/{width}x{height}/{brand_color}/{text_color}?text={quote(text)}"
            
            images.append({
                'url': url,
                'source': 'placeholder',
                'width': width,
                'height': height,
                'quality_score': 60 + (i * 5)
            })
        
        return images
    
    def _is_dark_color(self, hex_color: str) -> bool:
        """Verifica se uma cor é escura"""
        hex_color = hex_color.replace('#', '')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    
    async def scrape_vehicle_images(self, vehicle: Dict, max_images: int = 5) -> List[Dict]:
        """Faz scraping de imagens para um veículo específico no RobustCar"""
        marca = vehicle['marca']
        modelo = vehicle['modelo']
        ano = vehicle.get('ano')
        
        logger.info(f"🔍 Buscando imagens para {marca} {modelo} {ano} no RobustCar...")
        
        # Configurar sessão HTTP
        connector = aiohttp.TCPConnector(limit=3)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': random.choice(self.user_agents)}
        ) as session:
            
            # 1. Primeiro tentar buscar no RobustCar
            robustcar_images = await self.scrape_robustcar_vehicle_images(vehicle, session)
            
            if robustcar_images:
                # Filtrar e limitar imagens do RobustCar
                filtered_images = robustcar_images[:max_images]
                self.stats['total_images_found'] += len(filtered_images)
                self.stats['high_quality_images'] += len([img for img in filtered_images if img['quality_score'] >= 80])
                
                logger.info(f"✅ Encontradas {len(filtered_images)} imagens no RobustCar para {marca} {modelo}")
                return filtered_images
            
            # 2. Se não encontrou no RobustCar, usar fallbacks
            logger.warning(f"⚠️ Nenhuma imagem encontrada no RobustCar para {marca} {modelo}, usando fallbacks...")
            
            all_images = []
            
            # Buscar em fontes alternativas como backup
            search_term = f"{marca} {modelo}"
            
            try:
                # Unsplash como backup
                unsplash_images = await self.search_unsplash_images(search_term, session)
                all_images.extend(unsplash_images)
                
                await asyncio.sleep(0.5)
                
                # Picsum como backup
                picsum_images = await self.search_picsum_images(search_term, session)
                all_images.extend(picsum_images)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Erro na busca de backup: {str(e)}")
            
            # Adicionar placeholders personalizados
            placeholder_images = await self.search_placeholder_images(marca, modelo, ano)
            all_images.extend(placeholder_images)
            
            # Filtrar e ordenar por qualidade
            filtered_images = []
            seen_urls = set()
            
            for img in all_images:
                if img['url'] not in seen_urls and img['width'] >= self.min_width and img['height'] >= self.min_height:
                    seen_urls.add(img['url'])
                    filtered_images.append(img)
            
            # Ordenar por score de qualidade
            filtered_images.sort(key=lambda x: x['quality_score'], reverse=True)
            
            # Retornar as melhores imagens
            result = filtered_images[:max_images]
            
            self.stats['total_images_found'] += len(result)
            self.stats['high_quality_images'] += len([img for img in result if img['quality_score'] >= 80])
            
            logger.info(f"✅ Encontradas {len(result)} imagens de backup para {marca} {modelo}")
            return result
    
    async def scrape_multiple_vehicles(self, vehicles: List[Dict], max_concurrent: int = 3) -> Dict[str, List[Dict]]:
        """Faz scraping para múltiplos veículos com controle de concorrência"""
        logger.info(f"Iniciando scraping para {len(vehicles)} veículos...")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(vehicle: Dict) -> Tuple[str, List[Dict]]:
            async with semaphore:
                try:
                    images = await self.scrape_vehicle_images(vehicle)
                    self.stats['vehicles_processed'] += 1
                    self.stats['successful_searches'] += 1
                    
                    # Pausa entre veículos para ser respeitoso com os serviços
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    return str(vehicle['vehicle_id']), images
                    
                except Exception as e:
                    logger.error(f"Erro no scraping para {vehicle['marca']} {vehicle['modelo']}: {str(e)}")
                    self.stats['vehicles_processed'] += 1
                    self.stats['failed_searches'] += 1
                    self.failed_searches.append({
                        'vehicle_id': vehicle['vehicle_id'],
                        'marca': vehicle['marca'],
                        'modelo': vehicle['modelo'],
                        'error': str(e)
                    })
                    return str(vehicle['vehicle_id']), []
        
        # Executar scraping em paralelo
        tasks = [scrape_with_semaphore(vehicle) for vehicle in vehicles]
        results = await asyncio.gather(*tasks)
        
        # Organizar resultados
        scraped_data = {}
        for vehicle_id, images in results:
            scraped_data[vehicle_id] = images
        
        logger.info(f"Scraping concluído! {self.stats['successful_searches']} sucessos, {self.stats['failed_searches']} falhas")
        return scraped_data
    
    def save_scraped_data(self, scraped_data: Dict, filename: str = None) -> str:
        """Salva dados do scraping em arquivo"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_images_{timestamp}.json"
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'failed_searches': self.failed_searches,
            'scraped_images': scraped_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dados do scraping salvos em: {filename}")
        return filename
    
    def print_scraping_summary(self):
        """Imprime resumo do scraping"""
        print("\n" + "="*60)
        print("🔍 RESUMO DO SCRAPING DE IMAGENS")
        print("="*60)
        print(f"🚗 Veículos processados: {self.stats['vehicles_processed']}")
        print(f"✅ Buscas bem-sucedidas: {self.stats['successful_searches']}")
        print(f"❌ Buscas falharam: {self.stats['failed_searches']}")
        print(f"🖼️  Total de imagens encontradas: {self.stats['total_images_found']}")
        print(f"⭐ Imagens de alta qualidade: {self.stats['high_quality_images']}")
        
        if self.stats['vehicles_processed'] > 0:
            success_rate = (self.stats['successful_searches'] / self.stats['vehicles_processed']) * 100
            avg_images = self.stats['total_images_found'] / self.stats['vehicles_processed']
            print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
            print(f"📊 Média de imagens por veículo: {avg_images:.1f}")
        
        print("="*60)

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fazer scraping de imagens de veículos')
    parser.add_argument('--input', '-i', required=True, help='Arquivo JSON com veículos que precisam de scraping')
    parser.add_argument('--output', '-o', help='Arquivo de saída para imagens encontradas')
    parser.add_argument('--max-concurrent', type=int, default=3, help='Máximo de buscas simultâneas')
    parser.add_argument('--max-images', type=int, default=5, help='Máximo de imagens por veículo')
    parser.add_argument('--verbose', '-v', action='store_true', help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Carregar dados de entrada
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        vehicles_needing_scraping = input_data.get('vehicles_needing_scraping', [])
        
        if not vehicles_needing_scraping:
            logger.error("Nenhum veículo encontrado no arquivo de entrada")
            return
        
        logger.info(f"Carregados {len(vehicles_needing_scraping)} veículos para scraping")
        
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de entrada: {str(e)}")
        return
    
    # Executar scraping
    scraper = RobustCarScraper()
    
    try:
        scraped_data = await scraper.scrape_multiple_vehicles(
            vehicles_needing_scraping,
            max_concurrent=args.max_concurrent
        )
        
        # Salvar resultados
        output_file = scraper.save_scraped_data(scraped_data, args.output)
        
        # Mostrar resumo
        scraper.print_scraping_summary()
        
        logger.info(f"✅ Scraping concluído! Resultados salvos em: {output_file}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante scraping: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())