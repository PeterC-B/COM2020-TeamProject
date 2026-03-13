<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useMainStore } from '@/stores/main'
import { FetchRouteQueries, type RouteQueriesResponse } from '@/services/route_queries'

const mainStore = useMainStore()
const queries = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

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
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Start</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">End</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Popularity</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Most Recent</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Unique Users</th>
                        </tr>
                    </thead>

                    <tbody class="divide-y divide-slate-100">
                        <tr v-for="q in queries" :key="q.start + q.end" class="hover:bg-slate-50 transition-colors">
                            <td class="p-4 text-sm text-slate-600">{{ q.start }}</td>
                            <td class="p-4 text-sm text-slate-600">{{ q.end }}</td>
                            <td class="p-4 text-sm font-bold text-slate-900">{{ q.popularity }}</td>
                            <td class="p-4 text-xs font-semibold text-slate-500">{{ q.most_recent }}</td>
                            <td class="p-4 text-sm text-slate-600">{{ q.unique_users }}</td>
                        </tr>
                    </tbody>

                </table>
            </div>
        </div>
    </div>
</template>
