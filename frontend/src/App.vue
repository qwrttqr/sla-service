<template>
  <div class="app-root">
    <!-- Header with compact status & metrics -->
    <HeaderBar
      :isBackendOnline="isBackendOnline"
      :loading="loading"
      :totalRequests="requests.length"
      :assignedCount="assignments.length"
      :unassignedCount="unassignedIds.length"
      @open-uploader="showUploader = true"
      @open-emergency="showEmergencyModal = true"
      @run-demo="runDemo"
    />

    <!-- Main Content Layout -->
    <main class="app-main">
      <!-- Workspace: 3-Column Tri-Pane Command Center -->
      <div class="workspace-grid">
        <!-- 1. Left Panel: Engineers & Unassigned Requests -->
        <div class="sidebar-pane">
          <div class="tab-switcher">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'engineers' }"
              @click="activeTab = 'engineers'"
            >
              Инженеры
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'unassigned' }"
              @click="activeTab = 'unassigned'"
            >
              Заявки
            </button>
          </div>

          <div class="tab-content">
            <EngineersPanel
              v-if="activeTab === 'engineers'"
              :engineers="engineers"
              :assignments="assignments"
              :selectedEngineerId="selectedEngineerId"
              @select-engineer="selectedEngineerId = $event"
            />
            <UnassignedPanel
              v-else
              :unassignedIds="unassignedIds"
              :unassignedReasons="unassignedReasons"
              :requests="requests"
              :engineers="engineers"
              @assign-request="handleAssignUnassigned"
              @cancel-request="handleCancelUnassigned"
              @focus-request="focusRequestId = $event"
            />
          </div>
        </div>

        <!-- 2. Center Panel: Leaflet Map with OSRM Street Paths -->
        <div class="map-pane">
          <MapView
            :engineers="engineers"
            :assignments="assignments"
            :requests="requests"
            :unassignedIds="unassignedIds"
            :unassignedReasons="unassignedReasons"
            :selectedEngineerId="selectedEngineerId"
            :focusRequestId="focusRequestId"
            @reset-filter="selectedEngineerId = null"
            @select-task="handleSelectTask"
          />
        </div>

        <!-- 3. Right Panel: Dispatch Feed OR Task Inspector -->
        <div class="right-pane">
          <InspectorSidebar
            v-if="selectedTask"
            :task="selectedTask.task"
            :requestDetails="selectedTask.requestDetails"
            :engineers="engineers"
            @close="selectedTask = null"
            @reassign-task="handleReassignTask"
            @cancel-task="handleCancelTask"
          />
          <DispatchFeed
            v-else
            :assignments="assignments"
            :requests="requests"
            :engineers="engineers"
            :unassignedCount="unassignedIds.length"
            @select-task="handleSelectTask"
          />
        </div>
      </div>

      <!-- Bottom: Shift & Route Timeline Gantt (Expandable) -->
      <TimelineGantt
        v-if="engineers.length > 0 || assignments.length > 0"
        :engineers="engineers"
        :assignments="assignments"
        :requests="requests"
        :selectedEngineerId="selectedEngineerId"
        @focus-request="focusRequestId = $event"
        @select-task="handleSelectTask"
      />
    </main>

    <!-- Upload Dialog (Redesigned with UI/UX Pro Max) -->
    <UploaderDialog
      v-model="showUploader"
      :loading="loading"
      @submit-files="handleFilesSubmit"
    />

    <!-- Emergency Injection Dialog (Redesigned with UI/UX Pro Max) -->
    <EmergencyModal
      v-model="showEmergencyModal"
      @inject-emergency="handleInjectEmergency"
    />

    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Papa from 'papaparse'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import HeaderBar from './components/HeaderBar.vue'
import MapView from './components/MapView.vue'
import EngineersPanel from './components/EngineersPanel.vue'
import UnassignedPanel from './components/UnassignedPanel.vue'
import DispatchFeed from './components/DispatchFeed.vue'
import InspectorSidebar from './components/InspectorSidebar.vue'
import TimelineGantt from './components/TimelineGantt.vue'
import UploaderDialog from './components/UploaderDialog.vue'
import EmergencyModal from './components/EmergencyModal.vue'

import { checkBackendHealth, submitPlanningCsv } from './api/planningApi'
import { demoEngineersCsv, demoRequestsCsv } from './utils/demoData'
import { getCoordinatesForAddress } from './utils/geoUtils'
import { getEngineerName } from './utils/engineers'
import { formatMskTime } from './utils/dateUtils'

const toast = useToast()

