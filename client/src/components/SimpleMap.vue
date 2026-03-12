<script setup lang="ts">
import {
    assertFeatureCollection,
    parseFeatureId,
    parseFeaturePointCoordinates,
    type coordinates,
    type GeoJson,
} from '@/components/simple-map/geoJsonUtils'
import { useMapSelection } from '@/components/simple-map/useMapSelection'
import {
    EDGE_BASE_LAYER,
    EDGE_HIGHLIGHT_LAYER,
    EDGE_HIT_LAYER,
    NODE_BASE_LAYER,
    NODE_HIGHLIGHT_LAYER,
    NODE_HIT_LAYER,
} from '@/lib/mapLayers'
import { fetchGraphData } from '@/services/graph'
import maplibregl, { type FilterSpecification, type LngLatLike, type Map } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
    routes?: Array<Array<[number, number]>>
    nodes?: GeoJson | null
    edges?: GeoJson | null
    center?: coordinates | null
    locations?: GeoJson | null
}>()

const emit = defineEmits<{
    (
        event: 'selection-change',
        payload: {
            start: [number, number] | null
            end: [number, number] | null
            startNodeId: number | null
            endNodeId: number | null
            start_location: string | null
            end_location: string | null
        },
    ): void
    (
        event: 'center-change',
        payload: [number, number],
    ): void
}>()

const mapEl = ref<HTMLDivElement | null>(null)
let map: Map | null = null

const nodes = ref<GeoJson | null>(null)
const edges = ref<GeoJson | null>(null)
const map_center = ref<LngLatLike | null>(null)
const locations = ref<GeoJson | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const {
    applyEdgeSelection,
    applyNodeSelection,
    clearFeatureSelection,
    dispose,
    selectedEdgeId,
    selectedNodeId,
    setMap,
} = useMapSelection((payload) => emit('selection-change', payload))

const selectableLayers = [
    'nodes-circle-hit',
    'edges-line-hit',
    'nodes-circle',
    'edges-line',
] as const
const selectableLayerIds = [...selectableLayers]
const layerToSelection: Record<(typeof selectableLayers)[number], 'node' | 'edge'> = {
    'nodes-circle-hit': 'node',
    'edges-line-hit': 'edge',
    'nodes-circle': 'node',
    'edges-line': 'edge',
}

const routeSourceId = 'routes'
const routeColors = ['#2563eb', '#ef4444', '#16a34a']
const routeLayerIds = routeColors.map((_, index) => `route-line-${index}`)

function getSelectableNodeIds(): number[] {
    const featureCollection = props.locations
    if (!featureCollection?.features) return []

    return featureCollection.features
        .map((feature) => Number(feature.properties?.node_id))
        .filter((value) => Number.isFinite(value))
}

function applySelectableNodeFilters() {
    if (!map) return
    if (!map.getLayer('nodes-circle') || !map.getLayer('nodes-circle-hit')) return

    const selectableNodeIds = getSelectableNodeIds()
    if (!selectableNodeIds.length) {
        map.setFilter('nodes-circle', ['==', ['get', 'node_id'], -1])
        map.setFilter('nodes-circle-hit', ['==', ['get', 'node_id'], -1])
        return
    }

    const idFilter: FilterSpecification = ['in', ['get', 'node_id'], ['literal', selectableNodeIds]]
    map.setFilter('nodes-circle', idFilter)
    map.setFilter('nodes-circle-hit', idFilter)
}

function toMapCoordinates(point: [number, number]): [number, number] {
    // Backend route geometry is (lat, lon), but MapLibre expects (lon, lat).
    const [lat, lon] = point
    return [lon, lat]
}

function buildRouteFeatureCollection(routes: Array<Array<[number, number]>>): GeoJSON.FeatureCollection {
    return {
        type: 'FeatureCollection',
        features: routes.slice(0, routeColors.length).flatMap((route, routeIndex) => {
            if (route.length < 2) return []
            return [
                {
                    type: 'Feature',
                    properties: { routeIndex },
                    geometry: {
                        type: 'LineString',
                        coordinates: route.map(toMapCoordinates),
                    },
                },
            ]
        }),
    }
}

