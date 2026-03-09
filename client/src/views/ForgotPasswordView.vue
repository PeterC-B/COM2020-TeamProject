<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { forgotPassword } from '@/services/auth'
import { useMainStore } from '@/stores/main'

const router = useRouter()

const username = ref('')
const email = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref<string | null>(null)
const success = ref(false)
const isLoading = ref(false)

const canSubmit = computed(() =>
    username.value.trim().length > 0 &&
    email.value.trim().length > 0 &&
    newPassword.value.trim().length > 0 &&
    confirmPassword.value.trim().length > 0 &&
    newPassword.value === confirmPassword.value &&
    !isLoading.value
)

const mainStore = useMainStore()

async function handleSubmit() {
    if (!canSubmit.value) {
        error.value = 'Please fill out all fields correctly.'
        return
    }

    error.value = null
    isLoading.value = true

    try {
        await forgotPassword(username.value.trim(), email.value.trim(), newPassword.value)
        success.value = true
        mainStore.clearAccessToken()
        router.push("/login")
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Unable to reset password.'
    } finally {
        isLoading.value = false
    }
}
</script>

<template>
    <div class="flex min-h-[80vh] items-center justify-center px-4 antialiased">
        <section class="w-full max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
            <div class="h-2 bg-indigo-600"></div>

            <div class="p-8 pb-6">
                <header class="mb-8 text-center">
                    <h1 class="text-3xl font-bold text-slate-900 tracking-tight">Reset Password</h1>
                    <p class="mt-2 text-sm text-slate-500">Enter your details to reset your password.</p>
                </header>

                <form class="space-y-5" @submit.prevent="handleSubmit" v-if="!success">
                    <div>
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Username</label>
                        <input v-model="username" type="text" class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;" placeholder="Enter username" />
                    </div>

                    <div>
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Email</label>
                        <input v-model="email" type="email" class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;" placeholder="Enter email" />
                    </div>

                    <div>
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">New Password</label>
                        <input v-model="newPassword" type="password" class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;" placeholder="New password" />
                    </div>

                    <div>
                        <label class="text-xs font-bold uppercase tracking-wider text-slate-500">Confirm Password</label>
                        <input v-model="confirmPassword" type="password" class="block w-full rounded-xl border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 outline-none;" placeholder="Confirm password" />
                    </div>

                    <div v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-100;">{{ error }}</div>

                    <button type="submit" class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg hover:bg-slate-800 transition-all;" :disabled="!canSubmit">
                        <span v-if="isLoading">Resetting...</span>
                        <span v-else>Reset Password</span>
                    </button>
                </form>

                <div v-else class="text-center space-y-4">
                    <p class="text-green-600 font-semibold">Your password has been reset successfully.</p>
                    <router-link to="/login" class="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white shadow-lg hover:bg-slate-800 transition-all block text-center">Return to Login</router-link>
                </div>
            </div>
        </section>
    </div>
</template>