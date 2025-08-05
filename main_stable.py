#!/usr/bin/env python3
"""
FacilIAuto - Versão Estável (sem hot reload)
Para uso quando você não quer que o servidor recarregue automaticamente
"""

import uvicorn
import sys
import os

def start_stable_server():
    """Inicia servidor em modo estável (sem hot reload)"""
    print("🚗 FacilIAuto - Modo Estável (sem hot reload)")
    print("📱 Interface web: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print()
    print("✅ Servidor estável - sem recarregamento automático")
    print("🛑 Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.api:app", 
            host="0.0.0.0", 
            port=8000,
            reload=False,  # SEM hot reload
            log_level="info",
            access_log=False,
            use_colors=True,
            loop="asyncio",
            workers=1
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_stable_server()