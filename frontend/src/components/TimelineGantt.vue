<template>
  <div 
    class="timeline-container"
    :class="{ resizing: isResizing }"
    :style="{ height: timelineHeight + 'px' }"
  >
    <!-- Vertical Resizer Handle -->
    <div 
      class="timeline-resizer" 
      @mousedown="startResize" 
      @dblclick="resetHeight"
      title="Потяните для изменения высоты таймлайна (двойной клик — сброс)"
    >
      <div class="resizer-bar"></div>
    </div>

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
      </div>
    </div>

    <!-- 1. GANTT VIEW -->
    <div v-if="viewMode === 'gantt'" class="timeline-body">
      <!-- Time header ticks (dynamic hours) -->
      <div class="time-scale">
        <div class="eng-col-spacer">Инженер</div>
        <div class="ticks-container">
          <div 
            v-for="hour in hours" 
            :key="hour" 
            class="tick-item"
            :style="{ left: ((hour - START_HOUR) / (END_HOUR - START_HOUR)) * 100 + '%' }"
          >
            {{ formatHour(hour) }}
          </div>
        </div>
      </div>

      <!-- Engineer tracks with smooth scrolling -->
      <div class="tracks-container">
        <div class="tracks-scroll-inner">
          <!-- Global continuous vertical hour grid under all visits -->
          <div class="tracks-grid-overlay">
            <div
              v-for="hour in hours"
              :key="hour"
              class="global-hour-line"
              :style="{ left: ((hour - START_HOUR) / (END_HOUR - START_HOUR)) * 100 + '%' }"
            ></div>
          </div>

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

              <!-- Unified Visit Blocks (Zero collisions, sits on top of grid lines) -->
              <template v-for="block in getEngineerBlocks(eng.id ?? idx)" :key="block.id">
                <div
                  class="timeline-block block-work"
                  :style="getBlockStyle(block.workStartMinutes, block.workDurationMinutes)"
                  :title="`Заказ #${block.requestId} | Время работ: ${block.timeFormatted}`"
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
            <!-- Sequential Step Connector with true travel time from API -->
            <div class="flow-arrow">
              <span v-if="task.travel_time_minutes > 0" class="flow-travel-badge" title="Время в пути">
                🚗 {{ task.travel_time_minutes }} мин
              </span>
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
                <span class="step-sub">
                  {{ formatTime(task.time_from || task.planned_arrival) }}<template v-if="task.time_to"> – {{ formatTime(task.time_to) }}</template>
                </span>
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
import { IconTimeline } from '@tabler/icons-vue'
import { getEngineerColor } from '../utils/colors'
import { getEngineerName } from '../utils/engineers'
import { formatMskTime, getMskMinutesFromMidnight } from '../utils/dateUtils'

const props = defineProps({
  engineers: { type: Array, default: () => [] },
  assignments: { type: Array, default: () => [] },
  requests: { type: Array, default: () => [] },
  selectedEngineerId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['focus-request', 'select-task'])

const viewMode = ref('gantt') // 'gantt' | 'flow'

const START_HOUR = 10
const END_HOUR = 22
const TOTAL_MINUTES = (END_HOUR - START_HOUR) * 60

const timelineHeight = ref(340)
const isResizing = ref(false)

function startResize(e) {
  e.preventDefault()
  isResizing.value = true
  const startY = e.clientY
  const startHeight = timelineHeight.value

  const onMouseMove = (moveEvent) => {
    const deltaY = startY - moveEvent.clientY
    const minH = 180
    const maxH = Math.min(window.innerHeight - 140, 750)
    timelineHeight.value = Math.max(minH, Math.min(maxH, startHeight + deltaY))
  }

  const onMouseUp = () => {
    isResizing.value = false
    window.removeEventListener('mousemove', onMouseMove)
    window.removeEventListener('mouseup', onMouseUp)
  }

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
}

function resetHeight() {
  timelineHeight.value = 340
}

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
  return formatMskTime(val)
}

function timeStringToMinutes(str) {
  return getMskMinutesFromMidnight(str)
}

