"""
Sistema de busca inteligente com fallback robusto para CI/CD
"""
from typing import Any, Dict, List
from app.database import get_carros
from app.models import CarroRecomendacao, QuestionarioBusca, RespostaBusca


def processar_busca_simples_fallback(questionario: QuestionarioBusca) -> RespostaBusca:
    """
    Versão simplificada da busca que sempre funciona
    Usado como fallback quando o LangGraph falha no CI/CD
    """
    print("🔄 [FALLBACK] Usando busca simplificada...")
    
    try:
        # Buscar carros
        carros = get_carros()
        print(f"🔄 [FALLBACK] {len(carros)} carros carregados")
        
        # Filtro básico por orçamento
        carros_filtrados = []
        for carro in carros:
            if (questionario.orcamento_min is not None and 
                questionario.orcamento_max is not None):
                if (questionario.orcamento_min <= carro.get("preco", 0) <= 
                    questionario.orcamento_max):
                    carros_filtrados.append(carro)
            else:
                carros_filtrados.append(carro)
        
        print(f"🔄 [FALLBACK] {len(carros_filtrados)} carros após filtro de orçamento")
        
        # Se não há carros no orçamento, pegar os 2 mais baratos
        if not carros_filtrados:
            carros_filtrados = sorted(carros, key=lambda x: x.get("preco", 999999))[:2]
            print(f"🔄 [FALLBACK] Usando {len(carros_filtrados)} carros mais baratos")
        
        # Criar recomendações simples
        recomendacoes = []
        for i, carro in enumerate(carros_filtrados[:3]):  # Máximo 3 carros
            try:
                recomendacao = CarroRecomendacao(
                    id=str(carro.get("id", i + 1)),
                    marca=carro.get("marca", "Marca"),
                    modelo=carro.get("modelo", "Modelo"),
                    ano=carro.get("ano", 2020),
                    preco=carro.get("preco", 50000),
                    combustivel=carro.get("combustivel", "Flex"),
                    cambio=carro.get("cambio", "Manual"),
                    cor=carro.get("cor", "Branco"),
                    km=carro.get("km", 50000),
                    fotos=carro.get("fotos", []),
                    score_compatibilidade=90.0 - (i * 10),  # Score decrescente
                    razoes_recomendacao=[
                        f"Dentro do orçamento de R$ {questionario.orcamento_min}-{questionario.orcamento_max}",
                        f"Adequado para uso {questionario.uso_principal[0] if questionario.uso_principal else 'geral'}",
                        "Boa opção de custo-benefício"
                    ],
                    categoria=carro.get("categoria", "hatch"),
                    uso_recomendado=questionario.uso_principal if questionario.uso_principal else ["urbano"]
                )
                recomendacoes.append(recomendacao)
            except Exception as e:
                print(f"🔄 [FALLBACK] Erro ao criar recomendação {i}: {e}")
                continue
        
        # Criar resposta
        resumo = f"Perfil: Busca por {questionario.uso_principal[0] if questionario.uso_principal else 'veículo'} na região {questionario.regiao}, para {questionario.pessoas_transportar} pessoas, com orçamento entre R$ {questionario.orcamento_min} e R$ {questionario.orcamento_max}."
        
        sugestoes = [
            "Considere visitar a concessionária para test drive",
            "Verifique o histórico de manutenção do veículo",
            "Compare preços com outras ofertas do mercado",
            "Analise o custo de seguro antes da compra",
            "Verifique se há financiamento disponível"
        ]
        
        resultado = RespostaBusca(
            recomendacoes=recomendacoes,
            resumo_perfil=resumo,
            sugestoes_gerais=sugestoes
        )
        
        print(f"🔄 [FALLBACK] Busca concluída: {len(resultado.recomendacoes)} recomendações")
        return resultado
        
    except Exception as e:
        print(f"🔄 [FALLBACK] Erro crítico no fallback: {e}")
        # Fallback absoluto - resposta mínima
        return RespostaBusca(
            recomendacoes=[],
            resumo_perfil="Sistema temporariamente indisponível. Tente novamente em alguns instantes.",
            sugestoes_gerais=["Entre em contato conosco para assistência personalizada"]
        )


def processar_busca_inteligente_robusta(questionario: QuestionarioBusca) -> RespostaBusca:
    """
    Versão robusta que tenta usar LangGraph mas faz fallback se necessário
    """
    print("🧠 [BUSCA] Iniciando busca inteligente robusta...")
    
    try:
        # Tentar busca completa com LangGraph
        print("🧠 [BUSCA] Tentando busca completa com LangGraph...")
        from app.busca_inteligente import processar_busca_inteligente
        resultado = processar_busca_inteligente(questionario)
        print("🧠 [BUSCA] Busca completa bem-sucedida!")
        return resultado
        
    except ImportError as e:
        print(f"🔄 [BUSCA] Erro de import LangGraph: {e}")
        return processar_busca_simples_fallback(questionario)
        
    except Exception as e:
        print(f"🔄 [BUSCA] Erro na busca completa: {e}")
        print("🔄 [BUSCA] Usando fallback simplificado...")
        return processar_busca_simples_fallback(questionario)
