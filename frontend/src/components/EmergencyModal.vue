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
          <div class="modal-body dev-placeholder">
            <div class="dev-icon-circle">
              <IconInfoCircle :size="38" class="text-accent" />
            </div>
            <h4 class="dev-title">Функционал находится в разработке</h4>
            <p class="dev-desc">
              Динамическая вставка срочных заявок и перепланирование маршрутов в режиме реального времени находятся в разработке. 
              В текущей версии расчет оптимального графика выполняется пакетно через загрузку файлов CSV.
            </p>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button class="btn btn-action" @click="visible = false">
              Понятно
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import {
  IconBolt,
  IconX,
  IconInfoCircle,
} from '@tabler/icons-vue'

const props = defineProps({
  modelValue: Boolean,
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
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

.dev-placeholder {
  align-items: center;
  text-align: center;
  padding: 36px 24px;
  gap: 14px;
}

.dev-icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #fefce8;
  border: 1px solid #fef08a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.dev-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.dev-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.55;
  max-width: 420px;
  margin: 0;
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
  background: var(--accent-hover);
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
