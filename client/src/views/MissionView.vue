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

// Single source of truth
const canEdit = computed(() =>
    mainStore.userRole === 'ADMIN' ||
    mainStore.userRole === 'STAFF'
)

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
        selectedAnswer.value = null
    } catch {
        error.value = 'Failed to load mission'
    } finally {
        loading.value = false
    }
}

function startCreateMission() {
    if (!canEdit.value) {
        error.value = 'You do not have permission to create missions'
        return
    }

    isCreating.value = true
    selectedMission.value = null
    editableMission.value = emptyMission()
}

async function saveMission() {
    if (!canEdit.value) {
        error.value = 'You do not have permission to modify missions'
        return
    }

    if (!editableMission.value) return

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

// User-selected answer (for travellers)
const selectedAnswer = ref<string | null>(null)

// Split possible answers safely
const answerOptions = computed(() => {
    if (!editableMission.value?.possible_answers) return []

    return editableMission.value.possible_answers
        .split(',')
        .map(a => a.trim())
        .filter(Boolean)
})

// Handle answer selection
function pickAnswer(answer: string) {
    selectedAnswer.value = answer
}

onMounted(loadMissions)
</script>


<template>
    <section class="mx-auto max-w-5xl p-6 antialiased">
        <!-- Header -->
        <div class="mb-8 flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-slate-900">Missions</h1>
                <p class="text-slate-500">
                    Manage and create quest objectives for travellers.
                </p>
            </div>

            <!-- Create button (admins/staff only) -->
            <button
                v-if="canEdit"
                class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                @click="startCreateMission"
            >
                <span class="text-lg">+</span> New Mission
            </button>
        </div>

        <!-- Error -->
        <div
            v-if="error"
            class="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
            {{ error }}
        </div>

        <div class="grid grid-cols-1 gap-8 md:grid-cols-12">
            <!-- Mission list -->
            <div class="md:col-span-4">
                <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                    <div class="border-b border-slate-200 bg-slate-50 px-4 py-3">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Mission List
                        </h3>
                    </div>

                    <ul class="max-h-[600px] divide-y divide-slate-100 overflow-y-auto">
                        <li
                            v-if="loading && !missions.length"
                            class="p-8 text-center text-slate-400"
                        >
                            Loading…
                        </li>

                        <li
                            v-for="mission in missions"
                            :key="mission.mission_id"
                            class="cursor-pointer p-4 transition hover:bg-indigo-50"
                            :class="{
                                'bg-indigo-50 ring-1 ring-inset ring-indigo-500/20':
                                    selectedMission?.mission_id === mission.mission_id,
                            }"
                            @click="selectMission(mission.mission_id)"
                        >
                            <p class="font-semibold text-slate-900">
                                {{ mission.mission_name || 'Untitled Mission' }}
                            </p>
                            <span
                                class="mt-1 inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600"
                            >
                                Tier {{ mission.tier }}
                            </span>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Mission editor / viewer -->
            <div class="md:col-span-8">
                <div
                    v-if="editableMission"
                    class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                    <div class="mb-6 border-b border-slate-100 pb-4">
                        <h2 class="text-xl font-bold text-slate-900">
                            {{ isCreating
                                ? 'New Mission'
                                : canEdit
                                ? 'Edit Mission'
                                : 'Mission Details' }}
                        </h2>
                    </div>

                    <div class="space-y-5">
                        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
                            <div>
                                <label class="mb-1 block text-sm font-semibold text-slate-700">
                                    Mission Name
                                </label>
                                <input
                                    v-model="editableMission.mission_name"
                                    :disabled="!canEdit"
                                    class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                                />
                            </div>

                            <div>
                                <label class="mb-1 block text-sm font-semibold text-slate-700">
                                    Tier
                                </label>
                                <input
                                    v-model="editableMission.tier"
                                    :disabled="!canEdit"
                                    class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                                />
                            </div>
                        </div>

                        <div>
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Question
                            </label>
                            <textarea
                                v-model="editableMission.question"
                                rows="3"
                                :disabled="!canEdit"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                            />
                        </div>

                        <!-- Traveller Answer Selection -->
                        <div v-if="!canEdit && answerOptions.length">
                            <label class="mb-2 block text-sm font-semibold text-slate-700">
                                Choose your answer
                            </label>

                            <div class="grid gap-3 sm:grid-cols-2">
                                <button
                                    v-for="answer in answerOptions"
                                    :disabled="selectedAnswer != null"
                                    :key="answer"
                                    @click="pickAnswer(answer)"
                                    class="rounded-lg border px-4 py-2 text-sm font-medium transition"
                                    :class="selectedAnswer === answer
                                        ? 'border-indigo-600 bg-indigo-600 text-white'
                                        : 'border-slate-200 bg-white hover:bg-slate-50'"
                                >
                                    {{ answer }}
                                </button>
                            </div>
                        </div>

                        <p
                            v-if="selectedAnswer"
                            class="mt-3 text-sm font-semibold"
                            :class="
                                selectedAnswer === editableMission.answer
                                    ? 'text-emerald-600'
                                    : 'text-rose-600'
                            "
                        >
                            You selected: <strong>{{ selectedAnswer }}</strong>
                        </p>

                        <div v-if="selectedAnswer">
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Correct Answer
                            </label>
                            <input
                                v-model="editableMission.answer"
                                :disabled="!canEdit"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                            />
                        </div>

                        <!-- Save button -->
                        <div v-if="canEdit" class="pt-4">
                            <button
                                class="w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50"
                                :disabled="saving"
                                @click="saveMission"
                            >
                                {{ saving
                                    ? 'Saving…'
                                    : isCreating
                                    ? 'Create Mission'
                                    : 'Save Changes' }}
                            </button>
                        </div>
                    </div>
                </div>

                <div
                    v-else-if="!loading"
                    class="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 text-slate-500"
                >
                    Select a mission from the list or create a new one.
                </div>
            </div>
        </div>
    </section>
</template>