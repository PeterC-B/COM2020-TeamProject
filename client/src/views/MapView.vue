<script setup lang="ts">
import '@/assets/main.css'
import Disclaimer from '@/components/Disclaimer.vue'
import {
    assertFeatureCollection,
    type GeoJson,
    type coordinates,
} from '@/components/simple-map/geoJsonUtils'
import SimpleMap from '@/components/SimpleMap.vue'
import {
    activateGraphPreset,
    fetchGraphByCoordinates,
    fetchGraphData,
    fetchGraphPresets,
    fetchLikeLocations,
    fetchNodeContext
} from '@/services/graph'
import { fetchYensRoutes, type YensRoutesResponse } from '@/services/routing'
import { useMainStore } from '@/stores/main'
import ContextBox from '@/components/ContextBox.vue'

type ContextPayload =
    | {
        kind: 'node'
        id: number
        name: string
        nodeType: string
        coordinates: [number, number]
        extra?: string
    }
    | {
        kind: 'edge'
        id: number
        is_accessible: boolean
        greenery: number
        lighting: number
        surface_quality: number
    }
import { computed, onMounted, ref, watch } from 'vue'

type SelectionPayload = {
    start: [number, number] | null
    end: [number, number] | null
    startNodeId: number | null
    endNodeId: number | null
    start_location: string | null
    end_location: string | null
}

type PresetLocation = {
    code: string
    name: string
    lat: number
    lon: number
}

const selection = ref<SelectionPayload>({
    start: null,
    end: null,
    startNodeId: null,
    endNodeId: null,
    start_location: null,
    end_location: null,
})

const showContext = ref(false);
const selectedRouteIndex = ref<number | null>(null)
const contextPayload = ref<ContextPayload | null>(null)
let contextTimer: number | null = null;
let isHovering = false;
const hoveredFeatureId = ref<number | null>(null);
const lastNodeContextFetch = ref(0);

function to_text(text:string): string{
    if (typeof text !== 'string') return ''
    return text.replace(/_/g, ' ')
}

function capital_case(word: string): string{
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
}


function onShowContext(feature: any) {
    const geomType = feature._geometry?.type

    const id = geomType === 'Point' ? feature.properties.node_id : feature.properties.edge_id
    isHovering = true

    if (hoveredFeatureId.value === id) return
    hoveredFeatureId.value = id

    if (contextTimer) clearTimeout(contextTimer)

    contextTimer = window.setTimeout(async () => {
        if (!isHovering) return
        if (hoveredFeatureId.value !== id) return

        let payload: ContextPayload | null = null

        if (geomType === 'Point') {
            if (Date.now() - lastNodeContextFetch.value >= 3000) {
                lastNodeContextFetch.value = Date.now()
                try {
                    const nodeData = await fetchNodeContext(feature.properties.node_id)
                    payload = {
                        kind: 'node',
                        id: nodeData.node_id || feature.properties.node_id,
                        name:
                            nodeData.name !== 'NaN'
                                ? nodeData.name
                                : capital_case(to_text(nodeData.nodeType || feature.properties.type)),
                        nodeType: capital_case(to_text(nodeData.nodeType || feature.properties.type)),
                        coordinates: nodeData.coordinates || feature._geometry.coordinates,
                        extra:
                            nodeData.highway !== 'NaN'
                                ? capital_case(to_text(nodeData.highway))
                                : feature.properties.highway !== 'NaN'
                                ? capital_case(to_text(feature.properties.highway))
                                : undefined,
                    }
                } catch (e) {
                    payload = {
                        kind: 'node',
                        id: feature.properties.node_id,
                        name:
                            feature.properties.name !== 'NaN'
                                ? feature.properties.name
                                : capital_case(to_text(feature.properties.type)),
                        nodeType: capital_case(to_text(feature.properties.type)),
                        coordinates: feature._geometry.coordinates,
                        extra:
                            feature.properties.highway !== 'NaN'
                                ? capital_case(to_text(feature.properties.highway))
                                : undefined,
                    }
                }
            } else {
                payload = {
                    kind: 'node',
                    id: feature.properties.node_id,
                    name:
                        feature.properties.name !== 'NaN'
                            ? feature.properties.name
                            : capital_case(to_text(feature.properties.type)),
                    nodeType: capital_case(to_text(feature.properties.type)),
                    coordinates: feature._geometry.coordinates,
                    extra:
                        feature.properties.highway !== 'NaN'
                            ? capital_case(to_text(feature.properties.highway))
                            : undefined,
                }
            }
        } else if (geomType === 'LineString') {
            payload = {
                kind: 'edge',
                id: feature.properties.edge_id,
                is_accessible: feature.properties.is_accessible,
                greenery: feature.properties.greenery,
                lighting: feature.properties.lighting,
                surface_quality: feature.properties.surface_quality,
            }
        }

        if (payload) {
            contextPayload.value = payload
            showContext.value = true
        }
    }, 1000)
}

