<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchMissions, fetchMission, type Mission } from '@/services/missions'

const missions = ref<Mission[]>([])
const selectedMission = ref<Mission | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function loadMissions() {
    loading.value = true
    error.value = null

    try {
        missions.value = await fetchMissions()
    } catch {
        error.value = 'Failed to load missions'
    } finally {
        loading.value = false
    }
}

async function selectMission(id: string) {
    loading.value = true
    error.value = null

    try {
        selectedMission.value = await fetchMission(id)
    } catch {
        error.value = 'Failed to load mission'
    } finally {
        loading.value = false
    }
}

onMounted(loadMissions)
</script>

<template>
    <section class="mx-auto max-w-4xl p-4">
        <h1 class="mb-4 text-2xl font-semibold">Missions</h1>

        <p v-if="loading" class="text-slate-600">Loading…</p>
        <p v-if="error" class="text-red-600">{{ error }}</p>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <!-- Mission list -->
            <ul class="rounded border border-slate-300 bg-white p-3">
                <li
                    v-for="mission in missions"
                    :key="mission.mission_id"
                    class="cursor-pointer rounded px-3 py-2 hover:bg-slate-100"
                    @click="selectMission(mission.mission_id)"
                >
                    <p class="font-medium">{{ mission.mission_name }}</p>
                    <p class="text-sm text-slate-600">Tier: {{ mission.tier }}</p>
                </li>
            </ul>

            <!-- Mission details -->
            <div
                v-if="selectedMission"
                class="rounded border border-slate-300 bg-white p-4"
            >
                <h2 class="mb-2 text-xl font-semibold">
                    {{ selectedMission.mission_name }}
                </h2>

                <p class="mb-3 text-slate-700">
                    {{ selectedMission.question }}
                </p>

                <h3 class="mb-1 font-medium">Possible answers</h3>
                <ul class="list-disc pl-5 text-slate-700">
                    <li
                        v-for="answer in selectedMission.possible_answers.split(',')"
                        :key="answer"
                    >
                        {{ answer.trim() }}
                    </li>
                </ul>

                <p class="mt-3 text-sm text-slate-600">
                    Tier: {{ selectedMission.tier }}
                </p>
            </div>
        </div>
    </section>
</template>