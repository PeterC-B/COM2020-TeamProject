export const serializeCsvField = (value: unknown) => {
    if (value === null || value === undefined) {
        return ''
    }

    const text = typeof value === 'string' ? value : JSON.stringify(value)
    return `"${text.replace(/"/g, '""')}"`
}

export const buildCsvContent = (headers: string[], rows: unknown[][]) => {
    const serializedRows = rows.map((row) => row.map(serializeCsvField).join(','))
    return [headers.join(','), ...serializedRows].join('\r\n')
}

export const downloadCsv = (content: string, fileName: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
}
