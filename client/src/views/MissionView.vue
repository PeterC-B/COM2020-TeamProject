<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
    fetchMissions,
    fetchMission,
    updateMission,
    createMission,
    type Mission,
} from '@/services/missions'

import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()

// Travellers cannot edit or create
const canEdit = computed(() => mainStore.userRole !== 'travellers')

const missions = ref<Mission[]>([])
const selectedMission = ref<Mission | null>(null)
const editableMission = ref<Mission | null>(null)

const isCreating = ref(false)
const loading = ref(false)
const saving = ref(false)
const error = ref<string | null>(null)

function emptyMission(): Mission {
    return {
        mission_id: '',
        mission_name: '',
        question: '',
        possible_answers: '',
        answer: '',
        tier: '',
    }
}

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
    isCreating.value = false
    loading.value = true
    error.value = null

    try {
        const mission = await fetchMission(id)
        selectedMission.value = mission
        editableMission.value = { ...mission }
    } catch {
        error.value = 'Failed to load mission'
    } finally {
        loading.value = false
    }
}

function startCreateMission() {
    if (!canEdit.value) return
    isCreating.value = true
    selectedMission.value = null
    editableMission.value = emptyMission()
}

async function saveMission() {
    if (!editableMission.value || !canEdit.value) return

    saving.value = true
    error.value = null

    try {
        const result = isCreating.value
            ? await createMission(editableMission.value)
            : await updateMission(
                  editableMission.value.mission_id,
                  editableMission.value,
              )

        selectedMission.value = result
        editableMission.value = { ...result }
        isCreating.value = false
        await loadMissions()
    } catch {
        error.value = isCreating.value
            ? 'Failed to create mission'
            : 'Failed to update mission'
    } finally {
        saving.value = false
    }
}

onMounted(loadMissions)
</script>

<template>
    <section class="mx-auto max-w-4xl p-4">
        <h1 class="mb-4 text-2xl font-semibold">Missions</h1>

        <button
            v-if="canEdit"
            class="mb-4 rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
            @click="startCreateMission"
        >
            + New Mission
        </button>

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

            <!-- Editor -->
            <div
                v-if="editableMission"
                class="rounded border border-slate-300 bg-white p-4"
            >
                <h2 class="mb-3 text-xl font-semibold">
                    {{ isCreating ? 'Create Mission' : canEdit ? 'Edit Mission' : 'Mission Details' }}
                </h2>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Mission Name</span>
                    <input v-model="editableMission.mission_name" class="input" />
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Question</span>
                    <textarea v-model="editableMission.question" rows="3" class="input" />
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Possible Answers</span>
                    <input v-model="editableMission.possible_answers" class="input" />
                </label>

                <label class="block mb-2">
                    <span class="text-sm font-medium">Correct Answer</span>
                    <input v-model="editableMission.answer" class="input" />
                </label>

                <label class="block mb-4">
                    <span class="text-sm font-medium">Tier</span>
                    <input v-model="editableMission.tier" class="input" />
                </label>

                <button
                    v-if="canEdit"
                    class="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                    :disabled="saving"
                    @click="saveMission"
                >
                    {{ saving ? 'Saving…' : isCreating ? 'Create Mission' : 'Save Changes' }}
                </button>
            </div>
        </div>
    </section>
</template>