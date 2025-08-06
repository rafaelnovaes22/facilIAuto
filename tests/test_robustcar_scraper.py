#!/usr/bin/env python3
"""
Script de teste para o scraper do RobustCar
Testa a funcionalidade de busca e extração de imagens
"""

import asyncio
import json
import logging
from datetime import datetime

from vehicle_image_scraper import RobustCarScraper

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_robustcar_scraper():
    """Testa o scraper do RobustCar com veículos de exemplo"""

    # Veículos de teste
    test_vehicles = [
        {
            "vehicle_id": "test_1",
            "marca": "TOYOTA",
            "modelo": "COROLLA",
            "ano": 2023,
            "cor": "BRANCO",
        },
        {
            "vehicle_id": "test_2",
            "marca": "HONDA",
            "modelo": "CIVIC",
            "ano": 2022,
            "cor": "PRETO",
        },
        {
            "vehicle_id": "test_3",
            "marca": "VOLKSWAGEN",
            "modelo": "JETTA",
            "ano": 2024,
            "cor": "PRATA",
        },
        {
            "vehicle_id": "test_4",
            "marca": "HYUNDAI",
            "modelo": "HB20",
            "ano": 2023,
            "cor": "AZUL",
        },
        {
            "vehicle_id": "test_5",
            "marca": "CHEVROLET",
            "modelo": "ONIX",
            "ano": 2022,
            "cor": "VERMELHO",
        },
    ]

    print("🚀 INICIANDO TESTE DO SCRAPER ROBUSTCAR")
    print("=" * 60)

    scraper = RobustCarScraper()

    try:
        # Testar scraping para cada veículo
        for i, vehicle in enumerate(test_vehicles, 1):
            print(f"\n📋 TESTE {i}/5: {vehicle['marca']} {vehicle['modelo']} {vehicle['ano']}")
            print("-" * 50)

            try:
                images = await scraper.scrape_vehicle_images(vehicle, max_images=3)

                if images:
                    print(f"✅ Sucesso! Encontradas {len(images)} imagens:")
                    for j, img in enumerate(images, 1):
                        print(f"   {j}. {img['url']}")
                        print(f"      Fonte: {img['source']}, Qualidade: {img['quality_score']}")
                else:
                    print("❌ Nenhuma imagem encontrada")

            except Exception as e:
                print(f"❌ Erro: {str(e)}")
                scraper.stats["failed_searches"] += 1

            # Pausa entre testes
            await asyncio.sleep(2)

        # Mostrar estatísticas finais
        print("\n" + "=" * 60)
        print("📊 ESTATÍSTICAS FINAIS DO TESTE")
        print("=" * 60)
        scraper.print_scraping_summary()

        # Salvar resultados do teste
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "test_vehicles": test_vehicles,
            "statistics": scraper.stats,
            "failed_searches": scraper.failed_searches,
        }

        test_file = f"robustcar_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados salvos em: {test_file}")

        # Verificar se o teste foi bem-sucedido
        success_rate = (scraper.stats["successful_matches"] / len(test_vehicles)) * 100

        if success_rate >= 60:
            print(f"🎉 TESTE APROVADO! Taxa de sucesso: {success_rate:.1f}%")
        else:
            print(f"⚠️  TESTE PARCIAL. Taxa de sucesso: {success_rate:.1f}%")
            print("   Isso pode ser normal se o site RobustCar não tiver os veículos testados")

    except Exception as e:
        logger.error(f"❌ Erro durante teste: {str(e)}")
        raise


async def test_robustcar_connection():
    """Testa apenas a conexão com o site RobustCar"""
    print("🔗 TESTANDO CONEXÃO COM ROBUSTCAR...")

    scraper = RobustCarScraper()

    import aiohttp

    try:
        connector = aiohttp.TCPConnector(limit=3)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": scraper.user_agents[0]},
        ) as session:
            # Testar acesso ao site principal
            async with session.get(scraper.base_url) as response:
                if response.status == 200:
                    print(f"✅ Conexão com {scraper.base_url} bem-sucedida!")
                    print(f"   Status: {response.status}")
                    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

                    # Testar busca de veículos
                    vehicles = await scraper.get_robustcar_vehicles(session)
                    if vehicles:
                        print(f"✅ Encontrados {len(vehicles)} veículos no site!")
                        print("   Exemplos:")
                        for vehicle in vehicles[:3]:
                            print(f"   - {vehicle['marca']} {vehicle['modelo']} ({vehicle.get('ano', 'N/A')})")
                    else:
                        print("⚠️  Nenhum veículo encontrado (pode ser normal)")
                else:
                    print(f"❌ Erro de conexão: HTTP {response.status}")

    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        print("   Verifique se o site está acessível e sua conexão com a internet")


async def main():
    """Função principal do teste"""
    import argparse

    parser = argparse.ArgumentParser(description="Testar scraper do RobustCar")
    parser.add_argument(
        "--connection-only",
        action="store_true",
        help="Testar apenas a conexão com o site",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Log detalhado")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.connection_only:
            await test_robustcar_connection()
        else:
            await test_robustcar_connection()
            print("\n")
            await test_robustcar_scraper()

    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
