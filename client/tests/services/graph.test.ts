import { describe, it, expect, vi, beforeEach } from 'vitest'
import { 
  fetchGraphData, 
  fetchGraphPresets, 
  fetchLocationName, 
  fetchGraphByCoordinates 
} from '@/services/graph'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  get: vi.fn(),
  post: vi.fn(),
}))

global.fetch = vi.fn()

describe('Graph Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchGraphData()', () => {
    it('returns the nested data from the graph endpoint', async () => {
      const mockGraphData = {
        features: { nodes: {}, edges: {}, locations: {}, center: [0, 0] }
      }
      
      const mockResponse = {
        data: {
          data: mockGraphData,
          message: 'Success',
          status: 200
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse as any)
      const result = await fetchGraphData({ type: 'test' })
      expect(api.get).toHaveBeenCalledWith('/graph', { type: 'test' })
      expect(result).toEqual(mockGraphData)
    })
  })

  describe('fetchLocationName()', () => {
    it('passes node_id as a parameter and returns the name info', async () => {
      const mockLocation = { name: 'Library', information: 'Quiet zone' }
      const mockResponse = {
        data: { data: mockLocation }
      }
      vi.mocked(api.get).mockResolvedValue(mockResponse as any)
      const result = await fetchLocationName(123)
      expect(api.get).toHaveBeenCalledWith('/graph/location/name', { node_id: 123 })
      expect(result.name).toBe('Library')
    })
  })

  describe('fetchGraphByCoordinates()', () => {
    it('uses native fetch and returns the data payload', async () => {
      const mockGraphData = { features: { nodes: {}, edges: {}, locations: {}, center: [51, -3] } }
      const mockFetchResponse = {
        ok: true,
        json: async () => ({ data: mockGraphData })
      }

      vi.mocked(fetch).mockResolvedValue(mockFetchResponse as any)
      const result = await fetchGraphByCoordinates(51.5, -0.1)
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('lat=51.5'))
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('lon=-0.1'))
      expect(result).toEqual(mockGraphData)
    })

    it('throws a specific error message if the fetch fails', async () => {
      const mockErrorResponse = {
        ok: false,
        json: async () => ({ error: { message: 'Out of bounds' } })
      }
      vi.mocked(fetch).mockResolvedValue(mockErrorResponse as any)
      await expect(fetchGraphByCoordinates(0, 0)).rejects.toThrow('Out of bounds')
    })
  })

  describe('fetchGraphPresets()', () => {
    it('returns an array of presets', async () => {
      const mockPresets = [{ code: 'EX', name: 'Exeter', is_active: true }]
      vi.mocked(api.get).mockResolvedValue({
        data: { data: mockPresets }
      } as any)
      const result = await fetchGraphPresets()
      expect(api.get).toHaveBeenCalledWith('/graph/presets')
      expect(result).toHaveLength(1)
      expect(result[0].code).toBe('EX')
    })
  })
})