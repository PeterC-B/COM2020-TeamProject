<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
    fetchMissions,
    fetchMission,
    updateMission,
    type Mission,
} from '@/services/missions'

import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()

// Travellers cannot edit
const canEdit = computed(() => mainStore.userRole !== 'travellers')

const missions = ref<Mission[]>([])
const selectedMission = ref<Mission | null>(null)
const editableMission = ref<Mission | null>(null)

const loading = ref(false)
const error = ref<string | null>(null)
const saving = ref(false)

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
        const mission = await fetchMission(id)
        selectedMission.value = mission
        editableMission.value = { ...mission } // clone for editing
    } catch {
        error.value = 'Failed to load mission'
    } finally {
        loading.value = false
    }
}

async function saveMission() {
    if (!editableMission.value) return

    // Permission guard
    if (!canEdit.value) {
        error.value = 'You do not have permission to edit missions'
        return
    }

    saving.value = true
    error.value = null

    try {
        const updated = await updateMission(
            editableMission.value.mission_id,
            editableMission.value,
        )

        selectedMission.value = updated
        editableMission.value = { ...updated }
        await loadMissions()
    } catch {
        error.value = 'Failed to update mission'
    } finally {
        saving.value = false
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
                v-if="editableMission"
                class="rounded border border-slate-300 bg-white p-4"
            >
                <h2 class="mb-3 text-xl font-semibold">
                    {{ canEdit ? 'Edit Mission' : 'Mission Details' }}
                </h2>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Mission Name</span>
                    <input
                        v-model="editableMission.mission_name"
                        :disabled="!canEdit"
                        class="mt-1 w-full rounded border p-2 disabled:bg-slate-100"
                    />
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Question</span>
                    <textarea
                        v-model="editableMission.question"
                        :disabled="!canEdit"
                        class="mt-1 w-full rounded border p-2 disabled:bg-slate-100"
                        rows="3"
                    ></textarea>
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">
                        Possible Answers (comma-separated)
                    </span>
                    <input
                        v-model="editableMission.possible_answers"
                        :disabled="!canEdit"
                        class="mt-1 w-full rounded border p-2 disabled:bg-slate-100"
                    />
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Correct Answer</span>
                    <input
                        v-model="editableMission.answer"
                        :disabled="!canEdit"
                        class="mt-1 w-full rounded border p-2 disabled:bg-slate-100"
                    />
                </label>

                <label class="block mb-4">
                    <span class="text-sm font-medium">Tier</span>
                    <input
                        v-model="editableMission.tier"
                        :disabled="!canEdit"
                        class="mt-1 w-full rounded border p-2 disabled:bg-slate-100"
                    />
                </label>

                <button
                    v-if="canEdit"
                    class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                    :disabled="saving"
                    @click="saveMission"
                >
                    {{ saving ? 'Saving…' : 'Save Changes' }}
                </button>

                <p v-else class="text-sm text-slate-500 italic">
                    Travellers cannot edit missions.
                </p>
            </div>
        </div>
    </section>
</template>
