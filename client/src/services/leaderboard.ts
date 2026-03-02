import { get, post, put, deleteRequest, postPublic, type ApiEnvelope } from '@/services/api'

export interface MissionProgress {
    user_id: string
    mission_id: string
    status: 'incorrect' | 'correct'
    tier: 'EASY' | 'MEDIUM' | 'HARD'
}

export async function saveMissionProgress(payload: MissionProgress){
    console.log("Getting here")
    const response = await postPublic<ApiEnvelope<MissionProgress>>(
        `/leaderboard`,
        payload
    )
    return response.data.data
}

export async function fetchMissionProgress(mission_id : string, user_id : string){
    const response = await get<ApiEnvelope<MissionProgress>>(
        `/leaderboard/${user_id}/${mission_id}`
    )
    return response.data.data
}

export async function fetchAllMissionProgressForUser(user_id : string){
    const response = await get<ApiEnvelope<MissionProgress[]>>(
        `/leaderboard/${user_id}`
    )
    return response.data.data
}

export async function fetchAllMissionProgressForMission(mission_id : string){
    const response = await get<ApiEnvelope<MissionProgress[]>>(
        `/leaderboard/${mission_id}`
    )
    return response.data.data
}

export async function fetchAllMissionProgress(): Promise<MissionProgress[]>{
    const response = await get<ApiEnvelope<MissionProgress[]>>(
        `/leaderboard`
    )
    return response.data.data
}