<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div v-for="t in toasts" :key="t.id" :class="['toast-item', 'toast-' + t.type]">
        {{ t.message }}
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let id = 0

function show(message, type = 'info', duration = 2500) {
  const item = { id: ++id, message, type }
  toasts.value.push(item)
  setTimeout(() => {
    const idx = toasts.value.findIndex(t => t.id === item.id)
    if (idx > -1) toasts.value.splice(idx, 1)
  }, duration)
}

defineExpose({ show })

window._toast = { show }
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}
.toast-item {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}
.toast-success { background: #2ba471; }
.toast-error { background: #e34d59; }
.toast-info { background: #1a73e8; }
.toast-warning { background: #ff9800; }

.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { opacity: 0; transform: translateY(-16px); }
.toast-leave-to { opacity: 0; transform: translateY(-16px); }
</style>
