"""
Demo script showing how to use the SessionManager.

This demonstrates the key features:
- Creating and retrieving sessions
- Updating sessions with idempotency
- Managing user profile and conversation memory
- Calculating completeness and qualification scores
"""

import asyncio
import redis.asyncio as redis
from src.services.session_manager import SessionManager
from src.models.session import SessionState


async def main():
    """Run SessionManager demo."""
    
    # Initialize Redis client
    redis_client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=False
    )
    
    # Initialize SessionManager
    manager = SessionManager(
        redis_client=redis_client,
        duckdb_path="data/chatbot_context.duckdb"
    )
    
    print("=" * 60)
    print("SessionManager Demo")
    print("=" * 60)
    
    # Example phone number
    phone = "+5511999887766"
    
    # 1. Create or get session
    print(f"\n1. Creating session for {phone}...")
    session = await manager.get_or_create_session(phone)
    print(f"   ✓ Session created: {session.session_id}")
    print(f"   ✓ State: {session.state}")
    print(f"   ✓ Turn: {session.turn_id}")
    
    # 2. Simulate conversation
    print("\n2. Simulating conversation...")
    
    # User greeting
    session.add_message("user", "Olá! Quero comprar um carro.")
    session.state = SessionState.COLLECTING_PROFILE
    await manager.update_session(session)
    print(f"   ✓ User message added (turn {session.turn_id})")
    
    # Bot response
    session.add_message("assistant", "Olá! Vou te ajudar. Qual seu orçamento?")
    await manager.update_session(session)
    print(f"   ✓ Bot response added (turn {session.turn_id})")
    
    # User provides budget
    session.add_message("user", "Entre 50 e 80 mil reais")
    session.user_profile.orcamento_min = 50000
    session.user_profile.orcamento_max = 80000
    await manager.update_session(session)
    print(f"   ✓ Budget collected (turn {session.turn_id})")
    
    # 3. Check profile completeness
    print("\n3. Profile completeness:")
    print(f"   ✓ Completeness: {session.user_profile.completeness * 100:.0f}%")
    print(f"   ✓ Qualification score: {session.user_profile.qualification_score:.1f}/100")
    
    # 4. Add more profile data
    print("\n4. Collecting more profile data...")
    session.user_profile.uso_principal = "trabalho"
    session.user_profile.city = "São Paulo"
    session.user_profile.state = "SP"
    session.user_profile.prioridades = {
        "economia": 5,
        "conforto": 4,
        "seguranca": 5
    }
    session.user_profile.urgencia = "1-3 meses"
    await manager.update_session(session)
    
    print(f"   ✓ Completeness: {session.user_profile.completeness * 100:.0f}%")
    print(f"   ✓ Qualification score: {session.user_profile.qualification_score:.1f}/100")
    
    # 5. Show conversation memory
    print("\n5. Conversation memory:")
    print(f"   ✓ Total messages: {len(session.memory.messages)}")
    print(f"   ✓ Recent messages:")
    for msg in session.memory.get_recent_messages(3):
        role = msg["role"].upper()
        content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        print(f"      [{role}] {content}")
    
    # 6. Test idempotency
    print("\n6. Testing idempotency...")
    current_turn = session.turn_id
    session.turn_id = current_turn - 1  # Try to replay previous turn
    result = await manager.update_session(session)
    print(f"   ✓ Duplicate update rejected: {not result}")
    
    # 7. Retrieve session again
    print("\n7. Retrieving session from Redis...")
    retrieved = await manager.get_or_create_session(phone)
    print(f"   ✓ Session retrieved: {retrieved.session_id}")
    print(f"   ✓ Same session: {retrieved.session_id == session.session_id}")
    print(f"   ✓ Messages preserved: {len(retrieved.memory.messages)}")
    
    # 8. Get user history
    print("\n8. User history from DuckDB...")
    history = await manager.get_user_history(phone)
    print(f"   ✓ Previous sessions: {len(history)}")
    
    # 9. LGPD consent
    print("\n9. LGPD consent management...")
    print(f"   ✓ Consent given: {session.consent_given}")
    session.give_consent()
    await manager.update_session(session)
    print(f"   ✓ Consent given: {session.consent_given}")
    print(f"   ✓ Consent timestamp: {session.consent_timestamp}")
    
    # 10. Expire session
    print("\n10. Expiring session...")
    expired = await manager.expire_session(phone)
    print(f"   ✓ Session expired: {expired}")
    print(f"   ✓ Session archived to DuckDB")
    
    # Cleanup
    await manager.close()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
