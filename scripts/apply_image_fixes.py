#!/usr/bin/env python3
"""
Script integrado para aplicar todas as correções de imagem da Task 3
Combina migração de banco + validação + correção de URLs
"""

import asyncio
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'image_fixes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Executa todas as correções de imagem em sequência"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Aplicar todas as correções de imagem')
    parser.add_argument('--apply', action='store_true', 
                       help='Aplicar correções no banco (padrão é dry-run)')
    parser.add_argument('--skip-migration', action='store_true',
                       help='Pular migração de campos (se já executada)')
    parser.add_argument('--verbose', action='store_true',
                       help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== INICIANDO PROCESSO COMPLETO DE CORREÇÃO DE IMAGENS ===")
    
    try:
        # Etapa 1: Migração de campos (se necessário)
        if not args.skip_migration:
            logger.info("ETAPA 1: Adicionando campos de metadados...")
            from add_image_metadata_fields import ImageMetadataMigration
            
            migration = ImageMetadataMigration()
            migration.run_migration(dry_run=not args.apply)
            logger.info("✅ Migração de campos concluída")
        else:
            logger.info("⏭️ Migração de campos pulada")
        
        # Etapa 2: Validação e correção de URLs
        logger.info("ETAPA 2: Validando e corrigindo URLs de imagens...")
        from fix_database_image_urls import DatabaseImageFixer
        
        fixer = DatabaseImageFixer()
        await fixer.run_full_fix(dry_run=not args.apply)
        logger.info("✅ Validação e correção de URLs concluída")
        
        # Etapa 3: Relatório final
        logger.info("=== PROCESSO CONCLUÍDO COM SUCESSO ===")
        
        if not args.apply:
            logger.info("🔍 Este foi um DRY RUN - nenhuma alteração foi feita")
            logger.info("📝 Execute novamente com --apply para aplicar as correções")
        else:
            logger.info("✅ Todas as correções foram aplicadas no banco de dados")
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())