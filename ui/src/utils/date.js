import { DateTime } from 'luxon'

/**
 * Robust date formatter.
 * @param {string} timestamp 
 * @returns {string} local format
 */
export const formatDate = (timestamp) => {
  if (!timestamp) return 'Never'
  try {
    const dt = DateTime.fromISO(timestamp, { zone: 'utc' })
    if (!dt.isValid) {
        // Try fallback for DuckDB strings
        const dt2 = DateTime.fromSQL(timestamp, { zone: 'utc' })
        return dt2.isValid ? dt2.toLocal().toFormat('dd/MM/yyyy HH:mm') : timestamp
    }
    return dt.toLocal().toFormat('dd/MM/yyyy HH:mm')
  } catch (e) {
    return timestamp
  }
}

/**
 * Relative time (e.g. 5m ago)
 * @param {string} timestamp 
 * @returns {string} 
 */
export const formatRelativeTime = (timestamp) => {
    if (!timestamp) return 'Never'
    try {
        const dt = DateTime.fromISO(timestamp, { zone: 'utc' })
        if (!dt.isValid) {
            const dt2 = DateTime.fromSQL(timestamp, { zone: 'utc' })
            return dt2.isValid ? dt2.toLocal().toRelative() : 'Never'
        }
        return dt.toLocal().toRelative()
    } catch {
        return 'Never'
    }
}
/**
 * Parses a string to a Luxon DateTime, forcing UTC.
 */
export const parseUTC = (timestamp) => {
    if (!timestamp) return DateTime.now().toUTC()
    const dt = DateTime.fromISO(timestamp, { zone: 'utc' })
    if (dt.isValid) return dt
    const dt2 = DateTime.fromSQL(timestamp, { zone: 'utc' })
    return dt2.isValid ? dt2 : DateTime.now().toUTC()
}
