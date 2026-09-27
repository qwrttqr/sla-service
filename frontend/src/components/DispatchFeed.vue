<template>
  <div class="dispatch-feed-panel">
    <!-- Panel Header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="yellow-indicator"></span>
        <h3 class="panel-title">График выездов</h3>
      </div>
      <span class="count-pill">{{ filteredAssignments.length }}</span>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <button
        class="filter-chip"
        :class="{ active: filterMode === 'all' }"
        @click="filterMode = 'all'"
      >
        Все
      </button>
      <button
        class="filter-chip"
        :class="{ active: filterMode === 'emergency' }"
        @click="filterMode = 'emergency'"
      >
        Срочные
      </button>
    </div>

    <!-- Chronological List of Visits -->
    <div class="feed-content">
      <div v-if="filteredAssignments.length === 0" class="empty-feed">
        <span>Нет запланированных визитов</span>
      </div>

      <div
        v-for="task in filteredAssignments"
        :key="task.request_id"
        class="visit-item"
        @click="selectTask(task)"
      >
        <div class="visit-time-block">
          <span class="visit-time">{{ String(task.planned_arrival).slice(0, 5) }}</span>
          <span class="visit-travel">{{ task.travel_minutes }}м</span>
        </div>

        <div class="visit-divider"></div>

        <div class="visit-info">
          <div class="visit-row-top">
            <span class="visit-id">#{{ task.request_id }}</span>
            <span class="visit-badge" :class="{ 'badge-emergency': isEmergency(task.request_id) }">
              {{ isEmergency(task.request_id) ? 'Срочно' : getEngineerDisplayName(task.engineer_id) }}
            </span>
          </div>
          <div class="visit-address" :title="getRequestAddress(task.request_id)">
            {{ getRequestAddress(task.request_id) }}
          </div>
        </div>

        <IconChevronRight :size="16" class="visit-chevron" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { IconChevronRight } from '@tabler/icons-vue'

import { getEngineerName } from '../utils/engineers'

const props = defineProps({
  assignments: { type: Array, default: () => [] },
  requests: { type: Array, default: () => [] },
  engineers: { type: Array, default: () => [] },
  unassignedCount: { type: Number, default: 0 },
})

const emit = defineEmits(['select-task'])

const filterMode = ref('all')

const sortedAssignments = computed(() => {
  return [...props.assignments].sort((a, b) =>
    String(a.planned_arrival).localeCompare(String(b.planned_arrival))
  )
})

const filteredAssignments = computed(() => {
  if (filterMode.value === 'emergency') {
    return sortedAssignments.value.filter((t) => isEmergency(t.request_id))
  }
  return sortedAssignments.value
})

function getEngineerDisplayName(engId) {
  const eng = props.engineers.find((e) => Number(e.id) === Number(engId))
  return eng?.name || getEngineerName(engId)
}

function isEmergency(reqId) {
  const r = props.requests.find((x) => Number(x.request_id) === Number(reqId))
  return r && (r.work_type === 'emergency_work' || String(r.work_type).includes('emergency'))
}

function getRequestAddress(reqId) {
  const r = props.requests.find((x) => Number(x.request_id) === Number(reqId))
  return r?.address || 'Адрес не указан'
}

function selectTask(task) {
  const req = props.requests.find((x) => Number(x.request_id) === Number(task.request_id))
  emit('select-task', { task, requestDetails: req })
}
</script>

<style scoped>
.dispatch-feed-panel {
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
  padding: 10px 14px;
  border-bottom: 1px solid var(--border-color);
  background: #ffffff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.yellow-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent);
}

.panel-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.count-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 12px;
  background: #f4f4f5;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.filter-bar {
  display: flex;
  gap: 6px;
  padding: 8px 12px;
  background: #fafafa;
  border-bottom: 1px solid var(--border-color);
}

.filter-chip {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid var(--border-color);
  background: #ffffff;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-chip:hover {
  color: var(--text-main);
  border-color: var(--border-hover);
}

.filter-chip.active {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  border-color: var(--accent);
}

.feed-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-feed {
  padding: 30px 15px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

.visit-item {
  display: flex;
  align-items: center;
  padding: 9px 10px;
  border-radius: 6px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.15s ease;
  gap: 10px;
}

.visit-item:hover {
  background: #fefce8; /* subtle warm yellow hover */
  border-color: var(--accent);
  box-shadow: var(--shadow-xs);
}

.visit-time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 44px;
}

.visit-time {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-main);
}

.visit-travel {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.visit-divider {
  width: 1px;
  height: 28px;
  background-color: var(--border-color);
}

.visit-info {
  flex: 1;
  min-width: 0;
}

.visit-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}

.visit-id {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-main);
}

.visit-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: #f4f4f5;
  color: var(--text-secondary);
}

.badge-emergency {
  background: var(--danger-light);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.visit-address {
  font-size: 0.74rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.visit-chevron {
  color: var(--text-subtle);
  flex-shrink: 0;
}

.visit-item:hover .visit-chevron {
  color: var(--text-main);
}
</style>
