<template>
  <div class="timeline-container" :class="{ expanded: isExpanded }">
    <div class="timeline-header">
      <div class="header-left">
        <IconTimeline :size="20" class="text-accent" />
        <h3 class="title">График загрузки и маршрутов</h3>
        
        <!-- View Mode Switcher -->
        <div class="mode-switcher">
          <button
            class="mode-btn"
            :class="{ active: viewMode === 'gantt' }"
            @click="viewMode = 'gantt'"
          >
            Почасовой
          </button>
          <button
            class="mode-btn"
            :class="{ active: viewMode === 'flow' }"
            @click="viewMode = 'flow'"
          >
            Цепочка остановок
          </button>
        </div>
      </div>

      <div class="header-right-actions">
        <!-- Legend for Gantt -->
        <div class="legend" v-if="viewMode === 'gantt'">
          <div class="legend-item">
            <div class="legend-box box-work"></div>
            <span>Визит у клиента</span>
          </div>
          <div class="legend-item">
            <div class="legend-box box-shift"></div>
            <span>Смена</span>
          </div>
        </div>

        <!-- Height Expand/Collapse Button -->
        <button
          class="btn-expand-toggle"
          @click="isExpanded = !isExpanded"
          :title="isExpanded ? 'Свернуть таймлайн' : 'Развернуть таймлайн для детального просмотра'"
        >
          <IconMaximize v-if="!isExpanded" :size="15" />
          <IconMinimize v-else :size="15" />
          <span>{{ isExpanded ? 'Свернуть' : 'Развернуть' }}</span>
        </button>
      </div>
    </div>

    <!-- 1. GANTT VIEW -->
    <div v-if="viewMode === 'gantt'" class="timeline-body">
      <!-- Time header ticks (dynamic hours) -->
      <div class="time-scale">
        <div class="eng-col-spacer">Инженер</div>
        <div class="ticks-container">
          <div v-for="hour in hours" :key="hour" class="tick">
            {{ formatHour(hour) }}
          </div>
        </div>
      </div>

      <!-- Engineer tracks with smooth scrolling -->
      <div class="tracks-container">
        <div
          v-for="(eng, idx) in engineers"
          :key="eng.id ?? idx"
          class="track-row"
          :class="{ active: selectedEngineerId === (eng.id ?? idx) }"
        >
          <div class="eng-label" :title="eng.name || getEngineerName(eng.id ?? idx)">
            <span class="eng-dot" :style="{ backgroundColor: getEngineerColor(eng.id ?? idx) }"></span>
            <span class="eng-name-text">{{ eng.name || getEngineerName(eng.id ?? idx) }}</span>
          </div>

          <div class="track-timeline">
            <!-- Shift duration background -->
            <div
              class="shift-backdrop"
              :style="getShiftStyle(eng)"
            ></div>

            <!-- Unified Visit Blocks (Zero collisions, no overlapping travel boxes) -->
            <template v-for="block in getEngineerBlocks(eng.id ?? idx)" :key="block.id">
              <div
                class="timeline-block block-work"
                :style="getBlockStyle(block.workStartMinutes, block.workDurationMinutes)"
                :title="`Заказ #${block.requestId} | Прибытие: ${block.plannedArrival} (${block.travelMinutes} мин в пути)`"
                @click="onBlockClick(block)"
              >
                <span class="block-order">{{ block.assignment.order }}</span>
                <span class="block-label">#{{ block.requestId }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. STEP-BY-STEP FLOW VIEW -->
    <div v-else class="flow-view-body">
      <div
        v-for="(eng, idx) in engineers"
        :key="eng.id ?? idx"
        class="flow-engineer-row"
        :class="{ active: selectedEngineerId === (eng.id ?? idx) }"
      >
        <div class="flow-eng-badge" :style="{ borderColor: getEngineerColor(eng.id ?? idx) }">
          <span class="eng-dot" :style="{ backgroundColor: getEngineerColor(eng.id ?? idx) }"></span>
          <b>{{ eng.name || getEngineerName(eng.id ?? idx) }}</b>
        </div>

        <div class="flow-steps-chain">
          <!-- Home Base Step -->
          <div class="flow-step base-step">
            <span class="step-icon">🏢</span>
            <div class="step-info">
              <span class="step-title">Выезд</span>
              <span class="step-sub">{{ formatTime(eng.shift_start) }}</span>
            </div>
          </div>

          <!-- Sequential Assignment Steps -->
          <template v-for="task in getSortedAssignments(eng.id ?? idx)" :key="task.request_id">
            <!-- Connector with travel time -->
            <div class="flow-arrow">
              <span class="arrow-time">🚗 {{ task.travel_minutes }}м</span>
              <div class="arrow-line"></div>
            </div>

            <!-- Task Step Card -->
            <div
              class="flow-step task-step"
              :style="{ borderLeftColor: getEngineerColor(eng.id ?? idx) }"
              @click="onTaskClick(task)"
            >
              <div class="step-num" :style="{ background: getEngineerColor(eng.id ?? idx) }">
                {{ task.order }}
              </div>
              <div class="step-info">
                <span class="step-title">Заказ #{{ task.request_id }}</span>
                <span class="step-sub">{{ task.planned_arrival }}</span>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  IconTimeline,
  IconMaximize,
  IconMinimize,
} from '@tabler/icons-vue'
import { getEngineerColor } from '../utils/colors'
import { getEngineerName } from '../utils/engineers'

