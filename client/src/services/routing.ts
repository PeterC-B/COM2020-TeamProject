import { post } from '@/services/api'

const BASE_PATH = '/route'

export const ROUTE_ENDPOINTS = {
    dijkstra: `${BASE_PATH}/dijkstra`,
    astar: `${BASE_PATH}/astar`,
    yens: `${BASE_PATH}/yens`,
} as const

export type RouteRequest = {
    start: [number, number]
    end: [number, number]
    weights?: Record<string, number>
}

export type RouteResponse = {
    distance?: number
    geometry: Array<[number, number]>
    metadata?: Record<string, unknown>
    path?: number[]
}

export function fetchDijkstraRoute({
    start,
    end,
    weights,
}: RouteRequest): Promise<RouteResponse> {
    return post(ROUTE_ENDPOINTS.dijkstra, { start, end, weights }).then(({ data }) => data)
}

export function fetchAstarRoute({
    start,
    end,
    weights,
}: RouteRequest): Promise<RouteResponse> {
    return post(ROUTE_ENDPOINTS.astar, { start, end, weights }).then(({ data }) => data)
}

export type YensRouteRequest = RouteRequest & { k?: number }

export function fetchYensRoutes({
    start,
    end,
    k,
    weights,
}: YensRouteRequest): Promise<{ routes: RouteResponse[] }> {
    return post(ROUTE_ENDPOINTS.yens, { start, end, k, weights }).then(({ data }) => data)
}
