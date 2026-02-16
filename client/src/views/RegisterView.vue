<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { register } from '@/services/auth'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref<string | null>(null)
const success = ref(false)

const canSubmit = computed(
    () => username.value.trim().length > 0 && password.value.trim().length > 0,
)

async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'Enter username and password'
        return
    }

    error.value = null
    success.value = false

    try {
        await register(username.value.trim(), password.value)
        success.value = true

        // Small delay so the user sees success feedback
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
                <span>Password</span>
                <input
                    v-model="password"
                    type="password"
                    autocomplete="new-password"
                    class="rounded border border-slate-300 px-3 py-2"
                />
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