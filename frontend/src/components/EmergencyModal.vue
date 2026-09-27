<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="visible" class="modal-backdrop" @click.self="visible = false">
        <div class="modal-card">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="header-icon-box">
              <IconBolt :size="24" stroke-width="2.5" class="text-emergency" />
            </div>
            <div class="header-texts">
              <h3 class="modal-title">Экстренное перепланирование</h3>
              <p class="modal-subtitle">Встроить срочную заявку в маршрут без срыва SLA</p>
            </div>
            <button class="btn-close" @click="visible = false">
              <IconX :size="20" />
            </button>
          </div>

          <!-- Modal Body -->
          <div class="modal-body">
            <!-- Address Group -->
            <div class="form-group">
              <label class="form-label">
                <IconMapPin :size="15" class="label-icon" />
                <span>Адрес объекта в Москве</span>
              </label>
              <div class="input-wrapper">
                <input
                  v-model="address"
                  type="text"
                  class="custom-input"
                  placeholder="Введите улицу и дом..."
                />
              </div>

              <!-- Quick address pills -->
              <div class="chips-row">
                <span class="chips-hint">Быстрый выбор:</span>
                <button
                  v-for="qa in quickAddrs"
                  :key="qa"
                  type="button"
                  class="chip-btn"
                  @click="address = qa"
                >
                  {{ qa.split(',')[1].trim() }}
                </button>
              </div>
            </div>

            <!-- Two Columns: Work Type & Equipment -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">
                  <IconTool :size="15" class="label-icon" />
                  <span>Характер работ</span>
                </label>
                <CustomDropdown
                  v-model="workType"
                  :options="workTypeOptions"
                />
              </div>

              <div class="form-group">
                <label class="form-label">
                  <IconShieldCheck :size="15" class="label-icon" />
                  <span>Оснащение</span>
                </label>
                <CustomDropdown
                  v-model="requiredEquipment"
                  :options="equipmentOptions"
                />
              </div>
            </div>

            <!-- Two Columns: Time Window -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">
                  <IconClock :size="15" class="label-icon" />
                  <span>Начало окна SLA</span>
                </label>
                <input v-model="windowStart" type="time" class="custom-input time-input" />
              </div>

              <div class="form-group">
                <label class="form-label">
                  <IconAlertCircle :size="15" class="label-icon text-emergency" />
                  <span>Дедлайн SLA</span>
                </label>
                <input v-model="windowEnd" type="time" class="custom-input time-input" />
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="visible = false">
              Отмена
            </button>
            <button class="btn btn-action" :disabled="!address" @click="handleInject">
              <IconSparkles :size="17" />
              <span>Оптимизировать маршрут</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  IconBolt,
  IconX,
  IconMapPin,
  IconTool,
  IconShieldCheck,
  IconClock,
  IconAlertCircle,
  IconSparkles,
} from '@tabler/icons-vue'

import CustomDropdown from './CustomDropdown.vue'

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(['update:modelValue', 'inject-emergency'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const address = ref('г. Москва, ул. Большая Дмитровка, д. 12')
const workType = ref('emergency_work')
const requiredEquipment = ref('FTTB')
const windowStart = ref('12:00')
const windowEnd = ref('14:30')

const workTypeOptions = [
  { label: '🚨 Аварийный выезд (Срочно)', value: 'emergency_work' },
  { label: '⚡ Подключение абонента', value: 'connect_client' },
  { label: '🔧 Локальный ремонт', value: 'local_work_or_repair' },
]

const equipmentOptions = [
  { label: 'FTTB (Сварочный аппарат)', value: 'FTTB' },
  { label: 'FMC Терминал', value: 'FMC' },
  { label: 'Gigabit тестер', value: 'gigabit_connection' },
]

const quickAddrs = [
  'г. Москва, Цветной бульвар, д. 15',
  'г. Москва, ул. Садовая-Кудринская, д. 8',
  'г. Москва, Кутузовский пр-т, д. 22',
]

function handleInject() {
  if (!address.value) return

  emit('inject-emergency', {
    address: address.value,
    work_type: workType.value,
    required_equipment: requiredEquipment.value,
    window_start: windowStart.value,
    window_end: windowEnd.value,
  })

  visible.value = false
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
  max-width: 520px;
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
  background: #fef2f2;
  border: 1px solid #fee2e2;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text-emergency {
  color: #dc2626;
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
.btn-close:hover {
  background: #f1f5f9;
  color: var(--text-main);
}

.modal-body {
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #ffffff;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #475569;
}

.label-icon {
  color: var(--text-muted);
}

.custom-input, .custom-select {
  width: 100%;
  padding: 9px 13px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.85rem;
  color: var(--text-main);
  outline: none;
  transition: all 0.15s ease;
}

.custom-input:focus, .custom-select:focus {
  background: #ffffff;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}

.time-input {
  font-weight: 600;
  color: #1e293b;
}

.chips-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 3px;
}

.chips-hint {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.chip-btn {
  background: #f4f4f5;
  border: 1px solid var(--border-color);
  padding: 3px 9px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}
.chip-btn:hover {
  background: #fefce8;
  border-color: #fde047;
  color: #854d0e;
  transform: translateY(-1px);
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
.btn-ghost:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-action {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
}
.btn-action:hover:not(:disabled) {
  background: #d97706;
  color: #ffffff;
}
.btn-action:disabled {
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
