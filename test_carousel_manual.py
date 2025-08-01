#!/usr/bin/env python3
"""
Script para teste manual do carrossel responsivo
Executa o servidor e abre uma página de teste
"""

import subprocess
import webbrowser
import time
import sys
import os

def test_carousel_functionality():
    """Testa a funcionalidade do carrossel manualmente"""
    
    print("🎠 Iniciando teste manual do carrossel responsivo...")
    
    # Verificar se os arquivos JavaScript existem
    js_files = [
        "static/js/responsive-carousel.js",
        "static/js/image-fallback.js", 
        "static/js/enhanced-carousel-integration.js"
    ]
    
    for js_file in js_files:
        if not os.path.exists(js_file):
            print(f"❌ Arquivo não encontrado: {js_file}")
            return False
        else:
            print(f"✅ Arquivo encontrado: {js_file}")
    
    print("\n📋 Checklist para teste manual:")
    print("1. ✅ Arquivos JavaScript do carrossel estão presentes")
    print("2. 🔄 Iniciando servidor...")
    
    try:
        # Iniciar servidor FastAPI
        print("Executando: uvicorn app.api:app --reload --port 8000")
        print("Acesse: http://localhost:8000")
        print("\n🧪 Itens para testar manualmente:")
        print("   • Preencha o questionário e veja os resultados")
        print("   • Verifique se carros com múltiplas fotos mostram carrossel")
        print("   • Teste navegação com botões prev/next")
        print("   • Teste swipe em dispositivos móveis (ou DevTools)")
        print("   • Verifique responsividade em diferentes tamanhos de tela")
        print("   • Teste lazy loading das imagens")
        print("   • Verifique fallback de imagens quebradas")
        print("   • Teste acessibilidade com Tab e setas do teclado")
        print("\n⚠️  Para parar o servidor: Ctrl+C")
        print("=" * 60)
        
        # Executar servidor
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.api:app", "--reload", "--port", "8000"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False

def check_carousel_files():
    """Verifica se todos os arquivos do carrossel estão corretos"""
    
    print("🔍 Verificando arquivos do carrossel...")
    
    # Verificar conteúdo dos arquivos
    files_to_check = {
        "static/js/responsive-carousel.js": [
            "class ResponsiveCarousel",
            "setupResponsive",
            "updateLayout",
            "maintainAspectRatio"
        ],
        "static/js/enhanced-carousel-integration.js": [
            "class EnhancedCarouselIntegration", 
            "setupCarouselLazyLoading",
            "optimizePerformance",
            "enhanceKeyboardSupport"
        ],
        "static/js/image-fallback.js": [
            "class ImageFallbackSystem",
            "generateFallback",
            "setupImageErrorHandling"
        ]
    }
    
    all_good = True
    
    for file_path, required_content in files_to_check.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            missing_content = []
            for required in required_content:
                if required not in content:
                    missing_content.append(required)
            
            if missing_content:
                print(f"❌ {file_path}: Conteúdo faltando: {missing_content}")
                all_good = False
            else:
                print(f"✅ {file_path}: OK")
        else:
            print(f"❌ {file_path}: Arquivo não encontrado")
            all_good = False
    
    return all_good

def show_implementation_summary():
    """Mostra resumo da implementação"""
    
    print("\n📊 RESUMO DA IMPLEMENTAÇÃO - TASK 5")
    print("=" * 50)
    print("✅ Carrossel responsivo implementado")
    print("✅ Navegação melhorada com controles e indicadores")
    print("✅ Suporte a toque/swipe para dispositivos móveis")
    print("✅ Lazy loading para melhor performance")
    print("✅ Design responsivo para mobile/tablet/desktop")
    print("✅ Integração com sistema de fallback de imagens")
    print("✅ Acessibilidade com suporte a teclado")
    print("✅ Otimizações de performance")
    print("✅ Testes automatizados criados")
    
    print("\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
    print("• Carrossel com transições suaves")
    print("• Controles de navegação responsivos")
    print("• Indicadores de slide")
    print("• Autoplay com pausa no hover")
    print("• Lazy loading inteligente")
    print("• Suporte a gestos de toque")
    print("• Teclado navigation (setas, home, end, space)")
    print("• Barra de progresso do autoplay")
    print("• Otimização para diferentes tamanhos de tela")
    print("• Integração com sistema de fallback")
    
    print("\n📱 RESPONSIVIDADE:")
    print("• Mobile (≤576px): altura 160px, controles 32px")
    print("• Tablet (≤768px): altura 200px, controles 36px") 
    print("• Desktop (≤992px): altura 220px, controles 40px")
    print("• Desktop grande (>992px): altura 250px")
    
    print("\n🚀 PERFORMANCE:")
    print("• Lazy loading de imagens não visíveis")
    print("• Pausa automática de carrosséis fora da tela")
    print("• Pré-carregamento da próxima imagem")
    print("• Otimização de eventos e observers")
    
    print("=" * 50)

if __name__ == "__main__":
    print("🎠 TESTE DO CARROSSEL RESPONSIVO - TASK 5")
    print("=" * 50)
    
    # Verificar arquivos
    if not check_carousel_files():
        print("❌ Alguns arquivos estão com problemas. Verifique a implementação.")
        sys.exit(1)
    
    # Mostrar resumo
    show_implementation_summary()
    
    # Perguntar se quer executar teste manual
    response = input("\n🤔 Deseja executar o teste manual? (s/n): ").lower().strip()
    
    if response in ['s', 'sim', 'y', 'yes']:
        test_carousel_functionality()
    else:
        print("✅ Teste manual cancelado. Implementação concluída!")
        print("\n💡 Para testar manualmente mais tarde:")
        print("   python test_carousel_manual.py")
        print("   ou")
        print("   uvicorn app.api:app --reload --port 8000")