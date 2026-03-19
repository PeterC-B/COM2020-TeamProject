import { describe, it, expect, vi, beforeEach } from 'vitest'
import { login, register, forgotPassword, list_all_users } from '@/services/auth'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  postPublic: vi.fn(),
  get: vi.fn(),
  put: vi.fn(),
  ApiRequestError: class extends Error {
    constructor(message: string, public code?: string, public status?: number) {
      super(message)
    }
  }
}))

describe('Auth Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login()', () => {
    it('returns token and user details on successful login', async () => {
      const mockLoginResponse = {
        data: {
          data: {
            access_token: 'fake-jwt-token',
            role: 'admin',
            username: 'testuser',
            email: 'test@test.com'
          },
          message: 'Login Successful',
          status: 200
        }
      }
      
      vi.mocked(api.postPublic).mockResolvedValue(mockLoginResponse as any)
      const result = await login('testuser', 'password123')
      expect(api.postPublic).toHaveBeenCalledWith('/user/login', {
        username: 'testuser',
        password: 'password123'
      })
      expect(result.token).toBe('fake-jwt-token')
      expect(result.user_details?.role).toBe('admin')
    })

    it('throws an error if the token is missing from the response', async () => {
      const mockEmptyResponse = { 
        data: { 
          data: {}, 
          message: 'Missing token', 
          status: 200 
        } 
      }
      vi.mocked(api.postPublic).mockResolvedValue(mockEmptyResponse as any)
      await expect(login('user', 'pass')).rejects.toThrow('Login response did not include a token')
    })
  })

  describe('register()', () => {
    it('sends the correct payload to the public register endpoint', async () => {
      const payload = { username: 'newuser', email: 'new@test.com', password: 'password' }
      const mockRegResponse = {
        data: {
          data: { user_id: 'uuid-123' },
          message: 'User Created',
          status: 201
        }
      }

      vi.mocked(api.postPublic).mockResolvedValue(mockRegResponse as any)

      await register(payload)
      expect(api.postPublic).toHaveBeenCalledWith('/user/register', payload)
    })
  })

  describe('list_all_users()', () => {
    it('maps users and adds a rank based on their list position', async () => {
      const mockUserList = [
        { user_id: '1', username: 'alice', password: 'p1', role: 'admin' },
        { user_id: '2', username: 'bob', password: 'p2', role: 'user' }
      ]
      
      const mockResponse = {
        data: {
          data: mockUserList,
          message: 'Success',
          status: 200
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse as any)
      const users = await list_all_users()
      expect(users).toHaveLength(2)
      expect(users[0].rank).toBe(1)
      expect(users[1].rank).toBe(2)
      expect(users[0].username).toBe('alice')
    })
  })

  describe('forgotPassword()', () => {
    it('extracts the reset status from the nested response data', async () => {
      const mockResponse = {
        data: {
          data: { reset: true },
          message: 'Reset email sent',
          status: 200
        }
      }

      vi.mocked(api.postPublic).mockResolvedValue(mockResponse as any)
      const result = await forgotPassword('user', 'email@test.com', 'newPass')
      expect(result?.reset).toBe(true)
      expect(api.postPublic).toHaveBeenCalledWith('/user/forgot-password', expect.objectContaining({
        new_password: 'newPass'
      }))
    })
  })
})