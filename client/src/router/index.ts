import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

import { pinia } from '@/stores'
import { useMainStore } from '@/stores/main'

const routes: RouteRecordRaw[] = [
    { path: '/login', component: () => import('@/views/LoginView.vue') },
    { path: '/register', component: () => import('@/views/RegisterView.vue') },
    { path: '/', component: () => import('@/views/HomeView.vue'), meta: { requiresAuth: true } },
    { path: '/map', component: () => import('@/views/MapView.vue'), meta: { requiresAuth: true } },
    { path: '/missions', component: () => import('@/views/MissionView.vue'), meta: { requiresAuth: true } },
    { path: '/forgot-password', component: () => import('@/views/ForgotPasswordView.vue') },
    { path: '/leaderboard', component: () => import('@/views/LeaderboardView.vue'), meta: { requiresAuth: true } },
    {
        path: '/profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true },
    },

    {
        path: '/:pathMatch(.*)*',
        component: () => import('@/views/NotFoundView.vue'),
        meta: { requiresAuth: true },
    },
    {
        path: '/analytics/route-queries',
        component: () => import('@/views/RouteQueriesView.vue'),
        meta: { requiresAuth: true, requiresAdmin: true }
    }

]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior() {
        return { top: 0 }
    },
})

router.beforeEach((to) => {
    const mainStore = useMainStore(pinia)

    const publicPages = ['/login', '/register']

    // Redirect authenticated users away from login/register
    if (publicPages.includes(to.path) && mainStore.isAuthenticated) {
        return '/'
    }

    // Require authentication
    if (to.meta.requiresAuth && !mainStore.isAuthenticated) {
        return { path: '/login', query: { redirect: to.fullPath } }
    }

    // Require admin role
    if (to.meta.requiresAdmin && (mainStore.userRole !== 'administrators' && mainStore.userRole !== 'developers')) {
        return '/'
    }

    return true
})

export default router
