import type { coordinates } from '@/components/simple-map/geoJsonUtils'
import { get, post, type ApiEnvelope } from '@/services/api'
import type { FeatureCollection } from 'geojson'

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

export type LocationNameResponse = {
    name: string
    information: string
}

export type GraphPreset = {
    code: string
    name: string
    lat: number
    lon: number
    is_active: boolean
    has_snapshot?: boolean
    snapshot?: GraphDataResponse | null
}

export function fetchGraphData(params: Record<string, unknown> = {}) {
    const response = get<ApiEnvelope<GraphDataResponse>>(GRAPH_ENDPOINT, params).then(
        ({ data }) => data.data,
    )
    return response
}

export function fetchGraphPresets() {
    return get<ApiEnvelope<GraphPreset[]>>(`${GRAPH_ENDPOINT}/presets`).then(({ data }) => data.data)
}

export function fetchGraphPresetSnapshot(presetCode: string) {
    return get<ApiEnvelope<GraphDataResponse>>(`${GRAPH_ENDPOINT}/presets/${presetCode}/snapshot`).then(
        ({ data }) => data.data,
    )
}

export function activateGraphPreset(presetCode: string) {
    return post<ApiEnvelope<GraphDataResponse>>(`${GRAPH_ENDPOINT}/presets/${presetCode}/activate`, {}).then(
        ({ data }) => data.data,
    )
}

export async function fetchLocationName(node_id: number) {
    const response = await get<ApiEnvelope<LocationNameResponse>>(`/graph/location/name`, {
        node_id,
    })

    return response.data.data
}

export async function fetchGraphByCoordinates(lat: number, lon: number) {
    const params = new URLSearchParams({
        lat: String(lat),
        lon: String(lon),
    })
    const response = await fetch(`/api${GRAPH_ENDPOINT}/coordinates?${params.toString()}`)

    if (!response.ok) {
        let message = 'Failed to fetch graph data'
        try {
            const errorPayload = (await response.json()) as {
                error?: { message?: string }
                message?: string
            }
            message = errorPayload?.error?.message || errorPayload?.message || message
        } catch {
            // Ignore JSON parse errors and keep default message.
        }
        throw new Error(message)
    }

    const payload = (await response.json()) as ApiEnvelope<GraphDataResponse>
    return payload.data
}

export async function fetchLikeLocations(start: string) {
    const response = await fetch(`/api${GRAPH_ENDPOINT}/locations?like_string=${start}`)

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
