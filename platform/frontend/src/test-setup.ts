// Test setup para Vitest
import { expect, afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest matchers
expect.extend(matchers)

// Cleanup após cada teste
afterEach(() => {
    cleanup()
})

