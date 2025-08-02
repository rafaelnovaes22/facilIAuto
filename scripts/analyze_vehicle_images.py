#!/usr/bin/env python3
"""
Sistema completo para análise e avaliação de imagens de veículos
Avalia qualidade, resolução e disponibilidade das imagens no banco
"""

import asyncio
import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from PIL import Image
import io
import requests
from urllib.parse import urlparse
import os

from app.config import DATABASE_CONFIG
from app.image_validation import ImageValidationService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'image_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageQualityAnalyzer:
    """Analisador de qualidade de imagens"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.min_width = 400
        self.min_height = 300
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.min_file_size = 10 * 1024  # 10KB
        self.supported_formats = ['JPEG', 'PNG', 'WebP']
        
        # Estatísticas
        self.stats = {
            'total_vehicles': 0,
            'total_images': 0,
            'valid_images': 0,
            'invalid_images': 0,
            'low_resolution': 0,
            'wrong_format': 0,
            'too_large': 0,
            'too_small': 0,
            'broken_urls': 0,
            'missing_images': 0
        }
        
        # Resultados detalhados
        self.analysis_results = []
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def get_all_vehicles_with_images(self) -> List[Dict]:
        """Obtém todos os veículos do banco"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT 
                    id,
                    marca,
                    modelo,
                    versao,
                    ano,
                    cor,
                    fotos,
                    fotos_validation_status,
                    fotos_validated_at,
                    disponivel
                FROM veiculos 
                WHERE disponivel = true
                ORDER BY marca, modelo, ano
            """
            
            cursor.execute(query)
            vehicles = cursor.fetchall()
            
            logger.info(f"Encontrados {len(vehicles)} veículos no banco")
            return vehicles
            
        finally:
            cursor.close()
            conn.close()
    
    async def analyze_image_quality(self, url: str, session: aiohttp.ClientSession) -> Dict:
        """Analisa a qualidade de uma imagem específica"""
        result = {
            'url': url,
            'is_valid': False,
            'width': 0,
            'height': 0,
            'file_size': 0,
            'format': None,
            'issues': [],
            'quality_score': 0
        }
        
        try:
            # Fazer download da imagem
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    result['issues'].append(f'HTTP {response.status}')
                    return result
                
                # Verificar tamanho do arquivo
                content = await response.read()
                result['file_size'] = len(content)
                
                if result['file_size'] < self.min_file_size:
                    result['issues'].append('Arquivo muito pequeno')
                elif result['file_size'] > self.max_file_size:
                    result['issues'].append('Arquivo muito grande')
                
                # Analisar imagem com PIL
                try:
                    with Image.open(io.BytesIO(content)) as img:
                        result['width'] = img.width
                        result['height'] = img.height
                        result['format'] = img.format
                        
                        # Verificar resolução
                        if img.width < self.min_width or img.height < self.min_height:
                            result['issues'].append(f'Resolução baixa ({img.width}x{img.height})')
                        
                        # Verificar formato
                        if img.format not in self.supported_formats:
                            result['issues'].append(f'Formato não suportado ({img.format})')
                        
                        # Verificar aspect ratio
                        aspect_ratio = img.width / img.height
                        if aspect_ratio < 1.0 or aspect_ratio > 2.0:
                            result['issues'].append(f'Aspect ratio inadequado ({aspect_ratio:.2f})')
                        
                        # Calcular score de qualidade
                        result['quality_score'] = self._calculate_quality_score(result)
                        
                        if len(result['issues']) == 0:
                            result['is_valid'] = True
                            
                except Exception as e:
                    result['issues'].append(f'Erro ao processar imagem: {str(e)}')
                    
        except asyncio.TimeoutError:
            result['issues'].append('Timeout ao baixar imagem')
        except Exception as e:
            result['issues'].append(f'Erro de rede: {str(e)}')
        
        return result
    
    def _calculate_quality_score(self, result: Dict) -> int:
        """Calcula score de qualidade da imagem (0-100)"""
        score = 100
        
        # Penalizar por resolução baixa
        if result['width'] < 600 or result['height'] < 400:
            score -= 20
        elif result['width'] < 800 or result['height'] < 600:
            score -= 10
        
        # Penalizar por tamanho de arquivo inadequado
        if result['file_size'] < 50 * 1024:  # < 50KB
            score -= 15
        elif result['file_size'] > 2 * 1024 * 1024:  # > 2MB
            score -= 10
        
        # Penalizar por formato inadequado
        if result['format'] not in ['JPEG', 'PNG']:
            score -= 5
        
        # Penalizar por aspect ratio inadequado
        if result['width'] > 0 and result['height'] > 0:
            aspect_ratio = result['width'] / result['height']
            if aspect_ratio < 1.2 or aspect_ratio > 1.8:
                score -= 10
        
        return max(0, score)
    
    async def analyze_vehicle_images(self, vehicles: List[Dict]) -> List[Dict]:
        """Analisa imagens de todos os veículos"""
        logger.info("Iniciando análise de qualidade das imagens...")
        
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'FacilIAuto-ImageAnalyzer/1.0'}
        ) as session:
            
            for vehicle in vehicles:
                self.stats['total_vehicles'] += 1
                
                vehicle_result = {
                    'vehicle_id': vehicle['id'],
                    'marca': vehicle['marca'],
                    'modelo': vehicle['modelo'],
                    'versao': vehicle.get('versao'),
                    'ano': vehicle['ano'],
                    'cor': vehicle.get('cor'),
                    'fotos_count': len(vehicle['fotos']) if vehicle['fotos'] else 0,
                    'image_analyses': [],
                    'needs_scraping': False,
                    'quality_issues': [],
                    'average_quality': 0
                }
                
                if not vehicle['fotos'] or len(vehicle['fotos']) == 0:
                    vehicle_result['needs_scraping'] = True
                    vehicle_result['quality_issues'].append('Nenhuma imagem cadastrada')
                    self.stats['missing_images'] += 1
                else:
                    # Analisar cada imagem
                    quality_scores = []
                    
                    for url in vehicle['fotos']:
                        if url and url.strip():
                            self.stats['total_images'] += 1
                            
                            image_analysis = await self.analyze_image_quality(url, session)
                            vehicle_result['image_analyses'].append(image_analysis)
                            
                            if image_analysis['is_valid']:
                                self.stats['valid_images'] += 1
                                quality_scores.append(image_analysis['quality_score'])
                            else:
                                self.stats['invalid_images'] += 1
                                
                                # Categorizar problemas
                                for issue in image_analysis['issues']:
                                    if 'HTTP' in issue:
                                        self.stats['broken_urls'] += 1
                                    elif 'Resolução baixa' in issue:
                                        self.stats['low_resolution'] += 1
                                    elif 'Formato não suportado' in issue:
                                        self.stats['wrong_format'] += 1
                                    elif 'muito grande' in issue:
                                        self.stats['too_large'] += 1
                                    elif 'muito pequeno' in issue:
                                        self.stats['too_small'] += 1
                    
                    # Calcular qualidade média
                    if quality_scores:
                        vehicle_result['average_quality'] = sum(quality_scores) / len(quality_scores)
                    
                    # Determinar se precisa de scraping
                    valid_images = len([a for a in vehicle_result['image_analyses'] if a['is_valid']])
                    
                    if valid_images == 0:
                        vehicle_result['needs_scraping'] = True
                        vehicle_result['quality_issues'].append('Todas as imagens são inválidas')
                    elif valid_images < 3:
                        vehicle_result['needs_scraping'] = True
                        vehicle_result['quality_issues'].append(f'Apenas {valid_images} imagens válidas')
                    elif vehicle_result['average_quality'] < 60:
                        vehicle_result['needs_scraping'] = True
                        vehicle_result['quality_issues'].append(f'Qualidade baixa (score: {vehicle_result["average_quality"]:.1f})')
                
                self.analysis_results.append(vehicle_result)
                
                # Log de progresso
                if self.stats['total_vehicles'] % 10 == 0:
                    logger.info(f"Analisados {self.stats['total_vehicles']} veículos...")
        
        logger.info("Análise de qualidade concluída!")
        return self.analysis_results
    
    def generate_report(self) -> Dict:
        """Gera relatório completo da análise"""
        vehicles_needing_scraping = [v for v in self.analysis_results if v['needs_scraping']]
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats.copy(),
            'summary': {
                'vehicles_analyzed': self.stats['total_vehicles'],
                'vehicles_needing_scraping': len(vehicles_needing_scraping),
                'scraping_percentage': (len(vehicles_needing_scraping) / self.stats['total_vehicles'] * 100) if self.stats['total_vehicles'] > 0 else 0,
                'average_images_per_vehicle': self.stats['total_images'] / self.stats['total_vehicles'] if self.stats['total_vehicles'] > 0 else 0,
                'image_validity_rate': (self.stats['valid_images'] / self.stats['total_images'] * 100) if self.stats['total_images'] > 0 else 0
            },
            'vehicles_needing_scraping': vehicles_needing_scraping,
            'top_issues': self._get_top_issues()
        }
        
        return report
    
    def _get_top_issues(self) -> List[Dict]:
        """Identifica os principais problemas encontrados"""
        issues = [
            {'issue': 'URLs quebradas', 'count': self.stats['broken_urls']},
            {'issue': 'Resolução baixa', 'count': self.stats['low_resolution']},
            {'issue': 'Imagens faltando', 'count': self.stats['missing_images']},
            {'issue': 'Formato inadequado', 'count': self.stats['wrong_format']},
            {'issue': 'Arquivo muito grande', 'count': self.stats['too_large']},
            {'issue': 'Arquivo muito pequeno', 'count': self.stats['too_small']}
        ]
        
        return sorted(issues, key=lambda x: x['count'], reverse=True)
    
    def save_report(self, report: Dict, filename: str = None) -> str:
        """Salva relatório em arquivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_analysis_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo em: {filename}")
        return filename
    
    def print_summary(self, report: Dict):
        """Imprime resumo do relatório"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE ANÁLISE DE IMAGENS")
        print("="*60)
        
        summary = report['summary']
        print(f"🚗 Veículos analisados: {summary['vehicles_analyzed']}")
        print(f"🖼️  Total de imagens: {report['statistics']['total_images']}")
        print(f"✅ Imagens válidas: {report['statistics']['valid_images']}")
        print(f"❌ Imagens inválidas: {report['statistics']['invalid_images']}")
        print(f"📈 Taxa de validade: {summary['image_validity_rate']:.1f}%")
        print(f"📊 Média de imagens por veículo: {summary['average_images_per_vehicle']:.1f}")
        
        print(f"\n🔄 NECESSIDADE DE SCRAPING:")
        print(f"Veículos que precisam de scraping: {summary['vehicles_needing_scraping']}")
        print(f"Porcentagem que precisa de scraping: {summary['scraping_percentage']:.1f}%")
        
        print(f"\n🔍 PRINCIPAIS PROBLEMAS:")
        for issue in report['top_issues'][:5]:
            if issue['count'] > 0:
                print(f"• {issue['issue']}: {issue['count']}")
        
        print("\n" + "="*60)

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analisar qualidade das imagens de veículos')
    parser.add_argument('--output', '-o', help='Arquivo de saída para o relatório')
    parser.add_argument('--verbose', '-v', action='store_true', help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = ImageQualityAnalyzer()
    
    try:
        # 1. Obter veículos do banco
        vehicles = analyzer.get_all_vehicles_with_images()
        
        if not vehicles:
            logger.error("Nenhum veículo encontrado no banco")
            return
        
        # 2. Analisar imagens
        await analyzer.analyze_vehicle_images(vehicles)
        
        # 3. Gerar relatório
        report = analyzer.generate_report()
        
        # 4. Salvar relatório
        report_file = analyzer.save_report(report, args.output)
        
        # 5. Mostrar resumo
        analyzer.print_summary(report)
        
        logger.info(f"✅ Análise concluída! Relatório salvo em: {report_file}")
        
    except Exception as e:
        logger.error(f"❌ Erro durante análise: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())