import maplibregl, { type Map } from 'maplibre-gl'
import { ref } from 'vue'
import { fetchLocationName, type LocationNameResponse } from '@/services/graph'

type SelectionPayload = {
    start: [number, number] | null
    end: [number, number] | null
    startNodeId: number | null
    endNodeId: number | null
    start_location: string | null
    end_location: string | null
}

export function useMapSelection(emitSelectionChange: (payload: SelectionPayload) => void) {
    let map: Map | null = null
    let startMarker: maplibregl.Marker | null = null
    let endMarker: maplibregl.Marker | null = null

    const selectedEdgeId = ref<number | null>(null)
    const selectedNodeId = ref<number | null>(null)
    const startPoint = ref<[number, number] | null>(null)
    const endPoint = ref<[number, number] | null>(null)
    const startNodeId = ref<number | null>(null)
    const endNodeId = ref<number | null>(null)
    const start_location = ref<string | null>(null)
    const end_location = ref<string | null>(null)

    function upsertMarker(marker: maplibregl.Marker | null, color: string, lngLat: [number, number]) {
        if (!map) return marker
        if (!marker) {
            marker = new maplibregl.Marker({ color })
        }
        marker.setLngLat(lngLat).addTo(map)
        return marker
    }

    function clearMarker(marker: maplibregl.Marker | null) {
        marker?.remove()
        return null
    }

    function setStartPoint(lngLat: [number, number] | null, nodeId: number | null, location: string | null) {
        startPoint.value = lngLat
        startNodeId.value = nodeId
        start_location.value = location
        if (lngLat) {
            startMarker = upsertMarker(startMarker, '#22c55e', lngLat)
        } else {
            startMarker = clearMarker(startMarker)
        }
    }

    function setEndPoint(lngLat: [number, number] | null, nodeId: number | null, location: string | null) {
        endPoint.value = lngLat
        endNodeId.value = nodeId
        end_location.value = location
        if (lngLat) {
            endMarker = upsertMarker(endMarker, '#ef4444', lngLat)
        } else {
            endMarker = clearMarker(endMarker)
        }
    }

    async function applyNodeSelection(
        nodeId: number | null,
        point: [number, number] | null,
        locationNameFromMap?: string | null,
    ) {
        if (nodeId === null || point === null) return

        console.log(nodeId)
        selectedNodeId.value = nodeId
        selectedEdgeId.value = null

        let location_name = locationNameFromMap ?? null
        if (!location_name) {
            location_name = await fetchLocationName(nodeId)
        }

        // First click sets start, second sets destination; third click starts a new pair.
        if (startPoint.value === null || (startPoint.value !== null && endPoint.value !== null)) {
            setStartPoint(point, nodeId, location_name)
            setEndPoint(null, null, null)
        } else {
            setEndPoint(point, nodeId, location_name)
        }

        emitSelectionChange({
            start: startPoint.value,
            end: endPoint.value,
            startNodeId: startNodeId.value,
            endNodeId: endNodeId.value,
            start_location: start_location.value,
            end_location: end_location.value
        })
    }

    function setMap(nextMap: Map | null) {
        map = nextMap
    }

    function clearFeatureSelection() {
        selectedNodeId.value = null
        selectedEdgeId.value = null
    }

    function applyEdgeSelection(edgeId: number | null) {
        selectedEdgeId.value = edgeId
        selectedNodeId.value = null
    }

    function dispose() {
        startMarker = clearMarker(startMarker)
        endMarker = clearMarker(endMarker)
        map = null
    }

    return {
        applyEdgeSelection,
        applyNodeSelection,
        clearFeatureSelection,
        dispose,
        selectedEdgeId,
        selectedNodeId,
        setMap,
    }
}
