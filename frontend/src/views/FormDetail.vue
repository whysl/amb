<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">填报表单</span>
      </div>
      <div class="top-right">
        <button class="pc-btn pc-btn-default pc-btn-sm" @click="saveForm" :disabled="saving">
          {{ saving ? '保存中...' : '保存草稿' }}
        </button>
        <button class="pc-btn pc-btn-primary pc-btn-sm" @click="submitForm" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交审核' }}
        </button>
      </div>
    </div>
    <div class="page-container">
      <div class="pc-card form-info-bar">
        <span class="fi-dept">{{ deptName }}</span>
        <span class="fi-period">{{ periodInfo }}</span>
        <span :class="['pc-status-tag', 'pc-status-' + form.status]">{{ statusLabel(form.status) }}</span>
        <button v-if="showBudgetRef && hasBudgetData" class="pc-btn pc-btn-default pc-btn-sm" @click="fillFromBudget" style="margin-left:auto">填入预算数据</button>
      </div>

      <div v-if="form.dept_review_comment" class="review-bar dept-bar">
        <strong>部门审核意见：</strong>{{ form.dept_review_comment }}
      </div>
      <div v-if="form.company_review_comment" class="review-bar company-bar">
        <strong>公司审核意见：</strong>{{ form.company_review_comment }}
      </div>

      <table class="pc-table form-table">
        <thead>
          <tr>
            <th style="width:70px">编码</th>
            <th style="width:200px;text-align:left">科目名称</th>
            <th style="width:150px">数值</th>
            <th style="width:50px">单位</th>
            <th style="width:110px;text-align:right" v-if="showBudgetRef">预算参考</th>
            <th style="text-align:left">备注</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="group in groupedSubjects" :key="group.category">
            <tr class="section-header">
              <td :colspan="showBudgetRef ? 6 : 5">{{ group.category }}</td>
            </tr>
            <tr v-for="s in group.subjects" :key="s.id">
              <td :class="{ calculated: s.is_calculated }">{{ s.code }}</td>
              <td style="text-align:left">{{ s.name }}</td>
              <td>
                <input class="f-input" :class="{ readonly: s.is_calculated }" type="number" step="0.01"
                  :placeholder="s.is_calculated ? '自动计算' : budgetPlaceholder(s)" :readonly="s.is_calculated"
                  :value="rawValues[s.id] ?? ''" @input="(e) => onInput(s.id, e.target.value)" />
              </td>
              <td class="unit-cell">{{ s.unit }}</td>
              <td style="text-align:right;font-size:12px;color:#999" v-if="showBudgetRef && !s.is_calculated">
                {{ fmtBudget(s.subject_id || s.id) }}
              </td>
              <td v-else-if="showBudgetRef"></td>
              <td>
                <input v-if="!s.is_calculated" class="remark-input" :value="remarks[s.id] ?? ''" placeholder="备注"
                  @input="(e) => remarks[s.id] = e.target.value" />
              </td>
            </tr>
          </template>
        </tbody>
      </table>

      <div class="pc-card" style="text-align:center">
        <button class="pc-btn pc-btn-default" @click="saveForm" :disabled="saving" style="margin-right:12px">
          {{ saving ? '保存中...' : '保存草稿' }}
        </button>
        <button class="pc-btn pc-btn-primary" @click="submitForm" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交审核' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '../api/http'
import { showToast, showSuccessToast } from '../utils/toast.js'

const route = useRoute()
const router = useRouter()
const formId = route.params.formId
const isNew = formId === 'new'

const form = reactive({
  id: null, period_id: null, department_id: null, dept_code: '', status: 'draft',
  dept_review_comment: '', company_review_comment: '',
  period_year: '', period_month: '', period_type: '',
  items: [],
})
const deptName = ref('')
const periodInfo = ref('')
const subjects = ref([])
const rawValues = reactive({})
const remarks = reactive({})
const budgetValues = reactive({})
const saving = ref(false)
const submitting = ref(false)

const showBudgetRef = computed(() => form.period_type === 'planned' || form.period_type === 'budget')

const hasBudgetData = computed(() => {
  return Object.keys(budgetValues).length > 0 && Object.values(budgetValues).some(v => v !== undefined && v !== null && v !== 0)
})

const groupedSubjects = computed(() => {
  const groups = {}
  const order = ['收入', '变动费用', '边界利益', '固定费用', '附加价值', '时间', '重要指标', '人工费']
  for (const s of subjects.value) {
    const cat = s.category || '其他'
    if (!groups[cat]) groups[cat] = { category: cat, subjects: [] }
    groups[cat].subjects.push(s)
  }
  return order.filter(o => groups[o]).map(o => groups[o])
})

const statusLabel = (s) => {
  const map = { draft: '草稿', submitted: '待部门审核', dept_approved: '待公司审核', dept_rejected: '部门驳回', company_approved: '已通过', company_rejected: '公司驳回' }
  return map[s] || s
}

const onInput = (subjectId, raw) => {
  rawValues[subjectId] = raw
  recalcAll()
}

