<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue'


const navItems = computed(() => {
    return [
        { label: 'Home', path: '/' },
        { label: 'Map', path: '/map' },
        { label: 'Missions', path: '/missions' },
        { label: 'Profile', path: '/profile' },
        { label: 'Register', path: '/register' },
    ]
})
</script>

<template>
    <div class="min-h-screen">
        <header class="border-b">
            <nav class="mx-auto max-w-5xl px-4 py-3 flex items-center gap-4">
                <div class="font-semibold">COM2020 Team Project</div>

                <div class="flex gap-3">
                    <RouterLink
                        v-for="item in navItems"
                        :key="item.path"
                        :to="item.path"
                        class="text-gray-600 hover:text-blue-500"
                        active-class="text-blue-600 font-semibold"
                        exact-active-class="text-blue-600 font-semibold"
                    >
                        {{ item.label }}
                    </RouterLink>
                </div>
            </nav>
        </header>

        <main class="mx-auto max-w-5xl px-4 py-6">
            <RouterView />
        </main>
    </div>
</template>
