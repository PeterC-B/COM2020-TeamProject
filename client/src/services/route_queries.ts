import { get, type ApiEnvelope } from '@/services/api'

export type RouteQueriesResponse = {
    query_id: string
    start: string
    end: string
    weights_json: JSON
    chosen_route_rank: number
    chosen_route_path: JSON
    timestamp: string
    name: string
}

export async function FetchRouteQueries() {
    const response = await get<ApiEnvelope<RouteQueriesResponse[]>>('/routing/queries')
    return response.data.data
  
export type MissionAnalyticsItem = {
    mission_id: string
    mission_name: string
    score: number
    status: string
    user_id: string
    chosen_answer: string
}

export type MissionAnalyticsPayload = {
    mission_analytics: MissionAnalyticsItem[]
}

export async function FetchMissionAnalytics(){
    const response = await get<ApiEnvelope<MissionAnalyticsItem[]>>(
        "/analytics/missions"
    )
    console.log("mission analytics")
    console.log(response.data.data)
    return response.data.data
}
