#!/usr/bin/env python3
"""
🚗 RobustCar Scraper - Sistema de Extração de Estoque
Agente Responsável: Data Analyst 📈

Este módulo extrai dados de carros do site robustcar.com.br
seguindo práticas éticas de web scraping e integração com
nosso framework de recomendação.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import logging
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CarData:
    """Estrutura padronizada dos dados do carro"""
    id: str
    nome: str
    marca: str
    modelo: str
    ano: int
    preco: float
    quilometragem: int
    combustivel: str
    cambio: str
    cor: str
    descricao: str
    imagens: List[str]
    url_original: str
    data_scraping: str
    disponivel: bool = True
    
    # Campos calculados para recomendação
    categoria: str = ""  # hatch, sedan, suv, etc.
    consumo_estimado: float = 0.0
    score_familia: float = 0.0
    score_economia: float = 0.0

class RobustCarScraper:
    """
    Scraper específico para RobustCar com guardrails do AI Engineer
    """
    
    def __init__(self):
        self.base_url = "https://robustcar.com.br"
        self.search_url = "https://robustcar.com.br/busca//pag/{}/ordem/ano-desc/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.carros_extraidos = []
        self.rate_limit_delay = 2  # segundos entre requests
        
    def verificar_robots_txt(self) -> bool:
        """Verificar se o scraping é permitido pelo robots.txt"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = self.session.get(robots_url)
            robots_content = response.text.lower()
            
            # Verificar se há restrições específicas
            if 'disallow: /busca' in robots_content:
                logger.warning("robots.txt proíbe acesso à área de busca")
                return False
                
            logger.info("robots.txt verificado - scraping permitido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar robots.txt: {e}")
            return True  # Continue se não conseguir verificar
    
    def extrair_carros_pagina(self, pagina: int) -> List[CarData]:
        """Extrair carros de uma página específica"""
        url = self.search_url.format(pagina)
        logger.info(f"Extraindo página {pagina}: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            # Fix encoding issue
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            carros = []
            
            # Seletores específicos para RobustCar baseado na análise real
            car_listings = soup.find_all('div', class_='carro')
            
            if not car_listings:
                # Fallback para estrutura alternativa
                car_listings = soup.find_all('div', class_='card')
            
            logger.info(f"Encontrados {len(car_listings)} carros na página {pagina}")
            
            for i, car_element in enumerate(car_listings):
                try:
                    carro = self.extrair_dados_carro(car_element, pagina, i)
                    if carro:
                        carros.append(carro)
                        
                except Exception as e:
                    logger.error(f"Erro ao extrair carro {i} da página {pagina}: {e}")
                    continue
            
            return carros
            
        except Exception as e:
            logger.error(f"Erro ao acessar página {pagina}: {e}")
            return []
    
    def extrair_dados_carro(self, element, pagina: int, index: int) -> Optional[CarData]:
        """Extrair dados de um carro específico"""
        try:
            # Seletores específicos para RobustCar baseado na análise real
            
            # Nome/Título - baseado na análise, está no link principal
            nome = ""
            
            # Tentar diferentes estratégias para encontrar o nome
            # 1. Link principal com href de carros
            link_carros = element.find('a', href=lambda x: x and 'carros/' in x)
            if link_carros:
                nome = link_carros.get_text(strip=True)
            
            # 2. Se não encontrou, tentar extrair do texto geral
            if not nome:
                full_text = element.get_text(strip=True)
                # O texto parece estar junto (ex: "2025CHEVROLET TRACKER T A LTFLEXPRATA...")
                # Vamos tentar separar por ano
                import re
                match = re.search(r'(\d{4})(.+)', full_text)
                if match:
                    ano_texto = match.group(1)
                    resto_texto = match.group(2)
                    # Tentar extrair marca e modelo
                    palavras = resto_texto.split()
                    if len(palavras) >= 2:
                        nome = f"{palavras[0]} {palavras[1]}"
                        if len(palavras) >= 3:
                            nome += f" {palavras[2]}"
            
            # 3. Fallback final
            if not nome:
                nome = f"Carro {pagina}-{index}"
            
            # Preço - estrutura específica da RobustCar: h3.preco > span
            preco = 0.0
            
            # 1. Buscar h3.preco (estrutura real identificada)
            preco_h3 = element.find('h3', class_='preco')
            if preco_h3:
                # O valor está dentro do span
                span_valor = preco_h3.find('span')
                if span_valor:
                    preco_text = span_valor.get_text(strip=True)
                    preco = self.extrair_preco(preco_text)
                else:
                    # Fallback: pegar todo o texto do h3
                    preco_text = preco_h3.get_text(strip=True)
                    preco = self.extrair_preco(preco_text)
            
            # 2. Fallback: buscar div.preco (caso mudança futura)
            if preco == 0.0:
                preco_div = element.find('div', class_='preco')
                if preco_div:
                    preco_text = preco_div.get_text(strip=True)
                    preco = self.extrair_preco(preco_text)
            
            # 3. Último fallback: buscar qualquer texto com valor monetário
            if preco == 0.0:
                text_content = element.get_text()
                import re
                # Buscar padrões como "97.990,00" ou "R$ 97.990,00"
                preco_match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', text_content)
                if preco_match:
                    preco = self.extrair_preco(preco_match.group(1))
            
            # Ano - extrair do nome ou buscar no texto
            ano = self.extrair_ano(nome)
            if ano == 2020:  # Se não encontrou no nome, buscar no elemento
                text_content = element.get_text()
                ano = self.extrair_ano(text_content)
            
            # Quilometragem - buscar no texto do elemento
            text_content = element.get_text()
            quilometragem = self.extrair_quilometragem(text_content)
            
            # URL do carro
            link_element = element.find('a', href=True)
            url_carro = urljoin(self.base_url, link_element['href']) if link_element else ""
            
            # Imagens - RobustCar usa data-src para lazy loading
            img_elements = element.find_all('img')
            imagens = []
            for img in img_elements:
                src = img.get('data-src') or img.get('src')
                if src:
                    if src.startswith('http'):
                        imagens.append(src)
                    else:
                        imagens.append(urljoin(self.base_url, src))
            
            # Extrair marca e modelo do nome
            marca, modelo = self.extrair_marca_modelo(nome)
            
            # Criar ID único
            car_id = f"robust_{pagina}_{index}_{int(time.time())}"
            
            carro = CarData(
                id=car_id,
                nome=nome,
                marca=marca,
                modelo=modelo,
                ano=ano,
                preco=preco,
                quilometragem=quilometragem,
                combustivel=self.inferir_combustivel(nome),
                cambio=self.inferir_cambio(nome),
                cor=self.inferir_cor(nome),
                descricao=nome,
                imagens=imagens,
                url_original=url_carro,
                data_scraping=datetime.now().isoformat(),
                disponivel=True
            )
            
            # Calcular campos para recomendação (AI Engineer)
            carro = self.enriquecer_dados_ia(carro)
            
            return carro
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do carro: {e}")
            return None
    
    def extrair_preco(self, preco_text: str) -> float:
        """Extrair preço numérico do texto - formato brasileiro"""
        try:
            import re
            
            # Limpar texto de entrada
            texto_limpo = preco_text.replace('R$', '').replace(' ', '').strip()
            
            # Buscar padrão específico brasileiro: 97.990,00
            match = re.search(r'(\d{1,3}(?:\.\d{3})*,\d{2})', texto_limpo)
            if match:
                preco_str = match.group(1)
                # Converter formato brasileiro para float
                # 97.990,00 → 97990.00
                preco_str = preco_str.replace('.', '').replace(',', '.')
                return float(preco_str)
            
            # Fallback: buscar qualquer sequência de números
            numeros = re.findall(r'[\d.,]+', texto_limpo)
            if numeros:
                for numero in numeros:
                    try:
                        # Tentar interpretar como formato brasileiro
                        if ',' in numero and numero.count(',') == 1:
                            # Formato: 97.990,00 ou 97990,00
                            numero_convertido = numero.replace('.', '').replace(',', '.')
                            valor = float(numero_convertido)
                            if valor > 1000:  # Sanidade: preço mínimo de carro
                                return valor
                    except:
                        continue
                        
        except Exception as e:
            logger.debug(f"Erro ao extrair preço '{preco_text}': {e}")
        
        return 0.0
    
    def extrair_ano(self, texto: str) -> int:
        """Extrair ano do texto"""
        try:
            import re
            anos = re.findall(r'20\d{2}', texto)
            if anos:
                return int(anos[0])
        except:
            pass
        return 2020
    
    def extrair_quilometragem(self, texto: str) -> int:
        """Extrair quilometragem do texto"""
        try:
            import re
            km_match = re.findall(r'(\d+(?:\.\d+)?)\s*km', texto.lower())
            if km_match:
                km_str = km_match[0].replace('.', '')
                return int(float(km_str))
        except:
            pass
        return 0
    
    def extrair_marca_modelo(self, nome: str) -> tuple:
        """Extrair marca e modelo do nome"""
        marcas_comuns = [
            'Toyota', 'Chevrolet', 'Volkswagen', 'Fiat', 'Honda', 'Hyundai',
            'Ford', 'Nissan', 'Peugeot', 'Renault', 'Citroën', 'Jeep',
            'BMW', 'Mercedes', 'Audi', 'Volvo', 'Mitsubishi', 'Kia'
        ]
        
        nome_upper = nome.upper()
        for marca in marcas_comuns:
            if marca.upper() in nome_upper:
                modelo = nome.replace(marca, '').strip()
                return marca, modelo
        
        # Se não encontrar marca conhecida, usar primeira palavra como marca
        palavras = nome.split()
        if len(palavras) >= 2:
            return palavras[0], ' '.join(palavras[1:])
        
        return 'Genérica', nome
    
    def inferir_combustivel(self, nome: str) -> str:
        """Inferir tipo de combustível baseado no nome"""
        nome_lower = nome.lower()
        if 'flex' in nome_lower:
            return 'Flex'
        elif 'diesel' in nome_lower:
            return 'Diesel'
        elif 'híbrido' in nome_lower or 'hybrid' in nome_lower:
            return 'Híbrido'
        elif 'elétrico' in nome_lower or 'electric' in nome_lower:
            return 'Elétrico'
        else:
            return 'Flex'  # Padrão brasileiro
    
    def inferir_cambio(self, nome: str) -> str:
        """Inferir tipo de câmbio baseado no nome"""
        nome_lower = nome.lower()
        if 'automático' in nome_lower or 'auto' in nome_lower:
            return 'Automático'
        elif 'manual' in nome_lower:
            return 'Manual'
        else:
            return 'Manual'  # Padrão para carros usados
    
    def inferir_cor(self, nome: str) -> str:
        """Inferir cor baseado no nome (limitado)"""
        cores = {
            'branco': 'Branco', 'prata': 'Prata', 'preto': 'Preto',
            'azul': 'Azul', 'vermelho': 'Vermelho', 'cinza': 'Cinza'
        }
        
        nome_lower = nome.lower()
        for cor_key, cor_value in cores.items():
            if cor_key in nome_lower:
                return cor_value
        
        return 'Não informado'
    
    def enriquecer_dados_ia(self, carro: CarData) -> CarData:
        """Enriquecer dados com campos calculados para IA (AI Engineer)"""
        
        # Categorizar tipo de veículo
        nome_lower = carro.nome.lower()
        if any(term in nome_lower for term in ['suv', 'crossover']):
            carro.categoria = 'SUV'
        elif any(term in nome_lower for term in ['sedan', '4 portas']):
            carro.categoria = 'Sedan'
        elif any(term in nome_lower for term in ['hatch', 'hb']):
            carro.categoria = 'Hatch'
        elif any(term in nome_lower for term in ['pickup', 'cabine']):
            carro.categoria = 'Pickup'
        else:
            carro.categoria = 'Hatch'  # Padrão
        
        # Score para famílias (baseado em tipo e ano)
        if carro.categoria in ['SUV', 'Sedan']:
            carro.score_familia = 0.8
        elif carro.categoria == 'Hatch' and carro.ano >= 2018:
            carro.score_familia = 0.6
        else:
            carro.score_familia = 0.4
        
        # Score economia (baseado em ano, marca e categoria)
        economia_base = 0.5
        if carro.ano >= 2020:
            economia_base += 0.2
        if carro.marca.lower() in ['toyota', 'honda', 'hyundai']:
            economia_base += 0.2
        if carro.categoria == 'Hatch':
            economia_base += 0.1
        
        carro.score_economia = min(economia_base, 1.0)
        
        # Estimativa de consumo (aproximada)
        if carro.categoria == 'Hatch':
            carro.consumo_estimado = 12.5
        elif carro.categoria == 'Sedan':
            carro.consumo_estimado = 11.0
        elif carro.categoria == 'SUV':
            carro.consumo_estimado = 9.5
        else:
            carro.consumo_estimado = 10.0
        
        return carro
    
    def scraping_completo(self, max_paginas: int = 10) -> List[CarData]:
        """Executar scraping completo com guardrails"""
        
        if not self.verificar_robots_txt():
            logger.error("Scraping não permitido pelo robots.txt")
            return []
        
        logger.info(f"Iniciando scraping da RobustCar - máximo {max_paginas} páginas")
        
        todos_carros = []
        paginas_vazias = 0
        
        for pagina in range(1, max_paginas + 1):
            carros_pagina = self.extrair_carros_pagina(pagina)
            
            if not carros_pagina:
                paginas_vazias += 1
                if paginas_vazias >= 3:  # Parar se 3 páginas consecutivas vazias
                    logger.info(f"3 páginas vazias consecutivas - parando scraping")
                    break
            else:
                paginas_vazias = 0
                todos_carros.extend(carros_pagina)
                logger.info(f"Página {pagina}: {len(carros_pagina)} carros extraídos")
            
            # Rate limiting para não sobrecarregar o servidor
            time.sleep(self.rate_limit_delay)
        
        logger.info(f"Scraping concluído: {len(todos_carros)} carros extraídos")
        self.carros_extraidos = todos_carros
        return todos_carros
    
    def salvar_dados(self, formato: str = 'json') -> str:
        """Salvar dados extraídos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if formato == 'json':
            filename = f"robustcar_estoque_{timestamp}.json"
            dados = [asdict(carro) for carro in self.carros_extraidos]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
                
        elif formato == 'csv':
            filename = f"robustcar_estoque_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if self.carros_extraidos:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.carros_extraidos[0]).keys())
                    writer.writeheader()
                    for carro in self.carros_extraidos:
                        writer.writerow(asdict(carro))
        
        logger.info(f"Dados salvos em: {filename}")
        return filename
    
    def gerar_relatorio_estoque(self) -> Dict:
        """Gerar relatório resumido do estoque"""
        if not self.carros_extraidos:
            return {}
        
        total_carros = len(self.carros_extraidos)
        preco_medio = sum(c.preco for c in self.carros_extraidos) / total_carros
        
        # Análise por marca
        marcas = {}
        for carro in self.carros_extraidos:
            marcas[carro.marca] = marcas.get(carro.marca, 0) + 1
        
        # Análise por categoria
        categorias = {}
        for carro in self.carros_extraidos:
            categorias[carro.categoria] = categorias.get(carro.categoria, 0) + 1
        
        # Análise por faixa de preço
        faixas_preco = {
            "até 30k": len([c for c in self.carros_extraidos if c.preco <= 30000]),
            "30k-50k": len([c for c in self.carros_extraidos if 30000 < c.preco <= 50000]),
            "50k-80k": len([c for c in self.carros_extraidos if 50000 < c.preco <= 80000]),
            "80k+": len([c for c in self.carros_extraidos if c.preco > 80000])
        }
        
        relatorio = {
            "total_carros": total_carros,
            "preco_medio": round(preco_medio, 2),
            "por_marca": marcas,
            "por_categoria": categorias,
            "por_faixa_preco": faixas_preco,
            "data_scraping": datetime.now().isoformat()
        }
        
        return relatorio

def main():
    """Função principal para execução do scraper"""
    scraper = RobustCarScraper()
    
    print("🚗 RobustCar Scraper - Iniciando...")
    print("="*50)
    
    # Executar scraping
    carros = scraper.scraping_completo(max_paginas=5)  # Começar com 5 páginas
    
    if carros:
        print(f"\n✅ Scraping concluído: {len(carros)} carros extraídos")
        
        # Salvar dados
        arquivo_json = scraper.salvar_dados('json')
        arquivo_csv = scraper.salvar_dados('csv')
        
        # Gerar relatório
        relatorio = scraper.gerar_relatorio_estoque()
        print(f"\n📊 Relatório do Estoque:")
        print(f"Total de carros: {relatorio['total_carros']}")
        print(f"Preço médio: R$ {relatorio['preco_medio']:,.2f}")
        print(f"Marcas: {list(relatorio['por_marca'].keys())}")
        print(f"Categorias: {list(relatorio['por_categoria'].keys())}")
        
        print(f"\n💾 Arquivos salvos:")
        print(f"- {arquivo_json}")
        print(f"- {arquivo_csv}")
        
    else:
        print("❌ Nenhum carro foi extraído. Verifique a estrutura do site.")

if __name__ == "__main__":
    main()
