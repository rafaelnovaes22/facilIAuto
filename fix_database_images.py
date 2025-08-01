#!/usr/bin/env python3
"""
Script para validar e corrigir URLs de imagens no banco de dados
"""

import sys
import os
import asyncio
from typing import List, Dict, Tuple

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.image_validation import validate_image_urls_sync, ImageValidationResult
from app.fallback_images import get_fallback_images, get_best_fallback
from app.database import get_carros
from app.config import DATABASE_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseImageFixer:
    """Classe para corrigir imagens no banco de dados"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.fixed_count = 0
        self.total_cars = 0
        self.validation_results = {}
    
    def get_connection(self):
        """Obtém conexão com o banco"""
        return psycopg2.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["database"],
            user=self.config["user"],
            password=self.config["password"]
        )
    
    def get_all_cars_with_images(self) -> List[Dict]:
        """Obtém todos os carros com suas imagens do banco"""
        print("🔍 Coletando carros com imagens do banco...")
        
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            query = """
                SELECT id, marca, modelo, versao, ano, cor, fotos
                FROM veiculos 
                WHERE fotos IS NOT NULL 
                AND array_length(fotos, 1) > 0
                ORDER BY marca, modelo
            """
            
            cursor.execute(query)
            cars = cursor.fetchall()
            
            print(f"📊 Encontrados {len(cars)} carros com imagens")
            return [dict(car) for car in cars]
            
        finally:
            cursor.close()
            conn.close()
    
    def validate_all_images(self, cars: List[Dict]) -> Dict[str, ImageValidationResult]:
        """Valida todas as URLs de imagens"""
        print("🔍 Validando todas as URLs de imagens...")
        
        # Coletar todas as URLs únicas
        all_urls = set()
        for car in cars:
            if car['fotos']:
                all_urls.update(car['fotos'])
        
        unique_urls = list(all_urls)
        print(f"🔗 Total de URLs únicas para validar: {len(unique_urls)}")
        
        # Validar URLs
        print("⏳ Validando URLs... (isso pode demorar alguns minutos)")
        results = validate_image_urls_sync(unique_urls, timeout=10)
        
        # Criar dicionário de resultados
        validation_dict = {}
        for result in results:
            validation_dict[result.url] = result
        
        # Estatísticas
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count
        
        print(f"📊 Resultados da validação:")
        print(f"✅ URLs válidas: {valid_count}")
        print(f"❌ URLs inválidas: {invalid_count}")
        print(f"📈 Taxa de sucesso: {valid_count/len(results)*100:.1f}%")
        
        return validation_dict
    
    def _determine_category(self, modelo: str, versao: str = "") -> str:
        """Determina a categoria do veículo baseado no modelo"""
        modelo_lower = modelo.lower()
        versao_lower = versao.lower() if versao else ""
        
        # SUVs e Crossovers
        if any(word in modelo_lower for word in ["tucson", "compass", "kicks", "t-cross", "nivus", "creta", "hr-v", "tracker"]):
            return "suv_compacto"
        
        if any(word in modelo_lower for word in ["santa fe", "sorento", "pilot", "pathfinder"]):
            return "suv_medio"
        
        if any(word in modelo_lower for word in ["x1", "x3", "q3", "glc", "macan"]):
            return "suv_premium"
        
        # Picapes
        if any(word in modelo_lower for word in ["ranger", "hilux", "amarok", "frontier", "s10", "toro"]):
            return "pickup"
        
        # Sedans
        if any(word in modelo_lower for word in ["corolla", "civic", "jetta", "cruze", "sentra", "city"]):
            return "sedan"
        
        # Hatches
        if any(word in modelo_lower for word in ["onix", "hb20", "polo", "gol", "argo", "ka", "march"]):
            return "hatch"
        
        # Default baseado na versão ou tamanho típico
        if "sedan" in versao_lower or "plus" in modelo_lower:
            return "sedan"
        
        return "hatch"  # Default

    def identify_cars_needing_fixes(self, cars: List[Dict], 
                                   validation_results: Dict[str, ImageValidationResult]) -> List[Dict]:
        """Identifica carros que precisam de correção"""
        print("\n🔧 Identificando carros que precisam de correção...")
        
        cars_to_fix = []
        
        for car in cars:
            if not car['fotos']:
                continue
            
            broken_urls = []
            for url in car['fotos']:
                result = validation_results.get(url)
                if result and not result.is_valid:
                    broken_urls.append(url)
            
            if broken_urls:
                # Determinar categoria baseada no modelo
                categoria = self._determine_category(car['modelo'], car.get('versao', ''))
                
                car_info = {
                    'id': car['id'],
                    'marca': car['marca'],
                    'modelo': car['modelo'],
                    'versao': car.get('versao'),
                    'ano': car['ano'],
                    'cor': car.get('cor'),
                    'categoria': categoria,
                    'original_fotos': car['fotos'],
                    'broken_urls': broken_urls,
                    'valid_urls': [url for url in car['fotos'] if url not in broken_urls]
                }
                cars_to_fix.append(car_info)
        
        print(f"🚗 Carros que precisam de correção: {len(cars_to_fix)}")
        return cars_to_fix
    
    def generate_fixed_images(self, car_info: Dict) -> List[str]:
        """Gera lista de imagens corrigidas para um carro"""
        marca = car_info['marca']
        modelo = car_info['modelo']
        categoria = car_info['categoria']
        
        # Manter URLs válidas
        fixed_images = car_info['valid_urls'].copy()
        
        # Calcular quantas imagens precisamos substituir
        num_broken = len(car_info['broken_urls'])
        
        if num_broken > 0:
            # Obter fallbacks
            fallback_images = get_fallback_images(marca, modelo, categoria)
            
            # Adicionar fallbacks até ter pelo menos 2 imagens
            target_count = max(2, len(car_info['original_fotos']))
            
            for fallback_url in fallback_images:
                if len(fixed_images) >= target_count:
                    break
                if fallback_url not in fixed_images:
                    fixed_images.append(fallback_url)
        
        # Garantir que temos pelo menos 1 imagem
        if not fixed_images:
            fallback = get_best_fallback(marca, modelo, categoria)
            fixed_images.append(fallback)
        
        return fixed_images
    
    def update_car_images(self, car_id: str, new_images: List[str]) -> bool:
        """Atualiza as imagens de um carro no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                UPDATE veiculos 
                SET fotos = %s 
                WHERE id = %s
            """
            
            cursor.execute(query, (new_images, car_id))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar carro {car_id}: {str(e)}")
            conn.rollback()
            return False
            
        finally:
            cursor.close()
            conn.close()
    
    def fix_all_cars(self, cars_to_fix: List[Dict], dry_run: bool = True) -> Dict:
        """Corrige todos os carros identificados"""
        print(f"\n🔧 {'[DRY RUN] ' if dry_run else ''}Corrigindo imagens dos carros...")
        
        results = {
            'total_cars': len(cars_to_fix),
            'successful_fixes': 0,
            'failed_fixes': 0,
            'details': []
        }
        
        for i, car_info in enumerate(cars_to_fix, 1):
            marca = car_info['marca']
            modelo = car_info['modelo']
            car_id = car_info['id']
            
            print(f"\n🚗 [{i}/{len(cars_to_fix)}] {marca} {modelo}")
            print(f"   ID: {car_id}")
            print(f"   URLs quebradas: {len(car_info['broken_urls'])}")
            print(f"   URLs válidas: {len(car_info['valid_urls'])}")
            
            # Gerar imagens corrigidas
            fixed_images = self.generate_fixed_images(car_info)
            
            print(f"   Imagens após correção: {len(fixed_images)}")
            for j, img in enumerate(fixed_images, 1):
                status = "✅ VÁLIDA" if img in car_info['valid_urls'] else "🔧 FALLBACK"
                print(f"     {j}. {status} - {img}")
            
            # Atualizar no banco (se não for dry run)
            if not dry_run:
                success = self.update_car_images(car_id, fixed_images)
                if success:
                    results['successful_fixes'] += 1
                    print("   ✅ Atualizado com sucesso!")
                else:
                    results['failed_fixes'] += 1
                    print("   ❌ Falha na atualização!")
            else:
                results['successful_fixes'] += 1
                print("   🔍 [DRY RUN] Seria atualizado")
            
            # Adicionar detalhes
            results['details'].append({
                'car_id': car_id,
                'marca': marca,
                'modelo': modelo,
                'broken_count': len(car_info['broken_urls']),
                'fixed_count': len(fixed_images),
                'success': True if dry_run else success
            })
        
        return results
    
    def generate_report(self, results: Dict, validation_results: Dict):
        """Gera relatório final"""
        print(f"\n📊 RELATÓRIO FINAL")
        print("=" * 50)
        
        print(f"🔍 Validação de URLs:")
        total_urls = len(validation_results)
        valid_urls = sum(1 for r in validation_results.values() if r.is_valid)
        invalid_urls = total_urls - valid_urls
        
        print(f"   Total de URLs: {total_urls}")
        print(f"   URLs válidas: {valid_urls} ({valid_urls/total_urls*100:.1f}%)")
        print(f"   URLs inválidas: {invalid_urls} ({invalid_urls/total_urls*100:.1f}%)")
        
        print(f"\n🔧 Correção de carros:")
        print(f"   Carros processados: {results['total_cars']}")
        print(f"   Correções bem-sucedidas: {results['successful_fixes']}")
        print(f"   Correções falhadas: {results['failed_fixes']}")
        
        if results['total_cars'] > 0:
            success_rate = results['successful_fixes'] / results['total_cars'] * 100
            print(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        # Estatísticas por tipo de erro
        error_types = {}
        for result in validation_results.values():
            if not result.is_valid and result.error_type:
                error_type = result.error_type.value
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            print(f"\n❌ Tipos de erro encontrados:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   {error_type}: {count} URLs")

def main():
    """Função principal"""
    print("🚗 FacilIAuto - Correção de Imagens no Banco de Dados")
    print("=" * 60)
    
    fixer = DatabaseImageFixer()
    
    try:
        # 1. Obter carros com imagens
        cars = fixer.get_all_cars_with_images()
        if not cars:
            print("⚠️ Nenhum carro com imagens encontrado no banco")
            return
        
        # 2. Validar todas as imagens
        validation_results = fixer.validate_all_images(cars)
        
        # 3. Identificar carros que precisam de correção
        cars_to_fix = fixer.identify_cars_needing_fixes(cars, validation_results)
        
        if not cars_to_fix:
            print("🎉 Nenhum carro precisa de correção! Todas as imagens estão funcionando.")
            return
        
        # 4. Mostrar preview das correções (dry run)
        print(f"\n🔍 PREVIEW DAS CORREÇÕES (DRY RUN)")
        print("-" * 40)
        results_dry = fixer.fix_all_cars(cars_to_fix, dry_run=True)
        
        # 5. Perguntar se deve aplicar as correções
        print(f"\n❓ Deseja aplicar as correções no banco de dados?")
        print(f"   Carros a serem corrigidos: {len(cars_to_fix)}")
        response = input("   Digite 'sim' para confirmar: ").lower().strip()
        
        if response == 'sim':
            print(f"\n🔧 APLICANDO CORREÇÕES NO BANCO DE DADOS")
            print("-" * 40)
            results_real = fixer.fix_all_cars(cars_to_fix, dry_run=False)
            fixer.generate_report(results_real, validation_results)
        else:
            print("❌ Correções canceladas pelo usuário")
            fixer.generate_report(results_dry, validation_results)
        
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()