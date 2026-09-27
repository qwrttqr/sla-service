<template>
  <div ref="rootRef" class="custom-dropdown">
    <button
      type="button"
      class="dropdown-trigger"
      :class="{ 'is-open': isOpen }"
      @click="toggleOpen"
    >
      <span class="trigger-text">
        {{ currentLabel || placeholder }}
      </span>
      <IconChevronDown :size="16" class="trigger-chevron" :class="{ rotated: isOpen }" />
    </button>

    <Transition name="dropdown-fade">
      <div v-if="isOpen" class="dropdown-menu">
        <div
          v-for="opt in normalizedOptions"
          :key="String(opt.value)"
          class="dropdown-item"
          :class="{ active: opt.value === modelValue }"
          @click="selectOption(opt.value)"
        >
          <span class="item-label">{{ opt.label }}</span>
          <IconCheck v-if="opt.value === modelValue" :size="14" class="item-check" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { IconChevronDown, IconCheck } from '@tabler/icons-vue'

const props = defineProps({
  modelValue: [String, Number, null],
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: 'Выберите...',
  },
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const rootRef = ref(null)

const normalizedOptions = computed(() => {
  return props.options.map((opt) => {
    if (typeof opt === 'object' && opt !== null && 'value' in opt) {
      return opt
    }
    return { label: String(opt), value: opt }
  })
})

const currentLabel = computed(() => {
  const match = normalizedOptions.value.find((opt) => opt.value === props.modelValue)
  return match ? match.label : ''
})

function toggleOpen() {
  isOpen.value = !isOpen.value
}

function selectOption(val) {
  emit('update:modelValue', val)
  isOpen.value = false
}

function handleClickOutside(e) {
  if (rootRef.value && !rootRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.custom-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.dropdown-trigger:hover {
  border-color: var(--border-hover);
}

.dropdown-trigger.is-open {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2);
}

.trigger-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.trigger-chevron {
  color: var(--text-muted);
  transition: transform 0.2s ease;
  flex-shrink: 0;
  margin-left: 6px;
}

.trigger-chevron.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 10px 25px -4px rgba(0, 0, 0, 0.12), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  max-height: 220px;
  overflow-y: auto;
  z-index: 1050;
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 10px;
  border-radius: 5px;
  font-size: 0.78rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.12s ease;
}

.dropdown-item:hover {
  background: #fefce8;
  color: #18181b;
}

.dropdown-item.active {
  background: #fef08a;
  color: #18181b;
  font-weight: 700;
}

.item-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-check {
  color: #854d0e;
  flex-shrink: 0;
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
