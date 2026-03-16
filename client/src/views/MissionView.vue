<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
    fetchMissions,
    fetchMission,
    updateMission,
    createMission,
    type Mission,
    deleteMission,
} from '@/services/missions'
import { saveMissionProgress, fetchMissionProgress, type MissionProgress } from '@/services/leaderboard'
import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()

const canEdit = computed(() =>
    mainStore.userRole === 'administrators' ||
    mainStore.userRole === 'developers'
)

const missions = ref<Mission[]>([])
const selectedMission = ref<Mission | null>(null)
const editableMission = ref<Mission | null>(null)

const missionProgress = ref<MissionProgress | null>(null)

const isCreating = ref(false)
const isEditing = ref(false)
const completedMission = ref(false)
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
        tier: 'MEDIUM',
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
        editableMission.value = { ...mission }
        selectedAnswer.value = null
        selectedMission.value = { ...mission }

        try {
            missionProgress.value = await fetchMissionProgress(
                id,
                mainStore.user_id ? mainStore.user_id : 'n/a'
            )
            completedMission.value = true

            // RESTORE SAVED ANSWER
            if (missionProgress.value?.selected_answer) {
                selectedAnswer.value = missionProgress.value.selected_answer
            }

        } catch {
            completedMission.value = false
        }
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

function startEditMission() {
    if (!canEdit.value) {
        error.value = 'You do not have permission to edit missions'
        return
    }

    if (!selectedMission.value) {
        error.value = 'Please select a mission to edit'
        return
    }

    isEditing.value = true
    editableMission.value = { ...selectedMission.value }
}

async function startDeleteMission() {
    if(!canEdit.value){
        error.value = 'You do not have permission to delete missions'
        return
    }

    const mission = selectedMission.value

    if (!mission || !mission.mission_id){
        error.value = 'Please select a mission to delete'
        return
    }

    await deleteMission(mission.mission_id)

    await loadMissions()
    selectedMission.value = null
    editableMission.value = null
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
                  editableMission.value.mission_id!,
                  editableMission.value,
              )

        selectedMission.value = result
        editableMission.value = { ...result }
        isCreating.value = false
        isEditing.value = false
        await loadMissions()
    } catch {
        error.value = isCreating.value
            ? 'Failed to create mission'
            : 'Failed to update mission'
    } finally {
        saving.value = false
    }
}

const selectedAnswer = ref<string | null>(null)

const answerOptions = computed(() => {
    if (!editableMission.value?.possible_answers) return []

    const possible_answers = editableMission.value.possible_answers
        .split(',')
        .map(a => a.trim())
        .filter(Boolean)

    const shuffled = [...possible_answers]

    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        const temp = shuffled[i]!
        shuffled[i] = shuffled[j]!
        shuffled[j] = temp
    }

    return shuffled
})

const tierProxy = computed({
    get() {
        return {
            EASY: "1",
            MEDIUM: "2",
            HARD: "3",
        }[editableMission.value?.tier ?? "EASY"]
    },
    set(value) {
        editableMission.value!.tier = {
            "1": "EASY",
            "2": "MEDIUM",
            "3": "HARD",
        }[value] as any
    },
})

function pickAnswer(answer: string) {
    if (completedMission.value) return
    selectedAnswer.value = answer
    saveProgress()
}

function completedText(correct: boolean){
    if (correct){
        return ", please try another."
    } else {
        return ", contact an admin to try again."
    }
}

async function saveProgress(){
    if (!selectedMission.value || !selectedAnswer.value) return

    const correct =
        selectedAnswer.value === selectedMission.value.answer
    const status = correct ? 'correct' : 'incorrect'
    const progress : MissionProgress = {
        user_id: mainStore.user_id || 'unknown_user',
        mission_id: selectedMission.value.mission_id!,
        status: status,
        score: get_score_from_tier(selectedMission.value.tier),
        selected_answer: selectedAnswer.value,
    }
    try{
        await saveMissionProgress(progress)
    } catch (e) {
        error.value = `Failed to save mission progress: ${e}`
    }
}

