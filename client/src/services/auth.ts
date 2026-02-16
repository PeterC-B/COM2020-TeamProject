import { postPublic, type ApiEnvelope } from '@/services/api'

import { defineStore } from 'pinia'

type LoginResponse = {
    access_token?: string
    role?: string
    username?: string
}

type RegisterPayload = {
    username: string
    email: string
    password: string
    role?: string
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

export async function register(payload: RegisterPayload) {
    await postPublic<ApiEnvelope<{ user_id: string }>>(
        '/user/register',
        payload,
    )
}