const isBackendOnline = ref(false)
const loading = ref(false)
const showUploader = ref(false)
const showEmergencyModal = ref(false)
const activeTab = ref('engineers')
const selectedEngineerId = ref(null)
const focusRequestId = ref(null)
const selectedTask = ref(null)

const engineers = ref([])
const requests = ref([])
const assignments = ref([])
const unassignedIds = ref([])
const unassignedReasons = ref({})

onMounted(async () => {
  isBackendOnline.value = await checkBackendHealth()
  setInterval(async () => {
    isBackendOnline.value = await checkBackendHealth()
  }, 10000)

  runDemo()
})

function handleSelectTask(data) {
  selectedTask.value = data
  focusRequestId.value = data.task?.request_id
}

function handleReassignTask({ requestId, newEngineerId }) {
  const task = assignments.value.find((a) => Number(a.request_id) === Number(requestId))
  if (!task) return

  const oldEng = task.engineer_id
  task.engineer_id = Number(newEngineerId)

  reindexEngineer(oldEng)
  reindexEngineer(newEngineerId)

  if (selectedTask.value && selectedTask.value.task.request_id === requestId) {
    selectedTask.value.task.engineer_id = Number(newEngineerId)
  }

  toast.add({
    severity: 'success',
    summary: 'Заказ переназначен',
    detail: `Заказ #${requestId} передан инженеру #${newEngineerId}`,
    life: 3000,
  })
}

function handleCancelTask(requestId) {
  const index = assignments.value.findIndex((a) => Number(a.request_id) === Number(requestId))
  if (index === -1) return

  const engId = assignments.value[index].engineer_id
  assignments.value.splice(index, 1)
  reindexEngineer(engId)

  selectedTask.value = null

  toast.add({
    severity: 'info',
    summary: 'Визит отменен',
    detail: `Заказ #${requestId} снят из расписания инженера #${engId}`,
    life: 3000,
  })
}

function reindexEngineer(engId) {
  const tasks = assignments.value
    .filter((a) => Number(a.engineer_id) === Number(engId))
    .sort((x, y) => String(x.planned_arrival).localeCompare(String(y.planned_arrival)))

  tasks.forEach((t, i) => {
    t.order = i + 1
  })
}

function handleAssignUnassigned({ requestId, engineerId }) {
  const req = requests.value.find((r) => Number(r.request_id) === Number(requestId))
  if (!req) return

  unassignedIds.value = unassignedIds.value.filter((id) => Number(id) !== Number(requestId))

  const engTasks = assignments.value.filter((a) => Number(a.engineer_id) === Number(engineerId))
  const nextOrder = engTasks.length + 1
  const arrivalTime = req.window_start ? formatMskTime(req.window_start) : '10:00'

  const newAssignment = {
    request_id: Number(requestId),
    engineer_id: Number(engineerId),
    order: nextOrder,
    planned_arrival: arrivalTime,
    travel_minutes: 20,
  }

  assignments.value.push(newAssignment)
  reindexEngineer(engineerId)

  handleSelectTask({ task: newAssignment, requestDetails: req })

  const engName = getEngineerName(engineerId)
  toast.add({
    severity: 'success',
    summary: 'Заявка распределена',
    detail: `Заказ #${requestId} успешно назначен инженеру ${engName}`,
    life: 3500,
  })
}

function handleCancelUnassigned(requestId) {
  unassignedIds.value = unassignedIds.value.filter((id) => Number(id) !== Number(requestId))
  toast.add({
    severity: 'info',
    summary: 'Заявка отменена',
    detail: `Заказ #${requestId} снят из очереди`,
    life: 3000,
  })
}

function handleInjectEmergency(emergencyData) {
  const newId = 900 + Math.floor(Math.random() * 90)

  const newReq = {
    request_id: newId,
    address: emergencyData.address,
    status: 'sent',
    work_type: emergencyData.work_type,
    window_start: `2026-09-26T${emergencyData.window_start}:00+03:00`,
    window_end: `2026-09-26T${emergencyData.window_end}:00+03:00`,
    point_coords: getCoordinatesForAddress(emergencyData.address),
  }
  requests.value.push(newReq)

  const targetEng = engineers.value.find((e) => e.vehicle === 'car') || engineers.value[0]
  const targetId = targetEng ? targetEng.id : 0

  const newAssignment = {
    request_id: newId,
    engineer_id: targetId,
    order: 1,
    planned_arrival: `${emergencyData.window_start}:00`,
    travel_minutes: 16,
  }

  assignments.value.push(newAssignment)
  reindexEngineer(targetId)

  handleSelectTask({ task: newAssignment, requestDetails: newReq })

  toast.add({
    severity: 'warn',
    summary: '🚨 Экстренное перепланирование',
    detail: `Срочная заявка #${newId} успешно встроена в маршрут инженера #${targetId}!`,
    life: 5000,
  })
}

