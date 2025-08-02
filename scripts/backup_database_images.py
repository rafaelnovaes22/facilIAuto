#!/usr/bin/env python3
"""
Script para fazer backup das imagens do banco antes de alterações
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Dict

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import DATABASE_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseImageBackup:
    """Classe para fazer backup das imagens do banco"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def create_backup(self) -> str:
        """Cria backup completo das imagens"""
        print("💾 Criando backup das imagens do banco...")
        
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Buscar todos os carros com imagens
            query = """
                SELECT id, marca, modelo, versao, ano, cor, fotos, 
                       created_at, updated_at
                FROM veiculos 
                WHERE fotos IS NOT NULL 
                AND array_length(fotos, 1) > 0
                ORDER BY marca, modelo
            """
            
            cursor.execute(query)
            cars = cursor.fetchall()
            
            # Converter para formato serializável
            backup_data = {
                "backup_info": {
                    "timestamp": self.backup_timestamp,
                    "total_cars": len(cars),
                    "database": self.config["database"],
                    "created_by": "backup_database_images.py"
                },
                "cars": []
            }
            
            total_images = 0
            for car in cars:
                car_data = {
                    "id": car["id"],
                    "marca": car["marca"],
                    "modelo": car["modelo"],
                    "versao": car["versao"],
                    "ano": car["ano"],
                    "cor": car["cor"],
                    "fotos": car["fotos"],
                    "created_at": car["created_at"].isoformat() if car["created_at"] else None,
                    "updated_at": car["updated_at"].isoformat() if car["updated_at"] else None
                }
                backup_data["cars"].append(car_data)
                total_images += len(car["fotos"]) if car["fotos"] else 0
            
            backup_data["backup_info"]["total_images"] = total_images
            
            # Salvar backup
            backup_filename = f"backup_images_{self.backup_timestamp}.json"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup criado: {backup_filename}")
            print(f"📊 Carros salvos: {len(cars)}")
            print(f"🖼️ Total de imagens: {total_images}")
            
            return backup_filename
            
        finally:
            cursor.close()
            conn.close()
    
    def restore_from_backup(self, backup_filename: str, dry_run: bool = True) -> bool:
        """Restaura imagens a partir de um backup"""
        print(f"🔄 {'[DRY RUN] ' if dry_run else ''}Restaurando backup: {backup_filename}")
        
        if not os.path.exists(backup_filename):
            print(f"❌ Arquivo de backup não encontrado: {backup_filename}")
            return False
        
        try:
            # Carregar backup
            with open(backup_filename, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            cars = backup_data.get("cars", [])
            backup_info = backup_data.get("backup_info", {})
            
            print(f"📊 Backup info:")
            print(f"   Data: {backup_info.get('timestamp', 'N/A')}")
            print(f"   Carros: {backup_info.get('total_cars', 0)}")
            print(f"   Imagens: {backup_info.get('total_images', 0)}")
            
            if not dry_run:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                try:
                    restored_count = 0
                    for car in cars:
                        car_id = car["id"]
                        fotos = car["fotos"]
                        
                        query = """
                            UPDATE veiculos 
                            SET fotos = %s 
                            WHERE id = %s
                        """
                        
                        cursor.execute(query, (fotos, car_id))
                        restored_count += 1
                    
                    conn.commit()
                    print(f"✅ Restaurados {restored_count} carros")
                    return True
                    
                except Exception as e:
                    print(f"❌ Erro durante restauração: {str(e)}")
                    conn.rollback()
                    return False
                    
                finally:
                    cursor.close()
                    conn.close()
            else:
                print(f"🔍 [DRY RUN] Seria restaurado {len(cars)} carros")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao processar backup: {str(e)}")
            return False
    
    def list_backups(self) -> List[str]:
        """Lista todos os backups disponíveis"""
        backup_files = []
        
        for filename in os.listdir('.'):
            if filename.startswith('backup_images_') and filename.endswith('.json'):
                backup_files.append(filename)
        
        backup_files.sort(reverse=True)  # Mais recentes primeiro
        return backup_files
    
    def show_backup_info(self, backup_filename: str):
        """Mostra informações de um backup"""
        if not os.path.exists(backup_filename):
            print(f"❌ Backup não encontrado: {backup_filename}")
            return
        
        try:
            with open(backup_filename, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            backup_info = backup_data.get("backup_info", {})
            cars = backup_data.get("cars", [])
            
            print(f"📋 Informações do backup: {backup_filename}")
            print(f"   Data: {backup_info.get('timestamp', 'N/A')}")
            print(f"   Carros: {backup_info.get('total_cars', 0)}")
            print(f"   Imagens: {backup_info.get('total_images', 0)}")
            print(f"   Banco: {backup_info.get('database', 'N/A')}")
            
            # Mostrar alguns exemplos
            if cars:
                print(f"\n📝 Primeiros 5 carros no backup:")
                for i, car in enumerate(cars[:5], 1):
                    fotos_count = len(car.get("fotos", []))
                    print(f"   {i}. {car.get('marca', 'N/A')} {car.get('modelo', 'N/A')} - {fotos_count} foto(s)")
                
                if len(cars) > 5:
                    print(f"   ... e mais {len(cars) - 5} carros")
            
        except Exception as e:
            print(f"❌ Erro ao ler backup: {str(e)}")

def main():
    """Função principal"""
    print("💾 FacilIAuto - Backup de Imagens do Banco")
    print("=" * 50)
    
    backup_service = DatabaseImageBackup()
    
    # Se executado com argumento, criar backup automaticamente
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        backup_filename = backup_service.create_backup()
        print(f"\n✅ Backup criado automaticamente!")
        print(f"📁 Arquivo: {backup_filename}")
        return
    
    print("Opções disponíveis:")
    print("1. Criar novo backup")
    print("2. Listar backups existentes")
    print("3. Ver informações de um backup")
    print("4. Restaurar backup")
    
    try:
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            # Criar backup
            backup_filename = backup_service.create_backup()
            print(f"\n✅ Backup criado com sucesso!")
            print(f"📁 Arquivo: {backup_filename}")
            
        elif choice == "2":
            # Listar backups
            backups = backup_service.list_backups()
            if backups:
                print(f"\n📋 Backups encontrados ({len(backups)}):")
                for i, backup in enumerate(backups, 1):
                    print(f"   {i}. {backup}")
            else:
                print("\n⚠️ Nenhum backup encontrado")
                
        elif choice == "3":
            # Ver informações
            backups = backup_service.list_backups()
            if not backups:
                print("\n⚠️ Nenhum backup encontrado")
                return
            
            print(f"\n📋 Backups disponíveis:")
            for i, backup in enumerate(backups, 1):
                print(f"   {i}. {backup}")
            
            try:
                backup_choice = int(input("\nEscolha um backup (número): ")) - 1
                if 0 <= backup_choice < len(backups):
                    backup_service.show_backup_info(backups[backup_choice])
                else:
                    print("❌ Opção inválida")
            except ValueError:
                print("❌ Por favor, digite um número válido")
                
        elif choice == "4":
            # Restaurar backup
            backups = backup_service.list_backups()
            if not backups:
                print("\n⚠️ Nenhum backup encontrado")
                return
            
            print(f"\n📋 Backups disponíveis:")
            for i, backup in enumerate(backups, 1):
                print(f"   {i}. {backup}")
            
            try:
                backup_choice = int(input("\nEscolha um backup (número): ")) - 1
                if 0 <= backup_choice < len(backups):
                    selected_backup = backups[backup_choice]
                    
                    # Mostrar informações do backup
                    backup_service.show_backup_info(selected_backup)
                    
                    # Confirmar restauração
                    confirm = input(f"\n❓ Deseja restaurar este backup? (sim/não): ").lower().strip()
                    if confirm == "sim":
                        success = backup_service.restore_from_backup(selected_backup, dry_run=False)
                        if success:
                            print("✅ Backup restaurado com sucesso!")
                        else:
                            print("❌ Falha na restauração do backup")
                    else:
                        print("❌ Restauração cancelada")
                else:
                    print("❌ Opção inválida")
            except ValueError:
                print("❌ Por favor, digite um número válido")
                
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()