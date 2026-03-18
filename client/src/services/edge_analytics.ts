import { get } from './api'

export interface EdgeAnalyticsRow {
    edge_id: number
    from_node: number
    to_node: number
    length: number
    travel_time: number
    access_score: number
    lighting: number
    greenery: number
    pollution: number
    surface_quality: number
    pub_distance: number
}

export async function FetchEdgeAnalytics(): Promise<EdgeAnalyticsRow[]> {
    const response = await get<{ status: string; data: EdgeAnalyticsRow[] }>('/analytics/edges')
    return response.data.data
}
