#!/usr/bin/env python3
"""
Script para testar o sistema de fallback de imagens
"""

import sys
import os
import asyncio

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.fallback_images import (
    FallbackImageService, 
    get_fallback_images, 
    get_best_fallback,
    create_vehicle_placeholder
)
from app.image_validation import validate_image_urls_sync
from app.database import get_carros

def test_fallback_service():
    """Testa o serviço de fallback com diferentes cenários"""
    print("🔧 Testando Sistema de Fallback de Imagens")
    print("=" * 50)
    
    service = FallbackImageService()
    
    # Teste 1: Fallback por categoria
    print("\n📋 Teste 1: Fallback por Categoria")
    print("-" * 30)
    
    test_vehicles = [
        ("Toyota", "Corolla", "sedan"),
        ("Volkswagen", "T-Cross", "suv_compacto"),
        ("Ford", "Ranger", "pickup"),
        ("Honda", "Civic", "sedan"),
        ("Chevrolet", "Onix", "hatch")
    ]
    
    for marca, modelo, categoria in test_vehicles:
        fallbacks = service.get_fallback_images(marca, modelo, categoria)
        print(f"🚗 {marca} {modelo} ({categoria}):")
        for i, url in enumerate(fallbacks, 1):
            print(f"   {i}. {url}")
        print()
    
    # Teste 2: Placeholders personalizados
    print("\n🎨 Teste 2: Placeholders Personalizados")
    print("-" * 30)
    
    custom_vehicles = [
        ("Toyota", "Corolla", 2023, "Branco"),
        ("BMW", "X1", 2024, "Preto"),
        ("Fiat", "Argo", 2022, None),
        ("Hyundai", "HB20", 2023, "Azul")
    ]
    
    for marca, modelo, ano, cor in custom_vehicles:
        placeholder = service.get_placeholder_with_info(marca, modelo, ano, cor)
        print(f"🎯 {marca} {modelo} {ano or ''} {cor or ''}:")
        print(f"   {placeholder}")
        print()
    
    # Teste 3: Seleção da melhor opção
    print("\n🏆 Teste 3: Seleção da Melhor Opção")
    print("-" * 30)
    
    failed_urls = [
        "https://example.com/broken.jpg",
        "https://via.placeholder.com/400x300/CC0000/FFFFFF?text=Toyota+Corolla"
    ]
    
    best_fallback = service.select_best_fallback(
        "Toyota", "Corolla", "sedan", failed_urls
    )
    print(f"🥇 Melhor fallback (evitando URLs quebradas):")
    print(f"   {best_fallback}")
    print()
    
    # Teste 4: Fallback por marca
    print("\n🏷️ Teste 4: Fallback por Marca")
    print("-" * 30)
    
    brands = ["Toyota", "BMW", "Fiat", "Volkswagen", "Honda"]
    for brand in brands:
        brand_fallbacks = service.get_brand_fallback_images(brand)
        print(f"🔖 {brand}:")
        for i, url in enumerate(brand_fallbacks, 1):
            print(f"   {i}. {url}")
        print()

def test_fallback_with_real_data():
    """Testa o sistema de fallback com dados reais do banco"""
    print("\n🗄️ Testando com Dados Reais do Banco")
    print("=" * 50)
    
    try:
        carros = get_carros()
        print(f"📊 Carros encontrados: {len(carros)}")
        
        # Pegar alguns carros para teste
        test_cars = carros[:5]
        
        service = FallbackImageService()
        
        for carro in test_cars:
            marca = carro.get('marca', 'Desconhecida')
            modelo = carro.get('modelo', 'Desconhecido')
            categoria = carro.get('categoria', 'hatch')
            ano = carro.get('ano', 2023)
            cor = carro.get('cor', None)
            
            print(f"\n🚗 {marca} {modelo} ({categoria})")
            print(f"   Ano: {ano}, Cor: {cor or 'N/A'}")
            
            # Gerar fallbacks
            fallbacks = service.get_fallback_images(marca, modelo, categoria)
            print("   Fallbacks gerados:")
            for i, url in enumerate(fallbacks, 1):
                print(f"     {i}. {url}")
            
            # Placeholder personalizado
            placeholder = service.get_placeholder_with_info(marca, modelo, ano, cor)
            print(f"   Placeholder personalizado:")
            print(f"     {placeholder}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar dados do banco: {str(e)}")

