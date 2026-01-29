<script setup lang="ts">
import {
    EDGE_BASE_LAYER,
    EDGE_HIGHLIGHT_LAYER,
    EDGE_HIT_LAYER,
    NODE_BASE_LAYER,
    NODE_HIGHLIGHT_LAYER,
    NODE_HIT_LAYER,
} from '@/lib/mapLayers'
import maplibregl, { type LngLatBoundsLike, type Map } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const mapEl = ref<HTMLDivElement | null>(null)
let map: Map | null = null

type GeoJson = GeoJSON.FeatureCollection

const nodes = ref<GeoJson | null>(null)
const edges = ref<GeoJson | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const selectedEdgeId = ref<number | null>(null)
const selectedNodeId = ref<number | null>(null)

const selectableLayers = [
    'nodes-circle-hit',
    'edges-line-hit',
    'nodes-circle',
    'edges-line',
] as const
const layerToSelection: Record<(typeof selectableLayers)[number], 'node' | 'edge'> = {
    'nodes-circle-hit': 'node',
    'edges-line-hit': 'edge',
    'nodes-circle': 'node',
    'edges-line': 'edge',
}

// Keep it loaded locally for now until the API is up and running.
async function loadGeoJSON(path: string): Promise<GeoJson> {
    const res = await fetch(path)
    if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`)
    return (await res.json()) as GeoJson
}

function parseFeatureId(value: unknown): number | null {
    if (typeof value === 'number') return Number.isFinite(value) ? value : null
    if (typeof value === 'string') {
        const parsed = Number(value)
        return Number.isFinite(parsed) ? parsed : null
    }
    return null
}

// When the component is first mounted we will setup the map and pull in the data.
onMounted(() => {
    map = new maplibregl.Map({
        container: mapEl.value!,
        style: 'https://demotiles.maplibre.org/style.json',
        center: [-0.1276, 51.5072],
        zoom: 12,
    })

    map.addControl(new maplibregl.NavigationControl(), 'top-right')

    map.on('load', async () => {
        if (!map) return
        try {
            loading.value = true
            error.value = null

            nodes.value = await loadGeoJSON('/data/maplibre/nodes.geojson')
            edges.value = await loadGeoJSON('/data/maplibre/edges.geojson')

            map.addSource('edges', {
                type: 'geojson',
                data: edges.value as GeoJSON.FeatureCollection,
            })
            map.addSource('nodes', {
                type: 'geojson',
                data: nodes.value as GeoJSON.FeatureCollection,
            })

            // Add all our layers
            map.addLayer(EDGE_BASE_LAYER)
            map.addLayer(EDGE_HIT_LAYER)
            map.addLayer(EDGE_HIGHLIGHT_LAYER)
            map.addLayer(NODE_BASE_LAYER)
            map.addLayer(NODE_HIT_LAYER)
            map.addLayer(NODE_HIGHLIGHT_LAYER)

            // Click to select an edge or node; hit layers make selection forgiving.
            map.on('click', (event) => {
                if (!map) return
                const features = map.queryRenderedFeatures(event.point, {
                    layers: selectableLayers as unknown as string[],
                })
                if (!features.length) {
                    selectedNodeId.value = null
                    selectedEdgeId.value = null
                    return
                }
                const feature = features[0]
                const layerId = feature.layer.id as (typeof selectableLayers)[number]
                if (layerToSelection[layerId] === 'node') {
                    selectedNodeId.value = parseFeatureId(feature.properties?.node_id)
                    selectedEdgeId.value = null
                    return
                }
                if (layerToSelection[layerId] === 'edge') {
                    selectedEdgeId.value = parseFeatureId(feature.properties?.edge_id)
                    selectedNodeId.value = null
                }
            })

            map.on('mousemove', (event) => {
                if (!map) return
                const features = map.queryRenderedFeatures(event.point, {
                    layers: selectableLayers as unknown as string[],
                })
                map.getCanvas().style.cursor = features.length ? 'pointer' : ''
            })

            const bounds = new maplibregl.LngLatBounds()
            const nodeFeatures = nodes.value.features
            for (const feature of nodeFeatures) {
                if (feature.geometry.type !== 'Point') continue
                const [lng, lat] = feature.geometry.coordinates as [number, number]
                bounds.extend([lng, lat])
            }
            if (!bounds.isEmpty()) {
                map.fitBounds(bounds as LngLatBoundsLike, { padding: 24, maxZoom: 16 })
                // Keep the camera locked to the dataset so you don't pan out to the world.
                map.setMaxBounds(bounds as LngLatBoundsLike)
                map.setRenderWorldCopies(false)
            }
        } catch (err) {
            error.value = err instanceof Error ? err.message : 'Failed to load GeoJSON'
        } finally {
            loading.value = false
        }
    })
})

watch(selectedEdgeId, (edgeId) => {
    if (!map) return
    if (!map.getLayer('edges-line-highlight')) return
    const value = edgeId ?? -1
    map.setFilter('edges-line-highlight', ['==', ['get', 'edge_id'], value])
})

watch(selectedNodeId, (nodeId) => {
    if (!map) return
    if (!map.getLayer('nodes-circle-highlight')) return
    const value = nodeId ?? -1
    map.setFilter('nodes-circle-highlight', ['==', ['get', 'node_id'], value])
})

onBeforeUnmount(() => {
    map?.remove()
    map = null
})
</script>

<template>
    <!-- fills viewport; adjust if you have a top nav -->
    <div ref="mapEl" class="h-[calc(100vh-64px)] w-full" />
</template>
