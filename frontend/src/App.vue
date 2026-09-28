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

    <!-- Emergency Injection Dialog -->
    <EmergencyModal
      v-model="showEmergencyModal"
    />

    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
})

function handleSelectTask(data) {
  selectedTask.value = data
  if (data?.task?.request_id) {
    focusRequestId.value = Number(data.task.request_id)
  }
  if (data?.task?.engineer_id !== undefined && data?.task?.engineer_id !== null) {
    selectedEngineerId.value = Number(data.task.engineer_id)
  }
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



async function handleFilesSubmit({ engineersFile, requestsFile }) {
  loading.value = true
  showUploader.value = false

  try {
    toast.add({
      severity: 'info',
      summary: 'Расчет...',
      detail: 'Сервис рассчитывает оптимальные маршруты с учетом дорожной ситуации.',
      life: 4000,
    })

    const result = await submitPlanningCsv(engineersFile, requestsFile)
    applyPlanResult(result)

    const assignedCount = result.assignments?.length || 0
    const unassignedCount = result.unassigned_requests?.length || result.unassigned_request_ids?.length || 0

    toast.add({
      severity: 'success',
      summary: 'Готово!',
      detail: `Распределено: ${assignedCount}, не назначено: ${unassignedCount}`,
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


function applyPlanResult(result) {
  if (!result) return

  // 1. Engineers from API response
  if (result.engineers && Array.isArray(result.engineers)) {
    engineers.value = result.engineers.map((be) => {
      const coords = be.start_point_lat && be.start_point_lon ? [be.start_point_lat, be.start_point_lon] : null
      return {
        id: Number(be.id),
        name: be.name || getEngineerName(be.id),
        office: be.office || 'Базовый офис',
        vehicle: be.vehicle || 'car',
        shift_start: be.shift_start,
        shift_end: be.shift_end,
        starting_point_coords: coords,
      }
    })
  }

  // 2. Requests from API response
  const reqList = []
  if (result.requests && Array.isArray(result.requests)) {
    result.requests.forEach((br) => {
      const coords = br.point ? [br.point.lat, br.point.lon] : (br.lat && br.lon ? [br.lat, br.lon] : null)
      reqList.push({
        request_id: Number(br.id),
        address: br.address || `Заявка #${br.id}`,
        work_type: br.work_type,
        window_start: br.request_start,
        window_end: br.request_end,
        point_coords: coords,
      })
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
        engineer_id: Number(a.engineer_id),
        request_id: Number(a.request_id),
        order: a.order ?? (idx + 1),
        planned_arrival: arrivalMsk,
        time_from: a.time_from,
        time_to: a.time_to,
        wait_minutes: a.wait_minutes ?? 0,
        travel_time_minutes: a.travel_time_minutes ?? 0,
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
      const coords = u.point ? [u.point.lat, u.point.lon] : null
      const existing = reqList.find((r) => r.request_id === uId)
      if (existing) {
        if (coords) existing.point_coords = coords
        if (u.address) existing.address = u.address
        if (u.work_type) existing.work_type = u.work_type
        if (u.request_start) existing.window_start = u.request_start
        if (u.request_end) existing.window_end = u.request_end
      } else {
        reqList.push({
          request_id: uId,
          address: u.address || `Заявка #${uId}`,
          work_type: u.work_type,
          window_start: u.request_start,
          window_end: u.request_end,
          point_coords: coords,
        })
      }
      return uId
    })
  } else if (result.unassigned_request_ids && Array.isArray(result.unassigned_request_ids)) {
    unassignedIds.value = result.unassigned_request_ids.map(Number)
  } else {
    unassignedIds.value = []
  }

  requests.value = reqList
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