const recalcAll = () => {
  for (const s of subjects.value) {
    if (s.is_calculated && s.formula) {
      try {
        let expr = s.formula
        for (const other of subjects.value) {
          const v = parseFloat(rawValues[other.id]) || 0
          expr = expr.replace(new RegExp('\\b' + other.code + '\\b', 'g'), String(v))
        }
        if (/[^0-9+\-*/.()\s]/.test(expr)) throw new Error('Invalid expression')
        const result = new Function('return ' + expr)()
        rawValues[s.id] = Math.abs(result) < 0.001 ? '0' : String(Math.round(result * 100) / 100)
      } catch (e) {
        rawValues[s.id] = ''
      }
    }
  }
}

const fetchSubjects = async () => {
  try {
    const { data } = await http.get('/org/my-department/subjects')
    subjects.value = data
    for (const s of data) {
      rawValues[s.id] = ''
      remarks[s.id] = ''
    }
  } catch (e) {}
}

const fetchBudgetRef = async () => {
  if (!showBudgetRef.value) return
  try {
    const params = { year: form.period_year }
    const { data } = await http.get(`/budget/${form.department_id}`, { params })
    for (const row of data.rows) {
      if (row.months && row.months[form.period_month] !== undefined) {
        budgetValues[row.subject_id] = row.months[form.period_month]
      }
    }
  } catch (e) {}
}

const fmtBudget = (sid) => {
  const v = budgetValues[sid]
  if (v === undefined || v === null) return '-'
  if (Math.abs(v) >= 10000) return (v / 10000).toFixed(2) + '万'
  return Number.isInteger(v) ? v.toLocaleString() : v.toFixed(2)
}

const fillFromBudget = () => {
  for (const s of subjects.value) {
    if (s.is_calculated) continue
    const v = budgetValues[s.id]
    if (v !== undefined && v !== null) {
      rawValues[s.id] = String(v)
    }
  }
  recalcAll()
  showSuccessToast('已填入预算数据，请核对后保存')
}

const budgetPlaceholder = (s) => {
  const v = budgetValues[s.id]
  if (v !== undefined && v !== null && v !== 0) return `预算: ${fmtBudget(s.id)}`
  return '请输入'
}

const fetchForm = async (id) => {
  try {
    const { data } = await http.get(`/forms/${id}`)
    Object.assign(form, data)
    deptName.value = data.dept_name || ''
    periodInfo.value = `${data.period_year}年${data.period_month}月 · ${({ actual: '实际', planned: '预定', budget: '预算' })[data.period_type] || data.period_type}`
    if (data.items) {
      for (const item of data.items) {
        rawValues[item.subject_id] = item.value !== null ? String(item.value) : ''
        remarks[item.subject_id] = item.remark || ''
      }
    }
    recalcAll()
    fetchBudgetRef()
  } catch (e) {}
}

const saveForm = async () => {
  saving.value = true
  try {
    const items = []
    for (const s of subjects.value) {
      const v = rawValues[s.id]
      if (v !== '' && v !== null && v !== undefined) {
        items.push({ subject_id: s.id, value: parseFloat(v), remark: remarks[s.id] || null })
      }
    }
    await http.post('/forms', { period_id: form.period_id, items })
    showSuccessToast('保存成功')
  } catch (e) {} finally { saving.value = false }
}

const submitForm = async () => {
  if (!form.id) {
    await saveForm()
    showToast('请先保存草稿后再提交')
    return
  }
  submitting.value = true
  try {
    await http.put(`/forms/${form.id}/submit`)
    showSuccessToast('提交成功')
    router.push('/forms')
  } catch (e) {} finally { submitting.value = false }
}

onMounted(async () => {
  await fetchSubjects()
  if (!isNew) {
    await fetchForm(formId)
  } else {
    const info = JSON.parse(localStorage.getItem('user_info') || '{}')
    deptName.value = info.dept_name || ''
  }
})
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar {
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; padding: 0 4px; }
.top-title { font-size: 17px; font-weight: 600; }
.top-right { display: flex; gap: 8px; }
.form-info-bar { display: flex; align-items: center; gap: 12px; }
.fi-dept { font-size: 18px; font-weight: 700; }
.fi-period { background: #e8f0fe; color: #1a73e8; padding: 3px 12px; border-radius: 4px; font-size: 13px; }
.form-table { margin-bottom: 0; }
.form-table th { position: sticky; top: 0; z-index: 10; }
.form-table td { vertical-align: middle; padding: 6px 10px; }
.form-table .calculated { color: #1a73e8; font-weight: 600; }
.f-input {
  width: 100%; border: 1px solid #e0e0e0; border-radius: 4px;
  padding: 7px 10px; font-size: 13px; text-align: right; outline: none;
}
.f-input:focus { border-color: #1a73e8; }
.f-input.readonly { background: #f5f7fa; color: #1a73e8; font-weight: 600; }
.unit-cell { color: #999; font-size: 12px; }
.remark-input {
  width: 100%; border: 1px solid #e0e0e0; border-radius: 4px;
  padding: 6px 8px; font-size: 12px; outline: none;
}
.remark-input:focus { border-color: #1a73e8; }
.review-bar { padding: 10px 16px; border-radius: 6px; margin-bottom: 12px; font-size: 13px; }
.dept-bar { background: #fff3e0; color: #e65100; }
.company-bar { background: #fce4ec; color: #c62828; }
</style>
