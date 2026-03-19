<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'
import { FetchMissionAnalytics } from '@/services/route_queries'
import { computed } from 'vue'

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
        <h1 class="text-3xl font-bold text-slate-900 mb-8">Mission Analytics</h1>

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
