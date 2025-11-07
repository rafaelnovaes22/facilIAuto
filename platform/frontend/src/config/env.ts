// 💻 Tech Lead: Environment variable validation and configuration

/**
 * Validates and exports environment variables with type safety
 * Throws error on app startup if required variables are missing
 */

interface EnvConfig {
    apiUrl: string
    whatsappNumber: string
    isDevelopment: boolean
    isProduction: boolean
}

/**
 * Validates that a required environment variable exists
 * @param key - Environment variable name
 * @param value - Environment variable value
 * @throws Error if value is undefined or empty
 */
function validateEnvVar(key: string, value: string | undefined): string {
    if (!value || value.trim() === '') {
        throw new Error(
            `❌ Missing required environment variable: ${key}\n` +
            `Please check your .env file and ensure ${key} is set.`
        )
    }
    return value.trim()
}

/**
 * Validates API URL format
 * @param url - API URL to validate
 * @throws Error if URL format is invalid
 */
function validateApiUrl(url: string): string {
    try {
        const parsed = new URL(url)
        if (!['http:', 'https:'].includes(parsed.protocol)) {
            throw new Error('Protocol must be http: or https:')
        }
        return url
    } catch (error) {
        throw new Error(
            `❌ Invalid VITE_API_URL format: ${url}\n` +
            `Expected format: http://localhost:8000 or https://api.example.com\n` +
            `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
        )
    }
}

/**
 * Validates WhatsApp number format (DDI + DDD + Number)
 * @param number - WhatsApp number to validate
 * @throws Error if format is invalid
 */
function validateWhatsAppNumber(number: string): string {
    // Format: 55 (DDI) + 11 (DDD) + 9 digits
    const whatsappRegex = /^55\d{10,11}$/
    if (!whatsappRegex.test(number)) {
        throw new Error(
            `❌ Invalid VITE_WHATSAPP_NUMBER format: ${number}\n` +
            `Expected format: 5511949105033 (DDI + DDD + Number)`
        )
    }
    return number
}

/**
 * Load and validate environment configuration
 * This runs once when the module is imported
 */
function loadEnvConfig(): EnvConfig {
    const mode = import.meta.env.MODE
    const isDevelopment = mode === 'development'
    const isProduction = mode === 'production'

    console.log(`🔧 Loading environment configuration (${mode} mode)`)

    // Validate required environment variables
    const apiUrl = validateApiUrl(
        validateEnvVar('VITE_API_URL', import.meta.env.VITE_API_URL)
    )

    const whatsappNumber = validateWhatsAppNumber(
        validateEnvVar('VITE_WHATSAPP_NUMBER', import.meta.env.VITE_WHATSAPP_NUMBER)
    )

    console.log(`✅ Environment validated successfully`)
    console.log(`   API URL: ${apiUrl}`)
    console.log(`   WhatsApp: ${whatsappNumber}`)

    return {
        apiUrl,
        whatsappNumber,
        isDevelopment,
        isProduction,
    }
}

// Export validated configuration
// This will throw an error on app startup if validation fails
export const env = loadEnvConfig()

// Export individual values for convenience
export const API_URL = env.apiUrl
export const WHATSAPP_NUMBER = env.whatsappNumber
export const IS_DEVELOPMENT = env.isDevelopment
export const IS_PRODUCTION = env.isProduction
