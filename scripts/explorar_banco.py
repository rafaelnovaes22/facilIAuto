#!/usr/bin/env python3
"""
Script para explorar a estrutura do banco PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="carencia_db",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return None

def listar_tabelas(conn):
    """Lista todas as tabelas do banco"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tabelas = cursor.fetchall()
    cursor.close()
    return [t[0] for t in tabelas]

def descrever_tabela(conn, nome_tabela):
    """Descreve a estrutura de uma tabela"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, (nome_tabela,))
    
    colunas = cursor.fetchall()
    cursor.close()
    return colunas

def contar_registros(conn, nome_tabela):
    """Conta registros em uma tabela"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
    count = cursor.fetchone()[0]
    cursor.close()
    return count

def amostrar_dados(conn, nome_tabela, limite=5):
    """Mostra uma amostra dos dados da tabela"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT %s", (limite,))
    dados = cursor.fetchall()
    cursor.close()
    return dados

def main():
    print("🔍 Explorando banco de dados PostgreSQL...")
    print("=" * 60)
    
    # Conecta ao banco
    conn = conectar_banco()
    if not conn:
        print("❌ Falha na conexão com o banco!")
        return
    
    print("✅ Conectado ao banco com sucesso!")
    print()
    
    # Lista tabelas
    tabelas = listar_tabelas(conn)
    print(f"📋 Tabelas encontradas ({len(tabelas)}):")
    for i, tabela in enumerate(tabelas, 1):
        count = contar_registros(conn, tabela)
        print(f"  {i}. {tabela} ({count} registros)")
    print()
    
    # Analisa cada tabela
    for tabela in tabelas:
        print(f"🔍 Analisando tabela: {tabela}")
        print("-" * 40)
        
        # Estrutura da tabela
        colunas = descrever_tabela(conn, tabela)
        print("Estrutura:")
        for col in colunas:
            nome, tipo, nullable, default = col
            nullable_text = "NULL" if nullable == "YES" else "NOT NULL"
            default_text = f" DEFAULT {default}" if default else ""
            print(f"  • {nome}: {tipo} {nullable_text}{default_text}")
        
        # Amostra de dados
        print("\nAmostra de dados:")
        try:
            dados = amostrar_dados(conn, tabela)
            if dados:
                df = pd.DataFrame(dados)
                print(df.to_string(index=False))
            else:
                print("  (Tabela vazia)")
        except Exception as e:
            print(f"  Erro ao buscar dados: {e}")
        
        print("\n" + "=" * 60)
    
    conn.close()
    print("🏁 Exploração concluída!")

if __name__ == "__main__":
    main() 