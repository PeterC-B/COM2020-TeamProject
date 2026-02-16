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
            : await updateMission(editableMission.value.mission_id, editableMission.value)

        selectedMission.value = result
        editableMission.value = { ...result }
        isCreating.value = false
        await loadMissions()
    } catch {
        error.value = isCreating.value ? 'Failed to create' : 'Failed to update'
    } finally {
        saving.value = false
    }
}

onMounted(loadMissions)
</script>

<template>
    <section class="mx-auto max-w-5xl p-6 antialiased">
        <div class="mb-8 flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold text-slate-900">Missions</h1>
                <p class="text-slate-500">Manage and create quest objectives for travellers.</p>
            </div>
            <button
                v-if="canEdit"
                class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
                @click="startCreateMission"
            >
                <span class="text-lg">+</span> New Mission
            </button>
        </div>

        <div v-if="error" class="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-700 border border-red-200">
            {{ error }}
        </div>

        <div class="grid grid-cols-1 gap-8 md:grid-cols-12">
            <div class="md:col-span-4">
                <div class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
                    <div class="bg-slate-50 px-4 py-3 border-b border-slate-200">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500">Mission List</h3>
                    </div>
                    <ul class="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
                        <li v-if="loading && !missions.length" class="p-8 text-center text-slate-400">
                            <div class="animate-pulse">Loading...</div>
                        </li>
                        <li
                            v-for="mission in missions"
                            :key="mission.mission_id"
                            class="group cursor-pointer p-4 transition-colors hover:bg-indigo-50"
                            :class="{ 'bg-indigo-50 ring-1 ring-inset ring-indigo-500/20': selectedMission?.mission_id === mission.mission_id }"
                            @click="selectMission(mission.mission_id)"
                        >
                            <p class="font-semibold text-slate-900 group-hover:text-indigo-700">
                                {{ mission.mission_name || 'Untitled Mission' }}
                            </p>
                            <div class="mt-1 flex items-center gap-2">
                                <span class="inline-flex items-center rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                                    Tier {{ mission.tier }}
                                </span>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>

            <div class="md:col-span-8">
                <div v-if="editableMission" class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div class="mb-6 flex items-center justify-between border-b border-slate-100 pb-4">
                        <h2 class="text-xl font-bold text-slate-900">
                            {{ isCreating ? 'New Mission' : canEdit ? 'Edit Mission' : 'Mission Details' }}
                        </h2>
                    </div>

                    <div class="space-y-5">
                        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
                            <div class="sm:col-span-1">
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Mission Name</label>
                                <input v-model="editableMission.mission_name" type="text" placeholder="e.g. The Dragon's Lair" class="w-full rounded-lg border border-slate-200 text-sm shadow-sm transition-all
         focus:border-indigo-500 focus:ring-indigo-500
         disabled:bg-slate-50 disabled:text-slate-500" :disabled="!canEdit" />
                            </div>
                            <div class="sm:col-span-1">
                                <label class="block text-sm font-semibold text-slate-700 mb-1">Tier</label>
                                <input v-model="editableMission.tier" type="text" placeholder="e.g. Bronze" class="w-full rounded-lg border border-slate-200 text-sm shadow-sm transition-all
         focus:border-indigo-500 focus:ring-indigo-500
         disabled:bg-slate-50 disabled:text-slate-500" :disabled="!canEdit" />
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-1">Question</label>
                            <textarea v-model="editableMission.question" rows="3" placeholder="What is the mission objective?" class="w-full rounded-lg border border-slate-200 text-sm shadow-sm transition-all
         focus:border-indigo-500 focus:ring-indigo-500
         disabled:bg-slate-50 disabled:text-slate-500" :disabled="!canEdit" />
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-1">Possible Answers</label>
                            <input v-model="editableMission.possible_answers" placeholder="Separate by commas" class="w-full rounded-lg border border-slate-200 text-sm shadow-sm transition-all
         focus:border-indigo-500 focus:ring-indigo-500
         disabled:bg-slate-50 disabled:text-slate-500" :disabled="!canEdit" />
                        </div>

                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-1">Correct Answer</label>
                            <input v-model="editableMission.answer" placeholder="The exact correct response" class="w-full rounded-lg border border-slate-200 text-sm shadow-sm transition-all
         focus:border-indigo-500 focus:ring-indigo-500
         disabled:bg-slate-50 disabled:text-slate-500" :disabled="!canEdit" />
                        </div>

                        <div v-if="canEdit" class="pt-4">
                            <button
                                class="w-full flex justify-center items-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-slate-800 focus:ring-4 focus:ring-slate-200 transition-all disabled:opacity-50"
                                :disabled="saving"
                                @click="saveMission"
                            >
                                <template v-if="saving">
                                    <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                    Saving...
                                </template>
                                <template v-else>
                                    {{ isCreating ? 'Create Mission' : 'Save Changes' }}
                                </template>
                            </button>
                        </div>
                    </div>
                </div>

                <div v-else-if="!loading" class="flex h-64 flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 text-slate-500">
                    <p>Select a mission from the list or create a new one.</p>
                </div>
            </div>
        </div>
    </section>
</template>