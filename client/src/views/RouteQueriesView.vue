<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()
const queries = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
    try {
        const response = await axios.get('/api/routing/queries', {
            headers: {
                Authorization: `Bearer ${mainStore.accessToken}`
            }
        })
        queries.value = response.data.data
    } catch (err: any) {
        error.value = 'Failed to load route queries.'
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="p-6">
        <h1 class="text-2xl font-bold mb-4">Route Query Analytics</h1>

        <div v-if="loading">Loading...</div>
        <div v-else-if="error">{{ error }}</div>

        <table v-else class="min-w-full border-collapse border border-gray-300">
            <thead>
                <tr class="bg-gray-100">
                    <th class="border p-2">Start</th>
                    <th class="border p-2">End</th>
                    <th class="border p-2">Weights</th>
                    <th class="border p-2">Rank</th>
                    <th class="border p-2">Path</th>
                    <th class="border p-2">Timestamp</th>
                    <th class="border p-2">User</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="q in queries" :key="q.query_id">
                    <td class="border p-2">{{ q.start }}</td>
                    <td class="border p-2">{{ q.end }}</td>
                    <td class="border p-2">{{ q.weights_json }}</td>
                    <td class="border p-2">{{ q.chosen_route_rank }}</td>
                    <td class="border p-2">{{ q.chosen_route_path }}</td>
                    <td class="border p-2">{{ q.timestamp }}</td>
                    <td class="border p-2">{{ q.user_id ?? 'Anonymous' }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
