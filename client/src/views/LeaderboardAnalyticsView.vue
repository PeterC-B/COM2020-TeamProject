<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { fetchAllMissionProgress } from '@/services/leaderboard'
import { buildCsvContent, downloadCsv } from '@/lib/csv'

const loading = ref(true)
const error = ref<string | null>(null)
const rows = ref<any[]>([])

onMounted(async () => {
    try {
        rows.value = await fetchAllMissionProgress()
        console.log("MISSION PROGRESS:", rows.value)
    } catch (err) {
        error.value = 'Failed to load leaderboard analytics.'
    } finally {
        loading.value = false
    }
})

const leaderboard = computed(() => {
    const map = new Map()

    for (const entry of rows.value) {
        if (!map.has(entry.user_id)) {
            map.set(entry.user_id, {
                user_id: entry.user_id,
                total_score: 0,
                potential_score: 0,
                missions_attempted: 0,
                missions_correct: 0,
            })
        }

        const user = map.get(entry.user_id)

        user.potential_score += entry.score
        user.missions_attempted += 1

        if (entry.status === 'correct') {
            user.total_score += entry.score
            user.missions_correct += 1
        }
    }

    const list = Array.from(map.values())
    list.sort((a, b) => b.total_score - a.total_score)

    return list.map((u, index) => ({
        ...u,
        rank: index + 1,
        accuracy: u.missions_attempted > 0
            ? Math.round((u.missions_correct / u.missions_attempted) * 100)
            : 0,
        avg_score: u.missions_attempted > 0
            ? Math.round((u.total_score / u.missions_attempted) * 100) / 100
            : 0,
        tier: u.total_score >= 300 ? 'Gold'
        : u.total_score >= 150 ? 'Silver'
            : 'Bronze'
    }))
})

const csvHeaders = [
    'Rank',
    'User',
    'Score (Earned / Potential)',
    'Missions Completed',
    'Accuracy',
    'Avg Score',
    'Tier',
]

const buildLeaderboardCsvContent = () => {
    const rows = leaderboard.value.map((user) => [
        user.rank,
        user.user_id,
        `${user.total_score} / ${user.potential_score}`,
        user.missions_attempted,
        user.accuracy,
        user.avg_score,
        user.tier,
    ])

    return buildCsvContent(csvHeaders, rows)
}

const downloadLeaderboardCsv = () => {
    if (!leaderboard.value.length) {
        return
    }

    downloadCsv(buildLeaderboardCsvContent(), `leaderboard-analytics-${new Date().toISOString().slice(0, 10)}.csv`)
}
</script>

<template>
    <div class="mx-auto max-w-7xl p-6 antialiased">
        <div class="flex items-center justify-between gap-6 mb-8 flex-wrap">
            <h1 class="text-3xl font-bold text-slate-900">Leaderboard Analytics</h1>
            <button
                class="rounded-md border border-slate-200 bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:border-slate-900 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
                :disabled="loading || !leaderboard.length"
                @click="downloadLeaderboardCsv"
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
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Rank</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">User</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Score (Earned / Potential)</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Missions Completed</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Accuracy</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Avg Score</th>
                            <th class="border-b border-slate-200 p-4 text-xs font-bold uppercase tracking-wider text-slate-500">Tier</th>
                        </tr>
                    </thead>

                    <tbody class="divide-y divide-slate-100">
                        <tr
                            v-for="user in leaderboard"
                            :key="user.user_id"
                            class="hover:bg-slate-50 transition-colors"
                        >
                            <td class="p-4 text-sm font-bold text-slate-900">{{ user.rank }}</td>
                            <td class="p-4 text-sm font-bold text-slate-900">{{ user.user_id }}</td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ user.total_score }} / {{ user.potential_score }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ user.missions_attempted }}
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ user.accuracy }}%
                            </td>

                            <td class="p-4 text-sm text-slate-600">
                                {{ user.avg_score }}
                            </td>

                            <td class="p-4 text-sm">
                                <span
                                    :class="{
                                        'bg-yellow-100 text-yellow-800 px-2 py-1 rounded-md text-xs font-bold': user.tier === 'Gold',
                                        'bg-gray-200 text-gray-800 px-2 py-1 rounded-md text-xs font-bold': user.tier === 'Silver',
                                        'bg-amber-100 text-amber-800 px-2 py-1 rounded-md text-xs font-bold': user.tier === 'Bronze',
                                    }"
                                >
                                    {{ user.tier }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
