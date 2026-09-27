<template>
  <div class="unassigned-panel">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-title">Заявки вне плана</span>
        <span v-if="unassignedIds.length > 0" class="count-badge">{{ unassignedIds.length }}</span>
      </div>
    </div>

    <div v-if="unassignedIds.length === 0" class="empty-state">
      <IconCircleCheck :size="28" class="text-success" />
      <span>Все заявки распределены в графике</span>
    </div>

    <div v-else class="unassigned-list">
      <div
        v-for="id in unassignedIds"
        :key="id"
        class="unassigned-card"
        @click="$emit('focus-request', id)"
      >
        <div class="unassigned-top">
          <span class="req-id">Заявка #{{ id }}</span>
          <span class="risk-badge">Требует назначения</span>
        </div>

        <div class="unassigned-body">
          <p class="address-text" :title="getRequest(id)?.address">
            {{ getRequest(id)?.address || 'Адрес не указан' }}
          </p>

          <div class="details-row">
            <span class="pill-meta">
              {{ formatTime(getRequest(id)?.window_start) }} – {{ formatTime(getRequest(id)?.window_end) }}
            </span>
            <span v-if="getRequest(id)?.work_type" class="pill-meta">
              {{ formatWorkType(getRequest(id)?.work_type) }}
            </span>
          </div>

          <div v-if="unassignedReasons && unassignedReasons[id]" class="reason-row">
            <span class="reason-pill" :title="unassignedReasons[id]">{{ unassignedReasons[id] }}</span>
          </div>

          <!-- Dispatcher Action Controls -->
          <div class="assign-action-box" @click.stop>
            <div class="select-col">
              <CustomDropdown
                v-model="selectedEngMap[id]"
                :options="engineerDropdownOptions"
                placeholder="Инженер..."
              />
            </div>
            <button
              class="btn-assign-action"
              :disabled="selectedEngMap[id] === undefined || selectedEngMap[id] === null"
              @click="assignToEngineer(id)"
            >
              Назначить
            </button>
            <button
              class="btn-dismiss-action"
              title="Отменить заявку"
              @click="$emit('cancel-request', id)"
            >
              <IconTrash :size="13" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconCircleCheck, IconTrash } from '@tabler/icons-vue'
import CustomDropdown from './CustomDropdown.vue'
import { getEngineerName } from '../utils/engineers'
import { formatMskTime } from '../utils/dateUtils'

const props = defineProps({
  unassignedIds: { type: Array, default: () => [] },
  unassignedReasons: { type: Object, default: () => ({}) },
  requests: { type: Array, default: () => [] },
  engineers: { type: Array, default: () => [] },
})

const emit = defineEmits(['assign-request', 'cancel-request', 'focus-request'])

const selectedEngMap = ref({})

const engineerDropdownOptions = computed(() => {
  return props.engineers.map((eng, idx) => {
    const id = eng.id ?? idx
    const name = eng.name || getEngineerName(id)
    return {
      label: `${name} (#${id})`,
      value: id,
    }
  })
})

function getRequest(id) {
  return props.requests.find((r) => Number(r.request_id) === Number(id))
}

function formatTime(val) {
  return formatMskTime(val)
}

function formatWorkType(val) {
  if (!val) return ''
  const t = String(val).toLowerCase()
  if (t.includes('connect')) return 'Подключение'
  if (t.includes('emergency')) return 'Авария'
  if (t.includes('repair') || t.includes('local')) return 'Ремонт'
  return val
}

function assignToEngineer(requestId) {
  const engId = selectedEngMap.value[requestId]
  if (engId === undefined || engId === null) return
  emit('assign-request', { requestId, engineerId: engId })
}
</script>

<style scoped>
.unassigned-panel {
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

.count-badge {
  background: var(--danger-light);
  color: var(--danger);
  border: 1px solid var(--danger-border);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 16px;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.text-success {
  color: var(--success);
}

.unassigned-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.unassigned-card {
  flex-shrink: 0;
  padding: 10px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--accent);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.unassigned-card:hover {
  background: #fefce8;
  border-color: var(--accent);
}

.unassigned-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.req-id {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-main);
}

.risk-badge {
  font-size: 0.68rem;
  font-weight: 600;
  color: #854d0e;
  background: #fef9c3;
  padding: 1px 6px;
  border-radius: 4px;
  border: 1px solid #fde047;
}

.address-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.details-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.pill-meta {
  font-size: 0.68rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f4f4f5;
  color: var(--text-muted);
  border: 1px solid var(--border-color);
}

.assign-action-box {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border-color);
}

.select-col {
  flex: 1;
  min-width: 0;
}

.btn-assign-action {
  padding: 7px 11px;
  background: var(--accent);
  color: #18181b;
  border: none;
  border-radius: 6px;
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-assign-action:hover:not(:disabled) {
  background: #d97706;
  color: #ffffff;
}

.btn-assign-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-dismiss-action {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.btn-dismiss-action:hover {
  background: var(--danger-light);
  border-color: var(--danger-border);
  color: var(--danger);
}

.reason-row {
  margin-top: 5px;
}

.reason-pill {
  font-size: 0.72rem;
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 3px 7px;
  border-radius: 4px;
  display: block;
  line-height: 1.3;
  word-break: break-word;
}
</style>
