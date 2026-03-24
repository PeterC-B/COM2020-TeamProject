import { describe, it, expect, vi, beforeEach } from 'vitest'
import { FetchRouteQueries, FetchMissionAnalytics } from '@/services/route_queries'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  get: vi.fn(),
}))

describe('Route Queries Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('FetchRouteQueries()', () => {
    it('fetches an array of route query responses', async () => {
      const mockRoutes = [
        {
          start: 'Point A',
          end: 'Point B',
          name: 'Quickest Path',
          timestamp: '2026-03-18T12:00:00Z'
        }
      ]

      vi.mocked(api.get).mockResolvedValue({
        data: {
          data: mockRoutes,
          message: 'Success',
          status: 200
        }
      } as any)
      const result = await FetchRouteQueries()
      expect(api.get).toHaveBeenCalledWith('/routing/queries')
      expect(result).toHaveLength(1)
      expect(result[0].start).toBe('Point A')
    })
  })

  describe('FetchMissionAnalytics()', () => {
    it('unwraps the mission_analytics array from the payload', async () => {
      const mockAnalyticsItems = [
        { mission_id: 'm1', score: 100, status: 'correct' },
        { mission_id: 'm2', score: 0, status: 'incorrect' }
      ]

      const mockResponse = {
        data: {
          data: mockAnalyticsItems
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse as any)

      const result = await FetchMissionAnalytics()

      expect(api.get).toHaveBeenCalledWith('/analytics/missions')
      expect(Array.isArray(result)).toBe(true)
      expect(result).toHaveLength(2)
      expect(result[0].mission_id).toBe('m1')
    })
  })
})