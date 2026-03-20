<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { FetchMissionAnalytics } from '@/services/route_queries'
import { buildCsvContent, downloadCsv } from '@/lib/csv'

const queries = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

type MissionAccuracy = {
    mission_id: string
    mission_name: string
    total: number
    correct: number
    percentage: number
    most_chosen_answer: string
}

const missionAccuracy = computed<MissionAccuracy[]>(() => {
  const map = new Map<
    string,
    MissionAccuracy & { answerCounts: Record<string, number> }
  >()

  for (const q of queries.value) {
    if (!map.has(q.mission_id)) {
      map.set(q.mission_id, {
        mission_id: q.mission_id,
        mission_name: q.mission_name,
        total: 0,
        correct: 0,
        percentage: 0,
        most_chosen_answer: '—',
        answerCounts: {},
      })
    }

    const entry = map.get(q.mission_id)!
    entry.total++

    if (q.status === 'correct') {
      entry.correct++
    }
    
    if (q.chosen_answer) {
        entry.answerCounts[q.chosen_answer] = (entry.answerCounts[q.chosen_answer] ?? 0) + 1
    }
  }

  return Array.from(map.values())
    .map(({ answerCounts, ...m }) => {
      let topAnswer = '—'
      let topCount = 0

      for (const [answer, count] of Object.entries(answerCounts)) {
        if (count > topCount) {
          topAnswer = answer
          topCount = count
        }
      }

      return {
        ...m,
        percentage: Math.round((m.correct / m.total) * 100),
        most_chosen_answer: topAnswer,
      }
    })
    .sort((a, b) => b.percentage - a.percentage)
})

const csvHeaders = ['Mission', 'Times Correct', 'Times Completed', 'Percentage', 'Most Common Answer']

const buildMissionAnalyticsCsvContent = () => {
  const rows = missionAccuracy.value.map((entry) => [
    entry.mission_name,
    entry.correct,
    entry.total,
    entry.percentage,
    entry.most_chosen_answer,
  ])

  return buildCsvContent(csvHeaders, rows)
}

const downloadMissionAnalyticsCsv = () => {
  if (!missionAccuracy.value.length) {
    return
  }

  downloadCsv(buildMissionAnalyticsCsvContent(), `mission-analytics-${new Date().toISOString().slice(0, 10)}.csv`)
}


onMounted(async () => {
    try {
        queries.value = (await FetchMissionAnalytics())
    } catch (err: any) {
        error.value = 'Failed to load mission progress.'
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <div class="mx-auto max-w-7xl p-6 antialiased">
        <div class="flex items-center justify-between gap-6 mb-8 flex-wrap">
            <h1 class="text-3xl font-bold text-slate-900">Mission Analytics</h1>
            <button
                class="rounded-md border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:border-slate-900 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
                :disabled="loading || !missionAccuracy.length"
                @click="downloadMissionAnalyticsCsv"
            >
                Export CSV
            </button>
        </div>

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
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Mission</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Times correct</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Times completed</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Percentage</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Most common answer</th>
                        </tr>
                    </thead>

                    <tbody class="divide-y divide-slate-100">
                        <tr v-for="q in missionAccuracy" :key="q.mission_id" class="hover:bg-slate-50 transition-colors">
                            <td class="p-4 text-sm font-bold text-slate-900">{{ q.mission_name }}</td>
                            <td class="p-4 text-sm text-slate-600 max-w-[150px]">{{ q.correct ?? '--' }}</td>
                            <td class="p-4 text-sm text-slate-600 max-w-[150px]">{{ q.total ?? '--' }}</td>
                            <td class="p-4">
                                <span class="bg-indigo-50 text-indigo-700 px-2 py-1 rounded-md text-xs font-bold">{{ q.percentage }}%</span>
                            </td>
                            <td class="p-4 text-sm text-slate-600 max-w-[150px]">{{ q.most_chosen_answer ?? 'NaN' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
