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
