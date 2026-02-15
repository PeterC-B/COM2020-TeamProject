import router from '@/router'
import { useMainStore } from '@/stores/main'
import axios from 'axios'

export type ApiEnvelope<T, M = Record<string, unknown>> = {
    data: T
    meta?: M
}

// This will be used to extract the readable error message from API error responses
export class ApiRequestError extends Error {
    status?: number
    code?: string
    details?: unknown

    constructor(message: string, opts: { status?: number; code?: string; details?: unknown } = {}) {
        super(message)
        this.name = 'ApiRequestError'
        this.status = opts.status
        this.code = opts.code
        this.details = opts.details
    }
}

function normalizeApiError(error: unknown): Error {
    if (!axios.isAxiosError(error)) {
        return error instanceof Error ? error : new Error('Unexpected request error')
    }

    const responseData = error.response?.data as
        | {
              error?: { code?: string; message?: string; details?: unknown }
              message?: string
          }
        | undefined

    const message =
        responseData?.error?.message ||
        responseData?.message ||
        error.message ||
        'Request failed with unknown error'

    return new ApiRequestError(message, {
        status: error.response?.status,
        code: responseData?.error?.code,
        details: responseData?.error?.details,
    })
}

const http = axios.create({
    // baseURL: "SET THIS TO THE DEPLOYED BACKEND URL",
    baseURL: 'http://localhost:8000',
    // baseURL: 'https://xxmb1uh225.execute-api.eu-west-2.amazonaws.com/prod',
})

function getHeaders() {
    const mainStore = useMainStore()
    return mainStore.accessToken ? { Authorization: `Bearer ${mainStore.accessToken}` } : {}
}

http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            const mainStore = useMainStore()
            mainStore.clearAccessToken()
            void router.push('/login')
        }
        return Promise.reject(normalizeApiError(error))
    },
)

export function get<T = unknown>(endpoint: string, params: Record<string, unknown> = {}) {
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

export function postPublic<T = unknown>(endpoint: string, data: unknown) {
    return http.post<T>(endpoint, data)
}
