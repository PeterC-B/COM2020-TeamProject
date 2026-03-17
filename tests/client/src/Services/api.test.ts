import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { get, post, put, deleteRequest, ApiRequestError } from '@/services/api'

// mock router
const push = vi.fn()

vi.mock('@/router', () => ({
  default: {
    push,
  },
}))

// mock store
const mockStore = {
  accessToken: 'test-token',
  clearAccessToken: vi.fn(),
}

vi.mock('@/stores/main', () => ({
  useMainStore: () => mockStore,
}))

describe('API wrapper', () => {
  let mock: MockAdapter

  beforeEach(() => {
    mock = new MockAdapter(axios)
    vi.clearAllMocks()
  })

  it('GET request returns data', async () => {
    mock.onGet('/api/test').reply(200, { hello: 'world' })

    const res = await get('/test')

    expect(res.data.hello).toBe('world')
  })

  it('POST request sends data', async () => {
    mock.onPost('/api/items').reply(200, { success: true })

    const res = await post('/items', { name: 'item' })

    expect(res.data.success).toBe(true)
  })

  it('PUT request works', async () => {
    mock.onPut('/api/items/1').reply(200, { updated: true })

    const res = await put('/items/1', { name: 'updated' })

    expect(res.data.updated).toBe(true)
  })

  it('DELETE request works', async () => {
    mock.onDelete('/api/items/1').reply(200, { deleted: true })

    const res = await deleteRequest('/items/1')

    expect(res.data.deleted).toBe(true)
  })

  it('401 clears token and redirects to login', async () => {
    mock.onGet('/api/private').reply(401)

    await expect(get('/private')).rejects.toBeInstanceOf(ApiRequestError)

    expect(mockStore.clearAccessToken).toHaveBeenCalled()
    expect(push).toHaveBeenCalledWith('/login')
  })

  it('normalizes API error message', async () => {
    mock.onGet('/api/error').reply(400, {
      error: { message: 'Invalid request', code: 'BAD_REQUEST' },
    })

    try {
      await get('/error')
    } catch (err) {
      expect(err).toBeInstanceOf(ApiRequestError)
      expect((err as ApiRequestError).message).toBe('Invalid request')
      expect((err as ApiRequestError).code).toBe('BAD_REQUEST')
    }
  })
})