function onHideContext() {
    isHovering = false

    if (contextTimer) {
        clearTimeout(contextTimer)
        contextTimer = null
    }

    hoveredFeatureId.value = null
    showContext.value = false
    contextPayload.value = null
}

const mainStore = useMainStore()
const userId = computed(() => mainStore.user_id)

const nodes = ref<GeoJson | null>(null)
const edges = ref<GeoJson | null>(null)
const locations = ref<GeoJson | null>(null)
const mapCenter = ref<coordinates | null>(null)

const loadingRoute = ref(false)
const routeError = ref<string | null>(null)
const routeData = ref<YensRoutesResponse | null>(null)
const showDisclaimer = ref(false)
const locationQuery = ref('')
const locationSearchError = ref<string | null>(null)
type LocationSuggestion = { display_name: string; lat: string; lon: string }
const locationSuggestions = ref<LocationSuggestion[]>([])
const showSuggestions = ref(false)
const loadingSuggestions = ref(false)
const suppressSuggestionFetch = ref(false)
const selectingArea = ref(false)
const selectAreaError = ref<string | null>(null)
const routeGeometries = computed(() => routeData.value?.routes.map((route) => route.geometry) ?? [])

const weightFields = [
    { key: 'distance', label: 'Distance' },
    { key: 'lighting', label: 'Lighting' },
    { key: 'greenery', label: 'Greenery' },
    { key: 'surface_quality', label: 'Surface Quality' },
    { key: 'accessible', label: 'Accessible' },
] as const

const weights = ref({
    distance: 5,
    lighting: 5,
    greenery: 5,
    surface_quality: 5,
    accessible: false,
})

const defaultPresetLocations: PresetLocation[] = [
    { code: 'bristol', name: 'Bristol', lat: 51.4545, lon: -2.5879 },
    { code: 'liverpool', name: 'Liverpool', lat: 53.4084, lon: -2.9916 },
    { code: 'exeter', name: 'Exeter', lat: 50.7184, lon: -3.5339 },
    { code: 'basingstoke', name: 'Basingstoke', lat: 51.2665, lon: -1.0924 },
    { code: 'manchester', name: 'Manchester', lat: 53.4808, lon: -2.2426 },
    { code: 'birmingham', name: 'Birmingham', lat: 52.4862, lon: -1.8904 },
    { code: 'leeds', name: 'Leeds', lat: 53.8008, lon: -1.5491 },
    { code: 'nottingham', name: 'Nottingham', lat: 52.9548, lon: -1.1581 },
    { code: 'cardiff', name: 'Cardiff', lat: 51.4816, lon: -3.1791 },
    { code: 'southampton', name: 'Southampton', lat: 50.9097, lon: -1.4044 },
]
const presetLocations = ref<PresetLocation[]>([...defaultPresetLocations])
const activePresetCode = ref<string | null>(null)

const canRequestRoute = computed(() =>
    Boolean(selection.value.start && selection.value.end && !loadingRoute.value),
)

function onSelectionChange(payload: SelectionPayload) {
    selection.value = payload
}

function toLatLon(value: [number, number]): [number, number] {
    const [lng, lat] = value
    return [lat, lng]
}

function formatScore(value: number | null | undefined) {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return value.toFixed(2)
}

// Shows the map center just for debugging purposes
function formatCoordinate(value: number | null | undefined) {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return value.toFixed(6)
}

