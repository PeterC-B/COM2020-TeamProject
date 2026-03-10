<script setup lang="ts">
import { ref } from 'vue'

const isVisible = ref(true)

/* backend data stuff */

/* mock data to check if it looks okay */
const mockData = {
    name: "high street",
    type: "road segment",
    description: "nice piece of road"
}
</script>

<template>
    <div v-if="isVisible"
        class = "relative w-72 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl antialiased animate-in fade-in zoom-in duration-200">

        <header class="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-4 py-2 backdrop-blur-sm">
            <div class="flex items-center gap-2">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    {{ mockData.type }}
                </span>
                <div class="h-2 w-2 rounded-full bg-indigo-500"></div>
            </div>

            <button
                @click="isVisible = false"
                class="text-xl text-slate-400 hover:text-slate-600 transition-colors leading-none"
            >
                &times;
            </button>
        </header>

        <div class="p-5">
            <h3 class="text-lg font-bold text-slate-900 leading -tight">
                {{ mockData.name }}
            </h3>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1">
                <p class="text-sm leading-relaxed text-slate-600">
                    {{ mockData.description }}
                </p>
            </div>
        </div>

        <div class="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b border-slate-200 bg-white"></div>
    </div>
</template>
