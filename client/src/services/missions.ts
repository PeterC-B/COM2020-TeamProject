import { get, post, put, type ApiEnvelope } from '@/services/api'

export interface Mission {
    mission_id?: string       
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
    console.log('Fetched mission:', response.data.data)
    return response.data.data
}

export async function createMission(mission: Mission): Promise<Mission> {
    const { mission_id, ...payload } = mission

    const res = await fetch('/api/missions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    })

    console.log('Create mission response:', res)
    console.log("payload;", payload)

    if (!res.ok) {
        const errorText = await res.text()
        console.log('Create mission failed:', errorText)
        throw new Error(errorText || 'Failed to create mission')
    }

    return res.json()
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
