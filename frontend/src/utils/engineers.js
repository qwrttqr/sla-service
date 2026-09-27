export const DEFAULT_ENGINEER_NAMES = [
  'Алексей Смирнов',
  'Дмитрий Иванов',
  'Михаил Кузнецов',
  'Артем Новиков',
  'Сергей Морозов',
  'Илья Васильев',
  'Павел Соколов',
  'Евгений Попов',
]

export function getEngineerName(id) {
  const idx = Math.abs(Number(id) || 0)
  return DEFAULT_ENGINEER_NAMES[idx % DEFAULT_ENGINEER_NAMES.length]
}
