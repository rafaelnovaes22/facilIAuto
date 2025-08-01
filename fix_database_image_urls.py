#!/usr/bin/env python3
"""
Script para validar e corrigir URLs de imagens no banco de dados
Parte da Task 3: Update database layer to validate and fix existing image URLs
"""

import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

from app.config import DATABASE_CONFIG
from app.image_validation import ImageValidationService
from app.fallback_images import fallback_service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_url_fix.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseImageFixer:
    """Classe para validar e corrigir URLs de imagens no banco"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.validation_results = []
        self.fixed_count = 0
        self.total_processed = 0
        
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def get_all_vehicle_images(self) -> List[Dict]:
        """Obtém todos os veículos com suas imagens do banco"""
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
                    fotos,
                    cor
                FROM veiculos 
                WHERE disponivel = true 
                AND fotos IS NOT NULL 
                AND array_length(fotos, 1) > 0
                ORDER BY id
            """
            
            cursor.execute(query)
            vehicles = cursor.fetchall()
            
            logger.info(f"Encontrados {len(vehicles)} veículos com imagens para validar")
            return vehicles
            
        finally:
            cursor.close()
            conn.close()
    
    async def validate_vehicle_images(self, vehicles: List[Dict]) -> Dict:
        """Valida todas as imagens dos veículos"""
        logger.info("Iniciando validação de imagens...")
        
        all_urls = []
        url_to_vehicle = {}
        
        # Coletar todas as URLs para validação em lote
        for vehicle in vehicles:
            if vehicle['fotos']:
                for url in vehicle['fotos']:
                    if url and url.strip():
                        all_urls.append(url)
                        if url not in url_to_vehicle:
                            url_to_vehicle[url] = []
                        url_to_vehicle[url].append(vehicle)
        
        logger.info(f"Total de {len(all_urls)} URLs para validar")
        
        # Validar URLs em lote
        async with ImageValidationService(timeout=15, max_concurrent=5) as validator:
            validation_results = await validator.validate_multiple_urls(all_urls)
        
        # Organizar resultados por veículo
        vehicle_results = {}
        for vehicle in vehicles:
            vehicle_id = vehicle['id']
            vehicle_results[vehicle_id] = {
                'vehicle': vehicle,
                'image_results': [],
                'needs_fix': False
            }
            
            if vehicle['fotos']:
                for url in vehicle['fotos']:
                    if url and url.strip():
                        # Encontrar resultado da validação para esta URL
                        url_result = next((r for r in validation_results if r.url == url), None)
                        if url_result:
                            vehicle_results[vehicle_id]['image_results'].append(url_result)
                            if not url_result.is_valid:
                                vehicle_results[vehicle_id]['needs_fix'] = True
        
        # Gerar estatísticas
        summary = validator.get_validation_summary(validation_results)
        logger.info(f"Validação concluída: {summary}")
        
        return {
            'vehicle_results': vehicle_results,
            'summary': summary,
            'validation_results': validation_results
        }
    
    def determine_vehicle_category(self, vehicle: Dict) -> str:
        """Determina a categoria do veículo para fallback"""
        modelo = vehicle['modelo'].lower()
        versao = vehicle.get('versao', '').lower() if vehicle.get('versao') else ''
        
        # SUVs e Crossovers
        if any(word in modelo for word in ["tucson", "compass", "kicks", "t-cross", "nivus", "creta", "hr-v", "tracker"]):
            return "suv_compacto"
        
        if any(word in modelo for word in ["santa fe", "sorento", "pilot", "pathfinder"]):
            return "suv_medio"
        
        if any(word in modelo for word in ["x1", "x3", "q3", "glc", "macan"]):
            return "suv_premium"
        
        # Picapes
        if any(word in modelo for word in ["ranger", "hilux", "amarok", "frontier", "s10", "toro"]):
            return "pickup"
        
        # Sedans
        if any(word in modelo for word in ["corolla", "civic", "jetta", "cruze", "sentra", "city"]):
            return "sedan"
        
        # Hatches
        if any(word in modelo for word in ["onix", "hb20", "polo", "gol", "argo", "ka", "march"]):
            return "hatch"
        
        # Default baseado na versão
        if "sedan" in versao or "plus" in modelo:
            return "sedan"
        
        return "hatch"  # Default
    
    def fix_vehicle_images(self, validation_data: Dict) -> List[Dict]:
        """Corrige imagens quebradas dos veículos"""
        logger.info("Iniciando correção de imagens quebradas...")
        
        fixes_to_apply = []
        
        for vehicle_id, data in validation_data['vehicle_results'].items():
            if not data['needs_fix']:
                continue
                
            vehicle = data['vehicle']
            image_results = data['image_results']
            
            # Determinar categoria para fallback
            categoria = self.determine_vehicle_category(vehicle)
            
            # Coletar URLs válidas e gerar fallbacks para inválidas
            new_urls = []
            failed_urls = []
            
            for result in image_results:
                if result.is_valid:
                    new_urls.append(result.url)
                else:
                    failed_urls.append(result.url)
            
            # Se há URLs quebradas, gerar fallbacks
            if failed_urls:
                fallback_urls = fallback_service.get_fallback_images(
                    vehicle['marca'], 
                    vehicle['modelo'], 
                    categoria
                )
                
                # Adicionar fallbacks até ter pelo menos 3 imagens
                needed_fallbacks = max(0, 3 - len(new_urls))
                new_urls.extend(fallback_urls[:needed_fallbacks])
                
                logger.info(f"Veículo {vehicle['marca']} {vehicle['modelo']} (ID: {vehicle_id}): "
                          f"{len(failed_urls)} URLs quebradas, {len(fallback_urls[:needed_fallbacks])} fallbacks adicionados")
            
            # Se ainda não tem imagens suficientes, adicionar mais fallbacks
            if len(new_urls) < 1:
                fallback_urls = fallback_service.get_fallback_images(
                    vehicle['marca'], 
                    vehicle['modelo'], 
                    categoria
                )
                new_urls.extend(fallback_urls[:3])
            
            fixes_to_apply.append({
                'vehicle_id': vehicle_id,
                'vehicle': vehicle,
                'old_urls': vehicle['fotos'],
                'new_urls': new_urls,
                'failed_urls': failed_urls,
                'categoria': categoria
            })
        
        logger.info(f"Preparadas correções para {len(fixes_to_apply)} veículos")
        return fixes_to_apply
    
    def apply_fixes_to_database(self, fixes: List[Dict], dry_run: bool = True) -> None:
        """Aplica as correções no banco de dados"""
        if dry_run:
            logger.info("=== MODO DRY RUN - Nenhuma alteração será feita no banco ===")
        else:
            logger.info("=== APLICANDO CORREÇÕES NO BANCO DE DADOS ===")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for fix in fixes:
                vehicle_id = fix['vehicle_id']
                new_urls = fix['new_urls']
                vehicle = fix['vehicle']
                
                if dry_run:
                    logger.info(f"[DRY RUN] Atualizaria veículo {vehicle['marca']} {vehicle['modelo']} (ID: {vehicle_id})")
                    logger.info(f"[DRY RUN] URLs antigas: {len(fix['old_urls'])} -> URLs novas: {len(new_urls)}")
                    logger.info(f"[DRY RUN] Novas URLs: {new_urls}")
                else:
                    # Atualizar no banco
                    update_query = """
                        UPDATE veiculos 
                        SET fotos = %s, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """
                    
                    cursor.execute(update_query, (new_urls, vehicle_id))
                    self.fixed_count += 1
                    
                    logger.info(f"Atualizado veículo {vehicle['marca']} {vehicle['modelo']} (ID: {vehicle_id})")
                
                self.total_processed += 1
            
            if not dry_run:
                conn.commit()
                logger.info(f"Correções aplicadas com sucesso! {self.fixed_count} veículos atualizados.")
            else:
                logger.info(f"Dry run concluído. {len(fixes)} veículos seriam atualizados.")
                
        except Exception as e:
            if not dry_run:
                conn.rollback()
            logger.error(f"Erro ao aplicar correções: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_backup(self) -> str:
        """Cria backup das imagens antes das alterações"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_images_{timestamp}.json"
        
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT id, marca, modelo, fotos 
                FROM veiculos 
                WHERE fotos IS NOT NULL 
                AND array_length(fotos, 1) > 0
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
                    'fotos': vehicle['fotos']
                })
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup criado: {backup_file} ({len(backup_data)} veículos)")
            return backup_file
            
        finally:
            cursor.close()
            conn.close()
    
    async def run_full_fix(self, dry_run: bool = True) -> None:
        """Executa o processo completo de correção"""
        logger.info("=== INICIANDO CORREÇÃO DE IMAGENS DO BANCO DE DADOS ===")
        
        try:
            # 1. Criar backup
            backup_file = self.create_backup()
            
            # 2. Obter veículos com imagens
            vehicles = self.get_all_vehicle_images()
            
            if not vehicles:
                logger.info("Nenhum veículo com imagens encontrado")
                return
            
            # 3. Validar imagens
            validation_data = await self.validate_vehicle_images(vehicles)
            
            # 4. Preparar correções
            fixes = self.fix_vehicle_images(validation_data)
            
            if not fixes:
                logger.info("Nenhuma correção necessária!")
                return
            
            # 5. Aplicar correções
            self.apply_fixes_to_database(fixes, dry_run=dry_run)
            
            # 6. Relatório final
            logger.info("=== RELATÓRIO FINAL ===")
            logger.info(f"Backup criado: {backup_file}")
            logger.info(f"Veículos processados: {len(vehicles)}")
            logger.info(f"Veículos que precisavam de correção: {len(fixes)}")
            logger.info(f"Taxa de sucesso das imagens: {validation_data['summary']['success_rate']}%")
            
            if not dry_run:
                logger.info(f"Veículos atualizados no banco: {self.fixed_count}")
            else:
                logger.info("Execute novamente com --apply para aplicar as correções")
                
        except Exception as e:
            logger.error(f"Erro durante execução: {str(e)}")
            raise

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Corrigir URLs de imagens no banco de dados')
    parser.add_argument('--apply', action='store_true', 
                       help='Aplicar correções no banco (padrão é dry-run)')
    parser.add_argument('--verbose', action='store_true',
                       help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    fixer = DatabaseImageFixer()
    await fixer.run_full_fix(dry_run=not args.apply)

if __name__ == "__main__":
    asyncio.run(main())