function getSortedAssignments(engId) {
  return props.assignments
    .filter((a) => Number(a.engineer_id) === Number(engId))
    .sort((x, y) => x.order - y.order)
}

function getEngineerBlocks(engId) {
  const engAssignments = getSortedAssignments(engId)

  return engAssignments.map((a, i) => {
    const startMinutes = a.time_from ? getMskMinutesFromMidnight(a.time_from) : getMskMinutesFromMidnight(a.planned_arrival)
    const finishMinutes = a.time_to ? getMskMinutesFromMidnight(a.time_to) : startMinutes + 30
    const durationMinutes = Math.max(15, finishMinutes - startMinutes)
    const timeFormatted = a.time_from && a.time_to
      ? `${formatMskTime(a.time_from)} – ${formatMskTime(a.time_to)}`
      : formatMskTime(a.time_from || a.planned_arrival)

    return {
      id: `${engId}-${a.request_id}-${i}`,
      requestId: a.request_id,
      engineerId: engId,
      assignment: a,
      timeFormatted,
      workStartMinutes: startMinutes,
      workDurationMinutes: durationMinutes,
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
  const startMin = eng.shift_start ? getMskMinutesFromMidnight(eng.shift_start) : 10 * 60
  const endMin = eng.shift_end ? getMskMinutesFromMidnight(eng.shift_end) : 19 * 60

  const dayStartMinutes = START_HOUR * 60
  const dayEndMinutes = END_HOUR * 60

  const visibleStart = Math.max(dayStartMinutes, startMin)
  const visibleEnd = Math.min(dayEndMinutes, endMin)

  if (visibleEnd <= visibleStart) {
    return { display: 'none' }
  }

  const leftPercent = ((visibleStart - dayStartMinutes) / TOTAL_MINUTES) * 100
  const widthPercent = ((visibleEnd - visibleStart) / TOTAL_MINUTES) * 100

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
  padding: 12px 16px 10px 16px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  position: relative;
  min-height: 180px;
}

.timeline-container.resizing {
  user-select: none;
}

.timeline-resizer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 10px;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.resizer-bar {
  width: 44px;
  height: 4px;
  border-radius: 2px;
  background: #cbd5e1;
  transition: all 0.15s ease;
}

.timeline-resizer:hover .resizer-bar,
.timeline-container.resizing .resizer-bar {
  background: var(--accent);
  width: 58px;
  height: 5px;
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
  padding: 0 8px 6px 8px;
  margin-bottom: 6px;
  min-width: 800px;
  flex-shrink: 0;
}

.eng-col-spacer {
  width: 124px;
  flex-shrink: 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
}

.ticks-container {
  flex: 1;
  position: relative;
  height: 18px;
}

.tick-item {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.tick-item:first-child {
  transform: translateX(0);
}

.tick-item:last-child {
  transform: translateX(-100%);
}

.tracks-container {
  min-width: 800px;
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.tracks-scroll-inner {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 100%;
}

.tracks-grid-overlay {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 132px;
  right: 8px;
  pointer-events: none;
  z-index: 2;
}

.global-hour-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(148, 163, 184, 0.45);
  transform: translateX(-50%);
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
  z-index: 1;
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
  background: inherit;
  z-index: 3;
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
  z-index: 1;
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
  border: 1px solid var(--accent-hover);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.15s ease;
  z-index: 3;
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
  width: 180px;
  min-width: 180px;
  max-width: 180px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.8rem;
  flex-shrink: 0;
  overflow: hidden;
}

.flow-eng-badge b {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
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
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.base-step {
  width: 110px;
  min-width: 110px;
}

.flow-step:hover {
  border-color: var(--accent);
  transform: translateY(-1px);
}

.task-step {
  border-left-width: 4px;
  min-width: 135px;
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
  gap: 3px;
  flex-shrink: 0;
  padding: 0 4px;
}

.flow-travel-badge {
  font-size: 0.62rem;
  font-weight: 700;
  color: #854d0e;
  background: #fefce8;
  border: 1px solid #fde047;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
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
