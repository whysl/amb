<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">我的填报</span>
      </div>
    </div>
    <div class="page-container">
      <div class="pc-filter-bar">
        <label>年份</label>
        <input type="number" v-model="filterYear" placeholder="2026" />
        <label>月份</label>
        <input type="number" v-model="filterMonth" placeholder="4" />
        <button class="pc-btn pc-btn-primary pc-btn-sm" @click="fetchForms">查询</button>
        <button class="pc-btn pc-btn-success pc-btn-sm" @click="showNewDialog" style="margin-left:auto">+ 新建填报</button>
      </div>

      <div class="pc-card" v-if="forms.length === 0 && !loading">
        <div style="text-align:center;padding:40px;color:#999">
          <p style="font-size:16px;margin-bottom:8px">暂无填报记录</p>
          <p style="font-size:13px">点击右上角"+ 新建填报"开始在线填写数据</p>
        </div>
      </div>

      <table class="pc-table" v-if="forms.length > 0">
        <thead>
          <tr>
            <th>类型</th>
            <th>周期</th>
            <th>部门</th>
            <th>状态</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="form in forms" :key="form.id" style="cursor:pointer" @click="goForm(form.id)">
            <td>{{ typeLabel(form.period_type) }}</td>
            <td>{{ form.period_year }}年{{ form.period_month }}月</td>
            <td>{{ form.dept_name }}</td>
            <td><span :class="['pc-status-tag', 'pc-status-' + form.status]">{{ statusLabel(form.status) }}</span></td>
            <td class="time-cell">{{ form.updated_at?.slice(0, 16) || '-' }}</td>
            <td><button class="pc-btn pc-btn-primary pc-btn-sm" @click.stop="goForm(form.id)">查看</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <Modal v-model:show="dialogShow" title="新建填报" :width="420" @confirm="createNewForm">
      <div class="dialog-form">
        <div class="df-item" v-if="isAdmin">
          <label class="df-label">部门</label>
          <select class="df-select" v-model="newDeptId">
            <option v-for="d in deptOptions" :key="d.value" :value="d.value">{{ d.text }}</option>
          </select>
        </div>
        <div class="df-item">
          <label class="df-label">年份</label>
          <input type="number" class="df-input" v-model="newYear" />
        </div>
        <div class="df-item">
          <label class="df-label">月份</label>
          <input type="number" class="df-input" v-model="newMonth" />
        </div>
        <div class="df-item">
          <label class="df-label">类型</label>
          <select class="df-select" v-model="newPeriodType">
            <option v-for="o in newPeriodOptions" :key="o.value" :value="o.value">{{ o.text }}</option>
          </select>
        </div>
        <div class="period-hint" v-if="newPeriodType === 'planned'">
          系统将创建 <strong>{{ plannedYear }}年{{ plannedMonth }}月</strong> 的预定记录
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'
import { showToast, showSuccessToast } from '../utils/toast.js'
import Modal from '../components/Modal.vue'

const router = useRouter()
const forms = ref([])
const loading = ref(false)
const filterYear = ref(new Date().getFullYear())
const filterMonth = ref(new Date().getMonth() + 1)
const dialogShow = ref(false)
const newYear = ref(new Date().getFullYear())
const newMonth = ref(new Date().getMonth() + 1)
const newPeriodType = ref('actual')
const newDeptId = ref(null)
const deptOptions = ref([])
const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
const isAdmin = ref(userInfo.role === 'super_admin')
const newPeriodOptions = [
  { text: '本月实际', value: 'actual' },
  { text: '下月预定', value: 'planned' },
]

const plannedYear = computed(() => {
  if (newMonth.value === 12) return newYear.value + 1
  return newYear.value
})
const plannedMonth = computed(() => {
  if (newMonth.value === 12) return 1
  return newMonth.value + 1
})

const typeLabel = (t) => ({ actual: '实际', planned: '预定', budget: '预算' }[t] || t)
const statusLabel = (s) => {
  const map = { draft: '草稿', submitted: '待部门审核', dept_approved: '待公司审核', dept_rejected: '部门驳回', company_approved: '已通过', company_rejected: '公司驳回' }
  return map[s] || s
}

const fetchForms = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterYear.value) params.year = filterYear.value
    if (filterMonth.value) params.month = filterMonth.value
    const { data } = await http.get('/forms/my', { params })
    forms.value = data
  } catch (e) {} finally { loading.value = false }
}

const showNewDialog = () => {
  newYear.value = filterYear.value || new Date().getFullYear()
  newMonth.value = filterMonth.value || new Date().getMonth() + 1
  newPeriodType.value = 'actual'
  dialogShow.value = true
}

const createNewForm = async () => {
  try {
    let searchYear = Number(newYear.value)
    let searchMonth = Number(newMonth.value)
    if (newPeriodType.value === 'planned') {
      searchMonth += 1
      if (searchMonth > 12) {
        searchMonth = 1
        searchYear += 1
      }
    }
    const { data: periods } = await http.get('/periods')
    const periodList = Array.isArray(periods) ? periods : []
    const period = periodList.find(p => p.year === searchYear && p.month === searchMonth && p.period_type === newPeriodType.value)
    if (!period) {
      showToast(`未找到${searchYear}年${searchMonth}月的${typeLabel(newPeriodType.value)}周期，请先让管理员创建`)
      return
    }
    const { data } = await http.post('/forms', { period_id: period.id, items: [] }, { params: isAdmin.value && newDeptId.value ? { dept_id: newDeptId.value } : {} })
    showSuccessToast('创建成功')
    router.push(`/form/${data.form_id}`)
  } catch (e) {}
}

const goForm = (id) => router.push(`/form/${id}`)

onMounted(() => {
  fetchForms()
  if (isAdmin.value) {
    http.get('/org/departments').then(({ data }) => {
      deptOptions.value = data.filter(d => d.level >= 2).map(d => ({ text: d.name, value: d.id }))
    }).catch(() => {})
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar {
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  padding: 12px 20px; display: flex; align-items: center; color: #fff;
}
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
.top-title { font-size: 17px; font-weight: 600; }
.time-cell { font-size: 12px; color: #999; }
.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.df-item { display: flex; align-items: center; gap: 12px; }
.df-label { width: 60px; text-align: right; font-size: 14px; color: #555; flex-shrink: 0; }
.df-input { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; }
.df-input:focus { border-color: #1a73e8; }
.df-select { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; background: #fff; }
.df-select:focus { border-color: #1a73e8; }
.period-hint {
  background: #e8f0fe; color: #1a73e8; padding: 8px 12px;
  border-radius: 6px; font-size: 13px; text-align: center;
}
</style>
