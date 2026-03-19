import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchYensRoutes, type YensRouteRequest } from '@/services/routing'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  post: vi.fn(),
}))

describe('Routing Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'log').mockImplementation(() => {})
  })

  describe('fetchYensRoutes()', () => {
    it('sends coordinates and user_id to the routing endpoint', async () => {
      const requestPayload: YensRouteRequest = {
        start: [50.71, -3.53],
        end: [50.72, -3.54],
        user_id: 'user-123',
        k: 3,
        weights: { lighting: 0.5 }
      }

      const mockRouteData = {
        algorithm: 'yens' as const,
        requested_routes: 3,
        returned_routes: 1,
        routes: [
          {
            distance: 1200,
            geometry: [[50.71, -3.53], [50.72, -3.54]],
            indicators: { lighting: 0.8 }
          }
        ]
      }

      const mockResponse = {
        data: {
          data: mockRouteData,
          message: 'Route calculated',
          status: 200
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse as any)
      const result = await fetchYensRoutes(requestPayload)
      expect(api.post).toHaveBeenCalledWith('/routing', {
        start: [50.71, -3.53],
        end: [50.72, -3.54],
        k: 3,
        weights: { lighting: 0.5 },
        user_id: 'user-123'
      })
      expect(result.algorithm).toBe('yens')
      expect(result.routes[0].distance).toBe(1200)
    })

    it('logs the user_id to the console', async () => {
      const consoleSpy = vi.spyOn(console, 'log')
      const requestPayload: YensRouteRequest = {
        start: [0, 0],
        end: [1, 1],
        user_id: 'debug-user'
      }
      vi.mocked(api.post).mockResolvedValue({ data: { data: {} } } as any)
      await fetchYensRoutes(requestPayload)
      expect(consoleSpy).toHaveBeenCalledWith('debug-user')
    })
  })
})