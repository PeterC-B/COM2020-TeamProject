<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
    open: boolean
    payload: ContextPayload | null
}>()

type ContextPayload =
    | {
        kind: 'node'
        id: number
        name: string
        nodeType: string
        coordinates: [number, number]
        extra?: string
    }
    | {
        kind: 'edge'
        id: number
        is_accessible: boolean
        greenery: number
        lighting: number
        surface_quality: number
    }

const emit = defineEmits<{
    (e: 'close'): void
}>()

function to_text_values(type : string, value : number) : string{
    if(type === 'lighting'){
        if (value === 0.9){
            return "Yes"
        } else {
            return "No"
        }
    } else if (type === 'greenery'){
        if (value === 0.6){
            return "Good"
        } else if (value === 0.5){
            return "Average"
        } else {
            return "Poor"
        }
    } else if (type === 'surface'){
        if (value === 0.9){
            return "Good"
        } else if (value == 1.0){
            return "Average"
        } else {
            return "Poor"
        }
    }
    return ''
}

</script>

<template>
    <div v-if="open && payload" class="relative w-72 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl antialiased animate-in fade-in zoom-in duration-200">

        <header class="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-4 py-2 backdrop-blur-sm">
            <div class="flex items-center gap-2">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    {{ payload.kind === 'node' ? 'Node' : 'Edge' }}
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

        <!-- NODE -->
        <div v-if="payload.kind === 'node'" class="p-5">
            <h3 class="text-lg font-bold text-slate-900 leading -tight">{{ payload.name }}</h3>
            <p class="text-sm leading-relaxed text-slate-600">Type: {{ payload.nodeType }}</p>
            <p v-if="payload.extra" class="text-sm leading-relaxed text-slate-600">Extra: {{ payload.extra }}</p>
            <p class="text-sm leading-relaxed text-slate-600">Coords: {{ payload.coordinates }}</p>
        </div>

        <!-- EDGE -->
        <div v-else class="p-5">
            <p class="text-sm leading-relaxed text-slate-600">Edge ID: {{ payload.id }}</p>
            <p class="text-sm leading-relaxed text-slate-600">Is it accessible?: {{ payload.is_accessible ? "Yes" : "No" }}</p>
            <p class="text-sm leading-relaxed text-slate-600">Proximity to greenery: {{ to_text_values("greenery", payload.greenery) }}</p>
            <p class="text-sm leading-relaxed text-slate-600">Sufficiently lit?: {{ to_text_values("lighting", payload.lighting) }}</p>
            <p class="text-sm leading-relaxed text-slate-600">Surface Quality: {{ to_text_values("surface" ,payload.surface_quality) }}</p>
        </div>

        <!--<div class="p-5">
            <h3 class="text-lg font-bold text-slate-900 leading -tight" v-if="feature._geometry.type === 'Point'">
                {{ get_name(feature) }}
            </h3>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1" v-if="feature._geometry.type === 'Point'">
                <p class="text-sm leading-relaxed text-slate-600">
                    {{ get_type(feature) }}
                </p>
            </div>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1" v-if="feature._geometry.type === 'Point'">
                <p class="text-sm leading-relaxed text-slate-600">
                    {{ get_features(feature) }}
                </p>
            </div>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1" v-if="feature._geometry.type === 'Point'">
                <p class="text-sm leading-relaxed text-slate-600">
                    Coordinates: {{ feature._geometry.coordinates }}
                </p>
            </div>

            <div class="mt-3 max-h-32 overflow-y-auto-pr-1" v-if="feature._geometry.type === 'Linestring'">
                <p class="text-sm leading-relaxed text-slate-600 whitespace-pre-line">
                    {{ get_edge_weights(feature) }}
                </p>
            </div>
        </div>-->

        <div class="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b border-slate-200 bg-white"></div>
    </div>
</template>