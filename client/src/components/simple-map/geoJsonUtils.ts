export type GeoJson = GeoJSON.FeatureCollection
export type coordinates = [number, number]

export function parseFeatureId(value: unknown): number | null {
    if (typeof value === 'number') return Number.isFinite(value) ? value : null
    if (typeof value === 'string') {
        const parsed = Number(value)
        return Number.isFinite(parsed) ? parsed : null
    }
    return null
}

export function assertFeatureCollection(value: unknown, label: string): GeoJson {
    if (!value || typeof value !== 'object') {
        throw new Error(`Invalid ${label} GeoJSON response`)
    }
    const collection = value as GeoJSON.FeatureCollection
    if (!Array.isArray(collection.features)) {
        throw new Error(`Invalid ${label} GeoJSON features`)
    }
    return collection
}

export function parseFeaturePointCoordinates(value: unknown): [number, number] | null {
    if (!value || typeof value !== 'object') return null
    const geometry = (value as { geometry?: GeoJSON.Geometry }).geometry
    if (!geometry || geometry.type !== 'Point') return null
    const coordinates = geometry.coordinates as unknown
    if (!Array.isArray(coordinates) || coordinates.length < 2) return null

    const lng = Number(coordinates[0])
    const lat = Number(coordinates[1])
    if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null
    return [lng, lat]
}
