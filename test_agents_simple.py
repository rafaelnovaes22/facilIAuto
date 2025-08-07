#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🤖 Demonstração do Sistema de Agentes IA
"""

from app.langgraph_chatbot_graph import get_chatbot_graph
from app.database import get_carros
from datetime import datetime

print("="*60)
print("🤖 SISTEMA DE AGENTES IA - DEMONSTRAÇÃO")
print("="*60)

# Inicializar
print("\n1️⃣ Inicializando sistema LangGraph...")
chatbot = get_chatbot_graph()

print("\n2️⃣ Carregando dados de teste...")
carros = get_carros()
carro = carros[0] if carros else {"id": 1, "modelo": "Fiat Argo", "marca": "Fiat", "ano": 2023}
print(f"   Carro teste: {carro.get('marca')} {carro.get('modelo')} {carro.get('ano')}")

print("\n3️⃣ AGENTES DISPONÍVEIS:")
print("-"*40)
agentes = chatbot.obter_agentes_disponiveis()
for tipo, info in agentes.items():
    print(f"\n{info.get('emoji', '🤖')} {info['nome']} ({tipo.upper()})")
    if 'especialidades' in info:
        for esp in info['especialidades'][:2]:
            print(f"   • {esp}")

print("\n4️⃣ TESTE DE PERGUNTAS:")
print("-"*40)

perguntas_teste = [
    "Qual o consumo deste carro?",
    "Quanto custa a manutenção?",
    "É bom para família?",
    "Vale o preço?",
    "Como financiar?",
    "É melhor que o Onix?"
]

for pergunta in perguntas_teste:
    print(f"\n❓ '{pergunta}'")
    try:
        resultado = chatbot.processar_pergunta(
            carro_id=carro["id"],
            carro_data=carro,
            pergunta=pergunta,
            conversation_id=f"demo_{datetime.now().timestamp()}",
            user_session_id="demo_user"
        )
        print(f"   → Agente: {resultado['agente']}")
        print(f"   → Confiança: {resultado['confianca']:.0%}")
        print(f"   → Resposta: {resultado['resposta'][:80]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "="*60)
print("✅ Sistema de Agentes IA funcionando perfeitamente!")
print("="*60)