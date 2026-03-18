<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FetchEdgeAnalytics, type EdgeAnalyticsRow } from '@/services/edge_analytics'

const rows = ref<EdgeAnalyticsRow[]>([])
const loading = ref(true)

onMounted(async () => {
  rows.value = await FetchEdgeAnalytics()
  loading.value = false
})
</script>

<template>
  <div class="p-6 w-full">
    <h1 class="text-2xl font-semibold mb-6">Edge Analytics</h1>

    <div v-if="loading" class="text-gray-500 text-lg">
      Loading edge analytics…
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-gray-300 shadow-sm">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-100">
          <tr>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">EDGE ID</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">FROM</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">TO</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">LENGTH (m)</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">TRAVEL TIME (s)</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">ACCESS SCORE</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">LIGHTING</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">GREENERY</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">POLLUTION</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">SURFACE QUALITY</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">PUB DISTANCE</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="row in rows" :key="row.edge_id">
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.edge_id }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.from_node }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.to_node }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.length.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.travel_time.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.access_score.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.lighting.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.greenery.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.pollution.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.surface_quality.toFixed(2) }}</td>
            <td class="px-4 py-2 text-sm text-gray-800">{{ row.pub_distance.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
tbody tr:hover {
  background-color: #f9fafb;
}
</style>
