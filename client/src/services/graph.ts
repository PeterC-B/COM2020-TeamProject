import { get, type ApiEnvelope } from '@/services/api'
import type { FeatureCollection } from 'geojson'

const GRAPH_ENDPOINT = '/graph'

export type GraphDataResponse = {
    features: {
        nodes: FeatureCollection
        edges: FeatureCollection
    }
}

export function fetchGraphData(params: Record<string, unknown> = {}) {
    return get<ApiEnvelope<GraphDataResponse>>(GRAPH_ENDPOINT, params).then(
        ({ data }) => data.data,
    )
}

export async function fetchGraphByLocation(location: string) {
    const response = await fetch(
        `/api${GRAPH_ENDPOINT}/coordinates?location=${location}`
    )

    if (!response.ok) {
        throw new Error(`Failed to fetch graph data`)
    }   

    return response.json()
}

export async function fetchLikeLocations(start: string){
    const response = await fetch(
        `/api${GRAPH_ENDPOINT}/locations?like_string=${start}`
    )

    if (!response.ok) {
        throw new Error(`Failed to fetch graph data`)
    }   

    return response.json()
}