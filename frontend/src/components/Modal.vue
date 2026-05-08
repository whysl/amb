<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="show" @click.self="onClose">
      <div class="modal-panel" :style="width ? { maxWidth: width + 'px' } : {}">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <span class="modal-close" @click="onClose">&times;</span>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div class="modal-footer" v-if="$slots.footer">
          <slot name="footer" />
        </div>
        <div class="modal-footer" v-else-if="showFooter !== false">
          <button class="pc-btn pc-btn-default" @click="onClose">取消</button>
          <button class="pc-btn pc-btn-primary" @click="$emit('confirm')" style="margin-left:10px">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '' },
  width: { type: Number, default: 520 },
  confirmText: { type: String, default: '确定' },
  showFooter: { type: Boolean, default: true },
})

const emit = defineEmits(['update:show', 'confirm'])
const onClose = () => emit('update:show', false)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 80px;
  z-index: 3000;
}
.modal-panel {
  background: #fff;
  border-radius: 10px;
  width: 100%;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  animation: modal-in 0.2s ease;
}
@keyframes modal-in {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 22px 14px;
  border-bottom: 1px solid #f0f0f0;
}
.modal-header h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
}
.modal-close {
  font-size: 24px;
  color: #999;
  cursor: pointer;
  line-height: 1;
}
.modal-close:hover { color: #333; }
.modal-body {
  padding: 20px 22px;
  max-height: 60vh;
  overflow-y: auto;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 14px 22px 18px;
  border-top: 1px solid #f0f0f0;
}
</style>
