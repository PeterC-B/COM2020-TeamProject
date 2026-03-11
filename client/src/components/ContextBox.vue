<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
    open: boolean
    node: any
}>()

const emit = defineEmits<{
    (e: 'close'): void
}>()

function to_text(text:string): string{
    return text.replace(/_/g, ' ')
}

function capital_case(word: string): string{
    const lower = word.toLowerCase()
    return lower.charAt(0).toUpperCase() + lower.slice(1)
}

function get_name(node:any): string{
    if(node.properties.name === 'NaN'){
        return capital_case(to_text(node.properties.type))
    }
    return node.properties.name
}

function get_type(node:any): string{
    if(node.properties.name !== 'NaN'){
        return capital_case(to_text(node.properties.type))
    }
    return ''
}

function get_features(node:any): string{
    if(node.properties.highway !== "NaN"){
        return "Extra Feature: " + capital_case(to_text(node.properties.highway))
    }
    return ''
}
</script>

<template>
    <div v-if="open"
        class = "relative w-72 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl antialiased animate-in fade-in zoom-in duration-200">

        <header class="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-4 py-2 backdrop-blur-sm">
            <div class="flex items-center gap-2">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    node
                </span>
                <div class="h-2 w-2 rounded-full bg-indigo-500"></div>
            </div>

            <button
                @click="emit('close')"
                class="text-xl text-slate-400 hover:text-slate-600 transition-colors leading-none"
            >  
                &times;
            </button>
        </header>

        <div class="p-5">
            <h3 class="text-lg font-bold text-slate-900 leading -tight">
                {{ get_name(node) }}
            </h3>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1">
                <p class="text-sm leading-relaxed text-slate-600">
                    {{ get_type(node) }}
                </p>
            </div>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1">
                <p class="text-sm leading-relaxed text-slate-600">
                    {{ get_features(node) }}
                </p>
            </div>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1">
                <p class="text-sm leading-relaxed text-slate-600">
                    Coordinates: {{ node._geometry.coordinates }}
                </p>
            </div>
        </div>

        <div class="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b border-slate-200 bg-white"></div>
    </div>
</template>
