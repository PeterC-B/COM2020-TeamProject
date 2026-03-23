import { describe, it, expect, vi, beforeEach } from 'vitest'
import { 
  saveMissionProgress, 
  fetchMissionProgress, 
  fetchAllMissionProgressForUser,
  fetchAllMissionProgress 
} from '@/services/leaderboard'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  get: vi.fn(),
  postPublic: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  deleteRequest: vi.fn(),
}))

describe('Leaderboard Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('saveMissionProgress()', () => {
    it('sends progress data and returns the saved object', async () => {
      const payload = {
        user_id: 'u1',
        mission_id: 'm1',
        status: 'correct' as const,
        score: 100,
        chosenAnswer: 'Option A'
      }

      const mockResponse = {
        data: {
          data: payload,
          message: 'Saved',
          status: 201
        }
      }

      vi.mocked(api.postPublic).mockResolvedValue(mockResponse as any)
      const result = await saveMissionProgress(payload)
      expect(api.postPublic).toHaveBeenCalledWith('/leaderboard', payload)
      expect(result.score).toBe(100)
    })
  })

  describe('fetchMissionProgress()', () => {
    it('constructs the URL with user_id and mission_id correctly', async () => {
      const mockData = { user_id: 'u1', mission_id: 'm1', score: 50 }
      vi.mocked(api.get).mockResolvedValue({
        data: { data: mockData }
      } as any)
      const result = await fetchMissionProgress('m1', 'u1')
      expect(api.get).toHaveBeenCalledWith('/leaderboard/u1/m1')
      expect(result.user_id).toBe('u1')
    })
  })

  describe('fetchAllMissionProgressForUser()', () => {
    it('fetches all entries for a specific user', async () => {
      const mockList = [
        { mission_id: 'm1', score: 10 },
        { mission_id: 'm2', score: 20 }
      ]
      vi.mocked(api.get).mockResolvedValue({
        data: { data: mockList }
      } as any)
      const result = await fetchAllMissionProgressForUser('user-123')
      expect(api.get).toHaveBeenCalledWith('/leaderboard/user-123')
      expect(result).toHaveLength(2)
      expect(result[0].mission_id).toBe('m1')
    })
  })

  describe('fetchAllMissionProgress()', () => {
    it('fetches the global leaderboard list', async () => {
      const mockGlobalList = [{ user_id: 'u1', score: 500 }]
      vi.mocked(api.get).mockResolvedValue({
        data: { data: mockGlobalList }
      } as any)
      const result = await fetchAllMissionProgress()
      expect(api.get).toHaveBeenCalledWith('/leaderboard')
      expect(result[0].user_id).toBe('u1')
    })
  })
})