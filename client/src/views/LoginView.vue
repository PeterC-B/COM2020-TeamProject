<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { login } from '@/services/auth'
import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref<string | null>(null)
const isLoading = ref(false)

// Check that there is a username and password input
const canSubmit = computed(
    () => username.value.trim().length > 0 && password.value.trim().length > 0 && !isLoading.value,
)

// Send the request to the server and handle the response
async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'Please enter both username and password'
        return
    }
    error.value = null
    isLoading.value = true

    try {
        const token = await login(username.value.trim(), password.value)
        mainStore.setAccessToken(token)
        mainStore.setUserRole('user')

        const redirectPath = typeof route.query.redirect === 'string' ? route.query.redirect : '/map'
        await router.push(redirectPath)
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Invalid credentials. Please try again.'
    } finally {
        isLoading.value = false
    }
}
</script>

<template>
    <div class="flex min-h-[80vh] items-center justify-center px-4 antialiased">
        <section class="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div class="h-2 bg-indigo-600"></div>
            
            <div class="p-8">
                <header class="mb-8 text-center">
                    <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Welcome Back</h1>
                    <p class="mt-2 text-sm text-slate-500">Sign in to your account to continue.</p>
                </header>

                <form class="space-y-5" @submit.prevent="handleSubmit">
                    <div class="space-y-1">
                        <label for="username" class="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Username
                        </label>
                        <input
                            id="username"
                            v-model="username"
                            type="text"
                            autocomplete="username"
                            placeholder="username"
                            class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;"
                        />
                    </div>

                    <div class="space-y-1">
                        <div class="flex items-center justify-between">
                            <label for="password" class="text-xs font-bold uppercase tracking-wider text-slate-500">
                                Password
                            </label>
                        </div>
                        <input
                            id="password"
                            v-model="password"
                            type="password"
                            autocomplete="current-password"
                            placeholder="••••••••"
                            class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;"
                        />
                    </div>

                    <div v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100 flex items-center gap-2">
                        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                        {{ error }}
                    </div>

                    <button
                        type="submit"
                        class="group relative flex w-full items-center justify-center rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="!canSubmit"
                    >
                        <span v-if="isLoading" class="flex items-center gap-2">
                            <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Signing in...
                        </span>
                        <span v-else>Login to Dashboard</span>
                    </button>
                </form>

                <footer class="mt-8 text-center">
                    <p class="text-xs text-slate-400 italic">
                        By logging in, you agree to our terms and conditions.
                    </p>
                </footer>
            </div>
        </section>
    </div>
</template>