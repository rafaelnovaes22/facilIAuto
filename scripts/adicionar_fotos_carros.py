#!/usr/bin/env python3
"""
Script para adicionar fotos aos carros no banco PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configuração do banco
DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "carencia_db",
    "user": "postgres",
    "password": "postgres"
}

# URLs de exemplo de fotos de carros (usando links de imagens públicas)
FOTOS_CARROS = {
    # Exemplos de URLs de fotos de carros por marca/modelo
    "TOYOTA": [
        "https://www.toyota.com.br/content/dam/toyota/brazil/vehicles/corolla/2023/overview/corolla-sedan-2023-gallery-01.jpg",
        "https://www.toyota.com.br/content/dam/toyota/brazil/vehicles/corolla/2023/overview/corolla-sedan-2023-gallery-02.jpg"
    ],
    "HONDA": [
        "https://www.honda.com.br/content/dam/honda/brazil/cars/civic/2023/gallery/civic-2023-gallery-01.jpg",
        "https://www.honda.com.br/content/dam/honda/brazil/cars/civic/2023/gallery/civic-2023-gallery-02.jpg"
    ],
    "VOLKSWAGEN": [
        "https://www.vw.com.br/content/dam/vw-ngw/vw_pkw/importers/br/models/t-cross/gallery/t-cross-gallery-01.jpg",
        "https://www.vw.com.br/content/dam/vw-ngw/vw_pkw/importers/br/models/t-cross/gallery/t-cross-gallery-02.jpg"
    ],
    "HYUNDAI": [
        "https://www.hyundai.com.br/content/dam/hyundai/br/models/tucson/gallery/tucson-gallery-01.jpg",
        "https://www.hyundai.com.br/content/dam/hyundai/br/models/tucson/gallery/tucson-gallery-02.jpg"
    ],
    "CHEVROLET": [
        "https://www.chevrolet.com.br/content/dam/chevrolet/south-america/brazil/portuguese/index/cars/onix/2023/colorizer/onix-branco-summit.jpg",
        "https://www.chevrolet.com.br/content/dam/chevrolet/south-america/brazil/portuguese/index/cars/onix/2023/gallery/onix-gallery-01.jpg"
    ],
    "FORD": [
        "https://www.ford.com.br/content/dam/ford/brazil/vehicles/ranger/2023/gallery/ranger-gallery-01.jpg",
        "https://www.ford.com.br/content/dam/ford/brazil/vehicles/ranger/2023/gallery/ranger-gallery-02.jpg"
    ],
    "NISSAN": [
        "https://www.nissan.com.br/content/dam/nissan/brazil/vehicles/kicks/2023/gallery/kicks-gallery-01.jpg",
        "https://www.nissan.com.br/content/dam/nissan/brazil/vehicles/frontier/2023/gallery/frontier-gallery-01.jpg"
    ],
    "BMW": [
        "https://www.bmw.com.br/content/dam/bmw/common/all-models/x-series/x1/2023/gallery/x1-gallery-01.jpg",
        "https://www.bmw.com.br/content/dam/bmw/common/all-models/x-series/x1/2023/gallery/x1-gallery-02.jpg"
    ],
    "FIAT": [
        "https://www.fiat.com.br/content/dam/fiat/brazil/vehicles/argo/gallery/argo-gallery-01.jpg",
        "https://www.fiat.com.br/content/dam/fiat/brazil/vehicles/toro/gallery/toro-gallery-01.jpg"
    ],
    "JEEP": [
        "https://www.jeep.com.br/content/dam/jeep/brazil/vehicles/compass/2023/gallery/compass-gallery-01.jpg",
        "https://www.jeep.com.br/content/dam/jeep/brazil/vehicles/compass/2023/gallery/compass-gallery-02.jpg"
    ]
}

def adicionar_fotos_genericas():
    """Adiciona fotos genéricas baseadas na marca do carro"""
    conn = psycopg2.connect(
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        database=DATABASE_CONFIG["database"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"]
    )
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Busca todos os carros que não têm fotos
        cursor.execute("""
            SELECT id, marca, modelo 
            FROM veiculos 
            WHERE fotos IS NULL OR array_length(fotos, 1) IS NULL
            ORDER BY marca, modelo
        """)
        
        carros = cursor.fetchall()
        print(f"Encontrados {len(carros)} carros sem fotos")
        
        for carro in carros:
            marca = carro["marca"].upper()
            modelo = carro["modelo"].upper()
            
            # Seleciona fotos baseadas na marca
            fotos = FOTOS_CARROS.get(marca, [
                f"https://via.placeholder.com/400x300/0066cc/ffffff?text={marca}+{modelo}",
                f"https://via.placeholder.com/400x300/cc6600/ffffff?text={marca}+{modelo}"
            ])
            
            # Adiciona fotos específicas para alguns modelos conhecidos
            if "COROLLA" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/0066cc/ffffff?text=Toyota+Corolla+1",
                    "https://via.placeholder.com/400x300/0066cc/ffffff?text=Toyota+Corolla+2"
                ]
            elif "CIVIC" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/cc0000/ffffff?text=Honda+Civic+1", 
                    "https://via.placeholder.com/400x300/cc0000/ffffff?text=Honda+Civic+2"
                ]
            elif "T-CROSS" in modelo or "TCROSS" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/0099cc/ffffff?text=VW+T-Cross+1",
                    "https://via.placeholder.com/400x300/0099cc/ffffff?text=VW+T-Cross+2"
                ]
            elif "TUCSON" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/666666/ffffff?text=Hyundai+Tucson+1",
                    "https://via.placeholder.com/400x300/666666/ffffff?text=Hyundai+Tucson+2"
                ]
            elif "ONIX" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/ffcc00/000000?text=Chevrolet+Onix+1",
                    "https://via.placeholder.com/400x300/ffcc00/000000?text=Chevrolet+Onix+2"
                ]
            elif "RANGER" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/003366/ffffff?text=Ford+Ranger+1",
                    "https://via.placeholder.com/400x300/003366/ffffff?text=Ford+Ranger+2"
                ]
            elif "KICKS" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/ff6600/ffffff?text=Nissan+Kicks+1",
                    "https://via.placeholder.com/400x300/ff6600/ffffff?text=Nissan+Kicks+2"
                ]
            elif "FRONTIER" in modelo:
                fotos = [
                    "https://via.placeholder.com/400x300/333333/ffffff?text=Nissan+Frontier+1",
                    "https://via.placeholder.com/400x300/333333/ffffff?text=Nissan+Frontier+2"
                ]
            
            # Atualiza o carro com as fotos (usando array PostgreSQL)
            cursor.execute("""
                UPDATE veiculos 
                SET fotos = %s 
                WHERE id = %s
            """, (fotos, carro["id"]))
            
            print(f"✅ Adicionadas {len(fotos)} fotos para {marca} {modelo}")
        
        conn.commit()
        print(f"\n🎉 Processo concluído! Fotos adicionadas a {len(carros)} carros.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def listar_carros_com_fotos():
    """Lista carros que já têm fotos para verificação"""
    conn = psycopg2.connect(
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        database=DATABASE_CONFIG["database"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"]
    )
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT id, marca, modelo, fotos 
            FROM veiculos 
            WHERE fotos IS NOT NULL AND array_length(fotos, 1) > 0
            ORDER BY marca, modelo
            LIMIT 10
        """)
        
        carros = cursor.fetchall()
        
        print("\n📸 Carros com fotos (primeiros 10):")
        print("-" * 50)
        
        for carro in carros:
            fotos = carro["fotos"] if carro["fotos"] else []
            print(f"{carro['marca']} {carro['modelo']} - {len(fotos)} foto(s)")
            
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚗 Adicionando fotos aos carros...")
    print("=" * 50)
    
    # Adiciona fotos genéricas
    adicionar_fotos_genericas()
    
    # Lista alguns carros para verificação
    listar_carros_com_fotos() 