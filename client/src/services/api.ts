import axios from 'axios'
import { useMainStore } from '@/stores/main'
import router from '@/router'

const http = axios.create({
    // baseURL: "SET THIS TO THE DEPLOYED BACKEND URL",
    baseURL: 'http://localhost:5000',
})

function getHeaders() {
    const mainStore = useMainStore()
    return mainStore.accessToken
        ? { Authorization: `Bearer ${mainStore.accessToken}` }
        : {}
}

http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            const mainStore = useMainStore()
            mainStore.clearAccessToken()
            void router.push('/')
        }
        return Promise.reject(error)
    },
)

export function get<T = unknown>(
    endpoint: string,
    params: Record<string, unknown> = {},
) {
    return http.get<T>(endpoint, {
        headers: getHeaders(),
        params: params,
    })
}

export function post<T = unknown>(endpoint: string, data: unknown) {
    return http.post<T>(endpoint, data, {
        headers: getHeaders(),
    })
}

export function put<T = unknown>(endpoint: string, data: unknown) {
    return http.put<T>(endpoint, data, {
        headers: getHeaders(),
    })
}