const props = defineProps({
  engineers: { type: Array, default: () => [] },
  assignments: { type: Array, default: () => [] },
  requests: { type: Array, default: () => [] },
  selectedEngineerId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['focus-request', 'select-task'])

const viewMode = ref('gantt') // 'gantt' | 'flow'
const isExpanded = ref(false)

const START_HOUR = 8
const END_HOUR = 19
const TOTAL_MINUTES = (END_HOUR - START_HOUR) * 60

const hours = computed(() => {
  const arr = []
  for (let h = START_HOUR; h <= END_HOUR; h++) {
    arr.push(h)
  }
  return arr
})

function formatHour(h) {
  return `${String(h).padStart(2, '0')}:00`
}

function formatTime(val) {
  if (!val) return '--:--'
  return String(val).slice(11, 16) || val
}

function timeStringToMinutes(str) {
  if (!str) return 0
  const parts = String(str).split(':')
  const h = parseInt(parts[0], 10) || 0
  const m = parseInt(parts[1], 10) || 0
  return h * 60 + m
}

function getSortedAssignments(engId) {
  return props.assignments
    .filter((a) => Number(a.engineer_id) === Number(engId))
    .sort((x, y) => x.order - y.order)
}

function getEngineerBlocks(engId) {
  const engAssignments = getSortedAssignments(engId)

  return engAssignments.map((a, i) => {
    const plannedArrivalMinutes = timeStringToMinutes(a.planned_arrival)
    const travelMinutes = Number(a.travel_minutes) || 15
    const travelStartMinutes = Math.max(0, plannedArrivalMinutes - travelMinutes)
    const workDurationMinutes = 40

    return {
      id: `${engId}-${a.request_id}-${i}`,
      requestId: a.request_id,
      engineerId: engId,
      assignment: a,
      plannedArrival: a.planned_arrival,
      travelMinutes,
      travelStartMinutes,
      workStartMinutes: plannedArrivalMinutes,
      workDurationMinutes,
    }
  })
}

function onBlockClick(block) {
  emit('focus-request', block.requestId)
  const req = props.requests.find((r) => Number(r.request_id) === Number(block.requestId))
  emit('select-task', { task: block.assignment, requestDetails: req })
}

function onTaskClick(task) {
  emit('focus-request', task.request_id)
  const req = props.requests.find((r) => Number(r.request_id) === Number(task.request_id))
  emit('select-task', { task, requestDetails: req })
}

function getShiftStyle(eng) {
  const startMin = eng.shift_start ? timeStringToMinutes(String(eng.shift_start).slice(11, 16)) : 8 * 60
  const endMin = eng.shift_end ? timeStringToMinutes(String(eng.shift_end).slice(11, 16)) : 18 * 60

  const dayStartMinutes = START_HOUR * 60
  const offset = startMin - dayStartMinutes
  const duration = Math.max(60, endMin - startMin)

  const leftPercent = Math.max(0, (offset / TOTAL_MINUTES) * 100)
  const widthPercent = Math.min(100 - leftPercent, (duration / TOTAL_MINUTES) * 100)

  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`,
  }
}

function getBlockStyle(startMinutes, durationMinutes, customColor = null) {
  const dayStartMinutes = START_HOUR * 60
  const offset = startMinutes - dayStartMinutes
  const leftPercent = Math.max(0, Math.min(100, (offset / TOTAL_MINUTES) * 100))
  const widthPercent = Math.max(1.8, Math.min(100 - leftPercent, (durationMinutes / TOTAL_MINUTES) * 100))

  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`,
    ...(customColor ? { background: customColor } : {}),
  }
}
</script>

