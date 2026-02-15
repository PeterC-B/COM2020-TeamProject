import { postPublic, type ApiEnvelope } from '@/services/api'

type LoginResponse = {
    access_token?: string
    role?: string
    username?: string
}

export async function login(username: string, password: string) {
    const response = await postPublic<ApiEnvelope<LoginResponse>>('/user/login', {
        username,
        password,
    })

    console.log('Login response:', response)

    const token = response.data?.data?.access_token

    if (!token) {
        throw new Error('Login response did not include a token')
    }

    return token
}

export async function register(username: string, password: string) {
    const payload = await postPublic<{ data?: { access_token?: string } }>(
        '/user/register',
        { username, password },
    ).then(({ data }) => data)

    const token = payload.data?.access_token

    if (!token) {
        throw new Error('Register response did not include a token')
    }

    return token
}
