#!/usr/bin/env python3
"""
Scraper para RP Multimarcas (rpmultimarcas.com.br)
Extrai dados de veículos do site e gera arquivo JSON compatível com FacilIAuto.

Uso:
    python scraper_rp_multimarcas.py
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Adicionar backend ao path para importar o classificador
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.car_classifier import classifier

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RPMultimarcasScraper:
    """Scraper para o site da RP Multimarcas."""
    
    def __init__(self):
        self.base_url = "https://rpmultimarcas.com.br"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.vehicles = []
        
    def normalize_price(self, price_str: str) -> Optional[float]:
        """Normaliza string de preço para float."""
        try:
            # Remove R$, espaços e pontos, substitui vírgula por ponto
            price = re.sub(r'[R$\s.]', '', price_str)
            price = price.replace(',', '.')
            return float(price)
        except (ValueError, AttributeError):
            logger.warning(f"Não foi possível normalizar preço: {price_str}")
            return None
    
    def normalize_km(self, km_str: str) -> Optional[int]:
        """Normaliza string de quilometragem para int."""
        try:
            # Remove 'km' e espaços, mantém apenas números
            km = re.sub(r'[^\d]', '', km_str)
            return int(km) if km else None
        except (ValueError, AttributeError):
            logger.warning(f"Não foi possível normalizar km: {km_str}")
            return None
    
    def extract_year(self, year_str: str) -> Optional[int]:
        """Extrai ano de fabricação do formato '2010/2011'."""
        try:
            # Pega o primeiro ano (ano de fabricação)
            match = re.search(r'(\d{4})/(\d{4})', year_str)
            if match:
                return int(match.group(1))
            return None
        except (ValueError, AttributeError):
            logger.warning(f"Não foi possível extrair ano: {year_str}")
            return None
    
    def parse_vehicle_card(self, card) -> Optional[Dict]:
        """Extrai dados de um card de veículo."""
        try:
            vehicle = {}
            
            # Debug: mostra estrutura do card
            logger.debug(f"Card HTML: {card.prettify()[:500]}")
            
            # Extrai todos os textos do card
            all_texts = [t.strip() for t in card.stripped_strings]
            logger.debug(f"Textos encontrados: {all_texts}")
            
            # Busca marca (primeiro texto, geralmente)
            for text in all_texts:
                if text and len(text) > 2 and not any(c in text for c in ['R$', 'km', '/']):
                    vehicle['marca'] = text
                    break
            
            # Busca ano (formato: 2010/2011)
            for text in all_texts:
                if re.search(r'\d{4}/\d{4}', text):
                    vehicle['ano_texto'] = text
                    vehicle['ano'] = self.extract_year(text)
                    break
            
            # Busca preço (R$ XX.XXX,XX)
            for text in all_texts:
                if 'R$' in text:
                    vehicle['preco_texto'] = text
                    vehicle['preco'] = self.normalize_price(text)
                    break
            
            # Busca quilometragem (XXXXX km)
            for text in all_texts:
                if 'km' in text.lower() and 'R$' not in text:
                    vehicle['km_texto'] = text
                    vehicle['km'] = self.normalize_km(text)
                    break
            
            # Busca versão (texto mais longo que não seja marca, ano, preço ou km)
            for text in all_texts:
                if (len(text) > 10 and 
                    text != vehicle.get('marca') and 
                    text != vehicle.get('ano_texto') and
                    text != vehicle.get('preco_texto') and
                    text != vehicle.get('km_texto')):
                    vehicle['versao'] = text
                    break
            
            # Imagem
            img_elem = card.select_one('img')
            if img_elem:
                img_src = img_elem.get('src', '')
                if img_src and not img_src.startswith('http'):
                    img_src = self.base_url + img_src
                vehicle['imagem'] = img_src
            
            # Link para detalhes
            link_elem = card.select_one('a')
            if link_elem:
                href = link_elem.get('href', '')
                if href and not href.startswith('http'):
                    href = self.base_url + href
                vehicle['url'] = href
            
            # Validação mínima
            if vehicle.get('marca') and vehicle.get('preco'):
                return vehicle
            else:
                logger.warning(f"Card sem dados mínimos: {vehicle}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao processar card: {e}")
            return None
    
    def fetch_vehicles_from_api(self) -> List[Dict]:
        """Busca veículos diretamente da API."""
        api_url = f"{self.base_url}/Home/ListaEstoque"
        
        # Payload vazio para buscar todos os veículos
        payload = {
            'brand': '',
            'model': '',
            'yearMin': 0,
            'yearMax': 0,
            'valueMin': 0,
            'valueMax': 0,
        }
        
        logger.info(f"Buscando veículos da API: {api_url}")
        
        try:
            response = self.session.post(api_url, data=payload, timeout=30)
            response.raise_for_status()
            
            vehicles_data = response.json()
            logger.info(f"API retornou {len(vehicles_data)} veículos")
            
            return vehicles_data
            
        except requests.RequestException as e:
            logger.error(f"Erro ao acessar API: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return []
    
    def parse_api_vehicle(self, data: Dict) -> Optional[Dict]:
        """Converte dados da API para formato intermediário."""
        try:
            vehicle = {}
            
            # Campos da API (baseado no JavaScript)
            vehicle['id_original'] = data.get('id')
            vehicle['marca'] = data.get('marca', '')
            vehicle['modelo'] = data.get('modelo', '')
            vehicle['versao'] = data.get('versao', '')
            vehicle['cor'] = data.get('cor', '')
            vehicle['imagem'] = data.get('imageUrl', '')
            
            # Ano (pode vir como anoFabricacao/anoModelo ou ano)
            ano_fab = data.get('anoFabricacao') or data.get('ano')
            ano_mod = data.get('anoModelo') or data.get('ano')
            if ano_fab:
                vehicle['ano'] = int(ano_fab)
                vehicle['ano_texto'] = f"{ano_fab}/{ano_mod}" if ano_mod else str(ano_fab)
            
            # Preço
            preco = data.get('preco') or data.get('valor')
            if preco:
                vehicle['preco'] = float(preco)
                vehicle['preco_texto'] = f"R$ {preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Quilometragem
            km = data.get('km') or data.get('quilometragem')
            if km:
                vehicle['km'] = int(km)
                vehicle['km_texto'] = f"{km} km"
            
            # Câmbio
            cambio = data.get('cambio', '')
            vehicle['cambio'] = cambio
            
            # Combustível
            combustivel = data.get('combustivel', '')
            vehicle['combustivel'] = combustivel
            
            # Validação mínima
            if vehicle.get('marca') and vehicle.get('preco'):
                return vehicle
            else:
                logger.warning(f"Veículo da API sem dados mínimos: {vehicle}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao processar veículo da API: {e}")
            return None
    
    def scrape_listing_page(self, url: str = None) -> List[Dict]:
        """Extrai veículos da página de listagem (fallback se API falhar)."""
        if url is None:
            url = self.base_url
        
        logger.info(f"Acessando: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Busca todos os cards de veículos
            cards = soup.select('a.psCard')
            
            if not cards:
                # Fallback para outros seletores
                selectors = [
                    '.cardFeatured',
                    '.vehicle-card',
                    '.car-card',
                    '[class*="vehicle"]',
                    'article',
                    '.col-md-4',
                    '.col-lg-4',
                ]
                
                for selector in selectors:
                    cards = soup.select(selector)
                    if cards and len(cards) > 1:
                        logger.info(f"Encontrados {len(cards)} cards com seletor: {selector}")
                        break
            else:
                logger.info(f"Encontrados {len(cards)} cards com seletor: a.psCard")
            
            if not cards:
                logger.warning("Nenhum card encontrado!")
                return []
            
            vehicles = []
            for card in cards:
                vehicle = self.parse_vehicle_card(card)
                if vehicle:
                    vehicles.append(vehicle)
            
            logger.info(f"Extraídos {len(vehicles)} veículos do HTML")
            return vehicles
            
        except requests.RequestException as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return []
    
    def convert_to_faciliauto_format(self, vehicles: List[Dict]) -> List[Dict]:
        """Converte dados extraídos para formato FacilIAuto."""
        faciliauto_vehicles = []
        
        for idx, v in enumerate(vehicles, 1):
            try:
                # Monta nome completo do veículo
                nome_parts = []
                if v.get('marca'):
                    nome_parts.append(v['marca'])
                if v.get('versao'):
                    nome_parts.append(v['versao'])
                
                nome = ' '.join(nome_parts) if nome_parts else f"Veículo {idx}"
                
                # Classificar categoria automaticamente
                marca = v.get('marca', '')
                modelo = v.get('versao', '')
                ano = v.get('ano', 2020)
                categoria = classifier.classify(nome, modelo, ano, marca)
                
                vehicle = {
                    "id": f"rp_{idx:03d}",
                    "nome": nome,
                    "marca": marca,
                    "modelo": v.get('versao', '').split()[0] if v.get('versao') else '',
                    "versao": v.get('versao', ''),
                    "ano": ano,  # Campo correto para o modelo Car
                    "preco": v.get('preco'),
                    "quilometragem": v.get('km'),  # Campo correto para o modelo Car
                    "cambio": "Automático" if v.get('versao', '').lower().find('aut') != -1 else "Manual",
                    "combustivel": "Flex",  # Padrão, pode ser refinado
                    "cor": "",
                    "portas": 4,  # Padrão
                    "imagens": [v.get('imagem')] if v.get('imagem') else [],
                    "url": v.get('url', ''),
                    "categoria": categoria,  # Classificado automaticamente
                    "disponivel": True,
                    "data_atualizacao": datetime.now().isoformat()
                }
                
                faciliauto_vehicles.append(vehicle)
                
            except Exception as e:
                logger.error(f"Erro ao converter veículo {idx}: {e}")
                continue
        
        return faciliauto_vehicles
    
    def save_to_json(self, vehicles: List[Dict], filename: str):
        """Salva veículos em arquivo JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(vehicles, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados salvos em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao salvar JSON: {e}")
    
    def run(self):
        """Executa o scraping completo."""
        logger.info("=== Iniciando scraping RP Multimarcas ===")
        start_time = time.time()
        
        # Tenta buscar da API primeiro
        api_vehicles = self.fetch_vehicles_from_api()
        
        if api_vehicles:
            # Processa veículos da API
            raw_vehicles = []
            for v_data in api_vehicles:
                vehicle = self.parse_api_vehicle(v_data)
                if vehicle:
                    raw_vehicles.append(vehicle)
            
            logger.info(f"Processados {len(raw_vehicles)} veículos da API")
        else:
            # Fallback: extrai do HTML
            logger.warning("API falhou, tentando extrair do HTML...")
            raw_vehicles = self.scrape_listing_page()
        
        if not raw_vehicles:
            logger.error("Nenhum veículo extraído!")
            return
        
        # Salva dados brutos
        self.save_to_json(raw_vehicles, 'rp_multimarcas_raw.json')
        
        # Converte para formato FacilIAuto
        faciliauto_vehicles = self.convert_to_faciliauto_format(raw_vehicles)
        
        # Salva formato FacilIAuto
        output_file = 'platform/backend/data/rpmultimarcas_estoque.json'
        self.save_to_json(faciliauto_vehicles, output_file)
        
        elapsed = time.time() - start_time
        logger.info(f"=== Scraping concluído em {elapsed:.2f}s ===")
        logger.info(f"Total de veículos: {len(faciliauto_vehicles)}")


def main():
    scraper = RPMultimarcasScraper()
    scraper.run()


if __name__ == '__main__':
    main()
