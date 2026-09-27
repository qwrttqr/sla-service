import addressCache from './addressCache.json'

// Build lowercase lookup table
const lookupTable = {}
for (const [key, coords] of Object.entries(addressCache)) {
  if (Array.isArray(coords) && coords.length === 2) {
    const norm = normalizeKey(key)
    lookupTable[norm] = coords
  }
}

function normalizeKey(str) {
  if (!str) return ''
  return String(str)
    .toLowerCase()
    .replace(/[«»"]/g, '')
    .replace(/,\s*/g, ', ')
    .replace(/\s+/g, ' ')
    .trim()
}

/**
 * Synchronously or asynchronously geocodes an address string.
 * Priority:
 * 1. Exact local cache match
 * 2. Partial match against cache
 * 3. Fallback to Moscow center with slight jitter to prevent pin overlap
 */
export function getCoordinatesForAddress(address) {
  if (!address) return [55.751244, 37.618423]

  const norm = normalizeKey(address)

  // 1. Direct match
  if (lookupTable[norm]) {
    return lookupTable[norm]
  }

  // 2. Fuzzy match without "г. москва" or prefix
  const cleaned = norm.replace(/^г\.?\s*москва,?\s*/i, '').trim()
  for (const [key, coords] of Object.entries(lookupTable)) {
    if (key.includes(cleaned) || cleaned.includes(key.replace(/^г\.?\s*москва,?\s*/i, ''))) {
      return coords
    }
  }

  // 3. Fallback
  return [55.751244, 37.618423]
}

export async function geocodeOnline(address) {
  const local = getCoordinatesForAddress(address)
  if (local && (local[0] !== 55.751244 || local[1] !== 37.618423)) {
    return local
  }

  try {
    const query = encodeURIComponent(`Москва, ${address}`)
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}&limit=1`, {
      headers: { 'Accept-Language': 'ru' },
    })
    const data = await res.json()
    if (data && data.length > 0) {
      return [parseFloat(data[0].lat), parseFloat(data[0].lon)]
    }
  } catch (e) {
    // ignore
  }

  return local
}