async function runDemo() {
  loading.value = true
  try {
    parseEngineersCsv(demoEngineersCsv)
    parseRequestsCsv(demoRequestsCsv)

    const engFile = new File([demoEngineersCsv], 'engineers.csv', { type: 'text/csv' })
    const reqFile = new File([demoRequestsCsv], 'requests.csv', { type: 'text/csv' })

    const result = await submitPlanningCsv(engFile, reqFile)
    applyPlanResult(result)
  } catch (err) {
    applyFallbackDemoPlan()
  } finally {
    loading.value = false
  }
}

async function handleFilesSubmit({ engineersFile, requestsFile }) {
  loading.value = true
  showUploader.value = false

  try {
    const engText = await engineersFile.text()
    const reqText = await requestsFile.text()

    parseEngineersCsv(engText)
    parseRequestsCsv(reqText)

    toast.add({
      severity: 'info',
      summary: 'Расчет...',
      detail: 'Сервис рассчитывает оптимальные маршруты с учетом пробок OSRM.',
      life: 4000,
    })

    const result = await submitPlanningCsv(engineersFile, requestsFile)
    applyPlanResult(result)

    toast.add({
      severity: 'success',
      summary: 'Готово!',
      detail: `Распределено: ${result.assignments?.length || 0}, не назначено: ${result.unassigned_request_ids?.length || 0}`,
      life: 4000,
    })
  } catch (err) {
    console.error('Planning submit error:', err)
    toast.add({
      severity: 'error',
      summary: 'Ошибка расчета',
      detail: err.response?.data?.message || err.message || 'Не удалось выполнить расчет.',
      life: 6000,
    })
  } finally {
    loading.value = false
  }
}

function parseEngineersCsv(csvString) {
  const res = Papa.parse(csvString, { header: true, skipEmptyLines: true })
  engineers.value = res.data.map((row, i) => ({
    id: i,
    name: row.name || getEngineerName(i),
    office: row.office,
    vehicle: row.vehicle,
    shift_start: row.shift_start,
    shift_end: row.shift_end,
    skills: row.skills,
    equipment: row.equipment,
    starting_point_coords: getCoordinatesForAddress(row.office),
  }))
}

function parseRequestsCsv(csvString) {
  const res = Papa.parse(csvString, { header: true, skipEmptyLines: true })
  requests.value = res.data.map((row, i) => ({
    request_id: Number(row.request_id) || i + 100,
    address: row.address,
    status: row.status,
    work_type: row.work_type,
    window_start: row.window_start,
    window_end: row.window_end,
    point_coords: getCoordinatesForAddress(row.address),
  }))
}

