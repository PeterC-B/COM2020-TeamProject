<script setup lang="ts">
    import { ref, onMounted, computed } from 'vue'
    import {
        saveMissionProgress,
        fetchMissionProgress,
        fetchAllMissionProgressForMission,
        fetchAllMissionProgressForUser,
        type MissionProgress,
        fetchAllMissionProgress,
    } from '@/services/leaderboard'
    import { list_all_users, type Users } from '@/services/auth'
    import { useMainStore } from '@/stores/main'

    const mainStore = useMainStore()

    const leaderboard = ref<MissionProgress[]>([])
    const users = ref<Users[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)

    const joinedLeaderboard = computed(() => {
        if (!leaderboard.value.length || !users.value.length) return []

        // Aggregate scores per user
        const scores: Record<string, number> = {}
        const totals: Record<string, number> = {}

        leaderboard.value.forEach(progress => {
            scores[progress.user_id] = scores[progress.user_id] ?? 0
            totals[progress.user_id] = totals[progress.user_id] ?? 0

            if (progress.status === 'correct') {
                scores[progress.user_id] = (scores[progress.user_id] || 0) + progress.score
            }
            totals[progress.user_id] = (totals[progress.user_id] || 0) + progress.score
        })

        const combined = users.value.map(user => ({
            ...user,
            score: scores[user.user_id] ?? 0,
            total: totals[user.user_id] ?? 0
        }))

        combined.sort((a, b) => b.score - a.score)

        let currentRank = 0
        let lastScore: number | null = null

        return combined.map((user, index) => {
            if (user.score !== lastScore) {
                currentRank = index + 1
                lastScore = user.score
            }

            return {
                ...user,
                rank: currentRank
            }
        })
    })

    async function loadLeaderboard(){
        loading.value = true
        error.value = null
        try{
            leaderboard.value = await fetchAllMissionProgress()
        } catch {
            error.value = 'Failed to load leaderboard'
        }

        try{
            users.value = await list_all_users()
        } catch {
            error.value = 'Failed to load users'
        } finally {
            loading.value = false
        }
    }

    function capital_case(word: string): string{
        const lower = word.toLowerCase()
        return lower.charAt(0).toUpperCase() + lower.slice(1)
    }

    onMounted(loadLeaderboard)
</script>
<template>
    <section class="mx-auto max-w-5xl p-6 antialiased">
        <!-- Header -->
        <div class="mb-8 flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-slate-900">Leaderboard</h1>
                <p class="text-slate-500">
                    Manage and create quest objectives for travellers.
                </p>
            </div>
        </div>

        <!-- Error -->
        <div
            v-if="error"
            class="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
            {{ error }}
        </div>
    </section>
    <aside class="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm antialiased">
        <div class="border-b border-slate-100 bg-slate-50/50 px-5 py-4 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-100 text-amber-600">
                    <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20"> 
                    </svg>
                </div>
                <h3 class="text-sm font-bold uppercase tracking-wider text-slate-600">Top Travellers</h3>
            </div>
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Weekly Reset</span>
        </div>

        <div class="p-2">
            <div
                v-for="user in joinedLeaderboard"
                :key="user.user_id"
                class="group flex items-center justify-between rounded-xl px-4 py-3 transition-colors hover:bg-slate-50"
            >
                <div class="flex items-center gap-4">
                    <div class="flex h-6 w-6 items-center justify-center text-xs font-black italic">
                        <span :class="{
                            'text-amber-500 scale-125': user.rank === 1,
                            'text-slate-400': user.rank === 2,
                        }">
                            {{ user.rank }}
                        </span>
                    </div>  

                    <div>
                        <p class="text-sm font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                            {{ capital_case(user.username) }}
                        </p>

                        <p class="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                            Level {{ Math.floor(user.score / 200) }} Explorer
                        </p>
                    </div>
                </div>

                <div class="text-right">
                    <p class="text-sm font-black text-slate-900"> {{  user.score.toLocaleString() }}/{{ user.total.toLocaleString() }}</p>
                    <p class="text-[9px] font-bold text-emerald-500 uppercase tracking-widest">Points</p>
                </div>
            </div>
        </div>

        <div class="border-t border-slate-50 bg-slate-50/30 px-5 py-3 text-center">
            <button class="text-[11px] font-bold text-indigo-600 hover:text-indigo-500 hover:underline">
                View Full Rankings 
            </button>
        </div>
    </aside>
</template>