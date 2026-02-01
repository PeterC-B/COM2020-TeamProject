import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useMainStore = defineStore('main', () => {
    const accessToken = ref<string | null>(null)
    const isAuthenticated = computed(() => Boolean(accessToken.value))

    function setAccessToken(token: string | null) {
        accessToken.value = token
    }

    function clearAccessToken() {
        accessToken.value = null
    }

    return { accessToken, isAuthenticated, setAccessToken, clearAccessToken }
})
