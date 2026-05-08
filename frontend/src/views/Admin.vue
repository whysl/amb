<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">系统管理</span>
      </div>
    </div>
    <div class="page-container">
      <div class="tab-bar">
        <div :class="['tab-item', { active: activeTab === 0 }]" @click="activeTab = 0">周期管理</div>
        <div :class="['tab-item', { active: activeTab === 1 }]" @click="activeTab = 1">用户管理</div>
        <div :class="['tab-item', { active: activeTab === 2 }]" @click="activeTab = 2">预算管理</div>
      </div>

      <div v-show="activeTab === 0">
        <div class="pc-card">
          <div class="form-row">
            <label>年份</label><input type="number" v-model="newYear" placeholder="2026" />
            <label>月份</label><input type="number" v-model="newMonth" placeholder="4" />
            <button class="pc-btn pc-btn-primary" @click="createPeriod" :disabled="creating">
              {{ creating ? '创建中...' : '创建月度周期（本月实际+下月预定）' }}
            </button>
          </div>
        </div>
        <table class="pc-table">
          <thead><tr><th>年份</th><th>月份</th><th>类型</th><th>状态</th><th>填报数</th><th>创建时间</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="p in periods" :key="p.id">
              <td>{{ p.year }}</td><td>{{ p.month }}</td>
              <td>{{ typeLabel(p.period_type) }}</td>
              <td>{{ p.status === 'open' ? '开放' : '关闭' }}</td>
              <td>
                <span
                  v-if="(p.form_count ?? 0) > 0"
                  class="form-count-link"
                  @click="showPeriodForms(p)"
                >{{ p.form_count }}</span>
                <span v-else>0</span>
              </td>
              <td class="time-cell">{{ p.created_at?.slice(0, 16) || '-' }}</td>
              <td>
                <button
                  class="pc-btn pc-btn-danger pc-btn-sm"
                  :disabled="(p.form_count ?? 0) > 0"
                  @click="deletePeriod(p)"
                >删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-show="activeTab === 1">
        <div class="pc-card" style="margin-bottom:12px">
          <button class="pc-btn pc-btn-primary" @click="showUserDialog()">+ 新建用户</button>
        </div>
        <table class="pc-table">
          <thead><tr><th>用户名</th><th>姓名</th><th>角色</th><th>部门</th><th>手机号</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.username }}</td><td>{{ u.real_name }}</td>
              <td>{{ roleLabel(u.role) }}</td><td>{{ u.dept_name || '-' }}</td>
              <td>{{ u.phone || '-' }}</td>
              <td><span :class="['pc-status-tag', u.is_active ? 'pc-status-company_approved' : 'pc-status-dept_rejected']">{{ u.is_active ? '启用' : '禁用' }}</span></td>
              <td><button class="pc-btn pc-btn-primary pc-btn-sm" @click="showUserDialog(u)">编辑</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-show="activeTab === 2">
        <div class="pc-card">
          <div class="form-row">
            <label>部门</label>
            <select v-model="budgetDeptId" class="df-select" style="width:180px" @change="loadBudget">
              <option v-for="d in budgetDeptOptions" :key="d.value" :value="d.value">{{ d.text }}</option>
            </select>
            <label>年份</label>
            <input type="number" v-model="budgetYear" style="width:80px" />
            <button class="pc-btn pc-btn-primary pc-btn-sm" @click="loadBudget">加载预算</button>
            <button class="pc-btn pc-btn-success pc-btn-sm" @click="saveBudget" :disabled="budgetSaving" style="margin-left:auto">{{ budgetSaving ? '保存中...' : '保存预算' }}</button>
            <button class="pc-btn pc-btn-warning pc-btn-sm" @click="syncBudgetToForms" :disabled="budgetSyncing">{{ budgetSyncing ? '同步中...' : '同步到填报' }}</button>
            <span class="divider">|</span>
            <button class="pc-btn pc-btn-default pc-btn-sm" @click="downloadTemplate" title="下载Excel模板">下载模板</button>
            <button class="pc-btn pc-btn-default pc-btn-sm" @click="triggerImport" title="从Excel导入预算数据">导入Excel</button>
            <input type="file" ref="fileInput" accept=".xlsx,.xls" style="display:none" @change="handleFileImport" />
          </div>
        </div>

        <div class="pc-card" v-if="budgetRows.length > 0" style="overflow-x:auto;padding:0">
          <div class="budget-toolbar">
            <span class="budget-dept-name">{{ budgetDeptName }}</span>
            <span class="budget-year-label">{{ budgetYear }}年预算</span>
            <span class="budget-hint">直接在下表中填写各月预算金额，完成后点击"保存预算"</span>
          </div>
          <table class="pc-table budget-table">
            <thead>
              <tr>
                <th style="min-width:55px">编码</th>
                <th style="min-width:130px;text-align:left">科目名称</th>
                <th style="min-width:60px">类别</th>
                <th style="min-width:90px" v-for="m in 12" :key="m">{{ m }}月</th>
                <th style="min-width:100px">年度合计</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="group in budgetGrouped" :key="group.category">
                <tr class="section-header">
                  <td :colspan="16">{{ group.category }}</td>
                </tr>
                <tr v-for="row in group.rows" :key="row.subject_code">
                  <td>{{ row.subject_code }}</td>
                  <td style="text-align:left">{{ row.subject_name }}</td>
                  <td style="font-size:12px;color:#888">{{ row.category }}</td>
                  <td v-for="m in 12" :key="m">
                    <input type="number" step="0.01" class="budget-cell" v-model.number="row.months[m]" @focus="onBudgetCellFocus($event)" />
                  </td>
                  <td class="budget-year-total">{{ fmtBudgetTotal(row) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <div class="pc-card" v-else-if="budgetDeptId">
          <div style="text-align:center;padding:40px;color:#999">选择部门和年份后点击"加载预算"开始在线编辑</div>
        </div>
        <div class="pc-card" v-else>
          <div style="text-align:center;padding:40px;color:#999">请先选择部门，然后点击"加载预算"进行在线编辑</div>
        </div>
      </div>
    </div>

    <Modal v-model:show="userDialogShow" :title="editingUser ? '编辑用户' : '新建用户'" :width="480" @confirm="saveUser">
      <div class="dialog-form">
        <div class="df-item">
          <label class="df-label">用户名</label>
          <input class="df-input" v-model="userForm.username" placeholder="请输入用户名" :disabled="!!editingUser" />
        </div>
        <div class="df-item">
          <label class="df-label">密码</label>
          <input class="df-input" v-model="userForm.password" type="password" :placeholder="editingUser ? '留空不修改' : '默认1234'" />
        </div>
        <div class="df-item">
          <label class="df-label">姓名</label>
          <input class="df-input" v-model="userForm.real_name" placeholder="请输入姓名" />
        </div>
        <div class="df-item">
          <label class="df-label">角色</label>
          <select class="df-select" v-model="userForm.role">
            <option v-for="o in roleOptions" :key="o.value" :value="o.value">{{ o.text }}</option>
          </select>
        </div>
        <div class="df-item">
          <label class="df-label">部门</label>
          <select class="df-select" v-model="userForm.department_id">
            <option :value="null">不分配</option>
            <option v-for="d in deptSelectOptions" :key="d.value" :value="d.value">{{ d.text }}</option>
          </select>
        </div>
        <div class="df-item">
          <label class="df-label">手机号</label>
          <input class="df-input" v-model="userForm.phone" placeholder="选填" />
        </div>
        <div v-if="editingUser" class="df-item">
          <label class="df-label">状态</label>
          <div style="display:flex;align-items:center;gap:16px">
            <button class="pc-btn pc-btn-warning pc-btn-sm" @click="resetPassword">重置密码为1234</button>
            <label class="switch-label">
              <input type="checkbox" v-model="userForm.is_active" />
              <span>{{ userForm.is_active ? '启用' : '禁用' }}</span>
            </label>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-model:show="resetPwdShow" title="重置密码" :width="360" @confirm="confirmResetPwd" confirm-text="确认重置">
      <div style="text-align:center;padding:16px;font-size:14px">确定要将该用户密码重置为 <strong>1234</strong> 吗？</div>
    </Modal>

    <Modal v-model:show="formsModalShow" :title="`${formsModalTitle} — 填报列表`" :width="700" :show-footer="false">
      <table class="pc-table" v-if="periodForms.length > 0">
        <thead>
          <tr>
            <th>部门</th>
            <th>填报人</th>
            <th>状态</th>
            <th>更新时间</th>
            <th style="width:120px">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in periodForms" :key="f.id">
            <td>{{ f.dept_name }}</td>
            <td>{{ f.filler_name || '-' }}</td>
            <td><span :class="['pc-status-tag', 'pc-status-' + f.status]">{{ statusLabel(f.status) }}</span></td>
            <td class="time-cell">{{ f.updated_at?.slice(0, 16) || '-' }}</td>
            <td>
              <button class="pc-btn pc-btn-primary pc-btn-sm" @click="goFormDetail(f.id)" style="margin-right:4px">查看</button>
              <button class="pc-btn pc-btn-danger pc-btn-sm" @click="forceDeleteForm(f)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else style="text-align:center;padding:30px;color:#999">该周期下暂无填报</div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'
import { showSuccessToast } from '../utils/toast.js'
import Modal from '../components/Modal.vue'

const router = useRouter()
const activeTab = ref(0)
const newYear = ref(new Date().getFullYear())
const newMonth = ref(new Date().getMonth() + 1)
const creating = ref(false)
const periods = ref([])
const users = ref([])
const userDialogShow = ref(false)
const editingUser = ref(null)
const resetPwdShow = ref(false)
const formsModalShow = ref(false)
const formsModalTitle = ref('')
const periodForms = ref([])
const budgetDeptId = ref(null)
const budgetYear = ref(new Date().getFullYear())
const budgetRows = ref([])
const budgetDeptName = ref('')
const budgetSaving = ref(false)
const budgetSyncing = ref(false)
const budgetDeptOptions = ref([])
const fileInput = ref(null)

const budgetGrouped = computed(() => {
  const order = ['收入', '变动费用', '固定费用', '时间', '重要指标', '人工费']
  const groups = {}
  for (const row of budgetRows.value) {
    const cat = row.category || '其他'
    if (!groups[cat]) groups[cat] = { category: cat, rows: [] }
    groups[cat].rows.push(row)
  }
  return order.filter(o => groups[o]).map(o => groups[o])
})

const fmtBudgetTotal = (row) => {
  let total = 0
  for (let m = 1; m <= 12; m++) {
    total += Number(row.months[m]) || 0
  }
  if (Math.abs(total) >= 10000) return (total / 10000).toFixed(2) + '万'
  return total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const onBudgetCellFocus = (e) => {
  e.target.select()
}

const roleOptions = [
  { text: '部门填报人', value: 'dept_filler' },
  { text: '部门审核人', value: 'dept_reviewer' },
  { text: '公司审核人', value: 'company_reviewer' },
  { text: '系统管理员', value: 'super_admin' },
]
const deptSelectOptions = ref([])
const userForm = ref({ username: '', password: '', real_name: '', role: 'dept_filler', department_id: null, phone: '', is_active: true })

const typeLabel = (t) => ({ actual: '实际', planned: '预定', budget: '预算' }[t] || t)
const roleLabel = (r) => ({ dept_filler: '填报人', dept_reviewer: '审核人', company_reviewer: '公司审核人', super_admin: '管理员' }[r] || r)

const fetchPeriods = async () => { try { const { data } = await http.get('/periods'); periods.value = data } catch (e) {} }
const createPeriod = async () => {
  if (!newYear.value || !newMonth.value) return
  creating.value = true
  try {
    await http.post('/periods/create-monthly', null, { params: { year: newYear.value, month: newMonth.value } })
    showSuccessToast('创建成功')
    fetchPeriods()
  } catch (e) {} finally { creating.value = false }
}
const deletePeriod = async (p) => {
  if (!confirm(`确定要删除 ${p.year}年${p.month}月 ${typeLabel(p.period_type)} 周期吗？此操作不可撤销。`)) return
  try {
    await http.delete(`/periods/${p.id}`)
    showSuccessToast('删除成功')
    fetchPeriods()
  } catch (e) {}
}
const showPeriodForms = async (p) => {
  formsModalTitle.value = `${p.year}年${p.month}月 ${typeLabel(p.period_type)}`
  formsModalShow.value = true
  try {
    const { data } = await http.get(`/forms/by-period/${p.id}`)
    periodForms.value = data
  } catch (e) { periodForms.value = [] }
}
const forceDeleteForm = async (f) => {
  if (!confirm(`确定要删除 ${f.dept_name} 的填报吗？此操作不可撤销。`)) return
  try {
    await http.delete(`/forms/${f.id}/force`)
    showSuccessToast('删除成功')
    periodForms.value = periodForms.value.filter(x => x.id !== f.id)
    fetchPeriods()
  } catch (e) {}
}
const goFormDetail = (id) => { formsModalShow.value = false; router.push(`/form/${id}`) }
const loadBudget = async () => {
  if (!budgetDeptId.value || !budgetYear.value) return
  try {
    const { data } = await http.get(`/budget/${budgetDeptId.value}`, { params: { year: budgetYear.value } })
    budgetRows.value = data.rows || []
    budgetDeptName.value = data.department_name || ''
  } catch (e) { budgetRows.value = [] }
}
const saveBudget = async () => {
  if (!budgetDeptId.value || !budgetYear.value) return
  budgetSaving.value = true
  try {
    const rows = budgetRows.value.map(r => ({
      subject_code: r.subject_code,
      jan: r.months[1] || 0, feb: r.months[2] || 0, mar: r.months[3] || 0,
      apr: r.months[4] || 0, may: r.months[5] || 0, jun: r.months[6] || 0,
      jul: r.months[7] || 0, aug: r.months[8] || 0, sep: r.months[9] || 0,
      oct: r.months[10] || 0, nov: r.months[11] || 0, dec: r.months[12] || 0,
    }))
    await http.put(`/budget/${budgetDeptId.value}`, { department_id: budgetDeptId.value, year: budgetYear.value, rows })
    showSuccessToast('预算保存成功')
  } catch (e) {} finally { budgetSaving.value = false }
}
const syncBudgetToForms = async () => {
  if (!budgetYear.value) return
  if (!confirm(`确定要将 ${budgetYear.value} 年预算同步到各部门的每月预算表单吗？`)) return
  budgetSyncing.value = true
  try {
    const { data } = await http.post(`/budget/sync-to-forms/${budgetYear.value}`)
    showSuccessToast(data.message)
  } catch (e) {} finally { budgetSyncing.value = false }
}
const downloadTemplate = () => {
  if (!budgetDeptId.value) { showSuccessToast('请先选择部门'); return }
  const token = localStorage.getItem('access_token')
  window.open(`/api/budget/template/${budgetDeptId.value}?year=${budgetYear.value}&token=${token}`)
}
const triggerImport = () => {
  if (!budgetDeptId.value) { showSuccessToast('请先选择部门'); return }
  fileInput.value?.click()
}
const handleFileImport = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  if (!confirm(`确定要导入 ${file.name} 到当前部门吗？这将覆盖该部门 ${budgetYear.value} 年的现有预算数据。`)) {
    fileInput.value.value = ''
    return
  }
  const form = new FormData()
  form.append('file', file)
  try {
    const { data } = await http.post(`/budget/import/${budgetDeptId.value}?year=${budgetYear.value}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    showSuccessToast(data.message)
    loadBudget()
  } catch (e) {}
  fileInput.value.value = ''
}
const statusLabel = (s) => {
  const map = { draft: '草稿', submitted: '待部门审核', dept_approved: '待公司审核', dept_rejected: '部门驳回', company_approved: '已通过', company_rejected: '公司驳回' }
  return map[s] || s
}
const fetchUsers = async () => { try { const { data } = await http.get('/auth/users'); users.value = data } catch (e) {} }
const fetchDepts = async () => { try { const { data } = await http.get('/org/departments'); deptSelectOptions.value = data.map(d => ({ text: d.name, value: d.id })); budgetDeptOptions.value = data.filter(d => d.level >= 2).map(d => ({ text: d.name, value: d.id })) } catch (e) {} }

const showUserDialog = (user = null) => {
  editingUser.value = user
  userForm.value = user
    ? { username: user.username, password: '', real_name: user.real_name, role: user.role, department_id: user.department_id, phone: user.phone || '', is_active: user.is_active }
    : { username: '', password: '', real_name: '', role: 'dept_filler', department_id: null, phone: '', is_active: true }
  userDialogShow.value = true
}

const saveUser = async () => {
  try {
    const sendPayload = { ...userForm.value }
    if (!sendPayload.password) delete sendPayload.password
    if (!sendPayload.department_id) sendPayload.department_id = null
    if (editingUser.value) {
      await http.put(`/auth/users/${editingUser.value.id}`, sendPayload)
    } else {
      if (!sendPayload.password) sendPayload.password = '1234'
      await http.post('/auth/users', sendPayload)
    }
    showSuccessToast('保存成功')
    userDialogShow.value = false
    fetchUsers()
  } catch (e) {}
}

const resetPassword = () => { resetPwdShow.value = true }
const confirmResetPwd = async () => {
  try {
    await http.put(`/auth/users/${editingUser.value.id}/password`, { new_password: '1234' })
    showSuccessToast('密码已重置为1234')
    resetPwdShow.value = false
  } catch (e) {}
}

onMounted(() => { fetchPeriods(); fetchUsers(); fetchDepts() })
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar { background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%); padding: 12px 20px; display: flex; align-items: center; color: #fff; }
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
.top-title { font-size: 17px; font-weight: 600; }
.tab-bar { display: flex; background: #fff; border-radius: 8px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.tab-item { flex: 1; text-align: center; padding: 12px; cursor: pointer; font-size: 14px; font-weight: 500; color: #666; border-bottom: 2px solid transparent; transition: all .2s; }
.tab-item.active { color: #1a73e8; border-bottom-color: #1a73e8; background: #f0f6ff; }
.tab-item:hover { background: #f8f9ff; }
.time-cell { font-size: 12px; color: #999; }
.form-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.form-row label { font-size: 14px; color: #666; }
.form-row input[type="number"] { width: 80px; padding: 7px 10px; border: 1px solid #d0d0d0; border-radius: 4px; font-size: 14px; }
.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.df-item { display: flex; align-items: center; gap: 12px; }
.df-label { width: 70px; text-align: right; font-size: 14px; color: #555; flex-shrink: 0; }
.df-input { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; }
.df-input:focus { border-color: #1a73e8; }
.df-input:disabled { background: #f5f5f5; color: #999; }
.df-select { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; background: #fff; }
.df-select:focus { border-color: #1a73e8; }
.switch-label { display: flex; align-items: center; gap: 6px; font-size: 14px; cursor: pointer; }
.form-count-link { color: #1a73e8; font-weight: 700; cursor: pointer; text-decoration: underline; }
.form-count-link:hover { color: #e34d59; }
.budget-cell { width: 80px; padding: 5px; border: 1px solid #e0e0e0; border-radius: 3px; font-size: 12px; text-align: right; outline: none; }
.budget-cell:focus { border-color: #1a73e8; box-shadow: 0 0 0 2px rgba(26,115,232,0.15); }
.budget-toolbar {
  display: flex; align-items: center; gap: 16px;
  padding: 10px 16px; background: #f8f9ff; border-bottom: 1px solid #e8e8e8;
}
.budget-dept-name { font-weight: 700; font-size: 15px; color: #1a73e8; }
.budget-year-label { font-size: 13px; color: #666; background: #e8f0fe; padding: 2px 10px; border-radius: 10px; }
.budget-hint { font-size: 12px; color: #999; margin-left: auto; }
.budget-table { font-size: 12px; }
.budget-table th { position: sticky; top: 0; z-index: 2; }
.budget-year-total { text-align: right; font-weight: 600; font-size: 12px; color: #1a73e8; }
.divider { color: #d0d0d0; font-size: 16px; margin: 0 4px; }
</style>
