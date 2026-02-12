import { get } from '@/services/api'

export type Mission = {
    mission_id: string
    mission_name: string
    question: string
    possible_answers: string
    answer: string
    tier: string
}

export async function fetchMissions(): Promise<Mission[]> {
    const response = await get<{ data: Mission[] }>('/missions')
    return response.data.data
}

export async function fetchMission(missionId: string): Promise<Mission> {
    const response = await get<{ data: Mission }>(`/missions/${missionId}`)
    return response.data.data
}