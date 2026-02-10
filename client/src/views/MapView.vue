<script setup lang="ts">
import { computed, ref } from 'vue'

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

async function requestRoute() {
    if (!selection.value.start || !selection.value.end) return

    loadingRoute.value = true
    routeError.value = null

    try {
        routeData.value = await fetchYensRoutes({
            start: toLatLon(selection.value.start),
            end: toLatLon(selection.value.end),
            k: 3,
        })
        console.log('Response received:', routeData.value)
    } catch (err) {
        routeData.value = null
        routeError.value = err instanceof Error ? err.message : 'Could not load route'
    } finally {
        loadingRoute.value = false
    }
}
</script>

<template>
    <section class="space-y-4">
        <h1 class="text-2xl font-semibold">Map</h1>

        <div class="rounded border border-slate-300 bg-white p-4">
            <p class="text-sm text-slate-700">
                Pick a start node (green), then a destination (red).
            </p>
            <p class="mt-2 text-sm text-slate-700">
                Start:
                {{ selection.start ? `${selection.start[0]}, ${selection.start[1]}` : 'Not set' }}
            </p>
            <p class="text-sm text-slate-700">
                Destination:
                {{ selection.end ? `${selection.end[0]}, ${selection.end[1]}` : 'Not set' }}
            </p>
            <p class="text-xs text-slate-500">Click a third node to start over.</p>
            <button
                class="mt-3 rounded bg-slate-900 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="!canRequestRoute"
                @click="requestRoute"
            >
                {{ loadingRoute ? 'Finding...' : 'Find Route' }}
            </button>
            <p v-if="routeError" class="mt-2 text-sm text-red-600">{{ routeError }}</p>
            <p v-if="routeData" class="mt-2 text-sm text-green-700">
                {{ routeData.returned_routes }} route option{{
                    routeData.returned_routes === 1 ? '' : 's'
                }}
                loaded.
            </p>
        </div>

        <SimpleMap @selection-change="onSelectionChange" />
    </section>
</template>