function get_score_from_tier(tier: string): number{
    if(tier === "EASY"){
        return 10
    } else if (tier === "MEDIUM"){
        return 20
    } else if (tier === "HARD"){
        return 30
    }
    return 0
}

function capital_case(word: string): string{
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
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
            <div v-if="canEdit" class="flex items-center gap-3">
                <button
                    class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    @click="startCreateMission"
                >
                    <span class="text-lg">+</span> New Mission
                </button>

                <button
                    v-if="selectedMission != null"
                    class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    @click="startEditMission"
                >
                    Edit Mission
                </button>

                <button
                    v-if="selectedMission != null"
                    class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    @click="startDeleteMission"
                >
                    Delete Mission
                </button>
            </div>

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
                            @click="selectMission(mission.mission_id!)"
                        >
                            <p class="font-semibold text-slate-900">
                                {{ mission.mission_name || 'Untitled Mission' }}
                            </p>
                            <span
                                class="mt-1 inline-flex rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600"
                            >
                                Tier: {{ capital_case(mission.tier) }}
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
                                : canEdit && isEditing
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
                                    :disabled="!((canEdit && isEditing) || isCreating)"
                                    class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                                />
                            </div>

                            <div>
                                <label class="mb-1 block text-sm font-semibold text-slate-700">
                                    Tier
                                </label>
                                <select
                                    v-model="tierProxy"
                                    :disabled="!((canEdit && isEditing) || isCreating)"
                                    class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                                >
                                <option value="1">Easy</option>
                                <option value="2">Medium</option>
                                <option value="3">Hard</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Question
                            </label>
                            <textarea
                                v-model="editableMission.question"
                                rows="3"
                                :disabled="!((canEdit && isEditing) || isCreating)"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                            />
                        </div>

                        <div v-if="(canEdit && isEditing) || isCreating">
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Possible Answers
                                <span class="ml-1 text-xs text-slate-400">(comma separated)</span>
                            </label>

                            <textarea
                                v-model="editableMission.possible_answers"
                                rows="2"
                                placeholder="Answer A, Answer B, Answer C"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm"
                            />

                            <p class="mt-1 text-xs text-slate-400">
                                These will be shuffled for travellers.
                            </p>
                        </div>

                        <div v-if="(canEdit && isEditing) || isCreating">
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Correct Answer
                            </label>

                            <input
                                v-model="editableMission.answer"
                                placeholder="Must match one of the possible answers"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm"
                            />
                        </div>


                        <div v-if="(!isEditing && answerOptions.length && !isCreating && !completedMission)">
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

                        <div v-if="completedMission">
                            <p class="mt-3 text-sm font-semibold">
                                You have already completed this mission and got it {{ missionProgress?.status }}{{ completedText(missionProgress?.status === "correct") }}
                            </p>
                        </div>

                        <p
                            v-if="selectedAnswer && !(isCreating || (canEdit && isEditing))"
                            class="mt-3 text-sm font-semibold"
                            :class="
                                selectedAnswer === editableMission.answer
                                    ? 'text-emerald-600'
                                    : 'text-rose-600'
                            "
                        >
                            You selected: <strong>{{ selectedAnswer }}</strong>
                        </p>

                        <div v-if="(selectedAnswer && !(isCreating || (canEdit && isEditing))) || completedMission">
                            <label class="mb-1 block text-sm font-semibold text-slate-700">
                                Correct Answer
                            </label>
                            <input
                                v-model="editableMission.answer"
                                :disabled="(!canEdit || isEditing || !isCreating)"
                                class="w-full rounded-lg border border-slate-200 p-2 text-sm disabled:bg-slate-50"
                            />
                        </div>

                        <div v-if="(canEdit && isEditing) || isCreating" class="pt-4">
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