// High-contrast distinct palette for engineers so each route and team is immediately recognizable
export const ENGINEER_PALETTE = [
  '#2563eb', // Royal Blue
  '#059669', // Emerald Green
  '#d97706', // Amber / Orange
  '#7c3aed', // Purple / Violet
  '#db2777', // Pink / Rose
  '#0891b2', // Teal / Cyan
  '#ea580c', // Coral / Deep Orange
  '#4f46e5', // Indigo
  '#16a34a', // Grass Green
  '#c026d3', // Fuchsia
  '#e11d48', // Crimson Red
  '#0284c7', // Sky Blue
  '#9333ea', // Deep Purple
  '#0d9488', // Dark Teal
  '#b45309', // Bronze / Brown
  '#4338ca', // Deep Indigo
]

export function getEngineerColor(id) {
  if (id === null || id === undefined) return '#2563eb'
  const num = Math.abs(Number(id))
  if (isNaN(num)) {
    let hash = 0
    const str = String(id)
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i)
      hash |= 0
    }
    return ENGINEER_PALETTE[Math.abs(hash) % ENGINEER_PALETTE.length]
  }
  return ENGINEER_PALETTE[num % ENGINEER_PALETTE.length]
}
