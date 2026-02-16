To wrap up your site's transformation, we’ll give the Registration page the same premium treatment as the Login page.

The main addition here is styling the select dropdown and the Success State, ensuring that when a user registers, they get a satisfying visual confirmation before being redirected.

Code snippet
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { register } from '@/services/auth'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const role = ref<'travellers' | 'administrators' | 'developers'>('travellers')

const error = ref<string | null>(null)
const success = ref(false)
const isLoading = ref(false)

const canSubmit = computed(
    () =>
        username.value.trim().length > 0 &&
        email.value.trim().length > 0 &&
        password.value.trim().length > 0 &&
        !isLoading.value,
)

async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'All fields are required'
        return
    }

    error.value = null
    success.value = false
    isLoading.value = true

    try {
        await register({
            username: username.value.trim(),
            email: email.value.trim(),
            password: password.value,
            role: role.value,
        })

        success.value = true

        setTimeout(() => {
            router.push('/login')
        }, 1200)
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Registration failed'
    } finally {
        isLoading.value = false
    }
}
</script>

<template>
    <div class="flex min-h-[85vh] items-center justify-center px-4 py-12 antialiased">
        <section class="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div class="h-2 bg-indigo-600 transition-all duration-500" :class="{ 'bg-emerald-500': success }"></div>
            
            <div class="p-8">
                <header class="mb-8 text-center">
                    <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Create Account</h1>
                    <p class="mt-2 text-sm text-slate-500">Join Healthy Streets and start exploring.</p>
                </header>

                <form v-if="!success" class="space-y-5" @submit.prevent="handleSubmit">
                    <div class="space-y-1">
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Username</label>
                        <input
                            v-model="username"
                            type="text"
                            autocomplete="username"
                            placeholder="Choose a display name"
                            class="input-field"
                        />
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Email Address</label>
                        <input
                            v-model="email"
                            type="email"
                            autocomplete="email"
                            placeholder="name@example.com"
                            class="input-field"
                        />
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Password</label>
                        <input
                            v-model="password"
                            type="password"
                            autocomplete="new-password"
                            placeholder="••••••••"
                            class="input-field"
                        />
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Account Type</label>
                        <div class="relative">
                            <select v-model="role" class="input-field appearance-none pr-10">
                                <option value="travellers">Traveller</option>
                                <option value="administrators">Administrator</option>
                                <option value="developers">Developer</option>
                            </select>
                            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
                                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                            </div>
                        </div>
                    </div>

                    <div v-if="error" class="flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-600">
                        <svg class="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
                        {{ error }}
                    </div>

                    <button
                        type="submit"
                        class="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg transition-all hover:bg-slate-800 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="!canSubmit"
                    >
                        <svg v-if="isLoading" class="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        {{ isLoading ? 'Creating account...' : 'Create Account' }}
                    </button>
                </form>

                <div v-else class="flex flex-col items-center py-8 text-center animate-in fade-in zoom-in duration-300">
                    <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                        <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                    </div>
                    <h2 class="text-2xl font-bold text-slate-900">Success!</h2>
                    <p class="mt-2 text-slate-500">Your account is ready. Taking you to login...</p>
                </div>

                <footer class="mt-8 border-t border-slate-100 pt-6 text-center">
                    <p class="text-sm text-slate-500">
                        Already have an account? 
                        <router-link to="/login" class="font-bold text-indigo-600 hover:text-indigo-500">Log in</router-link>
                    </p>
                </footer>
            </div>
        </section>
    </div>
</template>































<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { register } from '@/services/auth'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const role = ref<'travellers' | 'administrators' | 'developers'>('travellers')

const error = ref<string | null>(null)
const success = ref(false)

const canSubmit = computed(
    () =>
        username.value.trim().length > 0 &&
        email.value.trim().length > 0 &&
        password.value.trim().length > 0,
)

async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'All fields are required'
        return
    }

    error.value = null
    success.value = false

    try {
        await register({
            username: username.value.trim(),
            email: email.value.trim(),
            password: password.value,
            role: role.value,
        })

        success.value = true

        setTimeout(() => {
            router.push('/login')
        }, 800)
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Registration failed'
    }
}
</script>

<template>
    <section class="mx-auto max-w-md rounded border border-slate-300 bg-white p-4">
        <h1 class="text-xl font-semibold">Register</h1>
        <p class="mt-1 text-sm text-slate-600">Create an account to get started.</p>

        <form class="mt-4 grid gap-3" @submit.prevent="handleSubmit">
            <label class="grid gap-1 text-sm">
                <span>Username</span>
                <input
                    v-model="username"
                    type="text"
                    autocomplete="username"
                    class="rounded border border-slate-300 px-3 py-2"
                />
            </label>

            <label class="grid gap-1 text-sm">
                <span>Email</span>
                <input
                    v-model="email"
                    type="email"
                    autocomplete="email"
                    class="rounded border border-slate-300 px-3 py-2"
                />
            </label>

            <label class="grid gap-1 text-sm">
                <span>Password</span>
                <input
                    v-model="password"
                    type="password"
                    autocomplete="new-password"
                    class="rounded border border-slate-300 px-3 py-2"
                />
            </label>

            <label class="grid gap-1 text-sm">
                <span>Role</span>
                <select
                    v-model="role"
                    class="rounded border border-slate-300 px-3 py-2"
                >
                    <option value="travellers">Traveller</option>
                    <option value="administrators">Administrator</option>
                    <option value="developers">Developer</option>
                </select>
            </label>

            <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
            <p v-if="success" class="text-sm text-green-600">
                Account created! Redirecting to login…
            </p>

            <button
                type="submit"
                class="rounded bg-slate-900 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="!canSubmit"
            >
                Register
            </button>
        </form>
    </section>
</template>
