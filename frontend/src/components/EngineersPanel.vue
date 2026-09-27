<template>
  <div class="engineers-panel">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-title">Инженеры</span>
        <span class="count-pill">{{ engineers.length }}</span>
      </div>
      <button
        v-if="selectedEngineerId !== null"
        class="btn-clear-selection"
        @click="$emit('select-engineer', null)"
      >
        Сбросить
      </button>
    </div>

    <div class="engineers-list">
      <div
        v-for="(eng, idx) in engineers"
        :key="eng.id ?? idx"
        class="engineer-card"
        :class="{ active: selectedEngineerId === (eng.id ?? idx) }"
        @click="toggleSelect(eng.id ?? idx)"
      >
        <div class="eng-side-bar" :style="{ backgroundColor: getEngineerColor(eng.id ?? idx) }"></div>

        <div class="eng-body">
          <div class="eng-header-row">
            <span class="eng-title">{{ eng.name || getEngineerName(eng.id ?? idx) }}</span>
            <div class="vehicle-tag">
              <component :is="getVehicleIcon(eng.vehicle || eng.vehicle_type)" :size="13" />
              <span>{{ getVehicleLabel(eng.vehicle || eng.vehicle_type) }}</span>
            </div>
          </div>

          <div class="eng-address" :title="eng.office">
            {{ eng.office || 'Базовый офис' }}
          </div>

          <div class="eng-footer-row">
            <span class="eng-shift">
              {{ formatTime(eng.shift_start) }} – {{ formatTime(eng.shift_end) }}
            </span>
            <div class="eng-badges">
              <span class="pill-stat">
                Заявок: <b>{{ getEngineerAssignmentsCount(eng.id ?? idx) }}</b>
              </span>
              <span class="pill-stat">
                В пути: <b>{{ getEngineerTravelTime(eng.id ?? idx) }}м</b>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  IconCar, 
  IconBike, 
  IconWalk, 
  IconBus
} from '@tabler/icons-vue'
import { getEngineerColor } from '../utils/colors'
import { getEngineerName } from '../utils/engineers'
import { formatMskTime } from '../utils/dateUtils'

const props = defineProps({
  engineers: { type: Array, default: () => [] },
  assignments: { type: Array, default: () => [] },
  selectedEngineerId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['select-engineer'])

function toggleSelect(id) {
  if (props.selectedEngineerId === id) {
    emit('select-engineer', null)
  } else {
    emit('select-engineer', id)
  }
}

function getVehicleIcon(type) {
  const t = String(type || '').toLowerCase()
  if (t.includes('car')) return IconCar
  if (t.includes('bicycle') || t.includes('bike')) return IconBike
  if (t.includes('public') || t.includes('bus')) return IconBus
  return IconWalk
}

function getVehicleLabel(type) {
  const t = String(type || '').toLowerCase()
  if (t.includes('car')) return 'Авто'
  if (t.includes('bicycle') || t.includes('bike')) return 'Вело'
  if (t.includes('public') || t.includes('bus')) return 'Транспорт'
  return 'Пешком'
}

function formatTime(val) {
  return formatMskTime(val)
}

function getEngineerAssignmentsCount(id) {
  return props.assignments.filter((a) => Number(a.engineer_id) === Number(id)).length
}

function getEngineerTravelTime(id) {
  return props.assignments
    .filter((a) => Number(a.engineer_id) === Number(id))
    .reduce((sum, a) => sum + (Number(a.travel_minutes) || 0), 0)
}
</script>

<style scoped>
.engineers-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  background: #ffffff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.panel-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-main);
}

.count-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 12px;
  background: #f4f4f5;
  color: var(--text-secondary);
}

.btn-clear-selection {
  background: transparent;
  border: none;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  text-decoration: underline;
}

.btn-clear-selection:hover {
  color: var(--text-main);
}

.engineers-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f4f4f5;
}

.engineers-list::-webkit-scrollbar {
  width: 6px;
}

.engineers-list::-webkit-scrollbar-track {
  background: #f4f4f5;
  border-radius: 4px;
}

.engineers-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.engineers-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.engineer-card {
  display: flex;
  flex-shrink: 0;
  min-height: 62px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.15s ease;
}

.engineer-card:hover {
  border-color: var(--accent);
  background: #fefce8;
}

.engineer-card.active {
  border-color: var(--accent);
  background: #fefce8;
  box-shadow: var(--shadow-xs);
}

.eng-side-bar {
  width: 4px;
  flex-shrink: 0;
}

.eng-body {
  flex: 1;
  padding: 8px 10px;
  min-width: 0;
}

.eng-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 3px;
}

.eng-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-main);
}

.vehicle-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f4f4f5;
  color: var(--text-secondary);
}

.eng-address {
  font-size: 0.73rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.eng-footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.eng-shift {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.eng-badges {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pill-stat {
  font-size: 0.68rem;
  padding: 1px 5px;
  border-radius: 4px;
  background: #f4f4f5;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.pill-stat b {
  color: var(--text-main);
}
</style>