function emitMapCenter() {
    if (!map) return
    const center = map.getCenter()
    emit('center-change', [center.lat, center.lng])
}


function renderRoutes(routes: Array<Array<[number, number]>> = []) {
    if (!map || !map.isStyleLoaded()) return

    for (const layerId of routeLayerIds) {
        if (map.getLayer(layerId)) map.removeLayer(layerId)
    }
    if (map.getSource(routeSourceId)) {
        map.removeSource(routeSourceId)
    }

    map.addSource(routeSourceId, {
        type: 'geojson',
        data: buildRouteFeatureCollection(routes),
    })

    routeLayerIds.forEach((layerId, routeIndex) => {
        map?.addLayer({
            id: layerId,
            type: 'line',
            source: routeSourceId,
            filter: ['==', ['get', 'routeIndex'], routeIndex],
            paint: {
                'line-color': routeColors[routeIndex],
                'line-width': 4,
                'line-opacity': 0.95,
            },
        })
    })

    map.setCenter(map_center.value ? map_center.value : [-2.585757, 51.460498])
}

// Initialize map and load graph data.
onMounted(() => {
    map = new maplibregl.Map({
        container: mapEl.value!,
        style: {
            version: 8,
            sources: {
                osm: {
                    type: 'raster',
                    tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                    tileSize: 256,
                    attribution: '© OpenStreetMap contributors',
                },
            },
            layers: [
                {
                    id: 'osm',
                    type: 'raster',
                    source: 'osm',
                },
            ],
        },
        center: [-2.585757, 51.460498],
        zoom: 14,
    })

    setMap(map)

    map.addControl(new maplibregl.NavigationControl(), 'top-right')

    map.on('load', () => {
        if (!map) return
        loading.value = true
        error.value = null

        fetchGraphData()
            .then((graphData) => {
                if (!map) return
                const nodeCollection = assertFeatureCollection(graphData.features?.nodes, 'nodes')
                const edgeCollection = assertFeatureCollection(graphData.features?.edges, 'edges')
                const locationCollection = assertFeatureCollection(graphData.features?.locations, 'locations')
                nodes.value = nodeCollection
                edges.value = edgeCollection
                locations.value = locationCollection
                map_center.value = toMapCoordinates(graphData.features?.center)
                console.log(locationCollection)

                map.addSource('edges', {
                    type: 'geojson',
                    data: edgeCollection,
                })  
                map.addSource('nodes', {
                    type: 'geojson',
                    data: nodeCollection,
                })

                // Add render layers
                map.addLayer(EDGE_BASE_LAYER)
                map.addLayer(EDGE_HIT_LAYER)
                map.addLayer(EDGE_HIGHLIGHT_LAYER)
                map.addLayer(NODE_BASE_LAYER)
                map.addLayer(NODE_HIT_LAYER)
                map.addLayer(NODE_HIGHLIGHT_LAYER)
                applySelectableNodeFilters()
                renderRoutes(props.routes)
                emitMapCenter()

                map.on('moveend', () => {
                    emitMapCenter()
                })

                map.on('click', (event) => {
                    if (!map) return
                    const features = map.queryRenderedFeatures(event.point, {
                        layers: selectableLayerIds,
                    })
                    if (!features.length) {
                        clearFeatureSelection()
                        return
                    }

                    const feature = features[0]
                    if (!feature) return

                    const layerId = feature.layer.id as (typeof selectableLayers)[number]
                    if (layerToSelection[layerId] === 'node') {
                        const nodeId = parseFeatureId(feature.properties?.node_id)
                        const point = parseFeaturePointCoordinates(feature)
                        applyNodeSelection(nodeId, point)
                        return
                    }
                    if (layerToSelection[layerId] === 'edge') {
                        applyEdgeSelection(parseFeatureId(feature.properties?.edge_id))
                    }
                })

                map.on('mousemove', (event) => {
                    if (!map) return
                    const features = map.queryRenderedFeatures(event.point, {
                        layers: selectableLayerIds,
                    })
                    map.getCanvas().style.cursor = features.length ? 'pointer' : ''
                })

                const bounds = new maplibregl.LngLatBounds()
                const nodeFeatures = nodes.value.features
                for (const feature of nodeFeatures) {
                    if (feature.geometry.type !== 'Point') continue
                    const coordinates = feature.geometry.coordinates
                    if (coordinates.length < 2) continue
                    const lng = Number(coordinates[0])
                    const lat = Number(coordinates[1])
                    if (!Number.isFinite(lng) || !Number.isFinite(lat)) continue
                    bounds.extend([lng, lat])
                }
                if (!bounds.isEmpty()) {
                    map.fitBounds(bounds, { padding: 40, maxZoom: 20 })
                    // Keep camera constrained to the dataset extent.
                    map.setRenderWorldCopies(false)
                }

                //map.setLayoutProperty('edges-line', 'visibility', 'none')
                //map.setLayoutProperty('edges-line-hit', 'visibility', 'none')
                //map.setLayoutProperty('edges-line-highlight', 'visibility', 'none')

                map.setLayoutProperty('nodes-circle', 'visibility', 'visible')
                map.setLayoutProperty('nodes-circle-hit', 'visibility', 'visible')
                map.setLayoutProperty('nodes-circle-highlight', 'visibility', 'visible')
        })
    })
})

