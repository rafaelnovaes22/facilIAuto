#!/usr/bin/env python3
"""
FacilIAuto - Sistema de Busca Inteligente de Carros
Desenvolvido com LangGraph e FastAPI
"""

import uvicorn

if __name__ == "__main__":
    print("🚗 Iniciando FacilIAuto - Sistema de Busca Inteligente de Carros")
    print("📱 Interface web disponível em: http://localhost:8000")
    print("📚 Documentação da API em: http://localhost:8000/docs")
    print("🔧 Status da aplicação em: http://localhost:8000/health")
    print()
    print("Para parar o servidor, pressione Ctrl+C")
    print("-" * 50)
    
    # Configuração otimizada para evitar erros de hot reload
    uvicorn.run(
        "app.api:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        reload_excludes=["*.pyc", "*/__pycache__/*", "*/logs/*", "*/backups/*"],
        reload_includes=["*.py"],
        log_level="info",
        access_log=False,  # Reduz verbosidade
        use_colors=True,
        loop="asyncio"
    ) 