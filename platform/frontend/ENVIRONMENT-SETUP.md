# Environment Variable Setup - FacilIAuto Frontend

## Overview

The FacilIAuto frontend uses environment variables for configuration. This document explains how environment variables are managed, validated, and used across different environments.

## Environment Files

### `.env.development` (Development)
Used automatically when running `npm run dev`:
```bash
VITE_API_URL=http://localhost:8000
VITE_WHATSAPP_NUMBER=5511949105033
```

### `.env.production` (Production)
Used when building for production (`npm run build`):
```bash
VITE_API_URL=https://faciliauto-backend.up.railway.app
VITE_WHATSAPP_NUMBER=5511949105033
```

### `.env` (Local Override)
Optional file for local development overrides (not committed to git):
```bash
VITE_API_URL=http://localhost:8000
VITE_WHATSAPP_NUMBER=5511949105033
```

## Required Variables

| Variable | Required | Description | Format | Example |
|----------|----------|-------------|--------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `http(s)://...` | `http://localhost:8000` |
| `VITE_WHATSAPP_NUMBER` | ✅ Yes | WhatsApp contact number | DDI+DDD+Number | `5511949105033` |

## Automatic Validation

The application validates environment variables on startup using `src/config/env.ts`:

### Validations Performed

1. **Existence Check**: Ensures required variables are defined
2. **Format Validation**: 
   - API URL must start with `http://` or `https://`
   - WhatsApp number must match format: `55` (DDI) + `10-11 digits`
3. **Type Safety**: Exports validated values with TypeScript types

### Error Messages

If validation fails, you'll see clear error messages:

```
❌ Missing required environment variable: VITE_API_URL
Please check your .env file and ensure VITE_API_URL is set.
```

```
❌ Invalid VITE_API_URL format: invalid-url
Expected format: http://localhost:8000 or https://api.example.com
Error: Protocol must be http: or https:
```

```
❌ Invalid VITE_WHATSAPP_NUMBER format: 123456
Expected format: 5511949105033 (DDI + DDD + Number)
```

## Usage in Code

### ✅ Correct Way (Type-Safe)

```typescript
import { API_URL, WHATSAPP_NUMBER, IS_DEVELOPMENT } from '@/config/env'

// Use validated environment variables
const apiClient = axios.create({
  baseURL: API_URL
})

const whatsappLink = `https://wa.me/${WHATSAPP_NUMBER}`
```

### ❌ Incorrect Way (Not Validated)

```typescript
// Don't use import.meta.env directly
const apiUrl = import.meta.env.VITE_API_URL // No validation!
```

## Development Setup

### First Time Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. The `.env.development` file is already configured with defaults
4. Start development server:
   ```bash
   npm run dev
   ```

### Local Overrides

If you need different values locally:

1. Create `.env` file (not committed to git):
   ```bash
   cp .env.example .env
   ```
2. Edit values as needed
3. Restart dev server

## Production Deployment (Railway)

### Setting Environment Variables

1. Go to Railway Dashboard
2. Select the frontend service
3. Click **"Variables"**
4. Add required variables:
   - `VITE_API_URL`: Your backend URL
   - `VITE_WHATSAPP_NUMBER`: Your WhatsApp number
5. Railway will redeploy automatically

### Verification

After deployment, check the logs for validation messages:

```
🔧 Loading environment configuration (production mode)
✅ Environment validated successfully
   API URL: https://faciliauto-backend.up.railway.app
   WhatsApp: 5511949105033
```

## Troubleshooting

### Build Fails with "Missing required environment variable"

**Problem**: Required variable is not set

**Solution**:
1. Check that the variable exists in your `.env` file
2. Ensure the variable name is correct (case-sensitive)
3. Restart the dev server after adding variables

### Build Fails with "Invalid format"

**Problem**: Variable value doesn't match expected format

**Solution**:
1. Check API URL starts with `http://` or `https://`
2. Check WhatsApp number format: `5511949105033` (no spaces, dashes, or parentheses)
3. Remove any trailing spaces or newlines

### Variables Not Loading

**Problem**: Changes to `.env` file not reflected

**Solution**:
1. Restart the development server (`Ctrl+C` then `npm run dev`)
2. Clear browser cache
3. Check you're editing the correct `.env` file for your environment

### Production Build Uses Wrong URL

**Problem**: Production build connects to localhost

**Solution**:
1. Check `.env.production` has correct `VITE_API_URL`
2. In Railway, verify environment variables are set
3. Rebuild the application

## Adding New Environment Variables

1. **Add to environment files**:
   - `.env.development`
   - `.env.production`
   - `.env.example`

2. **Add validation in `src/config/env.ts`**:
   ```typescript
   const myVar = validateEnvVar('VITE_MY_VAR', import.meta.env.VITE_MY_VAR)
   export const MY_VAR = myVar
   ```

3. **Update documentation**:
   - This file
   - `src/config/README.md`
   - `docs/deployment/RAILWAY-DEPLOY.md`

4. **Update Railway**:
   - Add variable to Railway Dashboard
   - Redeploy

## Best Practices

✅ **Do**:
- Use `VITE_` prefix for all frontend environment variables
- Validate all required variables in `src/config/env.ts`
- Use type-safe exports from `@/config/env`
- Document new variables
- Commit `.env.development` and `.env.production` (non-sensitive defaults)

❌ **Don't**:
- Use `import.meta.env` directly in components
- Commit `.env` or `.env.local` files
- Store sensitive data in environment files committed to git
- Forget to update Railway variables after adding new ones

## Security Notes

- `.env.development` and `.env.production` contain **non-sensitive defaults**
- These files are committed to git for convenience
- `.env` and `.env.local` are ignored by git for local overrides
- Never commit API keys, passwords, or other secrets
- Use Railway's environment variables for production secrets

## References

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- `src/config/env.ts` - Validation logic
- `src/config/README.md` - Configuration module docs
- `docs/deployment/RAILWAY-DEPLOY.md` - Deployment guide
