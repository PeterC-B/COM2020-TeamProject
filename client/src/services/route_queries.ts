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
    console.log(`Response:`)
    console.log(response)
    return response.data.data
}
