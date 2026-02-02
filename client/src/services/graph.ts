import { get } from '@/services/api'
import type { FeatureCollection } from 'geojson'

const BASE_PATH = '/map'

export const GRAPH_ENDPOINTS = {
    nodes: `${BASE_PATH}/nodes`,
    edges: `${BASE_PATH}/edges`,
    geometry: `${BASE_PATH}/geometry`,
} as const

export function fetchNodes(
    params: Record<string, unknown> = {},
): Promise<FeatureCollection> {
    return get(GRAPH_ENDPOINTS.nodes, params).then(({ data }) => data)
}

export function fetchEdges(
    params: Record<string, unknown> = {},
): Promise<FeatureCollection> {
    return get(GRAPH_ENDPOINTS.edges, params).then(({ data }) => data)
}

export function fetchGeometry(
    params: Record<string, unknown> = {},
): Promise<FeatureCollection> {
    return get(GRAPH_ENDPOINTS.geometry, params).then(({ data }) => data)
}
