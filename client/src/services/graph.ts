import { get, type ApiEnvelope } from '@/services/api'
import type { FeatureCollection } from 'geojson'
import type { coordinates } from '@/components/simple-map/geoJsonUtils'

const GRAPH_ENDPOINT = '/graph'

export type GraphDataResponse = {
    features: {
        nodes: FeatureCollection
        edges: FeatureCollection
        locations: FeatureCollection
        center: coordinates
    }
}

export type NodeContextResponse = {
    name: string
    type: string
    opening_hours: string
}

export type LocationNameResponse = string

export function fetchGraphData(params: Record<string, unknown> = {}) {
    const response = get<ApiEnvelope<GraphDataResponse>>(GRAPH_ENDPOINT, params).then(
        ({ data }) => data.data,
    )
    return response
}

export async function fetchLocationName(node_id: number) {
    const response = await get<ApiEnvelope<LocationNameResponse>>(
        `/graph/location/name`,
        { node_id }
    )

    return response.data.data
}

export async function fetchGraphByLocation(location: string) {
    console.log("Fetching location")
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

export async function fetchNodeContext(node_id: number){
    const response = await get<ApiEnvelope<NodeContextResponse>>(
        `/graph/node?node_id=${node_id}`
    )

    return response.data.data
}

export async function fetchEdgeContext(edge_id: number){
    const response = await fetch(
        `/graph/edge?edge_id=${edge_id}`
    )

    if (!response.ok) {
        throw new Error(`Failed to fetch edge data`)
    }  

    return response.json()
}