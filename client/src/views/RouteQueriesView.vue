<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useMainStore } from '@/stores/main'
import { FetchRouteQueries, type RouteQueriesResponse } from '@/services/route_queries'

const mainStore = useMainStore()
const queries = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

function format_weights(weights: JSON): string{
    const result = Object.entries(weights)
        .map(([key, value]) => `${format_text(key)}: ${value}`)
        .join('\n')
    console.log(result)
    return result
}

function format_text(text: string) : string {
    return to_text(capital_case(text))
}

function to_text(text:string): string{
    return text.replace(/_/g, ' ')
}

function capital_case(word: string): string{
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
}


onMounted(async () => {
    try {
        queries.value = await FetchRouteQueries()
    } catch (err: any) {
        error.value = 'Failed to load route queries.'
    } finally {
        loading.value = false
        console.log(queries.value)
    }
})
</script>

<template>
    <div class="mx-auto max-w-7xl p-6 antialiased">
        <h1 class="text-3xl font-bold text-slate-900 mb-8">Route Query Analytics</h1>

        <div v-if="loading" class="p-12 text-center rounded-2xl border border-slate-200 bg-white text-slate-500 font-bold">
            Loading...
        </div>

        <div v-else-if="error" class="p-4 rounded-xl border border-red-200 bg-red-50 text-red-600 font-bold">
            {{ error }}
        </div>

        <div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div class="overflow-x-auto">
                <table class="w-full text-left border-separate border-spacing-0">
                    <thead>
                        <tr class="bg-slate-50">
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">User</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Start</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">End</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Weights</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Rank</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Path</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Timestamp</th>
                        </tr>
                    </thead>

                    <tbody class="divide-y divide-slate-100">
                        <tr v-for="q in queries" :key="q.query_id" class="hover:bg-slate-50 transition-colors">
                            <td class="p-4 text-sm font-bold text-slate-900">{{ capital_case(q.name) ?? 'Anonymous' }}</td>
                            <td class="p-4 text-sm text-slate-600 max-w-[150px]">{{ q.start }}</td>
                            <td class="p-4 text-sm text-slate-600 max-w-[150px]">{{ q.end }}</td>
                            <td class="p-4">
                                <code class="text-[10px] font-mono text-slate-400 block max-w-[400px] whitespace-pre-line">{{ format_weights(q.weights_json) }}</code>
                            </td>
                            <td class="p-4">
                                <span class="bg-indigo-50 text-indigo-700 px-2 py-1 rounded-md text-xs font-bold">#{{ q.chosen_route_rank }}</span>
                            </td>
                            <td class="p-4">
                                <p class="text-[10px] text-slate-400 truncate max-w-[100px]">{{ q.chosen_route_path }}</p>
                            </td>
                            <td class="p-4 text-xs font-semibold text-slate-500 max-w-[100px]">{{ q.timestamp }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
