#!/usr/bin/env python3
"""
Script para adicionar campos de metadados de imagem ao banco de dados
Parte da Task 3: Add database migration to include image metadata fields
"""

import psycopg2
import logging
from datetime import datetime
from app.config import DATABASE_CONFIG

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageMetadataMigration:
    """Classe para adicionar campos de metadados de imagem"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def check_existing_columns(self) -> dict:
        """Verifica quais colunas já existem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se as colunas já existem
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'veiculos' 
                AND column_name IN (
                    'fotos_metadata', 
                    'fotos_validated_at', 
                    'fotos_validation_status',
                    'updated_at'
                )
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            return {
                'fotos_metadata': 'fotos_metadata' in existing_columns,
                'fotos_validated_at': 'fotos_validated_at' in existing_columns,
                'fotos_validation_status': 'fotos_validation_status' in existing_columns,
                'updated_at': 'updated_at' in existing_columns
            }
            
        finally:
            cursor.close()
            conn.close()
    
    def add_metadata_columns(self, dry_run: bool = True) -> None:
        """Adiciona colunas de metadados de imagem"""
        existing = self.check_existing_columns()
        
        if dry_run:
            logger.info("=== MODO DRY RUN - Nenhuma alteração será feita ===")
        else:
            logger.info("=== ADICIONANDO COLUNAS DE METADADOS ===")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            migrations = []
            
            # 1. Campo para metadados das fotos (JSON)
            if not existing['fotos_metadata']:
                migrations.append({
                    'name': 'fotos_metadata',
                    'sql': """
                        ALTER TABLE veiculos 
                        ADD COLUMN fotos_metadata JSONB DEFAULT '[]'::jsonb
                    """,
                    'comment': """
                        COMMENT ON COLUMN veiculos.fotos_metadata IS 
                        'Metadados das fotos: validação, tamanho, tipo, etc.'
                    """
                })
            
            # 2. Campo para data da última validação
            if not existing['fotos_validated_at']:
                migrations.append({
                    'name': 'fotos_validated_at',
                    'sql': """
                        ALTER TABLE veiculos 
                        ADD COLUMN fotos_validated_at TIMESTAMP
                    """,
                    'comment': """
                        COMMENT ON COLUMN veiculos.fotos_validated_at IS 
                        'Data da última validação das URLs das fotos'
                    """
                })
            
            # 3. Campo para status de validação
            if not existing['fotos_validation_status']:
                migrations.append({
                    'name': 'fotos_validation_status',
                    'sql': """
                        ALTER TABLE veiculos 
                        ADD COLUMN fotos_validation_status VARCHAR(20) DEFAULT 'pending'
                    """,
                    'comment': """
                        COMMENT ON COLUMN veiculos.fotos_validation_status IS 
                        'Status da validação: pending, valid, invalid, mixed'
                    """
                })
            
            # 4. Campo para controle de atualizações
            if not existing['updated_at']:
                migrations.append({
                    'name': 'updated_at',
                    'sql': """
                        ALTER TABLE veiculos 
                        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """,
                    'comment': """
                        COMMENT ON COLUMN veiculos.updated_at IS 
                        'Data da última atualização do registro'
                    """
                })
            
            if not migrations:
                logger.info("Todas as colunas já existem. Nenhuma migração necessária.")
                return
            
            # Executar migrações
            for migration in migrations:
                if dry_run:
                    logger.info(f"[DRY RUN] Adicionaria coluna: {migration['name']}")
                    logger.info(f"[DRY RUN] SQL: {migration['sql'].strip()}")
                else:
                    logger.info(f"Adicionando coluna: {migration['name']}")
                    cursor.execute(migration['sql'])
                    cursor.execute(migration['comment'])
            
            # Criar índices para performance
            if not dry_run:
                indices = [
                    "CREATE INDEX IF NOT EXISTS idx_veiculos_fotos_validated_at ON veiculos(fotos_validated_at)",
                    "CREATE INDEX IF NOT EXISTS idx_veiculos_fotos_validation_status ON veiculos(fotos_validation_status)",
                    "CREATE INDEX IF NOT EXISTS idx_veiculos_updated_at ON veiculos(updated_at)"
                ]
                
                for index_sql in indices:
                    logger.info(f"Criando índice: {index_sql}")
                    cursor.execute(index_sql)
            
            # Criar trigger para updated_at
            if not existing['updated_at'] and not dry_run:
                trigger_sql = """
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = CURRENT_TIMESTAMP;
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                    
                    DROP TRIGGER IF EXISTS update_veiculos_updated_at ON veiculos;
                    
                    CREATE TRIGGER update_veiculos_updated_at
                        BEFORE UPDATE ON veiculos
                        FOR EACH ROW
                        EXECUTE FUNCTION update_updated_at_column();
                """
                
                logger.info("Criando trigger para updated_at")
                cursor.execute(trigger_sql)
            
            if not dry_run:
                conn.commit()
                logger.info("Migrações aplicadas com sucesso!")
            else:
                logger.info("Dry run concluído. Execute com --apply para aplicar as migrações.")
                
        except Exception as e:
            if not dry_run:
                conn.rollback()
            logger.error(f"Erro durante migração: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def populate_initial_metadata(self, dry_run: bool = True) -> None:
        """Popula metadados iniciais para registros existentes"""
        if dry_run:
            logger.info("=== DRY RUN - Populando metadados iniciais ===")
        else:
            logger.info("=== POPULANDO METADADOS INICIAIS ===")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Atualizar registros que têm fotos mas não têm metadados
            update_sql = """
                UPDATE veiculos 
                SET 
                    fotos_validation_status = 'pending',
                    fotos_validated_at = NULL,
                    fotos_metadata = '[]'::jsonb
                WHERE 
                    fotos IS NOT NULL 
                    AND array_length(fotos, 1) > 0
                    AND (fotos_validation_status IS NULL OR fotos_validation_status = '')
            """
            
            if dry_run:
                # Contar quantos registros seriam afetados
                count_sql = """
                    SELECT COUNT(*) 
                    FROM veiculos 
                    WHERE 
                        fotos IS NOT NULL 
                        AND array_length(fotos, 1) > 0
                        AND (fotos_validation_status IS NULL OR fotos_validation_status = '')
                """
                cursor.execute(count_sql)
                count = cursor.fetchone()[0]
                logger.info(f"[DRY RUN] {count} registros seriam atualizados com metadados iniciais")
            else:
                cursor.execute(update_sql)
                affected_rows = cursor.rowcount
                logger.info(f"Atualizados {affected_rows} registros com metadados iniciais")
                conn.commit()
                
        except Exception as e:
            if not dry_run:
                conn.rollback()
            logger.error(f"Erro ao popular metadados: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def run_migration(self, dry_run: bool = True) -> None:
        """Executa a migração completa"""
        logger.info("=== INICIANDO MIGRAÇÃO DE METADADOS DE IMAGEM ===")
        
        try:
            # 1. Verificar estado atual
            existing = self.check_existing_columns()
            logger.info(f"Colunas existentes: {existing}")
            
            # 2. Adicionar colunas
            self.add_metadata_columns(dry_run=dry_run)
            
            # 3. Popular dados iniciais (apenas se não for dry run e colunas foram criadas)
            if not dry_run and not all(existing.values()):
                self.populate_initial_metadata(dry_run=dry_run)
            
            logger.info("=== MIGRAÇÃO CONCLUÍDA ===")
            
        except Exception as e:
            logger.error(f"Erro durante migração: {str(e)}")
            raise

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Adicionar campos de metadados de imagem')
    parser.add_argument('--apply', action='store_true', 
                       help='Aplicar migrações no banco (padrão é dry-run)')
    parser.add_argument('--verbose', action='store_true',
                       help='Log detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    migration = ImageMetadataMigration()
    migration.run_migration(dry_run=not args.apply)

if __name__ == "__main__":
    main()