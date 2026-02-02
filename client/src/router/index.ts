import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
    { path: '/', component: () => import('@/views/HomeView.vue') },
    { path: '/map', component: () => import('@/views/MapView.vue') },
    { path: '/profile', component: () => import('@/views/ProfileView.vue') },

    { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFoundView.vue') },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior() {
        return { top: 0 }
    },
})

export default router
