import { describe, it, expect, afterEach ,beforeEach, vi } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { get, post, put, deleteRequest, ApiRequestError } from '@/services/api'
import router from '@/router/index'

vi.mock('@/router/index', () => ({
  default: {
    push: vi.fn(),
  },
}))

const mockStore = {
  accessToken: 'test-token',
  clearAccessToken: vi.fn(),
  isAuthenticated: true,
  userRole: 'users',
}

vi.mock('@/stores/main', () => ({
  useMainStore: () => mockStore,
}))

describe('API Service Wrapper', () => {
  let mock: MockAdapter

  beforeEach(() => {
    mock = new MockAdapter(axios)
    vi.clearAllMocks()
  })

  afterEach(() => {
    mock.restore()
  })

  it('performs a successful GET request', async () => {
    const mockData = { id: 1, name: 'Test Item' }
    mock.onGet('/api/items').reply(200, mockData)
    const response = await get('/items')
    expect(response.data).toEqual(mockData)
  })

  it('performs a successful POST request with data', async () => {
    mock.onPost('/api/items').reply(201, { success: true })
    const res = await post<{ success: boolean }>('/items', { name: 'New Item' })
    expect(res.data.success).toBe(true)
    const headers = res.config.headers as any
    expect(headers?.Authorization).toBe('Bearer test-token')
})

  it('handles 401 Unauthorized by clearing token and redirecting', async () => {
    mock.onGet('/api/protected').reply(401)
    await expect(get('/protected')).rejects.toThrow(ApiRequestError)
    expect(mockStore.clearAccessToken).toHaveBeenCalled()
    expect(router.push).toHaveBeenCalledWith('/login')
  })

  it('normalizes a 400 Bad Request error correctly', async () => {
    const errorPayload = {
      error: {
        message: 'Invalid input data',
        code: 'VALIDATION_ERROR',
        details: { field: 'email' }
      }
    }
    mock.onGet('/api/fail').reply(400, errorPayload)

    try {
      await get('/fail')
    } catch (error) {
      const err = error as ApiRequestError
      expect(err).toBeInstanceOf(ApiRequestError)
      expect(err.message).toBe('Invalid input data')
      expect(err.code).toBe('VALIDATION_ERROR')
      expect(err.status).toBe(400)
    }
  })

  it('performs a successful DELETE request', async () => {
    mock.onDelete('/api/items/1').reply(200, { deleted: true })
    const response = await deleteRequest<{ deleted: boolean }>('/items/1')
    expect(response.data.deleted).toBe(true)
  })
})