async function findLocation() {
    const query = locationQuery.value.trim()
    if (!query) {
        locationSearchError.value = 'Enter a location name'
        return
    }

    locationSearchError.value = null
    try {
        const response = (await fetchLikeLocations(query)) as {
            data?: Array<{ lat?: string; lon?: string }>
        }
        const firstMatch = response?.data?.[0]

        if (!firstMatch?.lat || !firstMatch?.lon) {
            locationSearchError.value = 'No matching place found'
            return
        }

        const lat = Number(firstMatch.lat)
        const lon = Number(firstMatch.lon)
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
            locationSearchError.value = 'Found place has invalid coordinates'
            return
        }

        // SimpleMap expects [lat, lon] on the `center` prop and converts to [lon, lat] internally.
        mapCenter.value = [lat, lon]
    } catch (err) {
        locationSearchError.value = err instanceof Error ? err.message : 'Failed to search location'
    }
}

function selectLocationSuggestion(suggestion: LocationSuggestion) {
    suppressSuggestionFetch.value = true
    locationQuery.value = suggestion.display_name
    showSuggestions.value = false

    const lat = Number(suggestion.lat)
    const lon = Number(suggestion.lon)
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
        locationSearchError.value = 'Selected place has invalid coordinates'
        return
    }

    locationSearchError.value = null
    // SimpleMap expects [lat, lon] on the `center` prop and converts to [lon, lat] internally.
    mapCenter.value = [lat, lon]
}

function onMapCenterChange(value: [number, number]) {
    mapCenter.value = value
}

async function selectPresetLocation(preset: PresetLocation) {
    suppressSuggestionFetch.value = true
    locationQuery.value = preset.name
    showSuggestions.value = false
    locationSearchError.value = null
    selectAreaError.value = null
    activePresetCode.value = preset.code
    mapCenter.value = [preset.lat, preset.lon]

    selectingArea.value = true
    try {  
        const graphData = await activateGraphPreset(preset.code)
        nodes.value = assertFeatureCollection(graphData.features?.nodes, 'nodes')
        edges.value = assertFeatureCollection(graphData.features?.edges, 'edges')
        locations.value = assertFeatureCollection(graphData.features?.locations, 'locations')
        mapCenter.value = graphData.features?.center ?? [preset.lat, preset.lon]
    } catch (err) {
        selectAreaError.value =
            err instanceof Error
                ? err.message
                : 'Failed to load preset snapshot. Ask backend to preload presets.'
    } finally {
        selectingArea.value = false
    }
}

async function selectCurrentArea() {
    const center = mapCenter.value
    if (!center) {
        selectAreaError.value = 'Move the map first to choose an area'
        return
    }

    selectAreaError.value = null
    selectingArea.value = true
    try {
        const [lat, lon] = center
        const graphData = await fetchGraphByCoordinates(lat, lon)
        nodes.value = assertFeatureCollection(graphData.features?.nodes, 'nodes')
        edges.value = assertFeatureCollection(graphData.features?.edges, 'edges')
        locations.value = assertFeatureCollection(graphData.features?.locations, 'locations')
        mapCenter.value = graphData.features?.center ?? [lat, lon]
    } catch (err) {
        selectAreaError.value = err instanceof Error ? err.message : 'Failed to select current area'
    } finally {
        selectingArea.value = false
    }
}

watch(
    () => locationQuery.value,
    async (value) => {
        if (suppressSuggestionFetch.value) {
            suppressSuggestionFetch.value = false
            return
        }
        const query = value.trim()
        if (query.length < 2) {
            locationSuggestions.value = []
            showSuggestions.value = false
            return
        }

        loadingSuggestions.value = true
        try {
            const response = (await fetchLikeLocations(query)) as { data?: LocationSuggestion[] }
            locationSuggestions.value = response.data ?? []
            showSuggestions.value = locationSuggestions.value.length > 0
        } catch {
            locationSuggestions.value = []
            showSuggestions.value = false
        } finally {
            loadingSuggestions.value = false
        }
    },
)

