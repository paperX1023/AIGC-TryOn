import axios from 'axios'

interface ApiValidationError {
    msg?: string
}

interface ApiErrorResponse {
    detail?: string | ApiValidationError[]
}

export function getApiErrorMessage(error: unknown, fallback: string) {
    if (!axios.isAxiosError<ApiErrorResponse>(error)) {
        return error instanceof Error && error.message.trim() ? error.message : fallback
    }

    const detail = error.response?.data?.detail

    if (typeof detail === 'string' && detail.trim()) {
        return detail
    }

    if (Array.isArray(detail)) {
        const message = detail
            .map((item) => item.msg)
            .filter(Boolean)
            .join('；')

        return message || fallback
    }

    return fallback
}
