#!/usr/bin/env python3
"""
Script para testar a validação das imagens atuais no banco de dados
"""

import asyncio
import sys
import os
from typing import List, Dict

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.image_validation import ImageValidationService, validate_image_urls_sync
from app.database import get_carros
from app.config import test_connection

def collect_all_image_urls() -> Dict[str, List[str]]:
    """
    Coleta todas as URLs de imagens dos carros no banco
    
    Returns:
        Dicionário com informações dos carros e suas URLs
    """
    print("🔍 Coletando URLs de imagens dos carros...")
    
    try:
        carros = get_carros()
        print(f"📊 Encontrados {len(carros)} carros no banco")
        
        car_images = {}
        all_urls = []
        
        for carro in carros:
            fotos = carro.get('fotos', [])
            if fotos:
                car_key = f"{carro['marca']} {carro['modelo']} ({carro['id']})"
                car_images[car_key] = fotos
                all_urls.extend(fotos)
        
        print(f"🖼️  Total de URLs de imagens encontradas: {len(all_urls)}")
        print(f"🚗 Carros com imagens: {len(car_images)}")
        
        return car_images
        
    except Exception as e:
        print(f"❌ Erro ao coletar imagens: {str(e)}")
        return {}

async def test_image_validation_service():
    """Testa o serviço de validação com algumas URLs de exemplo"""
    print("\n🧪 Testando serviço de validação com URLs de exemplo...")
    
    test_urls = [
        'https://httpbin.org/image/jpeg',  # URL que deve funcionar
        'https://httpbin.org/status/404',  # URL que retorna 404
        'https://httpbin.org/delay/15',    # URL que vai dar timeout
        'invalid-url-format',             # URL inválida
        'https://via.placeholder.com/400x300/0066cc/ffffff?text=Test+Image'  # Placeholder
    ]
    
    async with ImageValidationService(timeout=5) as validator:
        results = await validator.validate_multiple_urls(test_urls)
        
        print("\n📋 Resultados dos testes:")
        for result in results:
            status = "✅ VÁLIDA" if result.is_valid else "❌ INVÁLIDA"
            print(f"{status} - {result.url}")
            if not result.is_valid:
                print(f"   Erro: {result.error_type.value if result.error_type else 'N/A'}")
                print(f"   Mensagem: {result.error_message}")
            else:
                print(f"   Tipo: {result.content_type}")
                print(f"   Tempo: {result.response_time_ms}ms")
            print()
        
        # Gerar resumo
        summary = validator.get_validation_summary(results)
        print("📊 Resumo dos testes:")
        print(f"   Total: {summary['total']}")
        print(f"   Válidas: {summary['valid']}")
        print(f"   Inválidas: {summary['invalid']}")
        print(f"   Taxa de sucesso: {summary['success_rate']}%")
        if summary['error_breakdown']:
            print("   Tipos de erro:")
            for error_type, count in summary['error_breakdown'].items():
                print(f"     - {error_type}: {count}")

def validate_current_database_images():
    """Valida todas as imagens atuais do banco de dados"""
    print("\n🔍 Validando imagens atuais do banco de dados...")
    
    # Verificar conexão com banco
    if not test_connection():
        print("❌ Não foi possível conectar ao banco de dados")
        return
    
    # Coletar URLs
    car_images = collect_all_image_urls()
    if not car_images:
        print("⚠️  Nenhuma imagem encontrada no banco")
        return
    
    # Coletar todas as URLs únicas
    all_urls = []
    for fotos in car_images.values():
        all_urls.extend(fotos)
    
    unique_urls = list(set(all_urls))
    print(f"🔗 URLs únicas para validar: {len(unique_urls)}")
    
    # Validar URLs (versão síncrona para simplicidade)
    print("⏳ Validando URLs... (isso pode demorar alguns minutos)")
    
    try:
        results = validate_image_urls_sync(unique_urls, timeout=10)
        
        # Analisar resultados
        valid_urls = [r for r in results if r.is_valid]
        invalid_urls = [r for r in results if not r.is_valid]
        
        print(f"\n📊 Resultados da validação:")
        print(f"✅ URLs válidas: {len(valid_urls)}")
        print(f"❌ URLs inválidas: {len(invalid_urls)}")
        print(f"📈 Taxa de sucesso: {len(valid_urls)/len(results)*100:.1f}%")
        
        # Mostrar URLs inválidas
        if invalid_urls:
            print(f"\n❌ URLs com problemas:")
            error_counts = {}
            for result in invalid_urls:
                error_type = result.error_type.value if result.error_type else 'unknown'
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
                print(f"   {result.url}")
                print(f"     Erro: {result.error_message}")
            
            print(f"\n📋 Resumo dos erros:")
            for error_type, count in error_counts.items():
                print(f"   {error_type}: {count} URLs")
        
        # Identificar carros afetados
        print(f"\n🚗 Carros com imagens problemáticas:")
        affected_cars = []
        
        for car_name, fotos in car_images.items():
            car_invalid_urls = []
            for foto in fotos:
                for result in invalid_urls:
                    if result.url == foto:
                        car_invalid_urls.append(foto)
            
            if car_invalid_urls:
                affected_cars.append((car_name, car_invalid_urls))
        
        if affected_cars:
            for car_name, invalid_car_urls in affected_cars:
                print(f"   {car_name}: {len(invalid_car_urls)} imagem(ns) inválida(s)")
        else:
            print("   Nenhum carro afetado! 🎉")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro durante validação: {str(e)}")
        return []

def main():
    """Função principal"""
    print("🚗 FacilIAuto - Teste de Validação de Imagens")
    print("=" * 50)
    
    # Testar serviço com URLs de exemplo
    asyncio.run(test_image_validation_service())
    
    # Validar imagens do banco
    validate_current_database_images()
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()