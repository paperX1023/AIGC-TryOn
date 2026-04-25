export interface TryOnResult {
    record_id?: number | null
    person_image_path: string
    person_image_url: string
    cloth_image_path: string
    cloth_image_url: string
    result_image_path: string
    result_image_url: string
    status: string
    message: string
}
