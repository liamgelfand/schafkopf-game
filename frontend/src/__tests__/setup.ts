import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Cleanup after each test
afterEach(() => {
  cleanup()
  // Clear localStorage after each test
  if (typeof window !== 'undefined' && window.localStorage) {
    window.localStorage.clear()
  }
})

// Set up proper localStorage mock - only if window is available
if (typeof window !== 'undefined') {
  const localStorageMock = (() => {
    let store: Record<string, string> = {}

    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value.toString()
      },
      removeItem: (key: string) => {
        delete store[key]
      },
      clear: () => {
        store = {}
      },
      get length() {
        return Object.keys(store).length
      },
      key: (index: number) => {
        const keys = Object.keys(store)
        return keys[index] || null
      }
    }
  })()

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
    configurable: true
  })
}

