"""Verify webhook implementation."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings
from src.services.redis_client import get_redis_client
from src.services.whatsapp_client import get_whatsapp_client

settings = get_settings()


async def verify_redis():
    """Verify Redis connection."""
    print("🔍 Checking Redis connection...")
    try:
        redis = await get_redis_client()
        if redis is None:
            print("❌ Redis connection failed")
            return False

        # Test ping
        await redis.ping()
        print("✅ Redis connection successful")

        # Test set/get
        await redis.set("test_key", "test_value", ex=10)
        value = await redis.get("test_key")
        if value == "test_value":
            print("✅ Redis read/write working")
        else:
            print("❌ Redis read/write failed")
            return False

        return True
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False


async def verify_whatsapp_config():
    """Verify WhatsApp configuration."""
    print("\n🔍 Checking WhatsApp configuration...")

    # Check required settings
    required = [
        ("WHATSAPP_API_URL", settings.whatsapp_api_url),
        ("WHATSAPP_PHONE_NUMBER_ID", settings.whatsapp_phone_number_id),
        ("WHATSAPP_ACCESS_TOKEN", settings.whatsapp_access_token),
        ("WHATSAPP_VERIFY_TOKEN", settings.whatsapp_verify_token),
        ("WHATSAPP_WEBHOOK_SECRET", settings.whatsapp_webhook_secret),
    ]

    all_configured = True
    for name, value in required:
        if not value or value == "":
            print(f"❌ {name} not configured")
            all_configured = False
        else:
            # Mask sensitive values
            if "TOKEN" in name or "SECRET" in name:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print(f"✅ {name}: {masked}")
            else:
                print(f"✅ {name}: {value}")

    return all_configured


async def verify_whatsapp_client():
    """Verify WhatsApp client initialization."""
    print("\n🔍 Checking WhatsApp client...")
    try:
        client = await get_whatsapp_client()
        print("✅ WhatsApp client initialized")
        return True
    except Exception as e:
        print(f"❌ WhatsApp client error: {e}")
        return False


async def verify_webhook_endpoints():
    """Verify webhook endpoints are accessible."""
    print("\n🔍 Checking webhook endpoints...")
    try:
        import httpx

        # Check if server is running
        async with httpx.AsyncClient() as client:
            # Health check
            try:
                response = await client.get("http://localhost:8000/health")
                if response.status_code == 200:
                    print("✅ Health endpoint responding")
                else:
                    print(f"⚠️  Health endpoint returned {response.status_code}")
            except httpx.ConnectError:
                print("❌ Server not running on http://localhost:8000")
                print("   Start server with: uvicorn src.main:app --reload")
                return False

            # Webhook verification endpoint
            try:
                response = await client.get(
                    "http://localhost:8000/webhook/whatsapp",
                    params={
                        "hub.mode": "subscribe",
                        "hub.challenge": "test123",
                        "hub.verify_token": settings.whatsapp_verify_token,
                    },
                )
                if response.status_code == 200 and response.text == "test123":
                    print("✅ Webhook verification endpoint working")
                else:
                    print(f"❌ Webhook verification failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Webhook verification error: {e}")
                return False

        return True
    except ImportError:
        print("⚠️  httpx not available, skipping endpoint checks")
        return True


async def main():
    """Run all verification checks."""
    print("=" * 60)
    print("WhatsApp Webhook Verification")
    print("=" * 60)

    results = []

    # Check Redis
    results.append(("Redis", await verify_redis()))

    # Check WhatsApp config
    results.append(("WhatsApp Config", await verify_whatsapp_config()))

    # Check WhatsApp client
    results.append(("WhatsApp Client", await verify_whatsapp_client()))

    # Check webhook endpoints
    results.append(("Webhook Endpoints", await verify_webhook_endpoints()))

    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! Webhook is ready to use.")
        print("\nNext steps:")
        print("1. Configure webhook URL in Meta Developer Console")
        print("2. Send a test message to your WhatsApp number")
        print("3. Check logs for incoming messages")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Ensure Redis is running: docker run -d -p 6379:6379 redis:7-alpine")
        print("- Configure .env file with WhatsApp credentials")
        print("- Start server: uvicorn src.main:app --reload")

    # Cleanup
    from src.services.redis_client import close_redis_client
    from src.services.whatsapp_client import close_whatsapp_client

    await close_whatsapp_client()
    await close_redis_client()

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
