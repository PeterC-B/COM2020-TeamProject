<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FetchEdgeAnalytics, type EdgeAnalyticsRow } from '@/services/edge_analytics'
import { buildCsvContent, downloadCsv } from '@/lib/csv'

const rows = ref<EdgeAnalyticsRow[]>([])
const loading = ref(true)

const csvHeaders = [
  'Edge ID',
  'From',
  'To',
  'Length (m)',
  'Travel Time (s)',
  'Access Score',
  'Lighting',
  'Greenery',
  'Pollution',
  'Surface Quality',
  'Pub Distance',
]

const buildEdgeAnalyticsCsvContent = () => {
  const rowData = rows.value.map((row) => [
    row.edge_id,
    row.from_node,
    row.to_node,
    row.length.toFixed(2),
    row.travel_time.toFixed(2),
    row.access_score.toFixed(2),
    row.lighting.toFixed(2),
    row.greenery.toFixed(2),
    row.pollution.toFixed(2),
    row.surface_quality.toFixed(2),
    row.pub_distance.toFixed(2),
  ])

  return buildCsvContent(csvHeaders, rowData)
}

const downloadEdgeAnalyticsCsv = () => {
  if (!rows.value.length) {
    return
  }

  downloadCsv(buildEdgeAnalyticsCsvContent(), `edge-analytics-${new Date().toISOString().slice(0, 10)}.csv`)
}

onMounted(async () => {
  rows.value = await FetchEdgeAnalytics()
  loading.value = false
})
</script>

<template>
  <div class="p-6 w-full">
    <div class="flex items-center justify-between gap-6 mb-6 flex-wrap">
      <h1 class="text-2xl font-semibold">Edge Analytics</h1>
      <button
        class="rounded-md border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:border-slate-900 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="loading || !rows.length"
        @click="downloadEdgeAnalyticsCsv"
      >
        Export CSV
      </button>
    </div>

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
