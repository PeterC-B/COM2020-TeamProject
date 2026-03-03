import { postPublic, put, type ApiEnvelope } from '@/services/api'
import { defineStore } from 'pinia'

type LoginResponse = {
    access_token?: string
    role?: string
    username?: string
    email?: string
    password?: string
}

type RegisterPayload = {
    username: string
    email: string
    password: string
    role?: string
}

type ForgotPasswordResponse = {
    reset: boolean
}

export async function login(username: string, password: string) {
    const response = await postPublic<ApiEnvelope<LoginResponse>>('/user/login', {
        username,
        password,
    })

    console.log("Response: ", response.data.data)

    const token = response.data?.data?.access_token

    if (!token) {
        throw new Error('Login response did not include a token')
    }

    return {token, user_details: response.data?.data}
}

export async function register(payload: RegisterPayload) {
    await postPublic<ApiEnvelope<{ user_id: string }>>(
        '/user/register',
        payload,
    )
}

export async function forgotPassword(username: string, email: string, newPassword: string) {
    const response = await postPublic<ApiEnvelope<ForgotPasswordResponse>>(
        '/user/forgot-password',
        {
            username,
            email,
            new_password: newPassword,
        }
    )

    return response.data.data
}
