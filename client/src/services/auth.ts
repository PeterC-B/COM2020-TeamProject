import { post } from '@/services/api'

type LoginResponse = {
    access_token?: string
}

export async function login(username: string, password: string) {
    const payload = await post<{ data?: LoginResponse }>('/user/login', { username, password }).then(
        ({ data }) => data,
    )
    const token = payload.data?.access_token

    if (!token) {
        throw new Error('Login response did not include a token')
    }

    return token
}
