<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import '@/assets/main.css'
import Disclaimer from '@/components/Disclaimer.vue'
import SimpleMap from '@/components/SimpleMap.vue'
import { fetchYensRoutes, type YensRoutesResponse } from '@/services/routing'

type SelectionPayload = {
    start: [number, number] | null
    end: [number, number] | null
    startNodeId: number | null
    endNodeId: number | null
}

const selection = ref<SelectionPayload>({
    start: null,
    end: null,
    startNodeId: null,
    endNodeId: null,
})

const loadingRoute = ref(false)
const routeError = ref<string | null>(null)
const routeData = ref<YensRoutesResponse | null>(null)
const showDisclaimer = ref(false)
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
        })
    } catch (err) {
        routeData.value = null
        routeError.value = err instanceof Error ? err.message : 'Could not load route'
    } finally {
        loadingRoute.value = false
    }
}

onMounted(() => {
    showDisclaimer.value = true
})
</script>

<template>
    <section class="mx-auto max-w-6xl p-6 antialiased">
        <header class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
                <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Route Planner</h1>
                <p class="text-slate-500 text-sm italic">Customise your journey preferences and find the best path.</p>
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
                                    {{ selection.start ? `${selection.start[0].toFixed(4)}, ${selection.start[1].toFixed(4)}` : 'Click map to set' }}
                                </span>
                            </div>
                        </div>

                        <div class="flex items-center gap-3">
                            <div class="h-3 w-3 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]"></div>
                            <div class="flex flex-col">
                                <span class="text-[10px] font-bold uppercase text-slate-400">Destination</span>
                                <span class="text-sm font-medium text-slate-700">
                                    {{ selection.end ? `${selection.end[0].toFixed(4)}, ${selection.end[1].toFixed(4)}` : 'Click map to set' }}
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
            </aside>

            <div class="space-y-6 lg:col-span-8">
                <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white p-2 shadow-sm ring-1 ring-slate-100">
                    <SimpleMap :routes="routeGeometries" @selection-change="onSelectionChange" class="h-[500px] rounded-xl" />
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
                                    class="group transition-colors hover:bg-slate-50"
                                >
                                    <td class="rounded-l-lg bg-slate-50 px-4 py-3 font-bold text-slate-700 group-hover:bg-indigo-50 group-hover:text-indigo-700">
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