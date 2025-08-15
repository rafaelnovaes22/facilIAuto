#!/usr/bin/env python3
"""
Script para testar integração completa do ML com sistema existente
"""

import asyncio
import json
from datetime import datetime

# Importar tudo que já temos
from app.ml_mvp_processor import get_hybrid_processor
from app.models import QuestionarioBusca
from app.database import get_carros


def test_ml_integration():
    """
    Testa integração completa
    """
    print("=" * 60)
    print("🚀 TESTE DE INTEGRAÇÃO ML + SISTEMA EXISTENTE")
    print("=" * 60)
    
    # 1. Inicializar processador híbrido
    print("\n1️⃣ Inicializando processador híbrido...")
    processor = get_hybrid_processor()
    
    # 2. Verificar status
    print("\n2️⃣ Verificando status do sistema...")
    stats = processor.get_comprehensive_stats()
    
    print(f"   ML Treinado: {'✅' if stats['system_status']['ml_trained'] else '❌'}")
    print(f"   Amostras coletadas: {stats['system_status']['total_training_samples']}")
    print(f"   Pronto para treinar: {'✅' if stats['system_status']['ready_to_train'] else '❌'}")
    print(f"   Peso do ML: {stats['system_status']['ml_weight']:.0%}")
    
    # 3. Buscar carros para teste
    print("\n3️⃣ Buscando carros para teste...")
    carros = get_carros()[:5]  # Testar com 5 carros
    print(f"   Encontrados {len(carros)} carros")
    
    # 4. Criar questionário de teste
    print("\n4️⃣ Criando questionário de teste...")
    questionario = QuestionarioBusca(
        # Campos obrigatórios
        marca_preferida="Toyota",
        modelo_especifico="Corolla",
        urgencia="ate_15_dias",
        regiao="São Paulo",
        uso_principal=["urbano", "familia"],
        pessoas_transportar=5,
        espaco_carga="medio",
        potencia_desejada="media",
        prioridade="equilibrio",
        # Campos opcionais
        orcamento_min=50000,
        orcamento_max=100000,
        criancas=True,
        animais=False
    )
    print(f"   Uso principal: {questionario.uso_principal}")
    print(f"   Orçamento: R$ {questionario.orcamento_max:,.2f}" if questionario.orcamento_max else "   Orçamento: Não definido")
    
    # 5. Processar recomendações
    print("\n5️⃣ Processando recomendações com sistema híbrido...")
    print("-" * 60)
    
    resultados = []
    for i, carro in enumerate(carros, 1):
        print(f"\n   Carro {i}: {carro.get('marca')} {carro.get('modelo')} {carro.get('ano')}")
        
        # Processar com sistema híbrido
        resultado = processor.processar_recomendacao_completa(
            carro=carro,
            questionario=questionario,
            conversation_id=f"test_{datetime.now().timestamp()}",
            user_session_id="test_session",
            collect_data=True
        )
        
        # Exibir resultados
        print(f"   ├─ Score Final: {resultado['score']:.2f}")
        print(f"   ├─ Confiança: {resultado['confidence']:.0%}")
        print(f"   ├─ Método: {resultado['method']}")
        
        if resultado['components']:
            print(f"   ├─ Componentes:")
            print(f"   │  ├─ Busca: {resultado['components']['busca_score']:.2f}")
            print(f"   │  ├─ Uso: {resultado['components']['uso_score']:.2f}")
            print(f"   │  ├─ Regras: {resultado['components']['rule_score']:.2f}")
            if resultado['components']['ml_score']:
                print(f"   │  └─ ML: {resultado['components']['ml_score']:.2f}")
        
        if resultado['explanations']['principais']:
            print(f"   └─ Razões: {', '.join(resultado['explanations']['principais'][:2])}")
        
        resultados.append(resultado)
    
    # 6. Simular feedback de usuário
    print("\n\n6️⃣ Simulando feedback de usuário...")
    
    # Simular que o usuário gostou do primeiro e terceiro carro
    if len(carros) >= 3:
        # Like no primeiro
        processor.collector.collect_from_conversation(
            conversation_id=f"test_{datetime.now().timestamp()}",
            user_session_id="test_user_123",
            carro=carros[0],
            score=resultados[0]['score'],
            user_action="like"
        )
        print(f"   ✅ Feedback 'like' para {carros[0].get('modelo')}")
        
        # Contact no terceiro
        processor.collector.collect_from_conversation(
            conversation_id=f"test_{datetime.now().timestamp()}",
            user_session_id="test_user_123",
            carro=carros[2],
            score=resultados[2]['score'],
            user_action="contact"
        )
        print(f"   ✅ Feedback 'contact' para {carros[2].get('modelo')}")
    
    # 7. Verificar coleta de dados
    print("\n7️⃣ Verificando coleta de dados para ML...")
    new_stats = processor.get_comprehensive_stats()
    new_samples = new_stats['system_status']['total_training_samples']
    
    print(f"   Total de amostras agora: {new_samples}")
    if new_stats['system_status']['ready_to_train']:
        print("   ✅ Pronto para treinar modelo ML!")
        
        # 8. Tentar treinar modelo (se houver dados suficientes)
        print("\n8️⃣ Tentando treinar modelo ML...")
        success = processor.treinar_modelo_com_feedback()
        
        if success:
            print("   ✅ Modelo treinado com sucesso!")
            print(f"   Novo peso do ML: {processor.ml_weight:.0%}")
        else:
            print("   ⚠️ Treinamento ainda não possível (dados insuficientes)")
    else:
        samples_needed = new_stats['next_training']['samples_needed']
        print(f"   ⏳ Ainda faltam {samples_needed} amostras para treinar")
    
    # 9. Testar novamente após treinamento (se aplicável)
    if processor.ml_model.is_trained:
        print("\n9️⃣ Testando com modelo ML treinado...")
        
        # Processar um carro novamente
        if carros:
            resultado_ml = processor.processar_recomendacao_completa(
                carro=carros[0],
                questionario=questionario,
                conversation_id=f"test_ml_{datetime.now().timestamp()}",
                collect_data=False
            )
            
            print(f"   Carro: {carros[0].get('marca')} {carros[0].get('modelo')}")
            print(f"   Score com ML: {resultado_ml['score']:.2f}")
            print(f"   Método: {resultado_ml['method']}")
            
            if resultado_ml.get('metadata', {}).get('ml_weight'):
                print(f"   Peso ML aplicado: {resultado_ml['metadata']['ml_weight']:.0%}")
    
    # 10. Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DA INTEGRAÇÃO")
    print("=" * 60)
    
    final_stats = processor.get_comprehensive_stats()
    
    print(f"""
    Sistema Híbrido ML + Regras:
    ├─ Status: {'✅ Ativo' if final_stats['system_status']['ml_trained'] else '⏳ Em treinamento'}
    ├─ Total de amostras: {final_stats['system_status']['total_training_samples']}
    ├─ Peso do ML: {final_stats['system_status']['ml_weight']:.0%}
    ├─ Componentes ativos:
    │  ├─ Memory Manager: {final_stats['components_health']['memory_manager']}
    │  ├─ Uso Matcher: {final_stats['components_health']['uso_matcher']}
    │  ├─ ML Model: {final_stats['components_health']['ml_model']}
    │  └─ Collector: {final_stats['components_health']['collector']}
    └─ Próximo treinamento em: {final_stats['next_training']['estimated_time']}
    """)
    
    print("\n✅ Teste de integração concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_ml_integration()
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()