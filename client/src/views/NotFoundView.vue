<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <section>
    <h1 class="text-2xl font-semibold">404</h1>
    <p class="mt-2">That page doesn’t exist.</p>
    <RouterLink class="underline mt-4 inline-block" to="/">Go home</RouterLink>
  </section>
</template>
