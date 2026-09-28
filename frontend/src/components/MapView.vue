<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <!-- Active Filter Badge -->
    <div v-if="selectedEngineerId !== null" class="map-filter-banner">
      <span class="filter-dot" :style="{ backgroundColor: getEngineerColor(selectedEngineerId) }"></span>
      <span>Маршрут: {{ selectedEngineerName }}</span>
      <button class="btn-reset-filter" @click="$emit('reset-filter')">
        Показать всех
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getEngineerColor } from '../utils/colors'
import { getEngineerName } from '../utils/engineers'
import { formatMskTime } from '../utils/dateUtils'

const props = defineProps({
  engineers: { type: Array, default: () => [] },
  assignments: { type: Array, default: () => [] },
  requests: { type: Array, default: () => [] },
  unassignedIds: { type: Array, default: () => [] },
  unassignedReasons: { type: Object, default: () => ({}) },
  selectedEngineerId: { type: [Number, String, null], default: null },
  focusRequestId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['reset-filter', 'select-task'])

const mapContainer = ref(null)
let map = null
let markersLayer = null
let routesLayer = null
const markerInstanceMap = new Map()
const baseMarkerMap = new Map()

const selectedEngineerName = computed(() => {
  if (props.selectedEngineerId === null) return ''
  const eng = props.engineers.find((e) => Number(e.id) === Number(props.selectedEngineerId))
  return eng?.name || getEngineerName(props.selectedEngineerId)
})

onMounted(() => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    zoomControl: true,
  }).setView([55.751244, 37.618423], 12)

  // Remove the Leaflet Ukrainian flag prefix completely:
  if (map.attributionControl) {
    map.attributionControl.setPrefix('')
  }

  // Standard OpenStreetMap Tile Layer (100% Free, NO API key required)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  }).addTo(map)

  markersLayer = L.layerGroup().addTo(map)
  routesLayer = L.layerGroup().addTo(map)

  // Delegated click listener for interactive popup navigation buttons
  if (mapContainer.value) {
    mapContainer.value.addEventListener('click', (evt) => {
      const btn = evt.target.closest('.popup-nav-btn')
      if (!btn) return
      evt.preventDefault()
      evt.stopPropagation()

      if (btn.classList.contains('nav-btn-base')) {
        const engId = btn.dataset.baseEng
        const bm = baseMarkerMap.get(engId) || baseMarkerMap.get(Number(engId))
        if (bm) {
          map.panTo(bm.getLatLng(), { animate: true })
          setTimeout(() => bm.openPopup(), 80)
        }
      } else {
        const targetId = Number(btn.dataset.targetId)
        navigateToTask(targetId)
      }
    })
  }

  if (window.ResizeObserver && mapContainer.value) {
    const ro = new ResizeObserver(() => {
      map?.invalidateSize()
    })
    ro.observe(mapContainer.value)
  }

  renderData()
})

function navigateToTask(targetId) {
  const numId = Number(targetId)
  const marker = markerInstanceMap.get(numId)
  const task = props.assignments.find((a) => Number(a.request_id) === numId)
  const req = props.requests.find((r) => Number(r.request_id) === numId)

  if (marker) {
    map.panTo(marker.getLatLng(), { animate: true })
    setTimeout(() => {
      marker.openPopup()
    }, 80)
  }

  if (task) {
    emit('select-task', { task, requestDetails: req })
  }
}

watch(
  () => [props.assignments, props.engineers, props.requests, props.unassignedIds, props.selectedEngineerId],
  () => {
    nextTick(() => {
      renderData()
    })
  },
  { deep: true }
)

watch(
  () => props.focusRequestId,
  (reqId) => {
    if (!reqId || !map) return
    nextTick(() => {
      const marker = markerInstanceMap.get(Number(reqId))
      if (marker) {
        if (!marker.isPopupOpen()) {
          map.setView(marker.getLatLng(), Math.max(map.getZoom(), 14), { animate: true })
          marker.openPopup()
        }
      } else {
        const req = props.requests.find((r) => Number(r.request_id) === Number(reqId))
        const coords = req ? (req.point_coords || req.coords) : null
        if (coords && coords.length === 2) {
          map.setView(coords, Math.max(map.getZoom(), 14), { animate: true })
        }
      }
    })
  }
)

