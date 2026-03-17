import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Cleanup after each test
afterEach(() => {
  cleanup()
})

// Initialize i18n for tests (avoid "initReactI18next" warnings and render readable text)
if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    lng: 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    resources: {
      en: {
        translation: {
          game: {
            connecting: 'Connecting to game',
            loading: 'Waiting for game',
            notLoggedIn: 'You are not logged in',
            noRoomId: 'No room id provided',
            title: 'Game',
            yourTurnToBid: 'Your turn to bid',
            turnToBid: 'Turn to bid: {{name}}',
            passes: 'Passes: {{count}}',
            yourHand: 'Your hand',
            chooseBid: 'Choose your bid',
            makeYourBid: 'Make your bid',
            highestBid: 'Highest bid: {{contract}}',
            contract: 'Contract: {{contract}}',
            trick: 'Trick {{current}}',
            noCardsPlayed: 'No cards played',
            contracts: { rufer: 'Rufer', wenz: 'Wenz', solo: 'Solo' },
            suits: { eichel: 'Eichel', gras: 'Gras', herz: 'Herz', schellen: 'Schellen' },
            calledAce: 'Called ace',
            selectCalledAce: 'Select called ace',
          },
          errors: { gameNotFound: 'Game not found' },
          common: { backToHome: 'Back to home', makeBid: 'Make bid', pass: 'Pass' },
          login: { errorOccurred: 'An error occurred' },
        },
      },
    },
    react: { useSuspense: false },
  })
}

// Mock localStorage with an in-memory store (tests rely on setItem/getItem)
const store = new Map<string, string>()
const localStorageMock: Storage = {
  get length() {
    return store.size
  },
  clear: vi.fn(() => {
    store.clear()
  }),
  getItem: vi.fn((key: string) => {
    return store.has(key) ? store.get(key)! : null
  }),
  key: vi.fn((index: number) => {
    return Array.from(store.keys())[index] ?? null
  }),
  removeItem: vi.fn((key: string) => {
    store.delete(key)
  }),
  setItem: vi.fn((key: string, value: string) => {
    store.set(key, String(value))
  }),
} as any

globalThis.localStorage = localStorageMock

