<script setup lang="ts">
import { ref } from 'vue'

// mock data bcs idk how to implement backend
const leaderboardDate = ref([
    { id: 1, name: 'john doe', score: 20, rank: 1},
    { id: 2, name: 'jane doe', score: 15, rank: 2},
])

// fetchLeaderboard() or whatever the function is here
</script>

<template>
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
                v-for="user in leaderboardData"
                :key="user.id"
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
                            {{ user.name }}
                        </p>
                        <p class="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
                            Level {{ Math.floor(user.score / 200) }} Explorer
                        </p>
                    </div>
                </div>

                <div class="text-right">
                    <p class="text-sm font-black text-slate-900">{{ user.score.toLocaleString() }}</p>
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