async function renderData() {
  if (!map || !markersLayer || !routesLayer) return

  markersLayer.clearLayers()
  routesLayer.clearLayers()
  markerInstanceMap.clear()
  baseMarkerMap.clear()

  const allBounds = []

  const requestMap = new Map()
  props.requests.forEach((r) => requestMap.set(Number(r.request_id), r))

  const engineerAssignments = new Map()
  props.assignments.forEach((a) => {
    const engId = Number(a.engineer_id)
    if (!engineerAssignments.has(engId)) {
      engineerAssignments.set(engId, [])
    }
    engineerAssignments.get(engId).push(a)
  })

  for (const list of engineerAssignments.values()) {
    list.sort((x, y) => x.order - y.order)
  }

  // 1. Draw Engineers Bases and Routes
  for (let idx = 0; idx < props.engineers.length; idx++) {
    const eng = props.engineers[idx]
    const engId = Number(eng.id ?? idx)
    const isFiltered = props.selectedEngineerId !== null && Number(props.selectedEngineerId) !== engId

    if (isFiltered) continue

    const color = getEngineerColor(engId)
    const baseCoords = eng.starting_point_coords || eng.coords

    if (baseCoords && baseCoords.length === 2) {
      const lat = baseCoords[0]
      const lon = baseCoords[1]
      allBounds.push([lat, lon])

      const engName = eng.name || getEngineerName(engId)
      const tasks = engineerAssignments.get(engId) || []

      // Office / Starting Point Marker (Point 0)
      const baseIcon = L.divIcon({
        className: 'custom-div-icon',
        html: `<div class="marker-pin marker-base" style="background: ${color};" title="База (${engName})">0</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      })

      const baseMarker = L.marker([lat, lon], { icon: baseIcon })
      baseMarker.bindPopup(`
        <div style="font-family: inherit; font-size: 12px; line-height: 1.45; min-width: 195px;">
          <b style="color: ${color}; font-size: 13px;">База (0): ${engName}</b><br/>
          <span>Адрес: ${eng.office || 'Базовый офис'}</span><br/>
          <span>Транспорт: <b>${eng.vehicle_type || eng.vehicle || 'Авто'}</b></span><br/>
          <span>Смена: ${formatMskTime(eng.shift_start)} – ${formatMskTime(eng.shift_end)}</span>
          ${tasks.length > 0 ? `
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0;">
              <button class="popup-nav-btn nav-btn-next" data-target-id="${tasks[0].request_id}" style="width: 100%; padding: 6px 10px; font-size: 11px; font-weight: 700; border-radius: 6px; border: 1px solid #fde047; background: #fefce8; cursor: pointer; color: #854d0e; display: flex; align-items: center; justify-content: center; gap: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                К точке #1 (${formatMskTime(tasks[0].time_from || tasks[0].planned_arrival)}) →
              </button>
            </div>
          ` : ''}
        </div>
      `)
      markersLayer.addLayer(baseMarker)
      baseMarkerMap.set(engId, baseMarker)
      baseMarkerMap.set(String(engId), baseMarker)

      const routePoints = [[lat, lon]]

      // Sequential Numbered Points: 1, 2, 3...
      tasks.forEach((task, tIdx) => {
        const req = requestMap.get(Number(task.request_id))
        const reqCoords = req ? (req.point_coords || req.coords) : null

        if (reqCoords && reqCoords.length === 2) {
          const rLat = reqCoords[0]
          const rLon = reqCoords[1]
          allBounds.push([rLat, rLon])
          routePoints.push([rLat, rLon])

          const prevTask = tIdx > 0 ? tasks[tIdx - 1] : null
          const nextTask = tIdx < tasks.length - 1 ? tasks[tIdx + 1] : null

          const orderIcon = L.divIcon({
            className: 'custom-div-icon',
            html: `<div class="marker-pin" style="background: ${color};" title="Точка #${task.order} (${engName})">${task.order}</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          })

          const marker = L.marker([rLat, rLon], { icon: orderIcon })
          marker.bindPopup(`
            <div style="font-family: inherit; font-size: 12px; line-height: 1.45; min-width: 215px;">
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 5px;">
                <b style="color: ${color}; font-size: 13px;">Точка #${task.order}</b>
                <span style="font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600; color: #475569;">Заказ #${task.request_id}</span>
              </div>
              <div style="margin-bottom: 8px;">
                <div><b>Инженер:</b> ${engName}</div>
                <div><b>Адрес:</b> ${req ? req.address : 'Не указан'}</div>
                <div><b>Время работ:</b> ${formatMskTime(task.time_from || task.planned_arrival)}${task.time_to ? ' – ' + formatMskTime(task.time_to) : ''}</div>
              </div>
              <div style="display: flex; gap: 6px; border-top: 1px solid #e2e8f0; padding-top: 8px;">
                ${prevTask 
                  ? `<button class="popup-nav-btn nav-btn-prev" data-target-id="${prevTask.request_id}" style="flex: 1; padding: 5px 8px; font-size: 11px; font-weight: 600; border-radius: 5px; border: 1px solid #cbd5e1; background: #ffffff; cursor: pointer; color: #1e293b; display: flex; align-items: center; justify-content: center; gap: 4px;">← Точка #${prevTask.order}</button>`
                  : (baseCoords ? `<button class="popup-nav-btn nav-btn-base" data-base-eng="${engId}" style="flex: 1; padding: 5px 8px; font-size: 11px; font-weight: 600; border-radius: 5px; border: 1px solid #cbd5e1; background: #ffffff; cursor: pointer; color: #1e293b; display: flex; align-items: center; justify-content: center; gap: 4px;">← База (0)</button>` : '')
                }
                ${nextTask
                  ? `<button class="popup-nav-btn nav-btn-next" data-target-id="${nextTask.request_id}" style="flex: 1; padding: 5px 8px; font-size: 11px; font-weight: 700; border-radius: 5px; border: 1px solid #fde047; background: #fefce8; cursor: pointer; color: #854d0e; display: flex; align-items: center; justify-content: center; gap: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">Точка #${nextTask.order} →</button>`
                  : ''
                }
              </div>
            </div>
          `)

          marker.on('click', () => {
            emit('select-task', { task, requestDetails: req })
          })

          markersLayer.addLayer(marker)
          markerInstanceMap.set(Number(task.request_id), marker)
        }
      })

      // Draw route connecting Base -> Stop 1 -> Stop 2 -> ...
      if (routePoints.length > 1) {
        const polyline = L.polyline(routePoints, {
          color: color,
          weight: 3.5,
          opacity: 0.85,
          dashArray: '6, 6',
        })
        routesLayer.addLayer(polyline)
      }
    }
  }

  // 2. Draw Unassigned Requests
  if (props.selectedEngineerId === null) {
    props.unassignedIds.forEach((unId) => {
      const req = requestMap.get(Number(unId))
      const coords = req ? (req.point_coords || req.coords) : null

      if (coords && coords.length === 2) {
        allBounds.push([coords[0], coords[1]])

        const unassignedIcon = L.divIcon({
          className: 'custom-div-icon',
          html: `<div class="marker-pin marker-unassigned" title="Не назначено">!</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        })

        const marker = L.marker([coords[0], coords[1]], { icon: unassignedIcon })
        marker.bindPopup(`
          <div style="font-family: inherit; font-size: 13px; line-height: 1.5;">
            <b style="color: #ef4444; font-size: 14px;">⚠️ Не распределено: Заявка #${unId}</b><br/>
            <b>Адрес:</b> ${req ? req.address : 'Не указан'}<br/>
            <b>Окно:</b> ${formatMskTime(req?.window_start)} – ${formatMskTime(req?.window_end)}<br/>
            <span style="color: #dc2626; font-size: 12px;">${props.unassignedReasons?.[unId] || 'Не удалось включить в расписание инженеров по SLA.'}</span>
          </div>
        `)
        markersLayer.addLayer(marker)
        markerInstanceMap.set(Number(unId), marker)
      }
    })
  }

  if (allBounds.length > 1) {
    map.fitBounds(allBounds, { padding: [50, 50], maxZoom: 14 })
  } else if (allBounds.length === 1) {
    map.setView(allBounds[0], 13)
  }
}
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-filter-banner {
  position: absolute;
  top: 14px;
  left: 60px;
  z-index: 1000;
  background: #ffffff;
  border: 1px solid var(--accent);
  padding: 6px 14px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  box-shadow: var(--shadow-md);
  color: var(--text-main);
  animation: fadeIn 0.2s ease;
}

.filter-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.btn-reset-filter {
  background: #f1f5f9;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-left: 4px;
}
.btn-reset-filter:hover {
  background: #e2e8f0;
  color: var(--text-main);
}

.map-layer-indicator {
  position: absolute;
  bottom: 12px;
  left: 12px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(4px);
  border: 1px solid var(--border-color);
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-secondary);
  box-shadow: var(--shadow-xs);
  display: flex;
  align-items: center;
  gap: 6px;
}

.indicator-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.popup-nav-btn) {
  transition: all 0.15s ease;
}
:deep(.popup-nav-btn:hover) {
  opacity: 0.92;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
:deep(.popup-nav-btn.nav-btn-next:hover) {
  background: #fef08a !important;
}
:deep(.popup-nav-btn.nav-btn-prev:hover),
:deep(.popup-nav-btn.nav-btn-base:hover) {
  background: #f8fafc !important;
  border-color: #94a3b8 !important;
}
</style>
