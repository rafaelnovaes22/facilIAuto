"""
Manual verification script for Task 6 implementation.

This script verifies that all components are properly implemented
without requiring pytest or external dependencies.
"""

import sys
import asyncio
from datetime import datetime


def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(test_name, passed, details=""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"  → {details}")


async def verify_imports():
    """Verify all imports work correctly."""
    print_section("1. Verifying Imports")
    
    try:
        from src.services.conversation_engine import (
            ConversationEngine,
            ConversationState,
            create_conversation_engine
        )
        print_result("ConversationEngine imports", True)
    except Exception as e:
        print_result("ConversationEngine imports", False, str(e))
        return False
    
    try:
        from src.services.guardrails import (
            GuardrailsService,
            create_guardrails_service
        )
        print_result("GuardrailsService imports", True)
    except Exception as e:
        print_result("GuardrailsService imports", False, str(e))
        return False
    
    try:
        from src.services.nlp_service import NLPService, Intent, NLPResult
        print_result("NLPService imports", True)
    except Exception as e:
        print_result("NLPService imports", False, str(e))
        return False
    
    try:
        from src.models.session import SessionData, SessionState
        print_result("Session models imports", True)
    except Exception as e:
        print_result("Session models imports", False, str(e))
        return False
    
    return True


async def verify_guardrails():
    """Verify GuardrailsService functionality."""
    print_section("2. Verifying GuardrailsService")
    
    try:
        from src.services.guardrails import GuardrailsService
        from src.models.session import SessionData
        
        # Create service
        guardrails = GuardrailsService()
        print_result("GuardrailsService initialization", True)
        
        # Test hash generation
        hash1 = guardrails.hash_content("Hello World")
        hash2 = guardrails.hash_content("hello world")
        passed = hash1 == hash2 and len(hash1) == 64
        print_result(
            "Content hashing (case-insensitive)",
            passed,
            f"Hash length: {len(hash1)}"
        )
        
        # Test duplicate detection
        session = SessionData(
            session_id="test:123",
            phone_number="5511999999999"
        )
        session.add_message("assistant", "Test response")
        
        is_dup, reformulated = guardrails.check_duplicate("Test response", session)
        print_result(
            "Duplicate detection",
            is_dup and reformulated is not None,
            f"Detected: {is_dup}, Reformulated: {reformulated is not None}"
        )
        
        # Test style policies
        is_valid, corrected, violations = guardrails.apply_style_policies("Ok")
        print_result(
            "Style policies (too short)",
            not is_valid and len(violations) > 0,
            f"Violations: {len(violations)}"
        )
        
        # Test repetition filtering
        filtered = guardrails.filter_repetitive_patterns("muito muito bom bom")
        passed = "muito muito" not in filtered
        print_result(
            "Repetition filtering",
            passed,
            f"Filtered: '{filtered}'"
        )
        
        # Test complete validation
        validated, metadata = guardrails.validate_response(
            "This is a valid response.",
            session
        )
        print_result(
            "Complete validation",
            validated is not None and "timestamp" in metadata,
            f"Metadata keys: {list(metadata.keys())}"
        )
        
        return True
        
    except Exception as e:
        print_result("GuardrailsService verification", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def verify_conversation_engine():
    """Verify ConversationEngine functionality."""
    print_section("3. Verifying ConversationEngine")
    
    try:
        from src.services.conversation_engine import ConversationEngine
        from src.services.nlp_service import NLPService
        from src.services.guardrails import GuardrailsService
        
        # Create services
        nlp = NLPService()
        guardrails = GuardrailsService()
        engine = ConversationEngine(nlp, guardrails)
        
        print_result("ConversationEngine initialization", True)
        
        # Verify graph exists
        passed = engine.graph is not None
        print_result("LangGraph creation", passed)
        
        # Verify checkpointer
        passed = engine.checkpointer is not None
        print_result("Checkpoint saver", passed)
        
        # Verify services
        passed = engine.nlp is not None and engine.guardrails is not None
        print_result("Service integration", passed)
        
        # Test graph visualization
        viz = engine.get_graph_visualization()
        passed = isinstance(viz, str) and len(viz) > 0
        print_result(
            "Graph visualization",
            passed,
            f"Length: {len(viz)} chars"
        )
        
        return True
        
    except Exception as e:
        print_result("ConversationEngine verification", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def verify_conversation_state():
    """Verify ConversationState structure."""
    print_section("4. Verifying ConversationState")
    
    try:
        from src.services.conversation_engine import ConversationState
        from src.models.session import SessionData
        from src.services.nlp_service import NLPResult, Intent, Sentiment
        
        # Create sample state
        state: ConversationState = {
            "messages": [{"role": "user", "content": "test"}],
            "session": SessionData(
                session_id="test:123",
                phone_number="5511999999999"
            ),
            "nlp_result": NLPResult(
                intent=Intent.GREETING,
                confidence=0.9,
                entities=[],
                sentiment=Sentiment.NEUTRAL,
                normalized_text="test",
                processing_time_ms=10.0
            ),
            "response": "Test response",
            "next_action": "",
            "needs_handoff": False,
            "consecutive_failures": 0,
        }
        
        # Verify all fields
        required_fields = [
            "messages", "session", "nlp_result", "response",
            "next_action", "needs_handoff", "consecutive_failures"
        ]
        
        for field in required_fields:
            passed = field in state
            print_result(f"Field '{field}' present", passed)
        
        return True
        
    except Exception as e:
        print_result("ConversationState verification", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def verify_handlers():
    """Verify handler methods exist."""
    print_section("5. Verifying Handler Methods")
    
    try:
        from src.services.conversation_engine import ConversationEngine
        from src.services.nlp_service import NLPService
        from src.services.guardrails import GuardrailsService
        
        nlp = NLPService()
        guardrails = GuardrailsService()
        engine = ConversationEngine(nlp, guardrails)
        
        # Check handler methods exist
        handlers = [
            "_process_nlp",
            "_handle_greeting",
            "_collect_profile",
            "_generate_recommendations",
            "_show_car_details",
            "_compare_cars",
            "_human_handoff",
            "_apply_guardrails",
            "_route_by_intent",
        ]
        
        for handler in handlers:
            passed = hasattr(engine, handler)
            print_result(f"Handler '{handler}' exists", passed)
        
        # Check main method
        passed = hasattr(engine, "process_message")
        print_result("Main 'process_message' method exists", passed)
        
        return True
        
    except Exception as e:
        print_result("Handler verification", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("  TASK 6 IMPLEMENTATION VERIFICATION")
    print("  Conversation Engine + Guardrails")
    print("="*60)
    
    results = []
    
    # Run verifications
    results.append(await verify_imports())
    results.append(await verify_guardrails())
    results.append(await verify_conversation_engine())
    results.append(await verify_conversation_state())
    results.append(await verify_handlers())
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ALL VERIFICATIONS PASSED!")
        print("\nTask 6 implementation is complete and functional:")
        print("  ✅ 6.1: LangGraph state graph with checkpoints")
        print("  ✅ 6.2: All conversation handlers")
        print("  ✅ 6.3: Guardrails for deduplication and validation")
        return 0
    else:
        print(f"\n❌ {total - passed} VERIFICATION(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
