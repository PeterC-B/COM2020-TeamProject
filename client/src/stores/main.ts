import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useMainStore = defineStore('main', () => {
    const accessToken = ref<string | null>(null)
    const userRole = ref<string | null>(null)
    const username = ref<string | null>(null)
    const password = ref<string | null>(null)
    const email = ref<string | null>(null)
    const user_id = ref<string | null>(null)
    const isAuthenticated = computed(() => Boolean(accessToken.value))

    function setAccessToken(token: string | null) {
        accessToken.value = token
    }

    function clearAccessToken() {
        accessToken.value = null
        userRole.value = null
    }

    function setUserRole(role: string | null) {
        userRole.value = role
    }

    function setUserDetails(user_name: string | null, pass_word: string | null, email_address: string | null, user_ID: string | null){
        username.value = user_name
        password.value = pass_word
        email.value = email_address
        user_id.value = user_ID
    }

    return { accessToken, userRole, isAuthenticated, username, password, email, user_id, setAccessToken, setUserRole, clearAccessToken, setUserDetails}
})
