<template>
  <div v-if="task" class="inspector-sidebar">
    <div class="inspector-header">
      <button class="btn-icon" @click="$emit('close')" title="Назад">
        <IconArrowLeft :size="16" />
      </button>
      <div class="header-title">
        <span class="step-pill">Шаг {{ task.order }}</span>
        <h3>Заявка #{{ task.request_id }}</h3>
      </div>
      <button class="btn-icon" @click="$emit('close')" title="Закрыть">
        <IconX :size="16" />
      </button>
    </div>

    <div class="inspector-body">
      <!-- Timing & SLA Card -->
      <div class="timing-card">
        <div class="timing-col">
          <span class="timing-label">Прибытие</span>
          <span class="timing-val text-accent">{{ String(task.planned_arrival).slice(0, 5) }}</span>
        </div>
        <div class="timing-divider"></div>
        <div class="timing-col">
          <span class="timing-label">Окно SLA</span>
          <span class="timing-val">{{ formatTime(requestDetails?.window_start) }} – {{ formatTime(requestDetails?.window_end) }}</span>
        </div>
      </div>

      <!-- Core Details -->
      <div class="details-card">
        <div class="detail-row">
          <span class="detail-label">Адрес:</span>
          <span class="detail-value font-medium">{{ requestDetails?.address || 'Не указан' }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Тип работ:</span>
          <span class="detail-value">{{ formatWorkType(requestDetails?.work_type) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Текущий исполнитель:</span>
          <span class="detail-value font-medium">{{ currentEngineerName }} ({{ currentEngineerVehicle }})</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Время в пути:</span>
          <span class="detail-value">{{ task.travel_minutes }} мин</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-card">
        <span class="section-title">Переназначение</span>
        <div class="reassign-row">
          <div class="dropdown-wrap">
            <CustomDropdown
              v-model="targetEngineerId"
              :options="engineerDropdownOptions"
            />
          </div>
          <button class="btn btn-yellow" @click="handleReassign">
            Передать
          </button>
        </div>

        <div class="cancel-wrap">
          <button class="btn btn-cancel" @click="handleCancel">
            <IconTrash :size="14" />
            <span>Снять заявку с маршрута</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { IconArrowLeft, IconX, IconTrash } from '@tabler/icons-vue'
import CustomDropdown from './CustomDropdown.vue'
import { getEngineerName } from '../utils/engineers'

const props = defineProps({
  task: { type: Object, default: null },
  requestDetails: { type: Object, default: null },
  engineers: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'reassign-task', 'cancel-task'])

const targetEngineerId = ref(null)

watch(
  () => props.task,
  (newTask) => {
    if (newTask) {
      targetEngineerId.value = newTask.engineer_id
    }
  },
  { immediate: true }
)

const currentEngineerName = computed(() => {
  const eng = props.engineers.find((e) => Number(e.id) === Number(props.task?.engineer_id))
  return eng?.name || getEngineerName(props.task?.engineer_id)
})

const currentEngineerVehicle = computed(() => {
  const eng = props.engineers.find((e) => Number(e.id) === Number(props.task?.engineer_id))
  return getVehicleLabel(eng?.vehicle || eng?.vehicle_type)
})

const engineerDropdownOptions = computed(() => {
  return props.engineers.map((eng, idx) => {
    const id = eng.id ?? idx
    const name = eng.name || getEngineerName(id)
    return {
      label: `${name} (${getVehicleLabel(eng.vehicle || eng.vehicle_type)})`,
      value: id,
    }
  })
})

function getVehicleLabel(type) {
  const t = String(type || '').toLowerCase()
  if (t.includes('car')) return 'Авто'
  if (t.includes('bicycle') || t.includes('bike')) return 'Вело'
  if (t.includes('public') || t.includes('bus')) return 'Транспорт'
  return 'Пешком'
}

function formatWorkType(val) {
  if (!val) return 'Обслуживание'
  const t = String(val).toLowerCase()
  if (t.includes('connect')) return 'Подключение абонента'
  if (t.includes('emergency')) return 'Аварийно-восстановительные работы'
  if (t.includes('repair') || t.includes('local')) return 'Локальный ремонт'
  return val
}

function formatTime(val) {
  if (!val) return '--:--'
  const s = String(val)
  if (s.includes('T')) return s.slice(11, 16)
  return s.slice(0, 5)
}

function handleReassign() {
  if (targetEngineerId.value === props.task.engineer_id) return
  emit('reassign-task', {
    requestId: props.task.request_id,
    newEngineerId: targetEngineerId.value,
  })
}

function handleCancel() {
  emit('cancel-task', props.task.request_id)
}
</script>

<style scoped>
.inspector-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}

.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color);
  background: #ffffff;
}

.btn-icon {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.btn-icon:hover {
  background: #f4f4f5;
  color: var(--text-main);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title h3 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}

.step-pill {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
  background: var(--accent);
  color: #18181b;
}

.inspector-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timing-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 8px;
  background: #fafafa;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.timing-col {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.timing-label {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.timing-val {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-main);
}

.text-accent {
  color: #d97706; /* Warm amber/yellow */
}

.timing-divider {
  width: 1px;
  height: 24px;
  background-color: var(--border-color);
}

.details-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.detail-value {
  font-size: 0.78rem;
  color: var(--text-main);
  line-height: 1.3;
}

.font-medium {
  font-weight: 600;
}

.actions-card {
  padding: 10px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--text-main);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.reassign-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dropdown-wrap {
  flex: 1;
  min-width: 0;
}

.btn {
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.btn-yellow {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  white-space: nowrap;
}

.btn-yellow:hover {
  background: #d97706;
  color: #ffffff;
}

.cancel-wrap {
  margin-top: 4px;
}

.btn-cancel {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: #ffffff;
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.btn-cancel:hover {
  background: var(--danger-light);
}
</style>
