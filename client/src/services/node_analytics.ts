import { get } from './api'

type NodeAnalyticsRow = {
    node_id: number
    name: string | null
    type: string | null
    lat: number
    lon: number
}

export async function FetchNodeAnalytics(): Promise<NodeAnalyticsRow[]> {
    const response = await get<{ status: string; data: NodeAnalyticsRow[] }>('/analytics/nodes')
    return response.data.data
}
