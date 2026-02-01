import axios, { type AxiosResponse } from 'axios'

const http = axios.create({
    // baseURL: "SET THIS TO THE DEPLOYED BACKEND URL",
    baseURL: 'http://localhost:5000',
})

// This will be used once authentication is in place
// function getHeaders() {
//     return {
//         Authorization: `Bearer ${useMainStore().accessToken}`,
//     }
// }

http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            console.error('Unauthorized! Redirecting to login...')
        }
        return Promise.reject(error)
    },
)

export function get<T = unknown>(
    endpoint: string,
    params: Record<string, unknown> = {},
): Promise<AxiosResponse<T>> {
    return http.get<T>(endpoint, {
        // headers: getHeaders(),
        params: params,
    })
}

export function post<T = unknown>(endpoint: string, data: unknown): Promise<AxiosResponse<T>> {
    return http.post<T>(endpoint, data, {
        // headers: getHeaders(),
    })
}

export function put<T = unknown>(endpoint: string, data: unknown): Promise<AxiosResponse<T>> {
    return http.put<T>(endpoint, data, {
        // headers: getHeaders(),
    })
}