<style scoped>
.timeline-container {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 10px 16px;
  height: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  position: relative;
  transition: height 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.timeline-container.expanded {
  height: 350px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main);
}

.mode-switcher {
  display: flex;
  background: #f1f5f9;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 2px;
}

.mode-btn {
  padding: 4px 10px;
  border-radius: 6px;
  border: none;
  background: transparent;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-btn.active {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  box-shadow: var(--shadow-xs);
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.legend {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-box {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.box-work { background: var(--accent); }
.box-shift { background: #f4f4f5; border: 1px solid #d4d4d8; }

.btn-expand-toggle {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #f4f4f5;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-expand-toggle:hover {
  background: #e4e4e7;
  color: var(--text-main);
}

.timeline-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow-x: auto;
  overflow-y: auto;
}

.time-scale {
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 5px;
  margin-bottom: 6px;
  min-width: 700px;
  flex-shrink: 0;
}

.eng-col-spacer {
  width: 130px;
  flex-shrink: 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
}

.ticks-container {
  flex: 1;
  display: flex;
  justify-content: space-between;
}

.tick {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
}

.tracks-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 700px;
  flex: 1;
  overflow-y: auto;
}

.track-row {
  display: flex;
  align-items: center;
  height: 38px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0 8px;
  position: relative;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.track-row.active {
  background: #fefce8;
  border-color: var(--accent);
}

.eng-label {
  width: 124px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--text-main);
}

.eng-name-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.eng-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.track-timeline {
  flex: 1;
  height: 26px;
  background: #f4f4f5;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.shift-backdrop {
  position: absolute;
  top: 0;
  bottom: 0;
  background: #ffffff;
  border-left: 2px solid #a1a1aa;
  border-right: 2px solid #a1a1aa;
  opacity: 0.95;
}

.timeline-block {
  position: absolute;
  top: 2px;
  bottom: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 6px;
  font-size: 0.68rem;
  font-weight: 700;
  color: #18181b;
  background: var(--accent);
  border: 1px solid #d97706;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.15s ease;
  z-index: 2;
}

.timeline-block:hover {
  transform: scaleY(1.15);
  z-index: 10;
}

.block-order {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #18181b;
  color: #ffffff;
  font-size: 0.58rem;
  font-weight: 800;
  flex-shrink: 0;
}

.block-label {
  font-weight: 700;
}

.block-travel {
  background: #64748b;
  opacity: 0.95;
}

/* FLOW VIEW STYLES */
.flow-view-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: 10px;
  overflow-x: auto;
  overflow-y: auto;
  padding: 4px 0;
}

.flow-engineer-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  flex-shrink: 0;
}

.flow-engineer-row.active {
  background: #fefce8;
  border-color: var(--accent);
}

.flow-eng-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.8rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.flow-steps-chain {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  flex: 1;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.flow-step:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
}

.task-step {
  border-left-width: 4px;
}

.step-num {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-main);
}

.step-sub {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.flow-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.arrow-time {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
}

.arrow-line {
  width: 24px;
  height: 2px;
  background: #cbd5e1;
  position: relative;
}

.arrow-line::after {
  content: '';
  position: absolute;
  right: 0;
  top: -3px;
  border: solid #cbd5e1;
  border-width: 0 2px 2px 0;
  display: inline-block;
  padding: 3px;
  transform: rotate(-45deg);
}
</style>