function applyPlanResult(result) {
  if (!result) return

  // 1. Synchronize engineers start coordinates if returned by backend
  if (result.engineers && Array.isArray(result.engineers)) {
    result.engineers.forEach((be) => {
      const existing = engineers.value.find((e) => String(e.id) === String(be.id))
      const coords = be.start_point_lat && be.start_point_lon ? [be.start_point_lat, be.start_point_lon] : null
      if (existing) {
        if (coords) existing.starting_point_coords = coords
        if (be.shift_start) existing.shift_start = be.shift_start
        if (be.shift_end) existing.shift_end = be.shift_end
      } else {
        engineers.value.push({
          id: be.id,
          name: getEngineerName(be.id),
          office: 'Базовый офис',
          vehicle: 'car',
          shift_start: be.shift_start,
          shift_end: be.shift_end,
          starting_point_coords: coords,
        })
      }
    })
  }

  // 2. Synchronize request coordinates if returned by backend
  if (result.requests && Array.isArray(result.requests)) {
    result.requests.forEach((br) => {
      const existing = requests.value.find((r) => Number(r.request_id) === Number(br.id))
      const coords = br.point ? [br.point.lat, br.point.lon] : (br.lat && br.lon ? [br.lat, br.lon] : null)
      if (existing) {
        if (coords) existing.point_coords = coords
      } else {
        requests.value.push({
          request_id: Number(br.id),
          address: `Заявка #${br.id}`,
          point_coords: coords,
        })
      }
    })
  }

  // 3. Process assignments (chronologically order visits per engineer)
  const rawAssignments = result.assignments || []
  const engGroups = new Map()
  rawAssignments.forEach((a) => {
    const eId = String(a.engineer_id)
    if (!engGroups.has(eId)) engGroups.set(eId, [])
    engGroups.get(eId).push(a)
  })

  const mappedAssignments = []
  engGroups.forEach((taskList) => {
    taskList.sort((x, y) => String(x.time_from || x.planned_arrival).localeCompare(String(y.time_from || y.planned_arrival)))
    taskList.forEach((a, idx) => {
      const arrivalMsk = a.planned_arrival 
        ? formatMskTime(a.planned_arrival) 
        : (a.time_from ? formatMskTime(a.time_from) : '09:00')

      mappedAssignments.push({
        ...a,
        engineer_id: a.engineer_id,
        request_id: Number(a.request_id),
        order: a.order ?? (idx + 1),
        planned_arrival: arrivalMsk,
        time_from: a.time_from,
        time_to: a.time_to,
        wait_minutes: a.wait_minutes ?? 0,
        travel_minutes: a.travel_minutes ?? 20,
      })
    })
  })
  assignments.value = mappedAssignments

  // 4. Handle unassigned requests (support both unassigned_requests with reasons and legacy IDs)
  unassignedReasons.value = {}
  if (result.unassigned_requests && Array.isArray(result.unassigned_requests)) {
    unassignedIds.value = result.unassigned_requests.map((u) => {
      const uId = Number(u.id)
      if (u.reason) unassignedReasons.value[uId] = u.reason
      if (u.point) {
        const req = requests.value.find((r) => Number(r.request_id) === uId)
        if (req) req.point_coords = [u.point.lat, u.point.lon]
      }
      return uId
    })
  } else if (result.unassigned_request_ids && Array.isArray(result.unassigned_request_ids)) {
    unassignedIds.value = result.unassigned_request_ids.map(Number)
  } else {
    unassignedIds.value = []
  }
}

function applyFallbackDemoPlan() {
  assignments.value = [
    { request_id: 101, engineer_id: 0, order: 1, planned_arrival: '09:30', travel_minutes: 25 },
    { request_id: 103, engineer_id: 0, order: 2, planned_arrival: '11:15', travel_minutes: 20 },
    { request_id: 106, engineer_id: 0, order: 3, planned_arrival: '13:00', travel_minutes: 30 },
    { request_id: 102, engineer_id: 1, order: 1, planned_arrival: '10:30', travel_minutes: 18 },
    { request_id: 104, engineer_id: 1, order: 2, planned_arrival: '12:45', travel_minutes: 22 },
    { request_id: 107, engineer_id: 1, order: 3, planned_arrival: '15:00', travel_minutes: 25 },
    { request_id: 105, engineer_id: 2, order: 1, planned_arrival: '13:30', travel_minutes: 35 },
    { request_id: 108, engineer_id: 2, order: 2, planned_arrival: '16:00', travel_minutes: 20 },
  ]
  unassignedIds.value = [109]
  unassignedReasons.value = { 109: 'Не укладывается в окно SLA' }
}
</script>

<style scoped>
.app-root {
  height: 100vh;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-primary);
  overflow: hidden;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 10px 16px 12px 16px;
  gap: 10px;
  max-width: 1920px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
}

/* Tri-Pane Grid: Left 300px | Center Map 1fr | Right 320px */
.workspace-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  grid-template-rows: 100%;
  gap: 10px;
  min-height: 0;
  overflow: hidden;
}

.sidebar-pane {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

.tab-switcher {
  flex-shrink: 0;
  display: flex;
  background: #ffffff;
  padding: 3px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-xs);
}

.tab-btn {
  flex: 1;
  padding: 7px 10px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn.active {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  box-shadow: var(--shadow-xs);
}

.tab-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.map-pane {
  position: relative;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-xs);
}

.right-pane {
  height: 100%;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* On medium or compact viewports (e.g. devtools open, laptops <= 1200px):
   Left column stacks Engineers & Dispatch Feed, while Map stretches 100% full height */
@media (max-width: 1200px) {
  .workspace-grid {
    grid-template-columns: 290px 1fr;
    grid-template-rows: 1fr 1fr;
  }

  .sidebar-pane {
    grid-column: 1;
    grid-row: 1;
    height: 100%;
  }

  .right-pane {
    grid-column: 1;
    grid-row: 2;
    height: 100%;
  }

  .map-pane {
    grid-column: 2;
    grid-row: 1 / 3;
    height: 100%;
  }
}
</style>
