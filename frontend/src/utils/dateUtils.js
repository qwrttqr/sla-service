/**
 * Date and Time utilities for SLA Dispatcher.
 * Automatically handles conversion between UTC (from backend) and Europe/Moscow (MSK, UTC+3).
 */

const mskFormatter = new Intl.DateTimeFormat('ru-RU', {
  timeZone: 'Europe/Moscow',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

/**
 * Formats any ISO string, UTC datetime or time string into "HH:mm" in Moscow Time (Europe/Moscow).
 * @param {string|Date|null} val
 * @returns {string} e.g. "09:30"
 */
export function formatMskTime(val) {
  if (!val) return '--:--'
  const str = String(val).trim()

  // If already pure time like "09:30" or "09:30:00"
  if (/^\d{2}:\d{2}(:\d{2})?$/.test(str)) {
    return str.slice(0, 5)
  }

  const date = new Date(str)
  if (isNaN(date.getTime())) {
    if (str.includes('T')) return str.slice(11, 16)
    return str.slice(0, 5)
  }

  return mskFormatter.format(date)
}

/**
 * Returns minutes from midnight (0..1439) in Moscow Time (Europe/Moscow) for timeline positioning.
 * @param {string|Date|null} val
 * @returns {number}
 */
export function getMskMinutesFromMidnight(val) {
  if (!val) return 0
  const mskTime = formatMskTime(val)
  if (!mskTime || mskTime === '--:--') return 0
  const [h, m] = mskTime.split(':').map(Number)
  return (h || 0) * 60 + (m || 0)
}
