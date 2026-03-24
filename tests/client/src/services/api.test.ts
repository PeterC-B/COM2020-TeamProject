import { describe, it, expect, beforeEach, vi } from 'vitest'

// Axios Mock — with working interceptor + reject handling
vi.mock('axios', () => {
  let errorHandler: any = null

  const instance = {
    __resolve: null as any,
    __reject: null as any,

    get: vi.fn(() => {
      if (instance.__reject) {
        const err = instance.__reject
        instance.__reject = null

        if (errorHandler) {
          return errorHandler(err)
        }

        return Promise.reject(err)
      }

      return Promise.resolve(instance.__resolve)
    }),

    post: vi.fn(() => {
      if (instance.__reject) {
        const err = instance.__reject
        instance.__reject = null

        if (errorHandler) {
          return errorHandler(err)
        }

        return Promise.reject(err)
      }

      return Promise.resolve(instance.__resolve)
    }),

    delete: vi.fn(() => {
      if (instance.__reject) {
        const err = instance.__reject
        instance.__reject = null

        if (errorHandler) {
          return errorHandler(err)
        }

        return Promise.reject(err)
      }

      return Promise.resolve(instance.__resolve)
    }),

    put: vi.fn(() => {
      if (instance.__reject) {
        const err = instance.__reject
        instance.__reject = null

        if (errorHandler) {
          return errorHandler(err)
        }

        return Promise.reject(err)
      }

      return Promise.resolve(instance.__resolve)
    }),

    interceptors: {
      response: {
        use: vi.fn((success, error) => {
          errorHandler = error
        }),
      },
    },
  }

  return {
    __esModule: true,
    default: {
      create: vi.fn(() => instance),
      isAxiosError: (err: any) => err?.isAxiosError === true,
      __instance: instance,
    },
  }
})

// Router Mock
vi.mock('@/router/index', () => ({
  default: {
    push: vi.fn(),
  },
}))

// Pinia Store Mock
const mockStore = {
  accessToken: 'test-token',
  clearAccessToken: vi.fn(),
}

vi.mock('@/stores/main', () => ({
  useMainStore: () => mockStore,
}))

import axios from 'axios'
import { get, post, deleteRequest, ApiRequestError } from '@/services/api'
import router from '@/router/index'

const mockAxios = (axios as any).__instance

// Tests
describe('API Service Wrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAxios.__resolve = null
    mockAxios.__reject = null
  })

  it('performs a successful GET request', async () => {
    mockAxios.__resolve = {
      data: { id: 1 },
      config: {},
    }

    const res = await get<{ id: number }>('/items')

    expect(res.data.id).toEqual(1)
    expect(mockAxios.get).toHaveBeenCalledWith('/items', expect.any(Object))
  })

  it('performs a successful POST request with data', async () => {
    mockAxios.__resolve = {
      data: { success: true },
      config: { headers: { Authorization: 'Bearer test-token' } },
    }

    const res = await post<{ success: boolean }>('/items', {})

    expect(res.data.success).toBe(true)
    expect(res.config.headers.Authorization).toBe('Bearer test-token')
  })

  it('handles 401 Unauthorized', async () => {
    mockAxios.__reject = {
      isAxiosError: true,
      response: { status: 401 },
      message: 'Unauthorized',
    }

    await expect(get('/protected')).rejects.toBeInstanceOf(ApiRequestError)

    expect(mockStore.clearAccessToken).toHaveBeenCalled()
    expect(router.push).toHaveBeenCalledWith('/login')
  })

  it('normalizes a 400 error correctly', async () => {
    mockAxios.__reject = {
      isAxiosError: true,
      response: {
        status: 400,
        data: {
          error: {
            message: 'Invalid input data',
            code: 'VALIDATION_ERROR',
          },
        },
      },
      message: 'Bad Request',
    }

    try {
      await get('/fail')
    } catch (err) {
      const e = err as ApiRequestError

      expect(e.message).toBe('Invalid input data')
      expect(e.code).toBe('VALIDATION_ERROR')
      expect(e.status).toBe(400)
    }
  })

  it('performs a successful DELETE request', async () => {
    mockAxios.__resolve = {
      data: { deleted: true },
      config: {},
    }

    const res = await deleteRequest<{ deleted: boolean }>('/items/1')

    expect(res.data.deleted).toBe(true)
  })
})
