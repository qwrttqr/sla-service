<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo-box" title="SLA Route Planner">
        <IconRoute :size="20" stroke-width="2.5" />
      </div>
    </div>

    <!-- Center: Essential counts & status -->
    <div class="header-center">
      <div v-if="totalRequests > 0" class="counts-group">
        <div class="count-item">
          <span class="count-label">Заявок:</span>
          <span class="count-value">{{ totalRequests }}</span>
        </div>
        <div class="count-sep">/</div>
        <div class="count-item">
          <span class="count-label">В плане:</span>
          <span class="count-value">{{ assignedCount }}</span>
        </div>
        <div v-if="unassignedCount > 0" class="count-sep">/</div>
        <div v-if="unassignedCount > 0" class="count-item unassigned">
          <span class="count-label">Вне плана:</span>
          <span class="count-value">{{ unassignedCount }}</span>
        </div>
      </div>

      <div class="server-status" :class="{ online: isBackendOnline, offline: !isBackendOnline }">
        <span class="status-dot"></span>
        <span>{{ isBackendOnline ? 'Онлайн' : 'Офлайн' }}</span>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="header-right">
      <button class="btn btn-emergency" @click="$emit('open-emergency')" title="Срочная заявка">
        <IconBolt :size="16" />
        <span class="btn-text-full">Срочная заявка</span>
        <span class="btn-text-short">Срочно</span>
      </button>

      <button class="btn btn-yellow" :disabled="loading" @click="$emit('open-uploader')" title="Загрузить CSV">
        <IconFileSpreadsheet :size="16" />
        <span class="btn-text-full">Загрузить CSV</span>
        <span class="btn-text-short">CSV</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { 
  IconRoute, 
  IconFileSpreadsheet, 
  IconBolt
} from '@tabler/icons-vue'

defineProps({
  isBackendOnline: Boolean,
  loading: Boolean,
  totalRequests: { type: Number, default: 0 },
  assignedCount: { type: Number, default: 0 },
  unassignedCount: { type: Number, default: 0 },
})

defineEmits(['open-uploader', 'open-emergency'])
</script>

<style scoped>
.app-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  padding: 0 16px;
  height: 52px;
  flex-shrink: 0;
  background: #ffffff;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  z-index: 20;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-box {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--accent);
  color: #18181b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-center {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  white-space: nowrap;
  min-width: 0;
}

.counts-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-muted);
  background: #fafafa;
  padding: 5px 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.count-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.count-label {
  color: var(--text-muted);
}

.count-value {
  font-weight: 700;
  color: var(--text-main);
}

.count-sep {
  color: var(--border-hover);
  opacity: 0.6;
}

.count-item.unassigned .count-value {
  color: var(--danger);
}

.server-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--text-secondary);
  background: #fafafa;
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  font-weight: 500;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #94a3b8;
}

.server-status.online .status-dot {
  background-color: var(--success);
  box-shadow: 0 0 0 2px var(--success-border);
}

.server-status.offline .status-dot {
  background-color: var(--danger);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
  white-space: nowrap;
}

.btn-emergency {
  background: #fefce8;
  color: #854d0e;
  border-color: #fef08a;
}

.btn-emergency:hover {
  background: #fef9c3;
  border-color: #fde047;
}

.btn-outline {
  background: #ffffff;
  color: var(--text-secondary);
  border-color: var(--border-color);
}

.btn-outline:hover:not(:disabled) {
  background: #f4f4f5;
  color: var(--text-main);
  border-color: var(--border-hover);
}

.btn-yellow {
  background: var(--accent);
  color: #18181b;
  font-weight: 700;
}

.btn-yellow:hover:not(:disabled) {
  background: var(--accent-hover);
  color: #ffffff;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text-short {
  display: none;
}

@media (max-width: 1200px) {
  .btn-text-full {
    display: none;
  }
  .btn-text-short {
    display: inline;
  }
  .counts-group {
    padding: 4px 8px;
    gap: 6px;
    font-size: 0.76rem;
  }
  .server-status {
    padding: 4px 8px;
    font-size: 0.74rem;
  }
  .btn {
    padding: 5px 8px;
    font-size: 0.76rem;
  }
}

@media (max-width: 850px) {
  .btn-text-short {
    display: none;
  }
  .count-label {
    display: none;
  }
}
</style>
