import { describe, it, expect, vi, beforeEach } from 'vitest'
import { 
  fetchMissions, 
  fetchMission, 
  createMission, 
  updateMission, 
  deleteMission,
  type Mission 
} from '@/services/missions'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  deleteRequest: vi.fn(),
}))

describe('Missions Service', () => {
  const mockMission: Mission = {
    mission_id: 'm-123',
    mission_name: 'Test Mission',
    question: 'What is 2+2?',
    possible_answers: '3,4,5',
    answer: '4',
    tier: 'EASY'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchMissions()', () => {
    it('returns an array of missions', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { data: [mockMission], message: 'Success', status: 200 }
      } as any)
      const result = await fetchMissions()
      expect(api.get).toHaveBeenCalledWith('/missions')
      expect(result).toHaveLength(1)
      expect(result[0].mission_id).toBe('m-123')
    })
  })

  describe('fetchMission()', () => {
    it('fetches a single mission by ID', async () => {
      vi.mocked(api.get).mockResolvedValue({
        data: { data: mockMission }
      } as any)
      const result = await fetchMission('m-123')
      expect(api.get).toHaveBeenCalledWith('/missions/m-123')
      expect(result.mission_name).toBe('Test Mission')
    })
  })

  describe('createMission()', () => {
    it('removes mission_id from payload before posting', async () => {
      vi.mocked(api.post).mockResolvedValue({
        data: { data: mockMission }
      } as any)
      await createMission(mockMission)
      const expectedPayload = {
        mission_name: 'Test Mission',
        question: 'What is 2+2?',
        possible_answers: '3,4,5',
        answer: '4',
        tier: 'EASY'
      }
      expect(api.post).toHaveBeenCalledWith('/missions', expectedPayload)
    })
  })

  describe('updateMission()', () => {
    it('sends a partial payload to the correct ID', async () => {
      const updateData = { mission_name: 'Updated Name' }
      vi.mocked(api.put).mockResolvedValue({
        data: { data: { ...mockMission, ...updateData } }
      } as any)
      const result = await updateMission('m-123', updateData)
      expect(api.put).toHaveBeenCalledWith('/missions/m-123', updateData)
      expect(result.mission_name).toBe('Updated Name')
    })
  })

  describe('deleteMission()', () => {
    it('calls the delete endpoint with the mission ID', async () => {
      vi.mocked(api.deleteRequest).mockResolvedValue({
        data: { data: mockMission }
      } as any)
      const result = await deleteMission('m-123')
      expect(api.deleteRequest).toHaveBeenCalledWith('/missions/m-123')
      expect(result.mission_id).toBe('m-123')
    })
  })
})