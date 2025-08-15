#!/usr/bin/env python
"""
Script para reiniciar o servidor de forma limpa, evitando erros de hot reload
"""

import os
import signal
import subprocess
import sys
import time
import psutil

def kill_existing_servers():
    """Mata processos existentes do servidor"""
    print("🔍 Procurando processos do servidor...")
    
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Procurar processos Python executando main.py ou uvicorn
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if ('main.py' in cmdline or 'uvicorn' in cmdline) and 'python' in cmdline.lower():
                print(f"🔪 Matando processo {proc.info['pid']}: {cmdline}")
                proc.terminate()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed > 0:
        print(f"✅ {killed} processo(s) terminado(s)")
        time.sleep(2)  # Aguardar finalização
    else:
        print("✅ Nenhum processo ativo encontrado")

def start_server_clean():
    """Inicia o servidor de forma limpa"""
    print("🚀 Iniciando servidor de forma limpa...")
    
    # Configurar ambiente
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    # Comando para iniciar o servidor
    cmd = [sys.executable, "main.py"]
    
    try:
        # Iniciar processo
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("✅ Servidor iniciado!")
        print("📱 Acesse: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🛑 Para parar: Ctrl+C")
        print("-" * 50)
        
        # Mostrar output em tempo real
        try:
            for line in process.stdout:
                print(line.rstrip())
                
                # Detectar quando servidor está pronto
                if "Application startup complete" in line:
                    print("🎉 Servidor está pronto para uso!")
                    
        except KeyboardInterrupt:
            print("\n🛑 Parando servidor...")
            process.terminate()
            process.wait()
            print("✅ Servidor parado")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🔧 Reinicializador Limpo do FacilIAuto")
    print("=" * 50)
    
    # Passo 1: Matar processos existentes
    kill_existing_servers()
    
    # Passo 2: Iniciar servidor limpo
    start_server_clean()

if __name__ == "__main__":
    main()