async function requestRoute() {
    if (!selection.value.start || !selection.value.end) return

    loadingRoute.value = true
    routeError.value = null
    const normalizedWeights = {
        distance: Math.max(1, Math.min(10, weights.value.distance)),
        lighting: Math.max(1, Math.min(10, weights.value.lighting)),
        greenery: Math.max(1, Math.min(10, weights.value.greenery)),
        surface_quality: Math.max(1, Math.min(10, weights.value.surface_quality)),
        accessible: weights.value.accessible,
    }

    try {
        routeData.value = await fetchYensRoutes({
            start: toLatLon(selection.value.start),
            end: toLatLon(selection.value.end),
            k: 3,
            weights: normalizedWeights,
            user_id: userId.value ?? 'undefined',
        })
    } catch (err) {
        routeData.value = null
        routeError.value = err instanceof Error ? err.message : 'Could not load route'
    } finally {
        loadingRoute.value = false
    }
}

onMounted(async () => {
    showDisclaimer.value = true

    try {
        const presets = await fetchGraphPresets()
        if (Array.isArray(presets) && presets.length > 0) {
            presetLocations.value = presets.map((preset) => ({
                code: preset.code,
                name: preset.name,
                lat: Number(preset.lat),
                lon: Number(preset.lon),
            }))
        }
    } catch (err) {
        console.error('Failed to load graph presets, using defaults', err)
    }

    try {
        const graphData = await fetchGraphData()
        locations.value = graphData.features?.locations
        mapCenter.value = graphData.features?.center ?? null
    } catch (err) {
        console.error('Failed to load graph data on mount', err)
    }
})
</script>

