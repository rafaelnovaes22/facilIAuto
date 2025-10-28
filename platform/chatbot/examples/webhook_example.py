"""Example usage of webhook and WhatsApp client."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.whatsapp_client import get_whatsapp_client


async def example_send_text():
    """Example: Send a text message."""
    print("📤 Sending text message...")

    client = await get_whatsapp_client()

    result = await client.send_text_message(
        to="5511999999999",  # Replace with actual number
        text="Olá! Bem-vindo ao FacilIAuto! 🚗\n\nComo posso ajudar você hoje?",
    )

    print(f"✅ Message sent: {result['messages'][0]['id']}")


async def example_send_image():
    """Example: Send an image with caption."""
    print("\n📤 Sending image message...")

    client = await get_whatsapp_client()

    result = await client.send_image_message(
        to="5511999999999",
        image_url="https://example.com/honda-civic-2023.jpg",
        caption="🚗 Honda Civic 2023\n💰 R$ 125.000\n⭐ 95% de compatibilidade",
    )

    print(f"✅ Image sent: {result['messages'][0]['id']}")


async def example_send_interactive():
    """Example: Send interactive message with buttons."""
    print("\n📤 Sending interactive message...")

    client = await get_whatsapp_client()

    result = await client.send_interactive_message(
        to="5511999999999",
        header_text="FacilIAuto",
        body_text="Como posso ajudar você hoje?",
        buttons=[
            {"id": "see_cars", "title": "Ver carros"},
            {"id": "talk_seller", "title": "Falar com vendedor"},
            {"id": "help", "title": "Ajuda"},
        ],
        footer_text="Powered by FacilIAuto",
    )

    print(f"✅ Interactive message sent: {result['messages'][0]['id']}")


async def example_send_template():
    """Example: Send template message."""
    print("\n📤 Sending template message...")

    client = await get_whatsapp_client()

    result = await client.send_template_message(
        to="5511999999999",
        template_name="welcome_message",  # Must be pre-approved
        language_code="pt_BR",
        components=[
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "João"},  # Customer name
                ],
            }
        ],
    )

    print(f"✅ Template sent: {result['messages'][0]['id']}")


async def example_conversation_flow():
    """Example: Complete conversation flow."""
    print("\n💬 Starting conversation flow...")

    client = await get_whatsapp_client()

    # 1. Welcome message
    await client.send_text_message(
        to="5511999999999",
        text="Olá! 👋 Bem-vindo ao FacilIAuto!\n\nSou seu assistente virtual e vou te ajudar a encontrar o carro ideal.",
    )
    await asyncio.sleep(1)

    # 2. Ask for budget
    await client.send_text_message(
        to="5511999999999",
        text="Para começar, qual é o seu orçamento aproximado?",
    )
    await asyncio.sleep(2)

    # Simulate user response: "Até 80 mil"

    # 3. Ask for usage
    await client.send_text_message(
        to="5511999999999",
        text="Perfeito! E como você pretende usar o carro?\n\n1️⃣ Trabalho\n2️⃣ Família\n3️⃣ Lazer\n4️⃣ Todos os dias",
    )
    await asyncio.sleep(2)

    # Simulate user response: "Família"

    # 4. Show recommendations
    await client.send_text_message(
        to="5511999999999",
        text="Ótimo! Deixa eu buscar os melhores carros para você... 🔍",
    )
    await asyncio.sleep(1)

    # 5. Send car recommendations
    await client.send_image_message(
        to="5511999999999",
        image_url="https://example.com/honda-civic.jpg",
        caption=(
            "🎯 Encontrei ótimas opções!\n\n"
            "1. *Honda Civic* (2023)\n"
            "   💰 R$ 125.000\n"
            "   ⭐ 95% de compatibilidade\n"
            "   📝 Perfeito para família, econômico e confortável"
        ),
    )
    await asyncio.sleep(1)

    # 6. Ask for action
    await client.send_interactive_message(
        to="5511999999999",
        body_text="Gostou dessa opção?",
        buttons=[
            {"id": "details", "title": "Ver detalhes"},
            {"id": "more", "title": "Mais opções"},
            {"id": "contact", "title": "Falar com vendedor"},
        ],
    )

    print("✅ Conversation flow completed!")


async def main():
    """Run examples."""
    print("=" * 60)
    print("WhatsApp Client Examples")
    print("=" * 60)

    try:
        # Run examples
        # await example_send_text()
        # await example_send_image()
        # await example_send_interactive()
        # await example_send_template()
        await example_conversation_flow()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        from src.services.whatsapp_client import close_whatsapp_client

        await close_whatsapp_client()


if __name__ == "__main__":
    # Note: Replace "5511999999999" with actual WhatsApp number
    print("\n⚠️  Remember to replace '5511999999999' with actual number!")
    print("⚠️  Uncomment the examples you want to run in main()\n")

    asyncio.run(main())
