<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMainStore } from '@/stores/main'
import { FetchNodeAnalytics } from '@/services/node_analytics.ts'

const mainStore = useMainStore()

const rows = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

function to_text(text: string): string {
    return text.replace(/_/g, ' ')
}

function capital_case(word: string): string {
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
}

function formatCoordinate(value: number | null | undefined) {
    if (value === null || value === undefined || Number.isNaN(value)) return 'N/A'
    return value.toFixed(6)
}

const nodeAnalytics = computed(() => {
    return rows.value.map((n) => {
        const name =
            n.name && n.name !== 'NaN'
                ? n.name
                : capital_case(to_text(n.type ?? 'Unknown'))

        const type =
            n.type && n.type !== 'NaN'
                ? capital_case(to_text(n.type))
                : n.highway
                ? capital_case(to_text(n.highway))
                : 'Unknown'

        return {
            node_id: n.node_id,
            name,
            type,
            lat: n.lat,
            lon: n.lon,
        }
    })
})
    
onMounted(async () => {
    try {
        rows.value = await FetchNodeAnalytics()
    } catch (err) {
        error.value = 'Failed to load node analytics.'
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="mx-auto max-w-7xl p-6 antialiased">
        <h1 class="text-3xl font-bold text-slate-900 mb-8">Node Analytics</h1>

        <div
            v-if="loading"
            class="p-12 text-center rounded-2xl border border-slate-200 bg-white text-slate-500 font-bold"
        >
            Loading...
        </div>

        <div
            v-else-if="error"
            class="p-4 rounded-xl border border-red-200 bg-red-50 text-red-600 font-bold"
        >
            {{ error }}
        </div>

        <div
            v-else
            class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl"
        >
            <div class="overflow-x-auto">
                <table class="w-full text-left border-separate border-spacing-0">
                    <thead>
                        <tr class="bg-slate-50">
                            <th
                                class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500"
                            >
                                Node ID
                            </th>
                            <th
                                class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500"
                            >
                                Name
                            </th>
                            <th
                                class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500"
                            >
                                Type
                            </th>
                            <th
                                class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500"
                            >
                                Latitude
                            </th>
                            <th
                                class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500"
                            >
                                Longitude
                            </th>
                        </tr>
                    </thead>

                    <tbody class="divide-y divide-slate-100">
                        <tr
                            v-for="n in nodeAnalytics"
                            :key="n.node_id"
                            class="hover:bg-slate-50 transition-colors"
                        >
                            <td class="p-4 text-sm font-bold text-slate-900">
                                {{ n.node_id }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ n.name }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ n.type }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ formatCoordinate(n.lat) }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ formatCoordinate(n.lon) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
