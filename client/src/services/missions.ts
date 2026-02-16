import { get, post, put, type ApiEnvelope } from '@/services/api'

export type Mission = {
    mission_id: string
    mission_name: string
    question: string
    possible_answers: string
    answer: string
    tier: string
}

export async function fetchMissions(): Promise<Mission[]> {
    const response = await get<ApiEnvelope<Mission[]>>('/missions')
    return response.data.data
}

export async function fetchMission(missionId: string): Promise<Mission> {
    const response = await get<ApiEnvelope<Mission>>(`/missions/${missionId}`)
    return response.data.data
}

export async function createMission(mission: Mission): Promise<Mission> {
    const response = await post<ApiEnvelope<Mission>>('/missions', mission)
    return response.data.data
}

export async function updateMission(
    missionId: string,
    payload: Partial<Mission>
): Promise<Mission> {
    const response = await put<ApiEnvelope<Mission>>(
        `/missions/${missionId}`,
        payload
    )
    return response.data.data
}
