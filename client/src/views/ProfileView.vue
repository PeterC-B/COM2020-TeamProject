<script setup lang="ts">
import { useMainStore } from '@/stores/main'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const mainStore = useMainStore()
const router = useRouter()

const statusLabel = computed(() => (mainStore.isAuthenticated ? 'Logged in' : 'Logged out'))
const roleLabel = computed(() => mainStore.userRole ?? 'guest')

function handleLogin() {
    void router.push('/')
}

function handleLogout() {
    mainStore.clearAccessToken()
}
</script>

<template>
    <section class="grid gap-4">
        <div>
            <h1 class="text-lg font-semibold">Profile</h1>
            <p class="text-sm text-gray-600">Account status and access details.</p>
        </div>

        <div>
            <div class="grid gap-3 sm:grid-cols-2">
                <div class="space-y-1">
                    <div>Status</div>
                    <div>{{ statusLabel }}</div>
                </div>
                <div class="space-y-1">
                    <div>Role</div>
                    <div>{{ roleLabel }}</div>
                </div>
            </div>
        </div>

        <div class="flex flex-wrap gap-3">
            <button
                class="rounded border px-3 py-1.5 text-sm disabled:opacity-60"
                type="button"
                :disabled="mainStore.isAuthenticated"
                @click="handleLogin"
            >
                Login
            </button>
            <button
                class="rounded border px-3 py-1.5 text-sm disabled:opacity-60"
                type="button"
                :disabled="!mainStore.isAuthenticated"
                @click="handleLogout"
            >
                Logout
            </button>
        </div>
    </section>
</template>
