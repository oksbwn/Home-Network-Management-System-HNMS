/**
 * Formats a date string to the user's local equivalent.
 * Handles ISO strings properly.
 * Space-separated strings (SQL style) are treated as local time unless they contain explicit timezone info.
 * @param {string} timestamp 
 * @returns {string} Formatted local date string
 */
export const formatDate = (timestamp) => {
    if (!timestamp) return 'Never'
    
    let dateStr = timestamp
    // Handle SQL style "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SS"
    // We DO NOT append 'Z' here because the backend might be sending local time.
    if (typeof dateStr === 'string' && dateStr.includes(' ')) {
        dateStr = dateStr.replace(' ', 'T')
    }
    
    try {
        const date = new Date(dateStr)
        // Check for invalid date
        if (isNaN(date.getTime())) return timestamp

        const day = String(date.getDate()).padStart(2, '0')
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const year = date.getFullYear()
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        
        return `${day}/${month}/${year} ${hours}:${minutes}`
    } catch (e) {
        return timestamp
    }
}

/**
 * Returns a relative time string (e.g. "5m ago")
 * @param {string} timestamp 
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (timestamp) => {
    if (!timestamp) return 'Never'
    
    let dateStr = timestamp
    // Handle SQL style "YYYY-MM-DD HH:MM:SS" -> "YYYY-MM-DDTHH:MM:SS"
    if (typeof dateStr === 'string' && dateStr.includes(' ')) {
        dateStr = dateStr.replace(' ', 'T')
    }

    try {
        const date = new Date(dateStr)
        if (isNaN(date.getTime())) return 'Never'

        const now = new Date()
        const diff = now - date // milliseconds
        const seconds = Math.floor(diff / 1000)
        const minutes = Math.floor(seconds / 60)
        const hours = Math.floor(minutes / 60)
        const days = Math.floor(hours / 24)

        if (seconds < 60) return 'Just now'
        if (minutes < 60) return `${minutes}m ago`
        if (hours < 24) return `${hours}h ago`
        return `${days}d ago`
    } catch {
        return 'Never'
    }
}
