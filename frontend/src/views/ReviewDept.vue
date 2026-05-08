<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">部门审核</span>
      </div>
      <span class="top-count">待审核 {{ pendingList.length }} 条</span>
    </div>
    <div class="page-container">
      <div class="pc-card" v-if="pendingList.length === 0">
        <div style="text-align:center;padding:40px;color:#999">暂无待审核表单</div>
      </div>
      <table class="pc-table" v-if="pendingList.length > 0">
        <thead>
          <tr>
            <th>部门</th><th>周期</th><th>类型</th><th>填报人</th><th>更新时间</th><th style="width:180px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in pendingList" :key="f.id">
            <td><strong>{{ f.dept_name }}</strong></td>
            <td>{{ f.period_year }}年{{ f.period_month }}月</td>
            <td>{{ typeLabel(f.period_type) }}</td>
            <td>{{ f.filler_name || '-' }}</td>
            <td class="time-cell">{{ f.updated_at?.slice(0, 16) || '-' }}</td>
            <td>
              <button class="pc-btn pc-btn-primary pc-btn-sm" @click="showDetail(f)" style="margin-right:6px">查看</button>
              <button class="pc-btn pc-btn-success pc-btn-sm" @click="doReview(f, 'approve')" style="margin-right:4px">通过</button>
              <button class="pc-btn pc-btn-danger pc-btn-sm" @click="doReview(f, 'reject')">驳回</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Modal v-model:show="dialogShow" title="审核意见" :width="440" @confirm="confirmReview" :confirm-text="currentAction === 'approve' ? '确认通过' : '确认驳回'">
      <div class="dialog-form">
        <div class="df-item">
          <label class="df-label">操作</label>
          <span :style="{ color: currentAction === 'approve' ? '#2ba471' : '#e34d59', fontWeight: 600 }">{{ currentAction === 'approve' ? '通过' : '驳回' }}</span>
        </div>
        <div class="df-item">
          <label class="df-label">意见</label>
          <textarea class="df-textarea" v-model="comment" :placeholder="currentAction === 'reject' ? '驳回时必须填写审核意见' : '选填'"></textarea>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'
import { showToast, showSuccessToast } from '../utils/toast.js'
import Modal from '../components/Modal.vue'

const router = useRouter()
const pendingList = ref([])
const dialogShow = ref(false)
const comment = ref('')
const currentForm = ref(null)
const currentAction = ref('')
const typeLabel = (t) => ({ actual: '实际', planned: '预定', budget: '预算' }[t] || t)

const fetchPending = async () => {
  try { const { data } = await http.get('/forms/pending/dept'); pendingList.value = data } catch (e) {}
}
const doReview = (form, action) => { currentForm.value = form; currentAction.value = action; comment.value = ''; dialogShow.value = true }
const confirmReview = async () => {
  if (currentAction.value === 'reject' && !comment.value) { showToast('驳回时必须填写审核意见'); return }
  try {
    await http.put(`/forms/${currentForm.value.id}/dept-review`, { action: currentAction.value, comment: comment.value || null })
    showSuccessToast(currentAction.value === 'approve' ? '已通过' : '已驳回')
    dialogShow.value = false
    fetchPending()
  } catch (e) {}
}
const showDetail = (form) => router.push(`/form/${form.id}`)
onMounted(fetchPending)
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar { background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: #fff; }
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
.top-title { font-size: 17px; font-weight: 600; }
.top-count { font-size: 13px; opacity: 0.8; }
.time-cell { font-size: 12px; color: #999; }
.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.df-item { display: flex; align-items: flex-start; gap: 12px; }
.df-label { width: 60px; text-align: right; font-size: 14px; color: #555; flex-shrink: 0; padding-top: 8px; }
.df-textarea { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; min-height: 80px; resize: vertical; font-family: inherit; }
.df-textarea:focus { border-color: #1a73e8; }
</style>
