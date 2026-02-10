import { post } from '@/services/api'

type LoginResponse = {
    access_token?: string
    token?: string
    jwt?: string
}

export async function login(username: string, password: string) {
    const data = await post<LoginResponse>('/login', { username, password }).then(({ data }) => data)
    const token = data.access_token ?? data.token ?? data.jwt

    if (!token) {
        throw new Error('Login response did not include a token')
    }

    return token
}
