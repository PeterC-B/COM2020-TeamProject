<script setup lang="ts">
defineProps<{
    open: boolean
}>()

const emit = defineEmits<{
    (e: 'close'): void
}>()
</script>

<template>
    <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
    >
        <div class="w-full max-w-md rounded-lg bg-white p-4 shadow-xl">
            <h2 class="text-base font-semibold text-slate-900">Disclaimer</h2>
            <p class="mt-2 text-sm text-slate-700">
                This website is a student project. The route suggestions and safety scores are for <strong>demonstration purposes only</strong>. This is not real-time safety advice.
            </p>
            <div class="mt-4 flex justify-end">
                <button
                    type="button"
                    class="rounded bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700"
                    @click="emit('close')"
                >
                    I Understand
                </button>
            </div>
        </div>
    </div>
</template>
