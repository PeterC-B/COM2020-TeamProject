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
    import { useMainStore } from '@/stores/main'

    const mainStore = useMainStore()

    const leaderboard = ref<MissionProgress[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)

    async function loadLeaderboard(){
        loading.value = true
        error.value = null
        try{
            leaderboard.value = await fetchAllMissionProgress()
        } catch {
            error.value = 'Failed to load leaderboard'
        } finally {
            loading.value = false
        }
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
</template>