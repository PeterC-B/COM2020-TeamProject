<script setup lang="ts">
import { useMainStore } from '@/stores/main'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const mainStore = useMainStore()
const router = useRouter()

const statusLabel = computed(() => (mainStore.isAuthenticated ? 'Authenticated' : 'Guest Mode'))
const roleLabel = computed(() => mainStore.userRole ?? 'guest')
const username = computed(() => (mainStore.username))
const email = computed(() => (mainStore.email))
const user_id = computed(() => (mainStore.user_id))

const seeID = computed(() =>
    mainStore.userRole === 'developers'
)

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
                        <span class="text-xs font-semibold text-slate-700 capitalize">{{ roleLabel }}</span>
                    </div>
                </div>

                <button
                    v-if="!mainStore.isAuthenticated"
                    @click="handleLogin"
                    class="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2 text-sm font-bold text-white shadow-md transition-all hover:bg-slate-800 active:scale-95"
                >
                    Sign In
                </button>
                <button
                    v-else
                    @click="handleLogout"
                    class="group inline-flex items-center gap-2 rounded-lg  border border-slate-200 bg-white px-5 py-2 text-sm font-bold text-slate-700 shadow-sm transition-all hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600 active:scale-95"
                >
                    <span>Sign Out</span>
                    <svg class="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7" />
                    </svg>
                </button>
            </div>
        </div>
    </nav>

    <main class="mx-auto max-w-4xl px-4 py-12 antialiased sm:px-6 lg:px-8">
        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div class="border-b border-slate-100 bg-slate-50/50 px-6 py-8">
                <h1 class="text-2xl font-bold text-slate-900 tracking-tight">User Profile</h1>
                <p class="mt-1 text-sm text-slate-500">Personal Information and Account Settings</p>
            </div>

            <div class="divide-y divide-slate-100">
                <div class="grid grid-cols-1 px-6 py-6 sm:grid-cols-3 sm:gap-4" v-if="seeID">
                    <dt class="text-sm font-bold uppercase tracking-wider text-slate-400">User ID (developers only)</dt>
                    <dd class="mt-1 text-sm font-semibold text-slate-900 sm:col-span-2 sm:mt-0">
                        {{ user_id || 'N/A' }}
                    </dd>
                </div>
                <div class="grid grid-cols-1 px-6 py-6 sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-bold uppercase tracking-wider text-slate-400">Username</dt>
                    <dd class="mt-1 text-sm font-semibold text-slate-900 sm:col-span-2 sm:mt-0">
                        {{ username || 'N/A' }}
                    </dd>
                </div>

                <div class="grid grid-cols-1 px-6 py-6 sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-bold uppercase tracking-wider text-slate-400">Email Address</dt>
                    <dd class="mt-1 text-sm font-semibold text-slate-900 sm:col-span-2 sm:mt-0">
                        {{ email || 'N/A' }}
                    </dd>
                </div>

                <div class="grid grid-cols-1 px-6 py-6 sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-bold uppercase tracking-wider text-slate-400">Account Type</dt>
                    <dd class="mt-1 text-sm sm:col-span-2 sm:mt-0">
                        <span class="inline-flex items-center rounded-md bg-indigo-50 px-2 py-1 text-xs font-bold text-indigo-700 ring-1 ring-inset ring-indigo-700/10 capitalize">
                            {{ roleLabel }}
                        </span>
                    </dd>
                </div>

                <div class="grid grid-cols-1 px-6 py-6 sm:grid-cols-3 sm:gap-4">
                    <dt class="text-sm font-bold uppercase tracking-wider text-slate-400">Password</dt>
                    <dd class="mt-1 flex items-center gap-2 text-sm font-semibold text-slate-900 sm:col-span-2 sm:mt-0">
                        <span>••••••••••••</span>
                        <button class="text-[10px] font-bold uppercase tracking-tighter text-indigo-600 hover:text-indigo-500 underline decoration-indigo-200 underline-offset-4">
                            Change
                        </button>
                    </dd>
                </div>
            </div>

            <div class="bg-slate-50/50 px-6 py-4 border-t border-slate-100">
                <p class="text-[11px] text-slate-400 italic">
                    To update your profile information, please contact the administrator
                </p>
            </div>
        </div>
    </main>
</template>