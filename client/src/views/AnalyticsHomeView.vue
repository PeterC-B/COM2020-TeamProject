<script lang="ts"></script>

<template>
    <section class="mx-auto max-w-5xl p-6 antialiased">
        <div class="mt-10 flex items-center gap-x-2 border-b border-slate-200">

            <router-link
                to="/analytics/route-queries"
                class="px-6 py-3 text-sm font-bold transition-all hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 text-slate-500"
                active-class="text-indigo-600 border-indigo-600 bg-indigo-50/30"
            >
                Route Queries
            </router-link>

            <router-link
                to="/analytics/missions"
                class="px-6 py-3 text-sm font-bold transition-all hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 text-slate-500"
                active-class="text-indigo-600 border-indigo-600 bg-indigo-50/30"
            >
                Mission Progress
            </router-link>

            <router-link
                to="/analytics/leaderboard"
                class="px-6 py-3 text-sm font-bold transition-all hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 text-slate-500"
                active-class="text-indigo-600 border-indigo-600 bg-indigo-50/30"
            >
                Leaderboard
            </router-link>

            <router-link
                to="/analytics/node-analytics"
                class="px-6 py-3 text-sm font-bold transition-all hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 text-slate-500"
                active-class="text-indigo-600 border-indigo-600 bg-indigo-50/30"
            >
                Node Analytics
            </router-link>

            <router-link
                to="/analytics/edge-analytics"
                class="px-6 py-3 text-sm font-bold transition-all hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 text-slate-500"
                active-class="text-indigo-600 border-indigo-600 bg-indigo-50/30"
            >
                Edge Analytics
            </router-link>

        </div>
    </section>
</template>
