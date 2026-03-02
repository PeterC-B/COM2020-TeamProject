import { post, type ApiEnvelope } from '@/services/api'

const BASE_PATH = '/routing'

export const ROUTE_ENDPOINTS = {
    yens: BASE_PATH,
} as const

export type RouteRequest = {
    // Backend expects (lat, lon)
    start: [number, number]
    end: [number, number]
    weights?: Record<string, number>
}

export type RouteResponse = {
    distance?: number
    geometry: Array<[number, number]>
    indicators?: {
        lighting?: number
        greenery?: number
        surface_quality?: number
        amenity_proximity?: number
        weighted_score?: number
    }
    metadata?: Record<string, unknown>
    path?: number[]
}

export type YensRouteRequest = RouteRequest & { k?: number }

export type YensRoutesResponse = {
    algorithm: 'yens'
    requested_routes: number
    returned_routes: number
    routes: RouteResponse[]
    comparison?: {
        count?: number
        shortest_distance?: number | null
        longest_distance?: number | null
        average_distance?: number | null
    }
}

export function fetchYensRoutes({ start, end, k, weights }: YensRouteRequest) {
    console.log('Fetching Yens routes with parameters:', { start, end, k, weights })
    const response = post<ApiEnvelope<YensRoutesResponse>>(ROUTE_ENDPOINTS.yens, {
        start,
        end,
        k,
        weights,
    }).then(
        ({ data }) => data.data,
    )

    console.log(response)

    return response
}
