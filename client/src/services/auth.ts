import { postPublic } from '@/services/api'

type LoginResponse = {
    access_token?: string
}

export async function login(username: string, password: string) {
    const response = await postPublic<LoginResponse>(
        '/user/login',
        { username, password }
    )

    const token = response.data?.access_token

    if (!token) {
        throw new Error('Login response did not include a token')
    }

    return token
}
