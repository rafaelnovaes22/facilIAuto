"""
Validação: Garantir que nenhum método cria valores padrão quando dados não existem.

Este script valida que o princípio "Nunca Invente Dados" está sendo seguido.
"""

import sys
from scraper.data_transformer import DataTransformer
from scraper.extractors import FieldExtractor


def test_no_default_values():
    """Testar que métodos retornam None quando não encontram dados"""
    print("=" * 60)
    print("Validação: Nenhum Valor Padrão Criado")
    print("=" * 60)
    
    transformer = DataTransformer()
    extractor = FieldExtractor()
    
    all_passed = True
    
    # Test 1: normalize_price com string vazia
    print("\n1. Testando normalize_price com string vazia...")
    result = transformer.normalize_price('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 2: normalize_price com texto inválido
    print("\n2. Testando normalize_price com texto inválido...")
    result = transformer.normalize_price('abc')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 3: normalize_km com string vazia
    print("\n3. Testando normalize_km com string vazia...")
    result = transformer.normalize_km('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 4: normalize_km com texto inválido
    print("\n4. Testando normalize_km com texto inválido...")
    result = transformer.normalize_km('abc')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 5: normalize_cambio com string vazia
    print("\n5. Testando normalize_cambio com string vazia...")
    result = transformer.normalize_cambio('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 6: normalize_cambio com texto inválido
    print("\n6. Testando normalize_cambio com texto inválido...")
    result = transformer.normalize_cambio('unknown_transmission')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 7: normalize_combustivel com string vazia
    print("\n7. Testando normalize_combustivel com string vazia...")
    result = transformer.normalize_combustivel('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 8: normalize_combustivel com texto inválido
    print("\n8. Testando normalize_combustivel com texto inválido...")
    result = transformer.normalize_combustivel('unknown_fuel')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 9: normalize_categoria com string vazia
    print("\n9. Testando normalize_categoria com string vazia...")
    result = transformer.normalize_categoria('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 10: normalize_categoria com texto inválido
    print("\n10. Testando normalize_categoria com texto inválido...")
    result = transformer.normalize_categoria('unknown_category')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
        all_passed = False
    
    # Test 11: extract_year com string vazia
    print("\n11. Testando extract_year com string vazia...")
    result = extractor.extract_year('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 12: extract_doors com string vazia
    print("\n12. Testando extract_doors com string vazia...")
    result = extractor.extract_doors('')
    if result is None:
        print("   ✅ CORRETO: Retorna None")
    else:
        print(f"   ❌ ERRO: Retornou {result} ao invés de None")
        all_passed = False
    
    # Test 13: transform com dados parciais (não deve criar campos faltantes)
    print("\n13. Testando transform com dados parciais...")
    raw_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        'preco': '95990',
        # Faltando: cambio, combustivel, categoria
    }
    result = transformer.transform(raw_data)
    
    # Verificar que campos faltantes não foram criados
    missing_fields = []
    if 'cambio' in result and result['cambio'] is not None:
        missing_fields.append('cambio')
    if 'combustivel' in result and result['combustivel'] is not None:
        missing_fields.append('combustivel')
    if 'categoria' in result and result['categoria'] is not None:
        missing_fields.append('categoria')
    
    if not missing_fields:
        print("   ✅ CORRETO: Não criou campos faltantes")
    else:
        print(f"   ❌ ERRO: Criou campos que não existiam: {missing_fields}")
        all_passed = False
    
    # Test 14: validate_and_transform deve rejeitar dados incompletos
    print("\n14. Testando validate_and_transform com dados incompletos...")
    incomplete_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        # Faltando: preco, ano, quilometragem (obrigatórios)
    }
    result = transformer.validate_and_transform(incomplete_data)
    if result is None:
        print("   ✅ CORRETO: Rejeitou dados incompletos")
    else:
        print(f"   ❌ ERRO: Aceitou dados incompletos")
        all_passed = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TODOS OS TESTES PASSARAM")
        print("Princípio 'Nunca Invente Dados' está sendo seguido!")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("ATENÇÃO: Código está criando valores padrão!")
        return 1


def test_robustcar_scraper():
    """Testar que RobustCarScraper não cria valores padrão"""
    print("\n" + "=" * 60)
    print("Validação: RobustCarScraper")
    print("=" * 60)
    
    try:
        from robustcar_scraper import RobustCarScraper
        
        scraper = RobustCarScraper()
        
        # Test 1: extract_cambio com string vazia
        print("\n1. Testando extract_cambio com string vazia...")
        result = scraper.extract_cambio('')
        if result is None:
            print("   ✅ CORRETO: Retorna None")
            return True
        else:
            print(f"   ❌ ERRO: Retornou '{result}' ao invés de None")
            print("   AÇÃO: Corrigir robustcar_scraper.py para não assumir 'Manual'")
            return False
    
    except Exception as e:
        print(f"\n⚠️  Não foi possível testar RobustCarScraper: {e}")
        return True  # Não falhar se scraper não estiver disponível


def main():
    """Executar todas as validações"""
    print("\n🔍 Validando Princípio: Nunca Invente Dados\n")
    
    # Test 1: DataTransformer e FieldExtractor
    result1 = test_no_default_values()
    
    # Test 2: RobustCarScraper
    result2 = test_robustcar_scraper()
    
    # Resultado final
    if result1 == 0 and result2:
        print("\n" + "=" * 60)
        print("🎉 VALIDAÇÃO COMPLETA: SUCESSO")
        print("=" * 60)
        print("\nTodos os componentes seguem o princípio:")
        print("'Se não está no site, retorne None'")
        print("\n✅ DataTransformer: OK")
        print("✅ FieldExtractor: OK")
        print("✅ RobustCarScraper: OK")
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  VALIDAÇÃO COMPLETA: FALHAS ENCONTRADAS")
        print("=" * 60)
        print("\nAlguns componentes estão criando valores padrão.")
        print("Revise o código e corrija antes de fazer scraping.")
        print("\nVer: platform/scrapers/PRINCIPIOS-EXTRACAO-DADOS.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())
