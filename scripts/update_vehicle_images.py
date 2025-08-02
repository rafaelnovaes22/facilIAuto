#!/usr/bin/env python3
"""
Script integrado para atualizar imagens de veículos
Combina análise + scraping + atualização do banco de dados
"""

import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
from typing import List, Dict
import sys
import os

from app.config import DATABASE_CONFIG
from analyze_vehicle_images import ImageQualityAnalyzer
from vehicle_image_scraper import RobustCarScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'update_vehicle_images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VehicleImageUpdater:
    """Classe principal para atualizar imagens de veículos"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.analyzer = ImageQualityAnalyzer()
        self.scraper = RobustCarScraper()
        
        self.stats = {
            'vehicles_analyzed': 0,
            'vehicles_needing_update': 0,
            'vehicles_scraped': 0,
            'vehicles_updated': 0,
            'total_new_images': 0,
            'errors': 0
        }
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    async def analyze_all_images(self) -> Dict:
        """Analisa todas as imagens do banco"""
        logger.info("🔍 ETAPA 1: Analisando qualidade das imagens existentes...")
        
        # Obter veículos do banco
        vehicles = self.analyzer.get_all_vehicles_with_images()
        self.stats['vehicles_analyzed'] = len(vehicles)
        
        # Analisar imagens
        await self.analyzer.analyze_vehicle_images(vehicles)
        
        # Gerar relatório
        report = self.analyzer.generate_report()
        
        # Salvar relatório de análise
        analysis_file = self.analyzer.save_report(report, f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        self.stats['vehicles_needing_update'] = len(report['vehicles_needing_scraping'])
        
        logger.info(f"✅ Análise concluída: {self.stats['vehicles_needing_update']} veículos precisam de novas imagens")
        
        return report
    
    async def scrape_missing_images(self, vehicles_needing_scraping: List[Dict]) -> Dict:
        """Faz scraping de imagens para veículos que precisam"""
        if not vehicles_needing_scraping:
            logger.info("⏭️  Nenhum veículo precisa de scraping")
            return {}
        
        logger.info(f"🔍 ETAPA 2: Fazendo scraping de imagens para {len(vehicles_needing_scraping)} veículos...")
        
        # Executar scraping
        scraped_data = await self.scraper.scrape_multiple_vehicles(vehicles_needing_scraping, max_concurrent=2)
        
        # Salvar dados do scraping
        scraping_file = self.scraper.save_scraped_data(scraped_data, f"scraped_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        self.stats['vehicles_scraped'] = len([v for v in scraped_data.values() if v])
        self.stats['total_new_images'] = sum(len(images) for images in scraped_data.values())
        
        logger.info(f"✅ Scraping concluído: {self.stats['total_new_images']} novas imagens encontradas")
        
        return scraped_data
    
    def update_database_images(self, scraped_data: Dict, dry_run: bool = True) -> None:
        """Atualiza imagens no banco de dados"""
        if not scraped_data:
            logger.info("⏭️  Nenhuma imagem para atualizar no banco")
            return
        
        if dry_run:
            logger.info("🔍 ETAPA 3: Simulando atualização do banco (DRY RUN)...")
        else:
            logger.info("💾 ETAPA 3: Atualizando imagens no banco de dados...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for vehicle_id, images in scraped_data.items():
                if not images:
                    continue
                
                # Extrair apenas as URLs das imagens
                image_urls = [img['url'] for img in images]
                
                if dry_run:
                    logger.info(f"[DRY RUN] Atualizaria veículo ID {vehicle_id} com {len(image_urls)} imagens")
                    for i, url in enumerate(image_urls[:3]):  # Mostrar apenas as 3 primeiras
                        logger.info(f"[DRY RUN]   {i+1}. {url}")
                else:
                    # Atualizar no banco
                    update_query = """
                        UPDATE veiculos 
                        SET 
                            fotos = %s,
                            fotos_validation_status = 'valid',
                            fotos_validated_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """
                    
                    # Tentar converter para int, se falhar usar como string
                    try:
                        vehicle_id_param = int(vehicle_id)
                    except ValueError:
                        vehicle_id_param = vehicle_id
                    
                    cursor.execute(update_query, (image_urls, vehicle_id_param))
                    self.stats['vehicles_updated'] += 1
                    
                    logger.info(f"✅ Atualizado veículo ID {vehicle_id} com {len(image_urls)} imagens")
            
            if not dry_run:
                conn.commit()
                logger.info(f"✅ Banco atualizado com sucesso! {self.stats['vehicles_updated']} veículos atualizados")
            else:
                logger.info(f"✅ Dry run concluído. {len([v for v in scraped_data.values() if v])} veículos seriam atualizados")
                
        except Exception as e:
            if not dry_run:
                conn.rollback()
            logger.error(f"❌ Erro ao atualizar banco: {str(e)}")
            self.stats['errors'] += 1
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_backup(self) -> str:
        """Cria backup das imagens antes das alterações"""
        logger.info("💾 Criando backup das imagens atuais...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_images_before_update_{timestamp}.json"
        
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT id, marca, modelo, fotos, fotos_validation_status, fotos_validated_at
                FROM veiculos 
                WHERE fotos IS NOT NULL 
                ORDER BY id
            """
            
            cursor.execute(query)
            vehicles = cursor.fetchall()
            
            # Converter para formato serializável
            backup_data = []
            for vehicle in vehicles:
                backup_data.append({
                    'id': vehicle['id'],
                    'marca': vehicle['marca'],
                    'modelo': vehicle['modelo'],
                    'fotos': vehicle['fotos'],
                    'fotos_validation_status': vehicle['fotos_validation_status'],
                    'fotos_validated_at': vehicle['fotos_validated_at'].isoformat() if vehicle['fotos_validated_at'] else None
                })
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup criado: {backup_file} ({len(backup_data)} veículos)")
            return backup_file
            
        finally:
            cursor.close()
            conn.close()
    
    async def run_complete_update(self, dry_run: bool = True, force_scraping: bool = False) -> None:
        """Executa o processo completo de atualização"""
        logger.info("🚀 INICIANDO ATUALIZAÇÃO COMPLETA DE IMAGENS DE VEÍCULOS")
        logger.info("="*70)
        
        try:
            # Criar backup
            backup_file = self.create_backup()
            
            # Etapa 1: Análise
            analysis_report = await self.analyze_all_images()
            
            # Mostrar resumo da análise
            self.analyzer.print_summary(analysis_report)
            
            vehicles_needing_scraping = analysis_report['vehicles_needing_scraping']
            
            if not vehicles_needing_scraping and not force_scraping:
                logger.info("🎉 Todas as imagens estão em boa qualidade! Nenhuma atualização necessária.")
                return
            
            # Etapa 2: Scraping
            scraped_data = await self.scrape_missing_images(vehicles_needing_scraping)
            
            # Mostrar resumo do scraping
            self.scraper.print_scraping_summary()
            
            # Etapa 3: Atualização do banco
            self.update_database_images(scraped_data, dry_run=dry_run)
            
            # Relatório final
            self.print_final_report(backup_file, dry_run)
            
        except Exception as e:
            logger.error(f"❌ Erro durante atualização: {str(e)}")
            self.stats['errors'] += 1
            raise
    
    def print_final_report(self, backup_file: str, dry_run: bool):
        """Imprime relatório final"""
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - ATUALIZAÇÃO DE IMAGENS")
        print("="*70)
        print(f"📁 Backup criado: {backup_file}")
        print(f"🔍 Veículos analisados: {self.stats['vehicles_analyzed']}")
        print(f"⚠️  Veículos que precisavam de atualização: {self.stats['vehicles_needing_update']}")
        print(f"🔍 Veículos com scraping bem-sucedido: {self.stats['vehicles_scraped']}")
        print(f"🖼️  Total de novas imagens encontradas: {self.stats['total_new_images']}")
        
        if dry_run:
            print(f"🔍 [DRY RUN] Veículos que seriam atualizados: {len([1 for _ in range(self.stats['vehicles_scraped'])])}")
            print("⚠️  Execute novamente com --apply para aplicar as atualizações")
        else:
            print(f"✅ Veículos atualizados no banco: {self.stats['vehicles_updated']}")
        
        if self.stats['errors'] > 0:
            print(f"❌ Erros encontrados: {self.stats['errors']}")
        
        print("="*70)
        
        if not dry_run and self.stats['vehicles_updated'] > 0:
            print("🎉 ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
        elif dry_run:
            print("🔍 DRY RUN CONCLUÍDO - Nenhuma alteração foi feita")

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Atualizar imagens de veículos no banco')
    parser.add_argument('--apply', action='store_true', 
                       help='Aplicar atualizações no banco (padrão é dry-run)')
    parser.add_argument('--force-scraping', action='store_true',
                       help='Forçar scraping mesmo se não houver problemas detectados')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verificar dependências
    try:
        from PIL import Image
    except ImportError:
        logger.error("❌ Pillow não está instalado. Execute: pip install Pillow")
        sys.exit(1)
    
    updater = VehicleImageUpdater()
    await updater.run_complete_update(
        dry_run=not args.apply,
        force_scraping=args.force_scraping
    )

if __name__ == "__main__":
    asyncio.run(main())