def test_fallback_validation():
    """Testa se as URLs de fallback são válidas"""
    print("\n✅ Testando Validação das URLs de Fallback")
    print("=" * 50)
    
    service = FallbackImageService()
    
    # Coletar algumas URLs de fallback para teste
    test_urls = []
    
    # Fallbacks por categoria
    for categoria in ["sedan", "hatch", "suv_compacto"]:
        fallbacks = service.get_category_fallback_images(categoria)
        test_urls.extend(fallbacks[:2])  # Pegar apenas 2 de cada
    
    # Placeholders personalizados
    test_urls.append(service.get_placeholder_with_info("Toyota", "Corolla"))
    test_urls.append(service.get_placeholder_with_info("BMW", "X1", 2024, "Preto"))
    
    # Remover duplicatas
    unique_urls = list(set(test_urls))
    
    print(f"🔍 Validando {len(unique_urls)} URLs de fallback...")
    
    try:
        # Validar URLs (com timeout menor para ser mais rápido)
        results = validate_image_urls_sync(unique_urls, timeout=5)
        
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count
        
        print(f"\n📊 Resultados da validação:")
        print(f"✅ URLs válidas: {valid_count}")
        print(f"❌ URLs inválidas: {invalid_count}")
        print(f"📈 Taxa de sucesso: {valid_count/len(results)*100:.1f}%")
        
        # Mostrar URLs inválidas
        invalid_results = [r for r in results if not r.is_valid]
        if invalid_results:
            print(f"\n❌ URLs de fallback com problemas:")
            for result in invalid_results:
                print(f"   {result.url}")
                print(f"     Erro: {result.error_message}")
        
    except Exception as e:
        print(f"❌ Erro durante validação: {str(e)}")

def demonstrate_fallback_priority():
    """Demonstra a prioridade do sistema de fallback"""
    print("\n🎯 Demonstração da Prioridade de Fallback")
    print("=" * 50)
    
    service = FallbackImageService()
    
    # Simular cenário onde várias URLs falharam
    marca = "Toyota"
    modelo = "Corolla"
    categoria = "sedan"
    
    print(f"🚗 Veículo: {marca} {modelo} ({categoria})")
    
    # URLs que "falharam"
    failed_urls = [
        "https://original-image.com/corolla1.jpg",  # URL original
        "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=400&h=300&fit=crop&crop=center",  # Primeiro fallback
    ]
    
    print(f"\n❌ URLs que falharam:")
    for url in failed_urls:
        print(f"   {url}")
    
    # Obter próxima melhor opção
    best_option = service.select_best_fallback(marca, modelo, categoria, failed_urls)
    
    print(f"\n🏆 Melhor opção disponível:")
    print(f"   {best_option}")
    
    # Mostrar todas as opções disponíveis
    all_options = service.get_fallback_images(marca, modelo, categoria)
    print(f"\n📋 Todas as opções de fallback:")
    for i, url in enumerate(all_options, 1):
        status = "❌ FALHOU" if url in failed_urls else "✅ DISPONÍVEL"
        print(f"   {i}. {status} - {url}")

def main():
    """Função principal"""
    print("🚗 FacilIAuto - Teste do Sistema de Fallback")
    print("=" * 60)
    
    # Executar todos os testes
    test_fallback_service()
    test_fallback_with_real_data()
    test_fallback_validation()
    demonstrate_fallback_priority()
    
    print("\n✅ Todos os testes concluídos!")
    print("\n💡 O sistema de fallback está pronto para uso!")

if __name__ == "__main__":
    main()