import { get, post, put, deleteRequest, type ApiEnvelope } from '@/services/api'

export interface Mission {
    mission_id: string       
    mission_name: string
    question: string
    possible_answers: string
    answer: string
    tier: 'EASY' | 'MEDIUM' | 'HARD'
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
    const { mission_id, ...payload } = mission
    const res = await post<ApiEnvelope<Mission>>(`/missions`, payload)
    return res.data.data
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

export async function deleteMission(missionId: string){
    const response = await deleteRequest<ApiEnvelope<Mission>>(
        `/missions/${missionId}`
    )
    return response.data.data
}