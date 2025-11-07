# Configuration Module

This directory contains application configuration and environment variable management.

## Files

### `env.ts`

Validates and exports environment variables with type safety. This module runs on app startup and will throw an error if required variables are missing or invalid.

**Features**:
- ✅ Validates required environment variables exist
- ✅ Validates API URL format (http:// or https://)
- ✅ Validates WhatsApp number format (DDI + DDD + Number)
- ✅ Provides type-safe exports
- ✅ Logs configuration on startup

**Usage**:

```typescript
import { API_URL, WHATSAPP_NUMBER, IS_DEVELOPMENT } from '@/config/env'

// Use validated environment variables
const apiClient = axios.create({
  baseURL: API_URL
})
```

**Environment Variables**:

| Variable | Required | Format | Example |
|----------|----------|--------|---------|
| `VITE_API_URL` | Yes | http(s)://... | `http://localhost:8000` |
| `VITE_WHATSAPP_NUMBER` | Yes | DDI+DDD+Number | `5511949105033` |

**Error Handling**:

If validation fails, the app will not start and will display a clear error message:

```
❌ Missing required environment variable: VITE_API_URL
Please check your .env file and ensure VITE_API_URL is set.
```

```
❌ Invalid VITE_API_URL format: invalid-url
Expected format: http://localhost:8000 or https://api.example.com
```

## Environment Files

The project uses different `.env` files for different environments:

- `.env.development` - Used automatically in development mode (`npm run dev`)
- `.env.production` - Used in production builds (`npm run build`)
- `.env` - Fallback for local development (not committed to git)

**Development** (`.env.development`):
```bash
VITE_API_URL=http://localhost:8000
VITE_WHATSAPP_NUMBER=5511949105033
```

**Production** (`.env.production`):
```bash
VITE_API_URL=https://faciliauto-backend.up.railway.app
VITE_WHATSAPP_NUMBER=5511949105033
```

## Adding New Environment Variables

1. Add the variable to `.env.development` and `.env.production`
2. Add validation in `env.ts`:
   ```typescript
   const myVar = validateEnvVar('VITE_MY_VAR', import.meta.env.VITE_MY_VAR)
   ```
3. Export the validated value:
   ```typescript
   export const MY_VAR = myVar
   ```
4. Update Railway environment variables in production

## Best Practices

- ✅ Always prefix Vite environment variables with `VITE_`
- ✅ Validate all required variables in `env.ts`
- ✅ Use type-safe exports from `env.ts` instead of `import.meta.env` directly
- ✅ Document new variables in this README
- ❌ Never commit sensitive values to git
- ❌ Never use `import.meta.env` directly in components (use `env.ts` exports)