<template>
    <section class="mx-auto max-w-6xl p-6 antialiased">
        <header class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
                <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Route Planner</h1>
                <p class="text-slate-500 text-sm italic">
                    Customise your journey preferences and find the best path.
                </p>
                <p class="mt-2 text-xs text-slate-600">
                    Map center:
                    <span class="font-semibold">
                        {{ formatCoordinate(mapCenter?.[0] ?? null) }},
                        {{ formatCoordinate(mapCenter?.[1] ?? null) }}
                    </span>
                </p>
            </div>

            <div class="relative w-full max-w-xl">
                <div
                    class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm"
                >
                    <input
                        v-model="locationQuery"
                        type="text"
                        placeholder="Search for a location"
                        class="min-w-0 flex-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-500/20"
                    />
                    <button
                        type="button"
                        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 active:bg-indigo-700"
                        @click="findLocation"
                    >
                        Search
                    </button>
                    <button
                        type="button"
                        class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="selectingArea"
                        @click="selectCurrentArea"
                    >
                        {{ selectingArea ? 'Selecting...' : 'Select Area' }}
                    </button>
                </div>
                <p v-if="locationSearchError" class="mt-2 text-xs text-rose-600">
                    {{ locationSearchError }}
                </p>
                <p v-if="selectAreaError" class="mt-2 text-xs text-rose-600">
                    {{ selectAreaError }}
                </p>
                <div
                    v-if="showSuggestions"
                    class="absolute z-20 mt-2 max-h-56 w-full overflow-auto rounded-xl border border-slate-200 bg-white shadow-lg"
                >
                    <button
                        v-for="suggestion in locationSuggestions"
                        :key="suggestion.display_name"
                        type="button"
                        class="block w-full border-b border-slate-100 px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-slate-50"
                        @click="selectLocationSuggestion(suggestion)"
                    >
                        {{ suggestion.display_name }}
                    </button>
                </div>
                <p v-else-if="loadingSuggestions" class="mt-1 text-xs text-slate-500">
                    Searching places...
                </p>
            </div>
        </header>

        <Disclaimer :open="showDisclaimer" @close="showDisclaimer = false" />

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <aside class="space-y-6 lg:col-span-4">
                <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <h3 class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">
                        Location Details
                    </h3>

                    <div class="space-y-4">
                        <div class="flex items-center gap-3">
                            <div
                                class="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                            ></div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-bold uppercase text-slate-400"
                                    >Start Point</span
                                >
                                <span class="text-sm font-medium text-slate-700">
                                    {{
                                        selection.start_location
                                            ? `${selection.start_location}`
                                            : 'Click map to set'
                                    }}
                                </span>
                            </div>
                        </div>

                        <div class="flex items-center gap-3">
                            <div
                                class="h-3 w-3 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]"
                            ></div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-bold uppercase text-slate-400"
                                    >Destination</span
                                >
                                <span class="text-sm font-medium text-slate-700">
                                    {{
                                        selection.end_location
                                            ? `${selection.end_location}`
                                            : 'Click map to set'
                                    }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <p class="mt-4 text-[11px] text-slate-400 border-t border-slate-50 pt-3">
                        Tip: Select a third point on the map to reset your selection.
                    </p>
                </div>

                <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <h3 class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">
                        Route Preferences
                    </h3>

                    <div class="space-y-5">
                        <div v-for="(field, index) in weightFields" :key="field.key" class="group">
                            <div class="flex justify-between mb-1.5" v-if="index !== weightFields.length - 1">
                                <label class="text-sm font-semibold text-slate-700">{{
                                    field.label
                                }}</label>
                                <span
                                    class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 rounded"
                                    >{{ weights[field.key] }}</span
                                >
                            </div>
                            <input
                                v-if="index !== weightFields.length - 1"
                                v-model.number="weights[field.key]"
                                type="range"
                                min="1"
                                max="10"
                                step="1"
                                class="h-1.5 w-full cursor-pointer appearance-none rounded-lg bg-slate-100 accent-indigo-600 transition-all hover:bg-slate-200"
                            />
                            <div v-if="index === weightFields.length - 1">
                                <div class="flex justify-between mb-1.5" >
                                    <label class="text-sm font-semibold text-slate-700">{{
                                        field.label
                                    }}</label>
                                    <span
                                        class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 rounded"
                                        >{{ weights.accessible ? 'True' : 'False' }}</span
                                    >
                                </div>
                                <div class="relative inline-block w-11 h-5">
                                    <input :id="`accessible-switch-${index}`" v-model="weights.accessible" type="checkbox" class="peer appearance-none w-11 h-5 accent-indigo-600 rounded-full checked:bg-indigo-600 cursor-pointer transition-colors duration-300" />
                                    <label :for="`accessible-switch-${index}`" class="absolute top-0 left-0 w-5 h-5 bg-white rounded-full border border-slate-300 shadow-sm transition-transform duration-300 peer-checked:translate-x-6 peer-checked:border-slate-800 cursor-pointer">
                                    </label>
                                </div>
                            </div>

                        </div>
                    </div>

                    <button
                        class="mt-8 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg transition hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="!canRequestRoute"
                        @click="requestRoute"
                    >
                        <svg
                            v-if="loadingRoute"
                            class="h-4 w-4 animate-spin text-white"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                class="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                stroke-width="4"
                                fill="none"
                            ></circle>
                            <path
                                class="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                        </svg>
                        {{ loadingRoute ? 'Calculating Path...' : 'Find Best Route' }}
                    </button>

                    <p v-if="routeError" class="mt-3 text-center text-xs font-medium text-rose-600">
                        {{ routeError }}
                    </p>
                </div>

                <ContextBox
                    class="absolute top-2 left-1 z-50 pointer-events-auto"
                    :open="showContext"
                    :payload="contextPayload"
                    @close="onHideContext"
                />
            </aside>

            <div class="space-y-6 lg:col-span-8">
                <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-sm ring-1 ring-slate-100">
                    <SimpleMap 
                        :routes="routeGeometries" 
                        :nodes="nodes" 
                        :edges="edges" 
                        :center="mapCenter" 
                        :locations="locations" 
                        :selected_route_index="selectedRouteIndex"
                        @selection-change="onSelectionChange"
                        @show-context="onShowContext"
                        @hide-context="onHideContext"
                        @center-change="onMapCenterChange"
                        class="h-[700px] rounded-xl" 
                    />

                <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <div class="mb-3 flex items-center justify-between">
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400">
                            Preset Areas
                        </h3>
                    </div>
                    <div class="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
                        <button
                            v-for="preset in presetLocations"
                            :key="preset.code"
                            type="button"
                            :class="[
                                'rounded-lg border px-2 py-2 text-xs font-semibold transition',
                                activePresetCode === preset.code
                                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                                    : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-300 hover:bg-slate-100',
                            ]"
                            @click="selectPresetLocation(preset)"
                        >
                            {{ preset.name }}
                        </button>
                    </div>
                </div>

                <div
                    v-if="routeData"
                    class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden"
                >
                    <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-4">
                        <h2 class="text-lg font-bold text-slate-800">Route Comparison</h2>
                        <p class="text-xs text-slate-500">
                            Performance metrics across different path options.
                        </p>
                    </div>

                    <div class="overflow-x-auto p-4">
                        <table class="w-full text-left text-sm border-separate border-spacing-y-2">
                            <thead>
                                <tr
                                    class="text-[11px] font-bold uppercase tracking-wider text-slate-400"
                                >
                                    <th class="px-4 py-2">Option</th>
                                    <th class="px-2 py-2">Dist.</th>
                                    <th class="px-2 py-2">Score</th>
                                    <th class="px-2 py-2 text-center">Light</th>
                                    <th class="px-2 py-2 text-center">Green</th>
                                    <th class="px-2 py-2 text-center">Surface</th>
                                    <th class="px-2 py-2 text-center">Amenity</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr
                                    v-for="(route, index) in routeData.routes"
                                    :key="index"
                                    class="group transition-colors hover:bg-slate-50 relative"
                                    @click="selectedRouteIndex = selectedRouteIndex === index ? null : index"
                                >
                                    <td
                                        :class="[
                                            'rounded-l-lg px-4 py-3 font-bold transition-all',
                                            index === 0 ? 'route-blue' : '',
                                            index === 1 ? 'route-red' : '',
                                            index === 2 ? 'route-green' : '',
                                        ]"
                                    >
                                        #{{ index + 1 }}
                                    </td>

                                    <td class="px-2 py-3 font-medium">
                                        {{ formatScore(route.distance) }}
                                    </td>
                                    <td class="px-2 py-3 font-bold text-indigo-600">
                                        {{ formatScore(route.indicators?.weighted_score) }}
                                    </td>
                                    <td class="px-2 py-3 text-center text-slate-500">
                                        {{ formatScore(route.indicators?.lighting) }}
                                    </td>
                                    <td class="px-2 py-3 text-center text-slate-500">
                                        {{ formatScore(route.indicators?.greenery) }}
                                    </td>
                                    <td class="px-2 py-3 text-center text-slate-500">
                                        {{ formatScore(route.indicators?.surface_quality) }}
                                    </td>
                                    <td class="px-2 py-3 text-center text-slate-500 rounded-r-lg">
                                        {{ formatScore(route.indicators?.amenity_proximity) }}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div
                        v-if="routeData.comparison"
                        class="grid grid-cols-1 divide-y divide-slate-100 border-t border-slate-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0 bg-slate-50/30"
                    >
                        <div class="px-6 py-4">
                            <span
                                class="block text-[10px] font-bold uppercase tracking-widest text-slate-400"
                                >Shortest</span
                            >
                            <span class="text-sm font-semibold text-slate-700"
                                >{{ formatScore(routeData.comparison.shortest_distance) }}m</span
                            >
                        </div>
                        <div class="px-6 py-4">
                            <span
                                class="block text-[10px] font-bold uppercase tracking-widest text-slate-400"
                                >Longest</span
                            >
                            <span class="text-sm font-semibold text-slate-700"
                                >{{ formatScore(routeData.comparison.longest_distance) }}m</span
                            >
                        </div>
                        <div class="px-6 py-4">
                            <span
                                class="block text-[10px] font-bold uppercase tracking-widest text-slate-400"
                                >Average</span
                            >
                            <span class="text-sm font-semibold text-slate-700"
                                >{{ formatScore(routeData.comparison.average_distance) }}m</span
                            >
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </section>
</template>

<style scoped>
/* mapping table route options to map line colours */
.route-blue {
    background-color: rgba(37, 99, 235, 0.08);
    color: #2563eb;
}
.route-red {
    background-color: rgba(239, 68, 68, 0.08);
    color: #ef4444;
}
.route-green {
    background-color: rgba(22, 163, 74, 0.08);
    color: #16a34a;
}
</style>
