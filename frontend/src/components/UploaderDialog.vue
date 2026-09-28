<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-backdrop" @click.self="!loading && (visible = false)">
        <div class="modal-card">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="header-icon-box">
              <IconFileSpreadsheet :size="24" stroke-width="2.2" class="text-accent" />
            </div>
            <div class="header-texts">
              <h3 class="modal-title">Импорт данных планирования</h3>
              <p class="modal-subtitle">Загрузите реестры инженеров и заявок для расчета VRP</p>
            </div>
            <button class="btn-close" :disabled="loading" @click="visible = false">
              <IconX :size="20" />
            </button>
          </div>

          <!-- Modal Body -->
          <div class="modal-body">

            <!-- Engineers File Drop Zone -->
            <div class="drop-zone" :class="{ 'drop-active': engineersFile }">
              <input
                type="file"
                accept=".csv"
                id="eng-file-input"
                class="file-input"
                @change="onEngineersSelected"
              />
              <label for="eng-file-input" class="drop-label">
                <div class="drop-icon-box" :class="{ 'box-filled': engineersFile }">
                  <IconUsers v-if="!engineersFile" :size="24" />
                  <IconCheck v-else :size="24" class="text-emerald" />
                </div>
                <div class="drop-text">
                  <span class="file-name" v-if="engineersFile">
                    {{ engineersFile.name }} <b class="count-tag">({{ engineersCount }} инженеров)</b>
                  </span>
                  <span class="file-prompt" v-else>
                    Нажмите или перетащите <b>engineers.csv</b>
                  </span>
                  <span class="file-hint">office, shift_start, shift_end, skills, equipment, vehicle</span>
                </div>
              </label>
            </div>

            <!-- Requests File Drop Zone -->
            <div class="drop-zone" :class="{ 'drop-active': requestsFile }">
              <input
                type="file"
                accept=".csv"
                id="req-file-input"
                class="file-input"
                @change="onRequestsSelected"
              />
              <label for="req-file-input" class="drop-label">
                <div class="drop-icon-box" :class="{ 'box-filled': requestsFile }">
                  <IconClipboardList v-if="!requestsFile" :size="24" />
                  <IconCheck v-else :size="24" class="text-emerald" />
                </div>
                <div class="drop-text">
                  <span class="file-name" v-if="requestsFile">
                    {{ requestsFile.name }} <b class="count-tag">({{ requestsCount }} заявок)</b>
                  </span>
                  <span class="file-prompt" v-else>
                    Нажмите или перетащите <b>requests.csv</b>
                  </span>
                  <span class="file-hint">request_id, address, status, work_type, window_start, window_end</span>
                </div>
              </label>
            </div>

            <div v-if="errorMessage" class="error-banner">
              <IconAlertCircle :size="18" />
              <span>{{ errorMessage }}</span>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button class="btn btn-ghost" :disabled="loading" @click="visible = false">
              Отмена
            </button>
            <button
              class="btn btn-primary"
              :disabled="!engineersFile || !requestsFile || loading"
              @click="handleSubmit"
            >
              <IconSend :size="17" />
              <span>{{ loading ? 'Расчет маршрутов...' : 'Рассчитать маршруты' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import Papa from 'papaparse'
import {
  IconFileSpreadsheet,
  IconX,
  IconUsers,
  IconClipboardList,
  IconCheck,
  IconAlertCircle,
  IconSend,
} from '@tabler/icons-vue'

const props = defineProps({
  modelValue: Boolean,
  loading: Boolean,
})

const emit = defineEmits(['update:modelValue', 'submit-files'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const engineersFile = ref(null)
const requestsFile = ref(null)
const engineersCount = ref(0)
const requestsCount = ref(0)
const errorMessage = ref('')

function onEngineersSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  engineersFile.value = file
  Papa.parse(file, {
    header: true,
    complete: (results) => {
      engineersCount.value = results.data.filter((r) => r.office || r.shift_start).length
    },
  })
}

function onRequestsSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  requestsFile.value = file
  Papa.parse(file, {
    header: true,
    complete: (results) => {
      requestsCount.value = results.data.filter((r) => r.request_id || r.address).length
    },
  })
}

function handleSubmit() {
  if (!engineersFile.value || !requestsFile.value) {
    errorMessage.value = 'Пожалуйста, выберите оба файла.'
    return
  }
  errorMessage.value = ''
  emit('submit-files', {
    engineersFile: engineersFile.value,
    requestsFile: requestsFile.value,
  })
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-card {
  width: 100%;
  max-width: 580px;
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25), 0 0 0 1px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: cardPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardPop {
  0% { transform: scale(0.95); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-header {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid var(--border-color);
  background: #ffffff;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text-accent {
  color: var(--accent);
}

.header-texts {
  flex: 1;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
}

.modal-subtitle {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.btn-close {
  background: #f8fafc;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-close:hover:not(:disabled) {
  background: #f1f5f9;
  color: var(--text-main);
}

.modal-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #ffffff;
}


.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.15s ease;
}

.drop-zone:hover, .drop-active {
  border-color: var(--accent);
  background: #fefce8;
}

.file-input {
  display: none;
}

.drop-label {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: pointer;
}

.drop-icon-box {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.box-filled {
  background: #ecfdf5;
  border-color: #a7f3d0;
}

.text-emerald {
  color: #10b981;
}

.drop-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.file-name {
  font-weight: 700;
  font-size: 0.88rem;
  color: #0f172a;
}

.count-tag {
  color: #2563eb;
  font-size: 0.8rem;
}

.file-prompt {
  font-size: 0.875rem;
  color: #334155;
}

.file-hint {
  font-size: 0.72rem;
  color: #94a3b8;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  color: #dc2626;
}

.modal-footer {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
}

.btn-ghost {
  background: transparent;
  color: #64748b;
}
.btn-ghost:hover:not(:disabled) {
  background: #e2e8f0;
  color: #0f172a;
}

.drop-zone.drop-active {
  background: #fefce8;
  border-color: var(--accent);
}

.btn-primary {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}
.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  color: #ffffff;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

/* Modal Transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
