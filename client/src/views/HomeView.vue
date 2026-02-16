<script setup lang="ts"></script>

<template>
    <section class="mx-auto max-w-5xl p-6 antialiased">
        <div class="relative overflow-hidden rounded-3xl bg-slate-900 px-8 py-12 shadow-2xl sm:px-16 sm:py-20">
            <div class="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl"></div>
            <div class="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl"></div>

            <div class="relative z-10 max-w-2xl">
                <h1 class="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
                    Welcome to Healthy Streets
                </h1>
                <p class="mt-6 text-lg leading-8 text-slate-300">
                    Plan safer routes, play a game, and explore accessibility insights across your city. 
                <div class="mt-10 flex items-center gap-x-6">
                    <router-link
                        to="/map"
                        class="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                        Start Exploring
                    </router-link>
                    <router-link to="/missions" class="text-sm font-bold leading-6 text-white hover:text-indigo-400 transition">
                        View Missions <span aria-hidden="true">→</span>
                    </router-link>
                </div>
            </div>
        </div>

        <div class="mt-12 grid gap-8 sm:grid-cols-3">
            <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition hover:shadow-md">
                <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                    </svg>
                </div>
                <h3 class="text-lg font-bold text-slate-900">Safety First</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                    Choose your route based on lighting, surgace quality, and other safety indicators. 

            <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition hover:shadow-md">
                <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <h3 class="text-lg font-bold text-slate-900">Gamified Missions</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                    Compete with friends to complete missions and unlock better paths.
                </p>
            </div>
                </p>
            </div>

            <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm transition hover:shadow-md">
                <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                </div>
                <h3 class="text-lg font-bold text-slate-900">Deep Insights</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                    Use the map to discover safer ways to travel and understand how street features impact accessibility.
            </div>
        </div>

        <div class="mt-16 rounded-3xl bg-slate-50 p-8 sm:p-12">
            <div class="mx-auto max-w-2xl text-center">
                <h2 class="text-2xl font-bold text-slate-900">Ready to transform your commute?</h2>
                <p class="mt-4 text-slate-600 leading-relaxed">
                    By collecting and analyzing street-level data, we're helping cities become more walkable, safer, and more enjoyable.
                </p>
            </div>
        </div>
    </section>
</template>

































