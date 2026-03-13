<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import '@/assets/main.css'
import Disclaimer from '@/components/Disclaimer.vue'
import SimpleMap from '@/components/SimpleMap.vue'
import { fetchYensRoutes, type YensRoutesResponse } from '@/services/routing'
import { fetchGraphByLocation, fetchGraphData } from '@/services/graph'
import { assertFeatureCollection, type GeoJson, type coordinates } from '@/components/simple-map/geoJsonUtils'
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
        access_score: number
        greenery: number
        lighting: number
        surface_quality: number
    }

type SelectionPayload = {
    start: [number, number] | null
    end: [number, number] | null
    startNodeId: number | null
    endNodeId: number | null
    start_location: string | null
    end_location: string | null
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
const contextPayload = ref<ContextPayload | null>(null)
let contextTimer: number | null = null;
let isHovering = false;
const hoveredFeatureId = ref<number | null>(null);

function to_text(text:string): string{
    return text.replace(/_/g, ' ')
}

function capital_case(word: string): string{
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
}

function buildContextPayload(feature: any): ContextPayload | null {
    const geomType = feature._geometry?.type

    if (geomType === 'Point') {
        return {
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

    if (geomType === 'LineString') {
        return {
            kind: 'edge',
            id: feature.properties.edge_id,
            access_score: feature.properties.access_score,
            greenery: feature.properties.greenery,
            lighting: feature.properties.lighting,
            surface_quality: feature.properties.surface_quality,
        }
    }

    return null
}

function onShowContext(feature: any) {
    const payload = buildContextPayload(feature)
    if (!payload) return

    const id = payload.id
    isHovering = true

    if (hoveredFeatureId.value === id) return
    hoveredFeatureId.value = id

    if (contextTimer) clearTimeout(contextTimer)

    contextTimer = window.setTimeout(() => {
        if (!isHovering) return
        if (hoveredFeatureId.value !== id) return

        contextPayload.value = payload
        showContext.value = true
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
const user_ID = computed(() => (mainStore.user_id))

const nodes = ref<GeoJson | null>(null)
const edges = ref<GeoJson | null>(null)
const locations = ref<GeoJson | null>(null)
const map_center = ref<coordinates | null>(null)

const loadingRoute = ref(false)
const routeError = ref<string | null>(null)
const routeData = ref<YensRoutesResponse | null>(null)
const showDisclaimer = ref(false)
const chosen_location = ref('')
const routeGeometries = computed(() => routeData.value?.routes.map((route) => route.geometry) ?? [])

const weightFields = [
    { key: 'distance', label: 'Distance' },
    { key: 'lighting', label: 'Lighting' },
    { key: 'greenery', label: 'Greenery' },
    { key: 'surface_quality', label: 'Surface Quality' },
    { key: 'amenity_proximity', label: 'Amenity Proximity' },
] as const

const weights = ref({
    distance: 5,
    lighting: 5,
    greenery: 5,
    surface_quality: 5,
    amenity_proximity: 5,
})

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

async function findLocation(){
    await fetchGraphByLocation(chosen_location.value)
    const graphData = await fetchGraphData()

    nodes.value = assertFeatureCollection(graphData.features?.nodes, 'nodes')
    edges.value = assertFeatureCollection(graphData.features?.edges, 'edges')
    locations.value = graphData.features?.locations
    map_center.value = graphData.features?.center
}

async function requestRoute() {
    if (!selection.value.start || !selection.value.end) return

    loadingRoute.value = true
    routeError.value = null
    const normalizedWeights = Object.fromEntries(
        Object.entries(weights.value).map(([key, value]) => [
            key,
            Math.max(1, Math.min(10, Number(value) || 1)),
        ]),
    )

    try {
        routeData.value = await fetchYensRoutes({
            start: toLatLon(selection.value.start),
            end: toLatLon(selection.value.end),
            k: 3,
            weights: normalizedWeights,
            user_id: user_ID.value ?? "undefined"
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
        const graphData = await fetchGraphData()
        locations.value = graphData.features?.locations
        map_center.value = graphData.features?.center ?? null
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
                <p class="text-slate-500 text-sm italic">Customise your journey preferences and find the best path.</p>
            </div>

            <div>
                <select
                    name="locations"
                    v-model="chosen_location"
                    class="border rounded px-2 py-1"
                >
                    <option value="" disabled selected>Select a location</option>
                    <option
                    v-for="poi in locations?.features ?? []"
                    :key="poi.properties?.node_id"
                    :value="poi.properties?.name"
                    :hidden="poi.properties?.name === 'NaN'"
                    >
                    {{ poi.properties?.name }}
                    </option>
                </select>
            </div>

            <div>
                <input v-model="chosen_location" type="text" placeholder="Enter a location">
                <button type="button" @click="findLocation">Search</button>
            </div>
        </header>

        <Disclaimer :open="showDisclaimer" @close="showDisclaimer = false" />

        <div class="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <aside class="space-y-6 lg:col-span-4">
                <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <h3 class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">Location Details</h3>
                    
                    <div class="space-y-4">
                        <div class="flex items-center gap-3">
                            <div class="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-bold uppercase text-slate-400">Start Point</span>
                                <span class="text-sm font-medium text-slate-700">
                                    {{ selection.start_location ? `${selection.start_location}` : 'Click map to set' }}
                                </span>
                            </div>
                        </div>

                        <div class="flex items-center gap-3">
                            <div class="h-3 w-3 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]"></div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-bold uppercase text-slate-400">Destination</span>
                                <span class="text-sm font-medium text-slate-700">
                                    {{ selection.end_location ? `${selection.end_location}` : 'Click map to set' }}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <p class="mt-4 text-[11px] text-slate-400 border-t border-slate-50 pt-3">
                        Tip: Select a third point on the map to reset your selection.
                    </p>
                </div>

                <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                    <h3 class="mb-4 text-xs font-bold uppercase tracking-widest text-slate-400">Route Preferences</h3>
                    
                    <div class="space-y-5">
                        <div v-for="field in weightFields" :key="field.key" class="group">
                            <div class="flex justify-between mb-1.5">
                                <label class="text-sm font-semibold text-slate-700">{{ field.label }}</label>
                                <span class="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 rounded">{{ weights[field.key] }}</span>
                            </div>
                            <input
                                v-model.number="weights[field.key]"
                                type="range"
                                min="1"
                                max="10"
                                step="1"
                                class="h-1.5 w-full cursor-pointer appearance-none rounded-lg bg-slate-100 accent-indigo-600 transition-all hover:bg-slate-200"
                            />
                        </div>
                    </div>

                    <button
                        class="mt-8 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg transition hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40"
                        :disabled="!canRequestRoute"
                        @click="requestRoute"
                    >
                        <svg v-if="loadingRoute" class="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        {{ loadingRoute ? 'Calculating Path...' : 'Find Best Route' }}
                    </button>

                    <p v-if="routeError" class="mt-3 text-center text-xs font-medium text-rose-600">{{ routeError }}</p>
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
                        :center="map_center" 
                        :locations="locations" 
                        @selection-change="onSelectionChange"
                        @show-context="onShowContext"
                        @hide-context="onHideContext"
                        class="h-[700px] rounded-xl" 
                    />

                </div>

                <div v-if="routeData" class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                    <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-4">
                        <h2 class="text-lg font-bold text-slate-800">Route Comparison</h2>
                        <p class="text-xs text-slate-500">Performance metrics across different path options.</p>
                    </div>

                    <div class="overflow-x-auto p-4">
                        <table class="w-full text-left text-sm border-separate border-spacing-y-2">
                            <thead>
                                <tr class="text-[11px] font-bold uppercase tracking-wider text-slate-400">
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

                                    <td class="px-2 py-3 font-medium">{{ formatScore(route.distance) }}</td>
                                    <td class="px-2 py-3 font-bold text-indigo-600">{{ formatScore(route.indicators?.weighted_score) }}</td>
                                    <td class="px-2 py-3 text-center text-slate-500">{{ formatScore(route.indicators?.lighting) }}</td>
                                    <td class="px-2 py-3 text-center text-slate-500">{{ formatScore(route.indicators?.greenery) }}</td>
                                    <td class="px-2 py-3 text-center text-slate-500">{{ formatScore(route.indicators?.surface_quality) }}</td>
                                    <td class="px-2 py-3 text-center text-slate-500 rounded-r-lg">{{ formatScore(route.indicators?.amenity_proximity) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-if="routeData.comparison" class="grid grid-cols-1 divide-y divide-slate-100 border-t border-slate-100 sm:grid-cols-3 sm:divide-x sm:divide-y-0 bg-slate-50/30">
                        <div class="px-6 py-4">
                            <span class="block text-[10px] font-bold uppercase tracking-widest text-slate-400">Shortest</span>
                            <span class="text-sm font-semibold text-slate-700">{{ formatScore(routeData.comparison.shortest_distance) }}m</span>
                        </div>
                        <div class="px-6 py-4">
                            <span class="block text-[10px] font-bold uppercase tracking-widest text-slate-400">Longest</span>
                            <span class="text-sm font-semibold text-slate-700">{{ formatScore(routeData.comparison.longest_distance) }}m</span>
                        </div>
                        <div class="px-6 py-4">
                            <span class="block text-[10px] font-bold uppercase tracking-widest text-slate-400">Average</span>
                            <span class="text-sm font-semibold text-slate-700">{{ formatScore(routeData.comparison.average_distance) }}m</span>
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
