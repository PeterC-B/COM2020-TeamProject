<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { register } from '@/services/auth'
import { useMainStore } from '@/stores/main'

const mainStore = useMainStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref<string | null>(null)

// Basic input check
const canSubmit = computed(
    () => username.value.trim().length > 0 && password.value.trim().length > 0,
)

async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'Enter username and password'
        return
    }

    error.value = null

    try {
        await register(username.value.trim(), password.value)

        // After successful registration, go to login
        await router.push({
            path: '/login',
            query: { registered: 'true' },
        })
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
                <span>Password</span>
                <input
                    v-model="password"
                    type="password"
                    autocomplete="new-password"
                    class="rounded border border-slate-300 px-3 py-2"
                />
            </label>

            <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

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
