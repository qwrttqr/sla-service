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

const props = defineProps({
  engineers: { type: Array, default: () => [] },
  assignments: { type: Array, default: () => [] },
  requests: { type: Array, default: () => [] },
  unassignedIds: { type: Array, default: () => [] },
  selectedEngineerId: { type: [Number, String, null], default: null },
  focusRequestId: { type: [Number, String, null], default: null },
})

const emit = defineEmits(['reset-filter', 'select-task'])

const mapContainer = ref(null)
let map = null
let markersLayer = null
let routesLayer = null
const markerInstanceMap = new Map()

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

  if (window.ResizeObserver && mapContainer.value) {
    const ro = new ResizeObserver(() => {
      map?.invalidateSize()
    })
    ro.observe(mapContainer.value)
  }

  renderData()
})

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
    const marker = markerInstanceMap.get(Number(reqId))
    if (marker) {
      map.setView(marker.getLatLng(), 15, { animate: true })
      marker.openPopup()
    }
  }
)

async function renderData() {
  if (!map || !markersLayer || !routesLayer) return

  markersLayer.clearLayers()
  routesLayer.clearLayers()
  markerInstanceMap.clear()

  const allBounds = []

  const requestMap = new Map()
  props.requests.forEach((r) => requestMap.set(Number(r.request_id), r))

  const engineerAssignments = new Map()
  props.assignments.forEach((a) => {
    const engId = a.engineer_id
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
    const engId = eng.id ?? idx
    const isFiltered = props.selectedEngineerId !== null && props.selectedEngineerId !== engId

    if (isFiltered) continue

    const color = getEngineerColor(engId)
    const baseCoords = eng.starting_point_coords || eng.coords

    if (baseCoords && baseCoords.length === 2) {
      const lat = baseCoords[0]
      const lon = baseCoords[1]
      allBounds.push([lat, lon])

      const engName = eng.name || getEngineerName(engId)

      // Office / Starting Point Marker (Point 0)
      const baseIcon = L.divIcon({
        className: 'custom-div-icon',
        html: `<div class="marker-pin marker-base" style="background: ${color};" title="База (${engName})">0</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      })

      const baseMarker = L.marker([lat, lon], { icon: baseIcon })
      baseMarker.bindPopup(`
        <div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
          <b style="color: ${color}; font-size: 13px;">База: ${engName}</b><br/>
          <span>Адрес: ${eng.office || 'Базовый офис'}</span><br/>
          <span>Транспорт: <b>${eng.vehicle_type || eng.vehicle || 'Авто'}</b></span><br/>
          <span>Смена: ${eng.shift_start ? String(eng.shift_start).slice(11, 16) : '08:00'} – ${eng.shift_end ? String(eng.shift_end).slice(11, 16) : '18:00'}</span>
        </div>
      `)
      markersLayer.addLayer(baseMarker)

      const tasks = engineerAssignments.get(engId) || []

      // Sequential Numbered Points: 1, 2, 3...
      tasks.forEach((task) => {
        const req = requestMap.get(Number(task.request_id))
        const reqCoords = req ? (req.point_coords || req.coords) : null

        if (reqCoords && reqCoords.length === 2) {
          const rLat = reqCoords[0]
          const rLon = reqCoords[1]
          allBounds.push([rLat, rLon])

          const orderIcon = L.divIcon({
            className: 'custom-div-icon',
            html: `<div class="marker-pin" style="background: ${color};" title="Точка #${task.order} (${engName})">${task.order}</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
          })

          const marker = L.marker([rLat, rLon], { icon: orderIcon })
          marker.bindPopup(`
            <div style="font-family: inherit; font-size: 12px; line-height: 1.4;">
              <b style="color: ${color}; font-size: 13px;">Точка #${task.order}</b> (Заказ #${task.request_id})<br/>
              <b>Инженер:</b> ${engName}<br/>
              <b>Адрес:</b> ${req ? req.address : 'Не указан'}<br/>
              <b>Прибытие:</b> ${String(task.planned_arrival).slice(0, 5)}<br/>
              <div style="margin-top: 5px; font-weight: 600; color: #18181b; cursor: pointer; text-decoration: underline;">
                Открыть карточку
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
            <b>Окно:</b> ${req?.window_start ? String(req.window_start).slice(11, 16) : ''} - ${req?.window_end ? String(req.window_end).slice(11, 16) : ''}<br/>
            <span style="color: #dc2626;">Не удалось включить в расписание инженеров по SLA.</span>
          </div>
        `)
        markersLayer.addLayer(marker)
        markerInstanceMap.set(Number(unId), marker)
      }
    })
  }

  if (allBounds.length > 0) {
    map.fitBounds(allBounds, { padding: [40, 40], maxZoom: 14 })
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
</style>
