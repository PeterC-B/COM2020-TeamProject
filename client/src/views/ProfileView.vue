<script setup lang="ts">
import { useMainStore } from '@/stores/main'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const mainStore = useMainStore()
const router = useRouter()

const statusLabel = computed(() => (mainStore.isAuthenticated ? 'Authenticated' : 'Guest Mode'))
const roleLabel = computed(() => mainStore.userRole ?? 'guest')

function handleLogin() {
    void router.push('/login')
}

function handleLogout() {
    mainStore.clearAccessToken()
    void router.push('/login')
}
</script>

<template>
    <nav class="sticky top-0 z-50 w-full border-b border-slate-200 bg-white/80 backdrop-blur-md">
        <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
            
            <div class="flex items-center gap-2 cursor-pointer" @click="router.push('/')">
                <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 shadow-indigo-200 shadow-lg">
                    <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                </div>
                <span class="text-lg font-bold tracking-tight text-slate-900 hidden sm:block">
                    Healthy<span class="text-indigo-600">Streets</span>
                </span>
            </div>

            <div class="flex items-center gap-4">
                
                <div class="hidden items-center gap-3 md:flex">
                    <div class="flex flex-col items-end leading-none">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Status</span>
                        <span class="text-xs font-semibold" :class="mainStore.isAuthenticated ? 'text-emerald-600' : 'text-slate-500'">
                            {{ statusLabel }}
                        </span>
                    </div>
                    
                    <div class="h-8 w-[1px] bg-slate-200"></div>

                    <div class="flex flex-col items-end leading-none">
                        <span class="text-[10px] font-bold uppercase tracking-widest text-slate-400">Role</span>
                        <span class="text-xs font-semibold text-slate-700 capitalize">
                            {{ roleLabel }}
                        </span>
                    </div>
                </div>

                <button
                    v-if="!mainStore.isAuthenticated"
                    @click="handleLogin"
                    class="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2 text-sm font-bold text-white transition-all hover:bg-slate-800 active:scale-95 shadow-md"
                >
                    Sign In
                </button>

                <button
                    v-else
                    @click="handleLogout"
                    class="group inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-5 py-2 text-sm font-bold text-slate-700 transition-all hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600 active:scale-95 shadow-sm"
                >
                    <span>Sign Out</span>
                    <svg class="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7" />
                    </svg>
                </button>
            </div>
        </div>
    </nav>
</template>