watch(selectedEdgeId, (edgeId) => {
    if (!map!) return
    if (!map!.getLayer('edges-line-highlight')) return
    const value = edgeId ?? -1
    map!.setFilter('edges-line-highlight', ['==', ['get', 'edge_id'], value])
})

watch(selectedNodeId, (nodeId) => {
    if (!map!) return
    if (!map!.getLayer('nodes-circle-highlight')) return
    const value = nodeId ?? -1
    map!.setFilter('nodes-circle-highlight', ['==', ['get', 'node_id'], value])
})

watch(
  () => props.nodes,
  (newNodes) => {
    if (!map || !newNodes) return;

    if (map.getLayer('nodes-circle')) map.removeLayer('nodes-circle');
    if (map.getLayer('nodes-circle-hit')) map.removeLayer('nodes-circle-hit');
    if (map.getLayer('nodes-circle-highlight')) map.removeLayer('nodes-circle-highlight');
    if (map.getSource('nodes')) map.removeSource('nodes');

    map.addSource('nodes', {
      type: 'geojson',
      data: newNodes,
    });

    map.addLayer(NODE_BASE_LAYER);
    map.addLayer(NODE_HIT_LAYER);
    map.addLayer(NODE_HIGHLIGHT_LAYER);

    applySelectableNodeFilters();

    const bounds = new maplibregl.LngLatBounds();
    newNodes.features.forEach((f) => {
      if (f.geometry.type !== 'Point') return;

      const coords = f.geometry.coordinates;
      if (!Array.isArray(coords) || coords.length < 2) return;

      const [lng, lat] = coords;

      if (typeof lng === 'number' && typeof lat === 'number' && Number.isFinite(lng) && Number.isFinite(lat)) {
        bounds.extend([lng, lat]);
      }
    });

    if (!bounds.isEmpty()) {
      map.fitBounds(bounds, { padding: 40, maxZoom: 16 });
    }
  },
  { immediate: true }
);

watch(
    () => props.edges,
    (newEdges) => {
        if (!map || !newEdges) return
        const source = map.getSource('edges') as maplibregl.GeoJSONSource
        if (source) source.setData(newEdges)
    },
)

watch(
    () => props.locations,
    (newLocations) => {
        if (!map || !newLocations) return
        locations.value = newLocations
        applySelectableNodeFilters()
    },
    { immediate: true }
)

watch(
  () => props.center,
  (newCenter) => {
    if (!map || !newCenter) return
    map.setCenter(toMapCoordinates(newCenter))
  },
  { immediate: true }
)

onBeforeUnmount(() => {
    dispose()
    map?.remove()
    map = null
})

watch(
    () => props.routes,
    (routes) => {
        renderRoutes(routes ?? [])
    },
)
</script>

<template>
    <div ref="mapEl" class="h-[calc(100vh-48px)] w-full" />
</template>
