import { get, type ApiEnvelope } from './api'

export interface EdgeAnalyticsRow {
    edge_id: number
    from_node: number
    to_node: number
    length: number
    travel_time: number
    is_accessible: boolean
    lighting: number
    greenery: number
    pollution: number
    surface_quality: number
    pub_distance: number
}

export async function FetchEdgeAnalytics(): Promise<EdgeAnalyticsRow[]> {
    const response = await get<ApiEnvelope<EdgeAnalyticsRow[]>>('/analytics/edges')
    return response.data.data
}
